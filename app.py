import os
import webbrowser
import json
from pathlib import Path
import google.generativeai as genai
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import threading

# Import RAG engine
from utils.rag_engine import rag_engine

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

chat_session = None
rag_enabled = False


# ============================
# 🧠 ROUTE UTAMA
# ============================
@app.route('/')
def index():
    """Mengembalikan halaman utama chatbot"""
    return send_from_directory('.', 'index.html')


# ============================
# 🔑 SET API KEY
# ============================
@app.route('/set-api-key', methods=['POST'])
def set_api_key():
    global chat_session, rag_enabled
    api_key = request.json.get("api_key")

    if not api_key:
        return jsonify({"error": "API Key tidak boleh kosong."}), 400

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        chat_session = model.start_chat(history=[])

        # Initialize RAG engine
        rag_enabled = rag_engine.initialize()

        # Load dummy data if RAG is enabled
        if rag_enabled:
            rag_engine.load_dummy_data("./data/dummy_data")

        print("✅ Model Gemini dan RAG Engine berhasil diinisialisasi.")
        return jsonify({
            "message": "API Key diterima dan model berhasil diinisialisasi.",
            "rag_enabled": rag_enabled
        })
    except Exception as e:
        chat_session = None
        rag_enabled = False
        print(f"❌ Error saat inisialisasi Gemini: {e}")
        return jsonify({"error": "API Key tidak valid atau terjadi kesalahan pada server."}), 500


# ============================
# 💬 CHAT ENDPOINT (With RAG)
# ============================
@app.route('/chat', methods=['POST'])
def chat():
    global chat_session, rag_enabled

    if not chat_session:
        return jsonify({"error": "Harap masukkan API Key yang valid terlebih dahulu."}), 401

    user_message = request.json.get("message")
    use_rag = request.json.get("use_rag", True)

    if not user_message:
        return jsonify({"error": "Pesan tidak boleh kosong."}), 400

    try:
        # RAG-enhanced response (optional)
        if use_rag and rag_enabled:
            try:
                # Get relevant context from knowledge base
                context = rag_engine.get_context(user_message)

                if context:
                    # Build enhanced prompt with context
                    enhanced_prompt = f"""Based on the following context, answer the question.

Context: {context}

Question: {user_message}

Answer:"""

                    response = chat_session.send_message(enhanced_prompt)
                    return jsonify({
                        "response": response.text,
                        "rag_used": True,
                        "sources": extract_sources(context)
                    })
            except Exception as rag_error:
                print(f"RAG error: {rag_error}")
                # Continue to standard chat if RAG fails

        # Standard chat (no RAG or RAG failed)
        response = chat_session.send_message(user_message)
        return jsonify({
            "response": response.text,
            "rag_used": False,
            "sources": []
        })
        
    except Exception as e:
        print(f"❌ Error saat mengirim pesan ke Gemini: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Terjadi kesalahan: {str(e)}"}), 500


def extract_sources(context: str) -> list:
    """Extract source filenames from context."""
    sources = []
    for line in context.split('\n'):
        if line.startswith('[Source:'):
            source = line.replace('[Source:', '').replace(']', '').strip()
            if source not in sources:
                sources.append(source)
    return sources


# ============================
# 📁 DOCUMENT UPLOAD ENDPOINT
# ============================
@app.route('/upload-document', methods=['POST'])
def upload_document():
    """Upload and process a document for the knowledge base."""
    if not rag_enabled:
        return jsonify({"error": "RAG engine not initialized"}), 500
    
    try:
        # Check if file is in request
        if 'file' not in request.files:
            # Try to get raw text content
            data = request.json
            if data and 'content' in data and 'filename' in data:
                content = data['content']
                filename = data['filename']
                if rag_engine.add_document(content, filename):
                    return jsonify({
                        "message": f"Document {filename} added successfully",
                        "filename": filename
                    })
            return jsonify({"error": "No file or content provided"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Read file content based on type
        filename = file.filename
        content = ""
        
        if filename.endswith('.txt'):
            content = file.read().decode('utf-8')
        elif filename.endswith('.json'):
            content = file.read().decode('utf-8')
        elif filename.endswith('.pdf'):
            # Save and process PDF
            from PyPDF2 import PdfReader
            temp_path = f"./data/documents/{filename}"
            file.save(temp_path)
            reader = PdfReader(temp_path)
            for page in reader.pages:
                content += page.extract_text()
        elif filename.endswith('.docx'):
            # Save and process DOCX
            from docx import Document
            temp_path = f"./data/documents/{filename}"
            file.save(temp_path)
            doc = Document(temp_path)
            for para in doc.paragraphs:
                content += para.text + "\n"
        else:
            return jsonify({"error": "Unsupported file format. Use .txt, .json, .pdf, or .docx"}), 400
        
        # Add to RAG engine
        if rag_engine.add_document(content, filename):
            return jsonify({
                "message": f"Document {filename} processed successfully",
                "filename": filename
            })
        else:
            return jsonify({"error": "Failed to process document"}), 500
            
    except Exception as e:
        print(f"❌ Error uploading document: {e}")
        return jsonify({"error": str(e)}), 500


# ============================
# 📋 GET DOCUMENTS ENDPOINT
# ============================
@app.route('/get-documents', methods=['GET'])
def get_documents():
    """Get list of all documents in knowledge base."""
    if not rag_enabled:
        return jsonify({"error": "RAG engine not initialized"}), 500
    
    try:
        docs = rag_engine.get_all_documents()
        return jsonify({"documents": docs})
    except Exception as e:
        print(f"❌ Error getting documents: {e}")
        return jsonify({"error": str(e)}), 500


# ============================
# 🗑️ DELETE DOCUMENT ENDPOINT
# ============================
@app.route('/delete-document/<filename>', methods=['DELETE'])
def delete_document(filename):
    """Delete a document from the knowledge base."""
    if not rag_enabled:
        return jsonify({"error": "RAG engine not initialized"}), 500
    
    try:
        if rag_engine.remove_document(filename):
            return jsonify({"message": f"Document {filename} deleted successfully"})
        else:
            return jsonify({"error": f"Document {filename} not found"}), 404
    except Exception as e:
        print(f"❌ Error deleting document: {e}")
        return jsonify({"error": str(e)}), 500


# ============================
# 🔍 SEARCH KNOWLEDGE BASE
# ============================
@app.route('/search-knowledge', methods=['POST'])
def search_knowledge():
    """Search the knowledge base without sending to LLM."""
    if not rag_enabled:
        return jsonify({"error": "RAG engine not initialized"}), 500
    
    try:
        query = request.json.get("query", "")
        top_k = request.json.get("top_k", 3)
        
        results = rag_engine.search(query, top_k=top_k)
        return jsonify({"results": results})
        
    except Exception as e:
        print(f"❌ Error searching knowledge base: {e}")
        return jsonify({"error": str(e)}), 500


# ============================
# 🧹 CLEAR KNOWLEDGE BASE
# ============================
@app.route('/clear-knowledge', methods=['POST'])
def clear_knowledge():
    """Clear all documents from the knowledge base."""
    if not rag_enabled:
        return jsonify({"error": "RAG engine not initialized"}), 500
    
    try:
        rag_engine.clear_all()
        return jsonify({"message": "Knowledge base cleared successfully"})
    except Exception as e:
        print(f"❌ Error clearing knowledge base: {e}")
        return jsonify({"error": str(e)}), 500


# ============================
# 🌐 SERVE STATIC FILES
# ============================
@app.route('/<path:path>')
def serve_static(path):
    """Menyediakan file static seperti CSS dan JS"""
    return send_from_directory('.', path)


# ============================
# 🚀 AUTO OPEN BROWSER (once)
# ============================
def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")


if __name__ == '__main__':
    # Ensure directories exist
    os.makedirs("./data/documents", exist_ok=True)
    os.makedirs("./vector_store", exist_ok=True)
    
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        threading.Timer(1.0, open_browser).start()

    app.run(host='0.0.0.0', port=5000, debug=True)
