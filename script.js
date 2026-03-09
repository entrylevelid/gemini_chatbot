document.addEventListener("DOMContentLoaded", () => {
    // === DOM Elements ===
    const chatBox = document.getElementById("chat-box");
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");
    const typingIndicator = document.getElementById("typing-indicator");
    const apiKeyInput = document.getElementById("api-key-input");
    const saveKeyBtn = document.getElementById("save-key-btn");
    const apiKeySection = document.getElementById("api-key-section");
    const statusIndicator = document.getElementById("status-indicator");
    const ragToggle = document.getElementById("rag-toggle");
    const ragStatus = document.getElementById("rag-status");
    const uploadArea = document.getElementById("upload-area");
    const fileInput = document.getElementById("file-input");
    const documentList = document.getElementById("document-list");
    const clearKnowledgeBtn = document.getElementById("clear-knowledge-btn");
    const sidebarToggle = document.getElementById("sidebar-toggle");
    const sidebar = document.getElementById("sidebar");
    const mobileMenuBtn = document.getElementById("mobile-menu-btn");
    const uploadModal = document.getElementById("upload-modal");
    const modalClose = document.getElementById("modal-close");
    const uploadProgress = document.getElementById("upload-progress");
    const uploadSuccess = document.getElementById("upload-success");
    const uploadError = document.getElementById("upload-error");
    const uploadSuccessText = document.getElementById("upload-success-text");
    const uploadErrorText = document.getElementById("upload-error-text");

    // === State ===
    let isReady = false;
    let ragEnabled = true;

    // === Initialize ===
    function initializeChat() {
        addMessage("👋 Hi! I'm your RAG-powered AI Assistant. Please enter your Gemini API Key to get started.", "bot");
        loadDocuments();
    }

    // === API Key Handling ===
    async function handleSaveApiKey() {
        const apiKey = apiKeyInput.value.trim();
        if (!apiKey) {
            addMessage("⚠️ Please enter your API Key.", "bot");
            return;
        }

        saveKeyBtn.textContent = 'Validating...';
        saveKeyBtn.disabled = true;

        try {
            const response = await fetch('/set-api-key', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ api_key: apiKey })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Unknown error occurred.');
            }

            addMessage("✅ API Key validated successfully! You can now start chatting. The knowledge base has been loaded with sample data.", "bot");
            apiKeySection.style.display = 'none';
            userInput.disabled = false;
            sendBtn.disabled = false;
            userInput.focus();
            
            isReady = true;
            ragEnabled = data.rag_enabled || false;
            updateStatus('ready');
            updateRagStatus();
            loadDocuments();

        } catch (error) {
            console.error("API Key validation error:", error);
            addMessage(`❌ Failed to validate API Key: ${error.message}`, "bot");
        } finally {
            saveKeyBtn.textContent = 'Save';
            saveKeyBtn.disabled = false;
        }
    }

    // === Status Updates ===
    function updateStatus(status) {
        if (status === 'ready') {
            statusIndicator.classList.add('ready');
            statusIndicator.querySelector('.status-text').textContent = 'Ready';
        } else {
            statusIndicator.classList.remove('ready');
            statusIndicator.querySelector('.status-text').textContent = 'Waiting for API Key...';
        }
    }

    function updateRagStatus() {
        if (ragEnabled) {
            ragStatus.textContent = 'enabled';
            ragStatus.className = 'rag-status-active';
        } else {
            ragStatus.textContent = 'disabled';
            ragStatus.className = 'rag-status-inactive';
        }
    }

    // === Chat Functions ===
    function addMessage(message, sender, sources = []) {
        const messageElement = document.createElement("div");
        messageElement.classList.add("message", sender);

        const avatar = document.createElement("div");
        avatar.classList.add("message-avatar");
        avatar.textContent = sender === 'user' ? '🧑' : '🤖';

        const content = document.createElement("div");
        content.classList.add("message-content");

        const bubble = document.createElement("div");
        bubble.classList.add("message-bubble");
        
        // Process message text (bold, code blocks)
        bubble.innerHTML = formatMessage(message);

        content.appendChild(bubble);

        // Add sources if available
        if (sources && sources.length > 0) {
            const sourcesDiv = document.createElement("div");
            sourcesDiv.classList.add("message-sources");
            sourcesDiv.innerHTML = sources.map(source => 
                `<span class="source-tag">📄 ${escapeHtml(source)}</span>`
            ).join('');
            content.appendChild(sourcesDiv);
        }

        messageElement.appendChild(avatar);
        messageElement.appendChild(content);

        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function formatMessage(message) {
        // Escape HTML first
        let formatted = escapeHtml(message);
        
        // Bold (**text**)
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Code blocks (```code```)
        formatted = formatted.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
        
        // Inline code (`code`)
        formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');
        
        // Line breaks
        formatted = formatted.replace(/\n/g, '<br>');
        
        return formatted;
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    async function getBotResponse(message) {
        typingIndicator.classList.add('active');
        chatBox.scrollTop = chatBox.scrollHeight;

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    message: message,
                    use_rag: ragEnabled
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            addMessage(data.response, "bot", data.sources || []);

        } catch (error) {
            console.error("Error:", error);
            addMessage(`❌ Error: ${error.message}`, "bot");
        } finally {
            typingIndicator.classList.remove('active');
        }
    }

    function handleSendMessage() {
        const message = userInput.value.trim();
        if (message === "" || !isReady) return;

        addMessage(message, "user");
        userInput.value = "";
        getBotResponse(message);
    }

    // === Document Functions ===
    async function loadDocuments() {
        try {
            const response = await fetch('/get-documents');
            if (response.ok) {
                const data = await response.json();
                renderDocumentList(data.documents || []);
            }
        } catch (error) {
            console.error("Error loading documents:", error);
        }
    }

    function renderDocumentList(documents) {
        if (documents.length === 0) {
            documentList.innerHTML = '<p style="color: var(--text-muted); font-size: 0.85rem; text-align: center; padding: 20px;">No documents in knowledge base</p>';
            return;
        }

        documentList.innerHTML = documents.map(doc => `
            <div class="document-item" data-filename="${escapeHtml(doc.name)}">
                <div class="document-info">
                    <span class="document-icon">${getDocumentIcon(doc.name)}</span>
                    <span class="document-name" title="${escapeHtml(doc.name)}">${escapeHtml(doc.name)}</span>
                    <span class="document-chunks">${doc.chunks} chunks</span>
                </div>
                <button class="document-delete" title="Delete document" onclick="deleteDocument('${escapeHtml(doc.name)}')">
                    <svg width="16" height="16" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/>
                    </svg>
                </button>
            </div>
        `).join('');
    }

    function getDocumentIcon(filename) {
        const ext = filename.split('.').pop().toLowerCase();
        const icons = {
            'pdf': '📕',
            'docx': '📘',
            'txt': '📃',
            'json': '📋'
        };
        return icons[ext] || '📄';
    }

    async function uploadFile(file) {
        // Show modal with progress
        uploadModal.classList.add('active');
        uploadProgress.style.display = 'block';
        uploadSuccess.style.display = 'none';
        uploadError.style.display = 'none';

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/upload-document', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                uploadProgress.style.display = 'none';
                uploadSuccess.style.display = 'block';
                uploadSuccessText.textContent = `${file.name} has been added to the knowledge base.`;
                loadDocuments();
            } else {
                throw new Error(data.error || 'Upload failed');
            }
        } catch (error) {
            console.error("Upload error:", error);
            uploadProgress.style.display = 'none';
            uploadError.style.display = 'block';
            uploadErrorText.textContent = error.message;
        }
    }

    // Exposed function for delete button
    window.deleteDocument = async function(filename) {
        if (!confirm(`Delete "${filename}" from the knowledge base?`)) return;

        try {
            const response = await fetch(`/delete-document/${encodeURIComponent(filename)}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                loadDocuments();
                addMessage(`📄 Document "${filename}" has been deleted.`, "bot");
            } else {
                const data = await response.json();
                alert(data.error || 'Failed to delete document');
            }
        } catch (error) {
            console.error("Delete error:", error);
            alert('Failed to delete document');
        }
    };

    async function clearKnowledgeBase() {
        if (!confirm('Are you sure you want to clear all documents from the knowledge base? This cannot be undone.')) return;

        try {
            const response = await fetch('/clear-knowledge', {
                method: 'POST'
            });

            if (response.ok) {
                loadDocuments();
                addMessage("🗑️ Knowledge base has been cleared.", "bot");
            } else {
                const data = await response.json();
                alert(data.error || 'Failed to clear knowledge base');
            }
        } catch (error) {
            console.error("Clear error:", error);
            alert('Failed to clear knowledge base');
        }
    }

    // === Event Listeners ===
    saveKeyBtn.addEventListener("click", handleSaveApiKey);
    apiKeyInput.addEventListener("keypress", (event) => {
        if (event.key === "Enter") handleSaveApiKey();
    });

    sendBtn.addEventListener("click", handleSendMessage);
    userInput.addEventListener("keypress", (event) => {
        if (event.key === "Enter") handleSendMessage();
    });

    // RAG Toggle
    ragToggle.addEventListener("change", () => {
        ragEnabled = ragToggle.checked;
        updateRagStatus();
        addMessage(
            `RAG mode has been ${ragEnabled ? '✅ enabled' : '❌ disabled'}. ${
                ragEnabled 
                    ? 'I will use the knowledge base to answer your questions.' 
                    : 'I will answer using my general knowledge.'
            }`,
            "bot"
        );
    });

    // File Upload - Drag & Drop
    uploadArea.addEventListener('click', () => fileInput.click());
    
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            uploadFile(e.target.files[0]);
            fileInput.value = '';
        }
    });

    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('drag-over');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('drag-over');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');
        if (e.dataTransfer.files.length > 0) {
            uploadFile(e.dataTransfer.files[0]);
        }
    });

    // Modal Close
    modalClose.addEventListener('click', () => {
        uploadModal.classList.remove('active');
    });

    uploadModal.querySelector('.modal-overlay').addEventListener('click', () => {
        uploadModal.classList.remove('active');
    });

    // Clear Knowledge Base
    clearKnowledgeBtn.addEventListener('click', clearKnowledgeBase);

    // Sidebar Toggle
    sidebarToggle.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
    });

    // Mobile Menu
    mobileMenuBtn.addEventListener('click', () => {
        sidebar.classList.toggle('active');
    });

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', (e) => {
        if (window.innerWidth <= 768) {
            if (!sidebar.contains(e.target) && !mobileMenuBtn.contains(e.target)) {
                sidebar.classList.remove('active');
            }
        }
    });

    // === Start Application ===
    initializeChat();
});
