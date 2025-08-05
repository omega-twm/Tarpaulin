import os
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from fastapi.responses import StreamingResponse
import httpx

from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from langchain.schema import Document
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.callbacks.tracers import LangChainTracer
from langchain.callbacks.manager import CallbackManager

from canvas_service import get_user_courses, get_course_assignments, get_course_files, fetch_student_context

load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "true"

tracer = LangChainTracer()
cb_manager = CallbackManager([tracer])

app = FastAPI(title="Canvas RAG Service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

documents = []
vectordb = None

class QARequest(BaseModel):
    query: str

def strip_html(text: str) -> str:
    return re.sub(r"<[^>]*>", "", text)

def print_box(text: str, title: str = "", width: int = 60) -> None:
    """Print text in a nice ASCII box with proper text wrapping"""
    import textwrap
    
    # Wrap long lines
    wrapped_lines = []
    for line in text.split('\n'):
        if len(line) <= width - 4:
            wrapped_lines.append(line)
        else:
            # Wrap long lines
            wrapped = textwrap.wrap(line, width=width-4, break_long_words=False, break_on_hyphens=False)
            wrapped_lines.extend(wrapped)
    
    # Calculate box width
    content_width = max(len(line) for line in wrapped_lines) if wrapped_lines else 0
    if title:
        content_width = max(content_width, len(title) + 4)
    
    box_width = min(max(content_width + 4, 30), width)
    
    # Top border
    if title:
        title_padding = (box_width - len(title) - 4) // 2
        remaining_padding = box_width - len(title) - 4 - title_padding
        print(f"┌{title_padding * '─'} {title} {remaining_padding * '─'}┐")
    else:
        print(f"┌{'─' * (box_width - 2)}┐")
    
    # Content
    for line in wrapped_lines:
        padding = box_width - len(line) - 4
        print(f"│ {line}{' ' * padding} │")
    
    # Bottom border
    print(f"└{'─' * (box_width - 2)}┘")

def filter_actual_courses(courses):
    """Filter out information hub courses that aren't actual academic courses"""
    excluded_keywords = [
        'studentdemokratiet',
        'velkommen',
        'welcome',
        'informasjon',
        'information',
        'engasjement',
        'all you need to know',
        'alt du trenger å vite',
        'b-inf',
        'ifi'
    ]
    
    excluded_course_codes = [
        'b-inf',
        'ifi',
        'informasjon og engasjement',
        'alt du trenger å vite - all you need to know'
    ]
    
    filtered_courses = []
    for course in courses:
        course_name = course.get('name', '').lower()
        course_code = course.get('course_code', '').lower()
        
        # Check if course name or code contains excluded keywords
        is_info_hub = (
            any(keyword in course_name or keyword in course_code 
                for keyword in excluded_keywords) or
            course_code in excluded_course_codes or
            course_name in ['b-inf', 'ifi']
        )
        
        if not is_info_hub:
            filtered_courses.append(course)
    
    return filtered_courses

@app.on_event("startup")
async def startup_event():
    global documents, vectordb
    try:
        print_box("Fetching Canvas courses...", "STARTUP")
        all_courses = await get_user_courses()
        courses = filter_actual_courses(all_courses)  # Filter out info hubs
        
        filter_msg = f"Filtered courses: {len(courses)}/{len(all_courses)}\nExcluded information hubs"
        print_box(filter_msg, "COURSE FILTERING")
        
        documents.clear()

        for course in courses:
            cid = course["id"]
            cname = course.get("name", "")
            ccode = course.get("course_code", "")
            documents.append(Document(
                page_content=f"Kurs: {cname} ({ccode})",
                metadata={"type": "course", "course_id": cid}
            ))

            # Assignments (obliger)
            print_box(f"Fetching assignments for:\n{cname}", "ASSIGNMENTS")
            assignments = await get_course_assignments(cid)
            for a in assignments:
                content = f"{a.get('name', '')}\n{strip_html(a.get('description', ''))}"
                documents.append(Document(
                    page_content=content,
                    metadata={"type": "assignment", "course_id": cid, "assignment_id": a.get("id")}
                ))

            # Filer
            print_box(f"Fetching files for:\n{cname}", "FILES")
            files = await get_course_files(cid)
            for f in files:
                file_text = f"{f.get('display_name')} ({f.get('size')} bytes)"
                documents.append(Document(
                    page_content=file_text,
                    metadata={"type": "file", "course_id": cid, "file_id": f.get("id")}
                ))

        doc_summary = f"Total documents loaded: {len(documents)}"
        print_box(doc_summary, "DOCUMENT SUMMARY")
        
        if not documents:
            raise ValueError("No documents to embed")

        persist_dir = os.getenv("CHROMA_DB_DIR")
        
        # Check if vector database already exists
        try:
            # Try to load existing vector database first
            print_box("Checking for existing vector database...", "DATABASE CHECK")
            
            # For Groq, we'll use sentence-transformers for embeddings since Groq doesn't support embeddings
            if os.getenv("OPENAI_BASE_URL") and "groq" in os.getenv("OPENAI_BASE_URL").lower():
                print_box("Using local embeddings for Groq...", "EMBEDDINGS")
                from langchain_huggingface import HuggingFaceEmbeddings
                embeddings = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2",
                    model_kwargs={'device': 'cpu'}
                )
            else:
                # Use OpenAI embeddings for regular OpenAI API
                embeddings_kwargs = {"api_key": os.getenv("OPENAI_API_KEY")}
                if os.getenv("OPENAI_BASE_URL"):
                    embeddings_kwargs["base_url"] = os.getenv("OPENAI_BASE_URL")
                embeddings = OpenAIEmbeddings(**embeddings_kwargs)
            
            # Try to load existing database
            vectordb = Chroma(
                persist_directory=persist_dir,
                embedding_function=embeddings
            )
            
            # Check if database has documents by trying to get collection info
            collection = vectordb._collection
            if collection.count() > 0:
                cache_msg = f"Found existing vector database\nDocument count: {collection.count()}\nSkipping embedding creation"
                print_box(cache_msg, "CACHE HIT")
                return
            else:
                print_box("Empty vector database found\nWill recreate embeddings", "CACHE MISS")
                
        except Exception as load_error:
            error_msg = f"No existing vector database found\nCreating new embeddings\nReason: {load_error}"
            print_box(error_msg, "DATABASE INIT")
        
        # Create new embeddings if we reach here
        try:
            # Test embeddings before proceeding
            if os.getenv("OPENAI_BASE_URL") and "groq" in os.getenv("OPENAI_BASE_URL").lower():
                print_box("Initializing local embeddings for Groq...", "EMBEDDING INIT")
                from langchain_huggingface import HuggingFaceEmbeddings
                embeddings = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2",
                    model_kwargs={'device': 'cpu'}
                )
                # Test with a simple embedding call
                test_result = embeddings.embed_query("test")
                print_box("Local embeddings ready", "EMBEDDING SUCCESS")
            else:
                # Use OpenAI embeddings for regular OpenAI API
                embeddings_kwargs = {"api_key": os.getenv("OPENAI_API_KEY")}
                if os.getenv("OPENAI_BASE_URL"):
                    embeddings_kwargs["base_url"] = os.getenv("OPENAI_BASE_URL")
                
                embeddings = OpenAIEmbeddings(**embeddings_kwargs)
                # Test with a simple embedding call
                test_result = embeddings.embed_query("test")
                print_box("OpenAI embeddings validated", "EMBEDDING SUCCESS")
        except Exception as api_error:
            error_msg = f"Embeddings error: {api_error}\nContinuing without embeddings\nQA will not work"
            print_box(error_msg, "EMBEDDING ERROR")
            return
            
        # Create new vector database with documents
        print_box("Creating new vector database\nwith fresh documents...", "DATABASE CREATE")
        vectordb = Chroma(
            persist_directory=persist_dir,
            embedding_function=embeddings
        )
        vectordb.add_documents(documents)
        print_box("Vector database created and populated", "SUCCESS")

    except Exception as e:
        error_msg = f"Startup error: {e}\nApplication starting without QA functionality"
        print_box(error_msg, "STARTUP ERROR")

@app.post("/qa")
async def qa(req: QARequest):
    global vectordb
    if vectordb is None:
        raise HTTPException(
            status_code=503, 
            detail="Vector store not ready. Sjekk OpenAI API key og restart applikasjonen."
        )
    try:
        llm_kwargs = {
            "model": "llama-3.1-8b-instant",  # Current available Groq model
            "temperature": 0,
            "openai_api_key": os.getenv("OPENAI_API_KEY")
        }
        if os.getenv("OPENAI_BASE_URL"):
            llm_kwargs["openai_api_base"] = os.getenv("OPENAI_BASE_URL")
        
        llm = ChatOpenAI(**llm_kwargs)
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vectordb.as_retriever()
        )
        result = qa_chain.invoke({"query": req.query})
        return {"query": req.query, "result": result["result"]}
    except Exception as e:
        # Check if it's an OpenAI quota error
        error_msg = str(e)
        if "insufficient_quota" in error_msg or "quota" in error_msg.lower():
            raise HTTPException(
                status_code=402,
                detail="OpenAI API kvote oppbrukt. Sjekk din billing på OpenAI-kontoen din."
            )
        elif "api" in error_msg.lower() and ("key" in error_msg.lower() or "auth" in error_msg.lower()):
            raise HTTPException(
                status_code=401,
                detail="OpenAI API key ugyldig eller mangler. Sjekk OPENAI_API_KEY i .env filen."
            )
        else:
            raise HTTPException(status_code=500, detail=f"Intern server feil: {error_msg}")
    
@app.post("/refresh-embeddings")
async def refresh_embeddings():
    """Force refresh of embeddings from Canvas data"""
    global documents, vectordb
    try:
        # Re-run the startup process to refresh embeddings
        await startup_event()
        return {"message": "Embeddings refreshed successfully", "documents_loaded": len(documents)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refresh embeddings: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint to monitor service status"""
    global vectordb
    status = {
        "status": "healthy",
        "vector_db_ready": vectordb is not None,
        "documents_loaded": len(documents),
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "canvas_configured": bool(os.getenv("CANVAS_API_TOKEN")) and bool(os.getenv("CANVAS_DOMAIN"))
    }
    
    if not status["vector_db_ready"]:
        status["status"] = "degraded"
        status["message"] = "Vector database not initialized - QA functionality unavailable"
    
    return status

@app.get("/context")
async def get_context():
    try:
        all_courses = await get_user_courses()
        courses = filter_actual_courses(all_courses)  # Filter out info hubs

        # Assignments
        assignments_by_course = []
        files_by_course = []

        for course in courses:
            cid = course["id"]
            assignments = await get_course_assignments(cid)
            assignments_by_course.append({
                "course_id": cid,
                "assignments": assignments
            })

            # Include all files per course
            files = await get_course_files(cid)
            files_by_course.append({
                "course_id": cid,
                "files": files
            })

        return {
            "courses": courses,
            "assignments_by_course": assignments_by_course,
            "files_by_course": files_by_course,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/docs")
async def debug_docs():
    return [doc.metadata for doc in documents]

@app.get("/proxy/pdf/{course_id}/{file_id}")
async def proxy_pdf(course_id: int, file_id: int):
    url = f"https://{os.getenv('CANVAS_DOMAIN')}/api/v1/courses/{course_id}/files/{file_id}"
    headers = {"Authorization": f"Bearer {os.getenv('CANVAS_API_TOKEN')}"}

    async with httpx.AsyncClient(headers=headers) as client:
        # Get metadata
        meta_resp = await client.get(url)
        meta_resp.raise_for_status()
        download_url = meta_resp.json().get("url")

        # Stream file
        file_resp = await client.get(download_url)
        file_resp.raise_for_status()
        return StreamingResponse(
            file_resp.aiter_bytes(),
            media_type="application/pdf"
        )