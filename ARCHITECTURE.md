# 🏗️ RAG Chatbot Architecture

## 📋 Table of Contents

1. [Overview](#overview)
2. [System Architecture Diagram](#system-architecture-diagram)
3. [Flow Diagrams](#flow-diagrams)
4. [Component Details](#component-details)
5. [Technology Stack](#technology-stack)
6. [Data Flow](#data-flow)
7. [API Endpoints](#api-endpoints)
8. [RAG vs Standard Chat](#rag-vs-standard-chat)
9. [File Structure](#file-structure)

---

## Overview

This document describes the architecture of the **Gemini RAG Chatbot** - a Retrieval-Augmented Generation system that answers questions based on uploaded documents using Google Gemini AI.

### Key Features

- 🧠 **RAG-Powered Answers**: Responses based on your knowledge base
- 📁 **Multiple Document Formats**: PDF, DOCX, TXT, JSON support
- 📊 **Source Citations**: Every answer includes references
- 🎨 **Modern UI**: Glassmorphism design with dark theme
- 🔌 **Easy Integration**: RESTful API architecture

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐   │
│  │   Sidebar   │  │  Chat Area   │  │  Upload Modal       │   │
│  │  - API Key  │  │  - Messages  │  │  - Drag & Drop      │   │
│  │  - Docs     │  │  - Input     │  │  - Progress         │   │
│  │  - Settings │  │  - Typing    │  │  - Success/Error    │   │
│  └─────────────┘  └──────────────┘  └─────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↕ HTTP Requests
┌─────────────────────────────────────────────────────────────────┐
│                      FLASK BACKEND (app.py)                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    API Endpoints                         │  │
│  │  /set-api-key  →  Inisialisasi Gemini + RAG Engine      │  │
│  │  /chat         →  Process pertanyaan (dengan/tanpa RAG) │  │
│  │  /upload       →  Upload & process dokumen baru         │  │
│  │  /get-docs     →  List semua dokumen                    │  │
│  │  /delete       →  Hapus dokumen                         │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────────┐
│                    RAG ENGINE (utils/)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐   │
│  │  Document    │  │  Embedding   │  │  Vector Search     │   │
│  │  Loader      │  │  Generator   │  │  (ChromaDB)        │   │
│  │  - PDF       │  │  (Sentence   │  │  - Similarity      │   │
│  │  - DOCX      │  │   Transformer)│  │  - Retrieval       │   │
│  │  - TXT       │  │               │  │                    │   │
│  │  - JSON      │  │               │  │                    │   │
│  └──────────────┘  └──────────────┘  └────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────────┐
│                      EXTERNAL SERVICES                          │
│  ┌─────────────────────┐  ┌──────────────────────────────┐    │
│  │  Google Gemini API  │  │  ChromaDB (Vector Store)     │    │
│  │  - Chat Session     │  │  - Embeddings storage        │    │
│  │  - LLM Response     │  │  - Similarity search         │    │
│  └─────────────────────┘  └──────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Flow Diagrams

### 1️⃣ Initialization Flow (Saat API Key Dimasukkan)

```
User Input API Key
       ↓
[POST /set-api-key]
       ↓
Flask Backend
       ↓
┌─────────────────────────────────────┐
│ 1. Configure Gemini API             │
│    → genai.configure(api_key)       │
│    → Create GenerativeModel         │
│    → Start Chat Session             │
└─────────────────────────────────────┘
       ↓
┌─────────────────────────────────────┐
│ 2. Initialize RAG Engine            │
│    → Load SentenceTransformer       │
│    → Connect ChromaDB               │
│    → Create/Get Collection          │
└─────────────────────────────────────┘
       ↓
┌─────────────────────────────────────┐
│ 3. Load Dummy Data                  │
│    → Read JSON files                │
│    → Convert to text chunks         │
│    → Generate embeddings            │
│    → Store in ChromaDB              │
└─────────────────────────────────────┘
       ↓
Return: { rag_enabled: true }
```

---

### 2️⃣ RAG Chat Flow (Saat User Bertanya)

```
User: "What products does TechCorp offer?"
       ↓
[POST /chat] { message, use_rag: true }
       ↓
Flask Backend
       ↓
┌─────────────────────────────────────────┐
│ STEP 1: Check RAG Enabled?              │
│ → use_rag = true, rag_enabled = true    │
└─────────────────────────────────────────┘
       ↓
┌─────────────────────────────────────────┐
│ STEP 2: Search Knowledge Base           │
│ rag_engine.get_context(query)           │
│                                         │
│ a) Generate query embedding             │
│    → SentenceTransformer.encode()       │
│                                         │
│ b) Search ChromaDB                      │
│    → collection.query(embedding)        │
│    → Get top 5 similar chunks           │
│                                         │
│ c) Format context                       │
│    → Combine chunks with sources        │
└─────────────────────────────────────────┘
       ↓
┌─────────────────────────────────────────┐
│ STEP 3: Build Enhanced Prompt           │
│                                         │
│ Context: [retrieved documents]          │
│ Question: What products does TechCorp   │
│           offer?                        │
│ Answer:                                 │
└─────────────────────────────────────────┘
       ↓
┌─────────────────────────────────────────┐
│ STEP 4: Send to Gemini                  │
│ chat_session.send_message(prompt)       │
└─────────────────────────────────────────┘
       ↓
┌─────────────────────────────────────────┐
│ STEP 5: Return Response                 │
│ {                                       │
│   response: "Based on context...",      │
│   rag_used: true,                       │
│   sources: ["products.json", ...]       │
│ }                                       │
└─────────────────────────────────────────┘
       ↓
Display to User with Source Citations 📄
```

---

### 3️⃣ Document Upload Flow

```
User Drag & Drop File
       ↓
[POST /upload-document]
       ↓
Flask Backend
       ↓
┌─────────────────────────────────────────┐
│ 1. Read File Content                    │
│    - PDF  → PyPDF2                      │
│    - DOCX → python-docx                 │
│    - TXT  → Direct read                 │
│    - JSON → Direct read                 │
└─────────────────────────────────────────┘
       ↓
┌─────────────────────────────────────────┐
│ 2. Chunk Text                           │
│    - Split into 500 char chunks         │
│    - 50 char overlap                    │
│    - Break at sentence boundaries       │
└─────────────────────────────────────────┘
       ↓
┌─────────────────────────────────────────┐
│ 3. Generate Embeddings                  │
│    - SentenceTransformer.encode()       │
│    - Vector representation              │
└─────────────────────────────────────────┘
       ↓
┌─────────────────────────────────────────┐
│ 4. Store in ChromaDB                    │
│    - Add embeddings + metadata          │
│    - Index for fast search              │
└─────────────────────────────────────────┘
       ↓
Document ready for RAG queries! ✅
```

---

## Component Details

### Frontend (HTML/CSS/JS)

| Component | File | Responsibility |
|-----------|------|----------------|
| UI Layout | `index.html` | Sidebar, chat area, modals |
| Styling | `style.css` | Glassmorphism design, animations |
| Logic | `script.js` | API calls, state management, DOM updates |

**Key JavaScript Functions:**

```javascript
handleSaveApiKey()   // Validate API key
handleSendMessage()  // Send message to backend
getBotResponse()     // Get and display AI response
uploadFile()         // Handle document upload
loadDocuments()      // Fetch document list
deleteDocument()     // Remove document from KB
```

---

### Backend (Flask - app.py)

| Endpoint | Method | Function |
|----------|--------|----------|
| `/` | GET | Serve main page |
| `/set-api-key` | POST | Initialize Gemini + RAG |
| `/chat` | POST | Process chat message |
| `/upload-document` | POST | Upload new document |
| `/get-documents` | GET | List all documents |
| `/delete-document/<name>` | DELETE | Remove document |
| `/clear-knowledge` | POST | Clear all documents |
| `/search-knowledge` | POST | Search knowledge base |

---

### RAG Engine (utils/rag_engine.py)

```python
class RAGEngine:
    ├── initialize()        # Setup ChromaDB + embeddings
    ├── load_dummy_data()   # Load JSON files into KB
    ├── add_document()      # Add new document
    ├── remove_document()   # Delete document
    ├── search()            # Find relevant chunks
    ├── get_context()       # Format context for LLM
    ├── _chunk_text()       # Split text into chunks
    └── _dict_to_text()     # Convert JSON to readable text
```

**Key Methods:**

| Method | Purpose |
|--------|---------|
| `initialize()` | Load SentenceTransformer model, connect ChromaDB |
| `load_dummy_data()` | Pre-populate KB with sample JSON data |
| `add_document()` | Process and store new document |
| `search(query, top_k)` | Find similar chunks using vector similarity |
| `get_context(query)` | Retrieve and format context for LLM |
| `_chunk_text()` | Split text into overlapping chunks (500 chars, 50 overlap) |

---

## Technology Stack

```
┌─────────────────────────────────────────────┐
│              PRESENTATION LAYER             │
│  HTML5 | CSS3 | JavaScript (Vanilla)        │
│  Google Fonts (Inter, JetBrains Mono)       │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│              APPLICATION LAYER              │
│  Flask (Python Web Framework)               │
│  Flask-CORS (Cross-Origin Support)          │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│               RAG LAYER                     │
│  ChromaDB (Vector Database)                 │
│  SentenceTransformers (Embeddings)          │
│  PyPDF2, python-docx (Document Parsers)     │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│               AI LAYER                      │
│  Google Gemini API (LLM)                    │
└─────────────────────────────────────────────┘
```

### Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| Flask | 2.0+ | Web framework |
| Flask-CORS | 3.0+ | Cross-origin requests |
| google-generativeai | Latest | Google Gemini AI |
| chromadb | Latest | Vector database |
| sentence-transformers | Latest | Text embeddings |
| PyPDF2 | Latest | PDF parsing |
| python-docx | Latest | Word document parsing |

---

## 🧠 Core RAG Components

### Embedding Model

| Property | Value |
|----------|-------|
| **Model** | `all-MiniLM-L6-v2` |
| **Library** | SentenceTransformers |
| **Dimensions** | 384 |
| **Model Size** | ~90 MB |
| **Language Support** | Multilingual (including Indonesian) |
| **License** | Apache 2.0 (free for commercial use) |
| **Location** | `utils/rag_engine.py` line 23 |

**Why this model?**
- ✅ Lightweight & fast (~50ms per chunk)
- ✅ Good accuracy for semantic search
- ✅ Supports Indonesian language
- ✅ Runs offline (no API key needed)
- ✅ Free for commercial use

**Code Reference:**
```python
# utils/rag_engine.py
self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
```

---

### Chunking Configuration

| Parameter | Value | Description |
|-----------|-------|-------------|
| **Chunk Size** | 500 characters | Text per chunk |
| **Chunk Overlap** | 50 characters (10%) | Overlap between chunks |
| **Break Point** | Sentence boundaries (`.`, `\n`) | Split at natural points |
| **Location** | `utils/rag_engine.py` line 77 |

**Visual Example:**
```
Original Text: "Kalimat 1. Kalimat 2. Kalimat 3." (1500 chars)

Chunk 1: chars 0-500    [overlap: chars 450-500 → Chunk 2]
Chunk 2: chars 450-950  [overlap: chars 900-950 → Chunk 3]
Chunk 3: chars 900-1400
```

**Why these values?**
- **500 chars**: Enough context for retrieval, not too large for embeddings
- **50 overlap (10%)**: Maintains context across chunk boundaries
- **Sentence boundary**: Prevents cutting in the middle of words/sentences

**Code Reference:**
```python
# utils/rag_engine.py
def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50)
```

---

### Large Language Model (LLM)

| Property | Value |
|----------|-------|
| **Provider** | Google Gemini API |
| **Model** | `models/gemini-2.5-flash` |
| **API Version** | v1beta |
| **Usage** | Chat completion with RAG context |
| **Location** | `app.py` line 41 |

**Code Reference:**
```python
# app.py
model = genai.GenerativeModel('models/gemini-2.5-flash')
```

**Note:** Model name may change. Check available models with:
```python
import google.generativeai as genai
print([m.name for m in genai.list_models()])
```

---

### Vector Database

| Property | Value |
|----------|-------|
| **Database** | ChromaDB |
| **Type** | Persistent (disk-based) |
| **Storage Path** | `./vector_store/` |
| **Similarity Metric** | Cosine similarity (HNSW index) |
| **Collection Name** | `knowledge_base` |
| **Location** | `utils/rag_engine.py` line 27 |

**Code Reference:**
```python
# utils/rag_engine.py
self.client = chromadb.PersistentClient(
    path=self.persist_directory,
    settings=Settings(anonymized_telemetry=False, allow_reset=True)
)

self.collection = self.client.get_or_create_collection(
    name="knowledge_base",
    metadata={"hnsw:space": "cosine"}
)
```

---

### Orchestration Framework

| Framework | Status |
|-----------|--------|
| **LangChain** | ❌ NOT used |
| **LlamaIndex** | ❌ NOT used |
| **Implementation** | ✅ Native Python (manual) |

**Why Native Implementation?**
1. ✅ **Easier to understand** - No abstraction layers
2. ✅ **Fewer dependencies** - Faster installation
3. ✅ **Full control** - Customize every step
4. ✅ **Lighter** - No framework overhead
5. ✅ **Educational** - Learn RAG from scratch

**For Production:** Consider LangChain/LlamaIndex for advanced features (memory, agents, multi-chain workflows).

---

## Data Flow

### Knowledge Base Structure

```
data/
├── dummy_data/
│   ├── company_info.json    → Company profile
│   ├── products.json        → Product catalog
│   └── FAQ.json             → FAQ entries
├── documents/               → Uploaded files
└── vector_store/            → ChromaDB embeddings (auto-generated)
```

---

### Embedding Process

```
Text Document
    ↓
[Chunking: 500 chars, 50 overlap]
    ↓
Chunk 1: "TechCorp Indonesia is..."
Chunk 2: "Our mission is to..."
Chunk 3: "Products include..."
    ↓
[SentenceTransformer.encode()]
    ↓
Vector 1: [0.12, -0.45, 0.78, ...]  (384 dimensions)
Vector 2: [-0.23, 0.67, -0.12, ...]
Vector 3: [0.89, 0.01, -0.34, ...]
    ↓
[Store in ChromaDB]
    ↓
Ready for similarity search! 🔍
```

---

### Text Chunking Strategy

```
Original Text (1500 characters)
    ↓
┌─────────────────────────────────────┐
│ Chunk 1: chars 0-500                │
│ (overlap: 450-500 → next chunk)     │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│ Chunk 2: chars 450-950              │
│ (overlap: 900-950 → next chunk)     │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│ Chunk 3: chars 900-1400             │
│ (remaining text)                    │
└─────────────────────────────────────┘
```

**Why Overlapping Chunks?**
- Maintains context across chunk boundaries
- Prevents information loss at split points
- Improves retrieval accuracy

---

## API Endpoints

### Authentication

#### `POST /set-api-key`

Set Gemini API key and initialize RAG engine.

**Request:**
```json
{
  "api_key": "your-gemini-api-key"
}
```

**Response:**
```json
{
  "message": "API Key diterima dan model berhasil diinisialisasi.",
  "rag_enabled": true
}
```

---

### Chat

#### `POST /chat`

Send a message and get AI response (with optional RAG).

**Request:**
```json
{
  "message": "What products does TechCorp offer?",
  "use_rag": true
}
```

**Response:**
```json
{
  "response": "Based on the context, TechCorp offers...",
  "rag_used": true,
  "sources": ["products.json", "company_info.json"]
}
```

---

### Document Management

#### `POST /upload-document`

Upload a document to the knowledge base.

**Request:** `multipart/form-data` or `JSON`

**Response:**
```json
{
  "message": "Document products.json processed successfully",
  "filename": "products.json"
}
```

---

#### `GET /get-documents`

List all documents in the knowledge base.

**Response:**
```json
{
  "documents": [
    {
      "name": "products.json",
      "category": "dummy_data",
      "chunks": 15
    }
  ]
}
```

---

#### `DELETE /delete-document/<filename>`

Delete a specific document.

**Response:**
```json
{
  "message": "Document products.json deleted successfully"
}
```

---

#### `POST /clear-knowledge`

Clear all documents from the knowledge base.

**Response:**
```json
{
  "message": "Knowledge base cleared successfully"
}
```

---

#### `POST /search-knowledge`

Search the knowledge base (without LLM).

**Request:**
```json
{
  "query": "product pricing",
  "top_k": 3
}
```

**Response:**
```json
{
  "results": [
    {
      "content": "ChatGenius pricing: Starter Rp 2.5M...",
      "source": "products.json",
      "distance": 0.23
    }
  ]
}
```

---

## RAG vs Standard Chat

| Aspect | Standard Chat | RAG Chat |
|--------|--------------|----------|
| **Knowledge Source** | LLM training data only | Your documents + LLM |
| **Accuracy** | General knowledge | Specific to your data |
| **Citations** | ❌ No sources | ✅ With source references |
| **Hallucination Risk** | Higher | Lower |
| **Best For** | General Q&A, creative tasks | Domain-specific Q&A |
| **Response Time** | Faster | Slightly slower (retrieval + generation) |
| **Customization** | Limited | High (your own data) |

---

## File Structure

```
Gemini_Chatbot/
├── app.py                     # Flask backend with RAG endpoints
├── index.html                 # HTML structure
├── style.css                  # Modern glassmorphism styles
├── script.js                  # Frontend JavaScript
├── requirements.txt           # Python dependencies
├── README.md                  # User documentation
├── ARCHITECTURE.md            # This file
│
├── data/
│   ├── documents/             # Uploaded documents storage
│   └── dummy_data/            # Pre-loaded sample data
│       ├── company_info.json  # Company profile
│       ├── products.json      # Product catalog
│       └── FAQ.json           # FAQ entries
│
├── utils/
│   ├── __init__.py            # Package init
│   └── rag_engine.py          # RAG processing engine
│
└── vector_store/              # ChromaDB vector embeddings (auto-generated)
```

---

## Security Considerations (Demo Mode)

⚠️ **This is a demo application. Not production-ready.**

### Current Limitations

| Issue | Status | Risk Level |
|-------|--------|------------|
| API Key in memory only | ✅ Implemented (lost on refresh) | Medium |
| No user authentication | ⚠️ Not implemented | High |
| Debug mode enabled | ⚠️ `debug=True` | Medium |
| CORS enabled for all origins | ⚠️ `CORS(app)` | Medium |
| No rate limiting | ⚠️ Not implemented | Medium |
| No input sanitization | ⚠️ Basic only | Medium |

### Production Recommendations

- [ ] Use environment variables for API keys
- [ ] Implement user authentication (OAuth, JWT)
- [ ] Add rate limiting (Flask-Limiter)
- [ ] Enable HTTPS
- [ ] Add input validation & sanitization
- [ ] Implement logging & monitoring
- [ ] Add error handling & retry logic
- [ ] Use production WSGI server (Gunicorn, uWSGI)

---

## Performance Considerations

### Embedding Generation

- **Model**: `all-MiniLM-L6-v2` (384 dimensions)
- **Size**: ~90MB
- **Speed**: ~50ms per chunk
- **First run**: Downloads model automatically

### Vector Search

- **Database**: ChromaDB (persistent)
- **Search method**: Cosine similarity
- **Default top_k**: 5 results
- **Search speed**: ~10-50ms for 1000 chunks

### Response Time

| Operation | Typical Time |
|-----------|--------------|
| RAG retrieval | 50-100ms |
| Gemini API call | 500-2000ms |
| Total (RAG chat) | 600-2200ms |
| Standard chat | 500-2000ms |

---

## Troubleshooting

### Common Issues

#### 1. Model Not Found (404 Error)

```
Error: 404 models/gemini-xxx is not found
```

**Solution**: Check available models:
```python
import google.generativeai as genai
genai.configure(api_key="your-key")
print([m.name for m in genai.list_models()])
```

Update `app.py` with valid model name.

---

#### 2. RAG Engine Not Initialized

```
Error: RAG engine not initialized
```

**Solution**: 
1. Ensure API key is entered
2. Check if ChromaDB initialized successfully
3. Verify `sentence-transformers` is installed

---

#### 3. Document Upload Fails

```
Error: Unsupported file format
```

**Solution**: Use supported formats: `.txt`, `.json`, `.pdf`, `.docx`

---

## Future Enhancements

- [ ] Multi-language support (Indonesian, English, etc.)
- [ ] Advanced chunking (semantic chunking)
- [ ] Hybrid search (keyword + vector)
- [ ] Document versioning
- [ ] Chat history persistence
- [ ] Export conversations
- [ ] Admin dashboard
- [ ] Analytics & usage metrics
- [ ] Webhook integrations
- [ ] API key management UI

---

## Credits

- **Google Gemini** - LLM provider
- **ChromaDB** - Vector database
- **Hugging Face** - Sentence Transformers
- **Hacktiv8** - AI for Developer course

---

**Version**: 1.0  
**Last Updated**: March 2026
