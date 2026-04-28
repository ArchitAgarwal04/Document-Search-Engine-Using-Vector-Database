# 📄 DocSearch Engine — RAG-Powered Document Search & AI Chat

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi" />
  <img src="https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react" />
  <img src="https://img.shields.io/badge/ChromaDB-Vector_DB-orange?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker" />
  <img src="https://img.shields.io/badge/LLM-Groq_%7C_Gemini-purple?style=for-the-badge" />
</p>

A full-stack **semantic document search engine** powered by **RAG (Retrieval-Augmented Generation)**. Upload your PDFs, Word docs, or text files and instantly search them using natural language — or chat with an AI that reads your documents and answers questions based only on what's in them.

---

## 📑 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Design System](#design-system)
- [Pages & Components](#pages--components)
- [Backend API](#backend-api)
- [RAG Pipeline](#rag-pipeline)
- [LLM Providers](#llm-providers)
- [Authentication](#authentication)
- [Getting Started (Local Dev)](#getting-started-local-dev)
- [Docker Deployment](#docker-deployment)
- [Environment Variables](#environment-variables)
- [How It Works — End to End](#how-it-works--end-to-end)

---

## ✨ Features

| Feature | Description |
|---|---|
| 📤 **Document Upload** | Upload PDF, DOCX, and TXT files up to 50MB |
| 🔍 **Semantic Search** | Find relevant passages using vector similarity (not keyword matching) |
| 🤖 **AI Chat (RAG)** | Ask questions in natural language; AI answers using only your documents |
| 📖 **Source Citations** | Every AI answer shows which document/page the answer came from |
| 🔐 **JWT Auth** | Register/login with email; first user is auto-promoted to admin |
| 🔄 **Multi-LLM Support** | Switch between Groq (6000 RPM free) and Google Gemini via one config line |
| 🐳 **Docker Ready** | One command deploys the full stack with Docker Compose |
| ♾️ **Retry Logic** | Automatic exponential backoff on rate-limit errors (5s → 10s → 20s) |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        BROWSER                              │
│   React SPA (Vite) → served by Nginx on port 80            │
│   Pages: Login | Documents | Search | AI Chat              │
└──────────────────────┬──────────────────────────────────────┘
                       │ /api/* proxied by Nginx
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND  (FastAPI)                        │
│                    port 8000                                │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │   Auth   │  │ Documents│  │  Search  │  │   RAG    │  │
│  │  Router  │  │  Router  │  │  Router  │  │  Router  │  │
│  └──────────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
│                     │              │              │         │
│              ┌──────▼──────────────▼──────────────▼──────┐ │
│              │          Core Services                      │ │
│              │  ┌─────────────┐  ┌────────────────────┐  │ │
│              │  │  Embedder   │  │   VectorStore       │  │ │
│              │  │ (MiniLM-L6) │  │   (ChromaDB)        │  │ │
│              │  └──────┬──────┘  └──────────┬─────────┘  │ │
│              │         └──────────────────────┘           │ │
│              │  ┌──────────────────────────────────────┐  │ │
│              │  │         LLM Provider                  │  │ │
│              │  │   Groq (llama-3.1-8b) or Gemini      │  │ │
│              │  └──────────────────────────────────────┘  │ │
│              └─────────────────────────────────────────────┘ │
│                                                             │
│  SQLite (users, documents, chunks, query logs)             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

### Backend
| Technology | Version | Purpose |
|---|---|---|
| **FastAPI** | ≥0.115 | REST API framework with async support |
| **SQLAlchemy** | ≥2.0 | ORM for SQLite database |
| **ChromaDB** | ≥0.5 | Persistent vector database for embeddings |
| **sentence-transformers** | ≥3.0 | Local embedding model (`all-MiniLM-L6-v2`) |
| **PyPDF2** | ≥3.0 | PDF text extraction |
| **python-docx** | ≥1.1 | Word document text extraction |
| **LangChain** | ≥0.2 | Text splitting / chunking utilities |
| **Groq SDK** | ≥0.9 | Groq LLM API client |
| **google-generativeai** | ≥0.7 | Google Gemini LLM API client |
| **python-jose** | ≥3.3 | JWT token creation & verification |
| **passlib[bcrypt]** | ≥1.7 | Password hashing |
| **uvicorn** | ≥0.30 | ASGI server |

### Frontend
| Technology | Version | Purpose |
|---|---|---|
| **React** | 19 | UI framework |
| **Vite** | 8 | Build tool & dev server |
| **React Router DOM** | 7 | Client-side routing |
| **Axios** | ≥1.15 | HTTP client with interceptors |
| **React Hot Toast** | ≥2.6 | Toast notifications |
| **React Dropzone** | ≥15 | Drag-and-drop file uploads |
| **React Markdown** | ≥10 | Render AI responses as formatted markdown |
| **Lucide React** | ≥1.11 | Icon library |
| **Google Fonts (Inter)** | — | Typography |

### Infrastructure
| Technology | Purpose |
|---|---|
| **Docker + Docker Compose** | Container orchestration |
| **Nginx** | Serve React SPA + reverse proxy to backend |
| **SQLite** | Lightweight relational database (zero config) |

---

## 📁 Project Structure

```
Document Search Engine using vector DB/
├── docker-compose.yml          # Orchestrates backend + frontend containers
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env                    # All secrets and config (never commit this)
│   └── app/
│       ├── main.py             # FastAPI app, CORS, router registration
│       ├── config.py           # Pydantic settings (reads from .env)
│       ├── database.py         # SQLAlchemy engine + session setup
│       ├── models.py           # DB models: User, Document, Chunk, QueryLog
│       ├── schemas.py          # Pydantic request/response schemas
│       ├── auth/
│       │   ├── router.py       # POST /register, POST /login, GET /me
│       │   ├── jwt.py          # create_access_token, decode_token
│       │   └── dependencies.py # get_current_user, get_optional_user
│       ├── documents/
│       │   ├── router.py       # POST /upload, GET /, DELETE /{id}, GET /stats
│       │   ├── ingestion.py    # PDF/DOCX/TXT text extraction
│       │   └── chunker.py      # RecursiveCharacterTextSplitter (500 chars, 100 overlap)
│       ├── embeddings/
│       │   ├── embedder.py     # sentence-transformers model singleton
│       │   └── vector_store.py # ChromaDB wrapper (add, search, delete, count)
│       ├── search/
│       │   ├── router.py       # POST /search
│       │   └── retriever.py    # semantic_search(), mmr_rerank()
│       └── rag/
│           ├── router.py       # POST /rag/chat
│           ├── pipeline.py     # Full RAG pipeline + multi-provider LLM calls
│           └── prompts.py      # System prompt, user template, history template
│
└── frontend/
    ├── Dockerfile              # Multi-stage: Node build → Nginx serve
    ├── nginx.conf              # SPA routing + /api proxy to backend:8000
    ├── vite.config.js          # Dev proxy: /api → localhost:8000
    └── src/
        ├── main.jsx            # React root + BrowserRouter
        ├── App.jsx             # Route definitions
        ├── index.css           # Design system (CSS variables, components)
        ├── api/
        │   └── client.js       # Axios instance + JWT interceptor + 401 handler
        ├── context/
        │   └── AuthContext.jsx # Global auth state (user, token, login, logout)
        ├── pages/
        │   ├── LoginPage.jsx   # Register / Login form
        │   ├── DocumentsPage.jsx # Upload + list + delete documents
        │   ├── SearchPage.jsx  # Semantic search with result cards
        │   └── ChatPage.jsx    # RAG AI chat with conversation history
        └── components/
            ├── Sidebar.jsx     # Navigation sidebar with active state
            ├── FileUpload.jsx  # Drag-and-drop upload with progress
            └── ResultCard.jsx  # Search result card with similarity score bar
```

---

## 🎨 Design System

The UI uses a **custom dark glassmorphism design system** defined entirely in `frontend/src/index.css` using CSS custom properties.

### Color Palette
| Variable | Value | Usage |
|---|---|---|
| `--bg-primary` | `#0a0a0f` | Main page background |
| `--bg-secondary` | `#111118` | Sidebar background |
| `--bg-card` | `rgba(255,255,255,0.04)` | Card backgrounds |
| `--accent` | `#6c63ff` | Primary brand color (purple) |
| `--accent-light` | `#8b85ff` | Hover states, active links |
| `--glass` | `rgba(255,255,255,0.05)` | Glassmorphism base |
| `--glass-border` | `rgba(255,255,255,0.1)` | Card and input borders |
| `--text-primary` | `#f0f0ff` | Main body text |
| `--text-secondary` | `#9898b3` | Subtitles, labels |

### Typography
- **Font**: Inter (Google Fonts) — weights 300, 400, 500, 600, 700, 800
- `-webkit-font-smoothing: antialiased` for crisp rendering

### Animated Background
```css
body::before {
  background:
    radial-gradient(ellipse 80% 50% at 20% 0%,  rgba(108,99,255,0.12) ...),
    radial-gradient(ellipse 60% 40% at 80% 100%, rgba(99,179,255,0.08) ...);
}
```
Two soft radial gradients create a subtle living atmosphere behind all content.

### Reusable CSS Classes
| Class | Description |
|---|---|
| `.card` | Glassmorphism card with blur, border, hover lift |
| `.btn-primary` | Gradient purple button with glow shadow |
| `.btn-ghost` | Subtle transparent button |
| `.btn-danger` | Red-tinted destructive action button |
| `.input` | Glass-style text input with focus ring |
| `.badge-*` | Colored pill badges (success/warning/danger/info/accent) |
| `.chat-bubble.user` | Purple gradient message bubble (right-aligned) |
| `.chat-bubble.assistant` | Glass-style AI response bubble (left-aligned) |
| `.dropzone` | Dashed-border drag-and-drop upload zone |
| `.spinner` | Animated CSS loading spinner |
| `.fade-in` | Fade + slide-up entrance animation (0.4s) |
| `.score-bar` | Animated similarity score progress bar |

---

## 📱 Pages & Components

### LoginPage
- Tabbed Register / Login form
- JWT token stored in `localStorage` on success
- First registered user is auto-promoted to **admin**

### DocumentsPage
- Statistics bar: total documents, chunks indexed, queries run
- Drag-and-drop file upload (`react-dropzone`) supporting PDF / DOCX / TXT
- Document list with file type badge, chunk count, indexed status
- Delete button (owner or admin only)

### SearchPage
- Full-text semantic search input
- Returns top-N ranked result cards
- Each `ResultCard` shows: document name, page number, similarity score bar (0–100%), text preview

### ChatPage
- Persistent conversation history (per session)
- Messages rendered with `react-markdown` (supports bold, lists, code blocks)
- Source citations panel below each AI response
- Auto-scroll to latest message

### Sidebar
- Fixed left navigation (240px)
- Active page highlighted with accent background
- Logout button at bottom

---

## 🔌 Backend API

All endpoints are prefixed with `/api/v1`. Interactive docs at **http://localhost:8000/docs**.

### Auth
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/auth/register` | Register new user → returns JWT |
| `POST` | `/api/v1/auth/login` | Login → returns JWT |
| `GET` | `/api/v1/auth/me` | Get current user profile |

### Documents
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/documents/upload` | Upload PDF/DOCX/TXT, triggers full pipeline |
| `GET` | `/api/v1/documents/` | List all indexed documents |
| `DELETE` | `/api/v1/documents/{id}` | Delete document + its ChromaDB embeddings |
| `GET` | `/api/v1/documents/stats` | Dashboard statistics |

### Search
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/search` | Semantic vector search, returns ranked chunks |

### RAG Chat
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/rag/chat` | Ask a question, get AI answer + source citations |

---

## 🧠 RAG Pipeline

When you ask a question in the AI Chat tab, the following steps happen:

```
1. EMBED QUERY
   User question → all-MiniLM-L6-v2 → 384-dimension vector

2. RETRIEVE
   ChromaDB cosine similarity search → top 8 chunks
   Filter: similarity score ≥ 0.2

3. FORMAT CONTEXT
   Retrieved chunks formatted into a structured context block
   with document name, page number, and text

4. BUILD PROMPT
   System prompt + context block + conversation history + user question

5. CALL LLM (with retry)
   Groq or Gemini API call
   On 429: retry 3× with exponential backoff (5s → 10s → 20s)

6. RETURN ANSWER + SOURCES
   Answer text + top 3 source citations with page numbers
```

### Chunking Strategy
Documents are split into **500-character chunks** with **100-character overlap** using `RecursiveCharacterTextSplitter`. This ensures:
- Each Q&A pair in a document gets its own distinct embedding
- Context isn't lost at chunk boundaries (overlap)
- Chunks fit within embedding model token limits (512 tokens)

---

## 🤖 LLM Providers

Switch providers by changing one line in `backend/.env`:

```env
LLM_PROVIDER=groq      # or "gemini"
```

| Provider | Model | Free Tier Limits | Use When |
|---|---|---|---|
| **Groq** ✅ | `llama-3.1-8b-instant` | 6,000 RPM / 14,400 RPD | Default — best for development |
| **Gemini** | `gemini-2.0-flash-lite` | 30 RPM / 1,500 RPD | When you need Google's model specifically |

> Get a free Groq key at: https://console.groq.com/keys

---

## 🔐 Authentication

- Passwords hashed with **bcrypt** via `passlib`
- **JWT tokens** signed with HS256, configurable expiry (default 60 minutes)
- Token stored in `localStorage`, attached to every request via Axios request interceptor
- **Auto-logout** on 401 response via Axios response interceptor
- First registered user receives `role: "admin"`, all subsequent users get `role: "user"`

---

## 🚀 Getting Started (Local Dev)

### Prerequisites
- Python 3.11+
- Node.js 20+
- Git

### 1. Clone the repo
```bash
git clone https://github.com/ArchitAgarwal04/Document-Search-Engine-Using-Vector-Database.git
cd "Document Search Engine using vector DB"
```

### 2. Configure the backend
```bash
cd backend
```
Edit `.env` and fill in your API key:
```env
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_your_key_here     # get free key at console.groq.com
```

### 3. Start the backend
```powershell
# Windows
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
```bash
# Mac/Linux
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Backend runs at → **http://localhost:8000**
API Docs → **http://localhost:8000/docs**

### 4. Start the frontend
```bash
cd ../frontend
npm install
npm run dev
```
Frontend runs at → **http://localhost:5173**

---

## 🐳 Docker Deployment

Requires [Docker Desktop](https://www.docker.com/products/docker-desktop/).

### 1. Update backend/.env with your API key
```env
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_your_key_here
```

### 2. Build and start
```powershell
cd "Document Search Engine using vector DB"
docker compose up --build
```

> ⏱️ First build takes 3–5 minutes (downloads embedding model). Subsequent starts are instant.

### 3. Open the app
| Service | URL |
|---|---|
| **App** | http://localhost |
| **API** | http://localhost:8000 |
| **API Docs** | http://localhost:8000/docs |

### Other Docker commands
```bash
docker compose down          # stop containers
docker compose down -v       # stop + delete all data volumes
docker compose logs -f       # live logs (all services)
docker compose logs -f backend  # backend logs only
docker compose up --build    # rebuild after code changes
```

> **Data persistence:** Uploaded documents and ChromaDB embeddings are stored in a named Docker volume (`backend_data`) and survive container restarts.

---

## ⚙️ Environment Variables

All config lives in `backend/.env`:

```env
# ── LLM ──────────────────────────────────────────
LLM_PROVIDER=groq                     # "groq" or "gemini"
GROQ_API_KEY=gsk_...                  # https://console.groq.com/keys
GROQ_MODEL=llama-3.1-8b-instant

GEMINI_API_KEY=AIza...                # https://aistudio.google.com
GEMINI_MODEL=gemini-2.0-flash-lite

# ── Embedding ─────────────────────────────────────
EMBEDDING_MODEL=all-MiniLM-L6-v2     # runs fully locally, no API key needed

# ── Vector DB ─────────────────────────────────────
CHROMA_PERSIST_DIR=./data/chroma_db
CHROMA_COLLECTION_NAME=documents

# ── Search ────────────────────────────────────────
TOP_K_RESULTS=8                       # chunks retrieved per query
SIMILARITY_THRESHOLD=0.2              # minimum cosine similarity (0–1)

# ── Auth ──────────────────────────────────────────
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# ── File Upload ───────────────────────────────────
UPLOAD_DIR=./data/uploads
MAX_FILE_SIZE_MB=50

# ── App ───────────────────────────────────────────
APP_NAME=DocSearch Engine
DEBUG=true                            # set to false in production
FRONTEND_URL=http://localhost:5173    # overridden to http://localhost in Docker
```

---

## 🔄 How It Works — End to End

### Document Upload Flow
```
User drops PDF
    → Validate (type + size)
    → Save to disk (./data/uploads/)
    → Create DB record (status: "processing")
    → Extract text page by page (PyPDF2)
    → Split into 500-char chunks (LangChain splitter)
    → Embed each chunk (all-MiniLM-L6-v2 → 384-dim vector)
    → Store vectors + metadata in ChromaDB
    → Store chunk records in SQLite
    → Update DB record (status: "indexed")
```

### Search Flow
```
User types query
    → Embed query (same model as document chunks)
    → ChromaDB cosine similarity search (top 8 chunks)
    → Filter by similarity threshold (≥ 0.2)
    → Return ranked results with page numbers + score
```

### AI Chat Flow
```
User asks question
    → Embed question
    → Retrieve top 8 relevant chunks from ChromaDB
    → Build prompt: system instructions + context + history + question
    → Call Groq/Gemini API (with retry on rate limits)
    → Return answer + 3 source citations with page numbers
```

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

<p align="center">Built with ❤️ using FastAPI, React, ChromaDB, and open-source LLMs</p>
