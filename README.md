# 🤖 Gemini RAG Chatbot Assistant

A modern, RAG (Retrieval-Augmented Generation) powered chatbot built with Flask and Google Gemini AI. This chatbot can answer questions based on your own knowledge base documents.

![RAG Chatbot](https://img.shields.io/badge/RAG-Enabled-success)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Flask](https://img.shields.io/badge/Flask-2.0+-green)
![Gemini](https://img.shields.io/badge/Gemini-API-purple)

---

## ✨ Features

### 🧠 RAG Capabilities
- **Document-Based Answers**: Get responses based on your uploaded documents
- **Source Citation**: Every answer includes references to source documents
- **Multiple Formats**: Support for PDF, DOCX, TXT, and JSON files
- **Smart Search**: Semantic search using vector embeddings
- **Toggle RAG**: Switch between RAG mode and standard chat

### 📁 Knowledge Base
- **Pre-loaded Dummy Data**: Sample company info, products, and FAQ
- **Document Upload**: Drag & drop or browse to upload files
- **Document Management**: View and delete uploaded documents
- **Auto-Chunking**: Automatic text chunking for better retrieval

### 🎨 Modern UI
- **Glassmorphism Design**: Beautiful frosted glass effect
- **Dark Theme**: Eye-friendly dark mode with gradient accents
- **Responsive**: Works on desktop and mobile devices
- **Animated**: Smooth transitions and typing indicators
- **Collapsible Sidebar**: Maximize chat space when needed

---

## 🚀 Installation

### 1. Clone or Download
```bash
cd Gemini_Chatbot
```

### 2. Create Virtual Environment
**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

> ⚠️ **Note**: The first time you run the app, it will download the sentence transformer model (~90MB). This is automatic.

### 4. Get Gemini API Key
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key (you'll need this when running the app)

### 5. Run the Application
```bash
python app.py
```

The browser will automatically open to `http://127.0.0.1:5000`

---

## 📖 How to Use

### Basic Chat
1. Enter your Gemini API Key in the sidebar
2. Click "Save" to validate
3. Type your message and press Enter or click Send

### Using RAG Mode
1. **RAG is enabled by default** when you start
2. Ask questions about the pre-loaded dummy data:
   - "What products does TechCorp offer?"
   - "Tell me about ChatGenius pricing"
   - "What is the company's mission?"
   - "How do I contact support?"
3. The bot will search the knowledge base and cite sources

### Uploading Documents
1. Click the upload area in the sidebar or drag & drop a file
2. Supported formats: `.txt`, `.json`, `.pdf`, `.docx`
3. Wait for processing to complete
4. Your document will appear in the document list

### Managing Documents
- **View**: All documents are listed in the sidebar
- **Delete**: Click the × button next to any document
- **Clear All**: Click "Clear Knowledge" in Settings

### Toggling RAG
- Use the "RAG Mode" toggle in Settings
- **Enabled**: Bot uses knowledge base + AI
- **Disabled**: Bot uses only AI knowledge

---

## 📂 Project Structure

```
Gemini_Chatbot/
├── app.py                 # Flask backend with RAG endpoints
├── index.html             # HTML structure
├── style.css              # Modern glassmorphism styles
├── script.js              # Frontend JavaScript
├── requirements.txt       # Python dependencies
├── data/
│   ├── documents/         # Uploaded documents storage
│   └── dummy_data/        # Pre-loaded sample data
│       ├── company_info.json
│       ├── products.json
│       └── FAQ.json
├── utils/
│   └── rag_engine.py      # RAG processing engine
└── vector_store/          # ChromaDB vector embeddings
```

---

## 🔧 Configuration

### Environment Variables (Optional)
Create a `.env` file in the project root:

```env
FLASK_ENV=development
FLASK_PORT=5000
DEBUG=False
```

### Model Configuration
The app uses:
- **LLM**: Google Gemini 1.5 Flash
- **Embeddings**: SentenceTransformer (all-MiniLM-L6-v2)
- **Vector DB**: ChromaDB

---

## 📝 Dummy Data

The chatbot comes pre-loaded with sample data about "TechCorp Indonesia":

| File | Content |
|------|---------|
| `company_info.json` | Company profile, mission, values, services |
| `products.json` | 6 AI products with features, pricing, use cases |
| `FAQ.json` | 15 frequently asked questions with answers |

### Sample Questions to Try:
```
What is TechCorp Indonesia's mission?
Tell me about ChatGenius features
How much does DocuMind cost?
What are the company values?
How do I contact support?
What is RAG Chatbot Pro?
Are there discounts for startups?
What languages are supported?
```

---

## 🛠️ API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main chat interface |
| `/set-api-key` | POST | Set Gemini API key |
| `/chat` | POST | Send message (with optional RAG) |
| `/upload-document` | POST | Upload document to knowledge base |
| `/get-documents` | GET | List all documents |
| `/delete-document/<filename>` | DELETE | Remove a document |
| `/search-knowledge` | POST | Search knowledge base |
| `/clear-knowledge` | POST | Clear all documents |

---

## 🐛 Troubleshooting

### "RAG engine not initialized"
- This is normal if you haven't entered an API key yet
- Enter your API key to initialize RAG

### "Module not found" errors
```bash
pip install -r requirements.txt --upgrade
```

### Port already in use
Edit `app.py` and change the port number:
```python
app.run(host='0.0.0.0', port=5001, debug=True)
```

### Slow first response
- The first query downloads the embedding model
- Subsequent queries will be faster

### API Key errors
- Make sure your API key is valid
- Check your internet connection
- Visit [Google AI Studio](https://aistudio.google.com/) to verify

---

## 📚 Dependencies

```
Flask              # Web framework
Flask-Cors         # Cross-origin support
google-generativeai # Google Gemini AI
chromadb           # Vector database
sentence-transformers # Text embeddings
PyPDF2             # PDF parsing
python-docx        # Word document parsing
```

---

## 🎨 UI Features

- **Glassmorphism**: Frosted glass effect with backdrop blur
- **Gradient Accents**: Purple/blue gradient theme
- **Typing Indicator**: Animated dots while bot is thinking
- **Source Tags**: Visual citations for RAG responses
- **Drag & Drop**: Easy file upload
- **Mobile Responsive**: Hamburger menu for small screens
- **Dark Mode**: Easy on the eyes for long sessions

---

## 📄 License

This project is for educational purposes as part of the Hacktiv8 AI for Developer course.

---

## 🙏 Credits

- **Google Gemini** - LLM provider
- **Hacktiv8** - Course provider
- **ChromaDB** - Vector database
- **Hugging Face** - Sentence Transformers

---

## 📞 Support

For questions about this project, contact the course instructors or refer to the Hacktiv8 learning materials.

**Happy Chatting! 🚀**
