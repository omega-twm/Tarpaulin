# Canvas RAG Dashboard

An AI-powered “retrieval-augmented generation” (RAG) dashboard for Canvas LMS.  
Students can chat naturally about their courses, assignments, and profile—powered by a Python FastAPI backend that fetches Canvas data and a Next.js frontend that renders a conversational UI.

---

## 🚀 Architecture

canvas-rag-dashboard/
├── frontend/                      # Next.js React app
└── backend/                       # Python FastAPI microservice

- **frontend/**  
  - Built with Next.js + React + Tailwind  
  - Renders a chat UI (`CanvasChat.tsx`) that sends questions to the backend  

- **backend/**  
  - FastAPI service in Python  
  - `canvas_service.py` – wraps Canvas API calls (profile, courses, assignments)  
  - `app.py` – exposes `/context` and `/qa` endpoints  
  - Uses LangChain, Chroma (or other vector store), and OpenAI for embeddings & QA  

---

## 📋 Prerequisites

- **Node.js** ≥ 16  
- **Python** ≥ 3.9  
- Canvas API token and domain  
- OpenAI API key  

---

## ⚙️ Setup

### 1. Clone the repo

```bash
git clone https://github.com/your-org/canvas-rag-dashboard.git
cd canvas-rag-dashboard

2. Configure environment variables

Frontend (frontend/.env.local)

NEXT_PUBLIC_API_BASE=http://localhost:8000

Backend (backend/.env)

# Canvas API credentials
CANVAS_API_TOKEN=
CANVAS_DOMAIN=

# OpenAI API key
OPENAI_API_KEY=
# (Optional) FastAPI/Uvicorn settings
# PORT=8000
# HOST=0.0.0.0
# Chroma persistence
CHROMA_DB_DIR=./.chromadb


LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=

🏃‍♂️ Running Locally

Backend

cd backend
python -m venv .venv
source .venv/bin/activate       # macOS/Linux
# .venv\Scripts\activate        # Windows
pip install -r requirements.txt
uvicorn app:app --reload       # starts at http://localhost:8000

Frontend

cd frontend
npm install
npm run dev                    # starts at http://localhost:3000

🧰 Usage
	1.	Open your browser to http://localhost:3000
	2.	Ask questions like “What assignments do I have due soon?”
	3.	The frontend sends your query to POST /qa on the Python service, which:
	•	Fetches your Canvas context (/context)
	•	Embeds and indexes documents with LangChain & Chroma
	•	Runs a RetrievalQA chain via OpenAI
	•	Returns a natural-language answer

📁 Folder Structure

canvas-rag-dashboard/
├── frontend/
│   ├── .env.local
│   ├── package.json
│   └── src/
│       ├── pages/index.tsx
│       ├── components/CanvasChat.tsx
│       └── styles/globals.css
└── backend/
    ├── .env
    ├── requirements.txt
    ├── app.py
    ├── canvas_service.py
    └── models/canvas_types.py

🛠️ Contributing
	1.	Fork the repo
	2.	Create a feature branch (git checkout -b feature/...)
	3.	Commit & push
	4.	Open a Pull Request

Please follow the existing code style and add tests for any new features.

📄 License

This project is MIT-licensed. See LICENSE for details