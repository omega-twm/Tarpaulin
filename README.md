# Canvas AI Dashboard

An AI-powered "retrieval-augmented generation" (RAG) system for Canvas LMS with a professional CLI interface.  
Students can query their Canvas data naturally using a command-line tool powered by a Python FastAPI backend that fetches Canvas data and uses free AI services.

> **Note**: This project is based on the original Canvas RAG Dashboard. We've transformed it into a CLI-focused tool with enhanced filtering, free AI integration (Groq), and professional ASCII styling.

---


- **CLI Interface (cli.py)**  
  - Command-line tool with minimalist styling
  - Commands: `ask`, `health`, `context`, `refresh`, `debug`, `test`
  - Box formatting and text wrapping

- **Backend/**  
  - FastAPI service in Python  
  - `canvas_service.py` – wraps Canvas API calls (courses, assignments, files)  
  - `app.py` – exposes `/qa`, `/health`, `/context` endpoints with ASCII logging
  - Uses LangChain, ChromaDB, and Groq API for free AI processing
  - Smart course filtering to exclude information hubs
---

## Key Features

- **Free AI**: Uses Groq API (llama-3.1-8b-instant) instead of paid OpenAI
- **Local Embeddings**: HuggingFace sentence-transformers for vector search
- **Professional CLI**: ASCII art boxes and clean formatting
- **Smart Filtering**: Automatically excludes Canvas information hubs
- **Performance**: Caching to avoid re-running embeddings on startup
- **Test Mode**: Mock data for testing RAG functionality

---

## Prerequisites

- **Python** ≥ 3.9  
- **uv** (Python package manager) or **pip**
- Canvas API token and domain  
- **Groq API key** (free tier available)

---

## Setup

### 1. Clone and navigate

```bash
git clone <your-repo-url>
cd Tarpaulin
```

### 2. Configure environment variables

Create `Backend/.env`:

```bash
# Canvas API credentials
CANVAS_API_TOKEN=your_canvas_token_here
CANVAS_DOMAIN=your_institution.instructure.com

# Groq API (free alternative to OpenAI)
OPENAI_API_KEY=your_groq_api_key_here
OPENAI_BASE_URL=https://api.groq.com/openai/v1

# Database persistence
CHROMA_DB_DIR=./chroma_db

# Optional: LangSmith tracing
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=your_langsmith_key
LANGSMITH_PROJECT=CanvasAI
```

### 3. Install dependencies

```bash
# Using uv (recommended)
uv sync

# Or using pip
cd Backend
pip install -r requirements.txt
```

---

## Running the System

### Start the Backend

```bash
cd Backend
uvicorn app:app
```

### Use the CLI

```bash
# Check system health
canvas health

# View your Canvas context
canvas context

# Ask questions about your courses
canvas ask "What courses do I have?"
canvas ask "What assignments are due this week?"
canvas ask "Tell me about my machine learning course"

# Load test data (if no real courses available)
canvas test

# Refresh Canvas data
canvas refresh

# Debug information
canvas debug
```

---

## CLI Commands

| Command | Description | Example |
|---------|-------------|---------|
| `canvas ask "<question>"` | Ask AI about your Canvas data | `canvas ask "What assignments are due?"` |
| `canvas health` | Check system status | `canvas health` |
| `canvas context` | View courses, assignments, files | `canvas context` |
| `canvas refresh` | Update Canvas data | `canvas refresh` |
| `canvas test` | Load mock data for testing | `canvas test` |
| `canvas debug` | Show technical details | `canvas debug` |

---

## Project Structure

```
CanvasAIDashboard/
├── cli.py                    # Main CLI interface
├── setup_cli.sh              # CLI installation script
├── Backend/
│   ├── .env                  # Environment configuration
│   ├── requirements.txt      # Python dependencies
│   ├── app.py               # FastAPI backend with ASCII logging
│   └── canvas_service.py    # Canvas API integration
├── pyproject.toml           # uv configuration
└── README.md               # This file
```

---

## CLI Features

- Clean, terminal-friendly output
- Proper line breaks for long content  
- Unified design across all commands
- Clear error messages with helpful suggestions
- Response time tracking for queries

---

## Technical Details

- **AI Model**: Groq llama-3.1-8b-instant (free tier)
- **Embeddings**: HuggingFace sentence-transformers/all-MiniLM-L6-v2
- **Vector Database**: ChromaDB with persistence
- **Backend**: FastAPI with async support
- **Caching**: Smart embedding caching to improve startup performance

---

## Testing

The system includes a test mode for trying RAG functionality without real Canvas courses:

```bash
# Load mock data (2 courses, 3 assignments, 3 files)
canvas test

# Test with example queries
canvas ask "What courses do I have?"
canvas ask "Tell me about machine learning assignments" 
canvas ask "What files are available for studying?"
```

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test with `canvas test` and real Canvas data
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

Please maintain the ASCII art styling and ensure all CLI commands work properly.

---

## License

This project is MIT-licensed. See LICENSE for details.

---

## Acknowledgments

This project is based on the original Canvas RAG Dashboard concept https://github.com/maxtwotouch/CanvasAIDashboard.git We've enhanced it with:
- CLI interface
- Free AI integration using Groq API
- Local embeddings for cost-effective vector search
- Performance optimizations and caching

The CLI-focused approach makes it perfect for developers and power users who prefer terminal interfaces over web UIs.
