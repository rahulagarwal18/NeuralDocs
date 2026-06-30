document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const statusText = document.getElementById('statusText');
    const progressFill = document.getElementById('progressFill');
    
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    const chatHistory = document.getElementById('chatHistory');

    // Drag and Drop Handlers
    dropZone.addEventListener('click', () => fileInput.click());
    
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });
    
    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });
    
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            handleFileUpload(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFileUpload(e.target.files[0]);
        }
    });

    function handleFileUpload(file) {
        if (file.type !== 'application/pdf') {
            statusText.textContent = "Error: Only PDF files allowed.";
            statusText.style.color = "#ef4444";
            return;
        }

        statusText.textContent = "Uploading & Chunking PDF...";
        statusText.style.color = "var(--text-primary)";
        progressFill.style.width = "30%";

        const formData = new FormData();
        formData.append('file', file);

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) throw new Error(data.error);
            
            progressFill.style.width = "100%";
            statusText.textContent = data.message;
            statusText.style.color = "var(--success)";
            
            // Enable Chat
            chatInput.disabled = false;
            sendBtn.disabled = false;
            chatInput.focus();
            
            addMessage("system", `Document "${file.name}" has been processed and embedded into the vector database. What would you like to know?`);
        })
        .catch(error => {
            progressFill.style.width = "0%";
            statusText.textContent = error.message;
            statusText.style.color = "#ef4444";
        });
    }

    // Chat Handlers
    function addMessage(sender, text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.textContent = sender === 'system' ? '🧠' : '👤';
        
        const bubble = document.createElement('div');
        bubble.className = 'bubble';
        if (sender === 'system' && typeof marked !== 'undefined') {
            bubble.innerHTML = marked.parse(text);
        } else {
            bubble.textContent = text;
        }
        
        msgDiv.appendChild(avatar);
        msgDiv.appendChild(bubble);
        
        chatHistory.appendChild(msgDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    function handleSend() {
        const query = chatInput.value.trim();
        if (!query) return;

        addMessage('user', query);
        chatInput.value = '';
        chatInput.disabled = true;
        sendBtn.disabled = true;

        fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) throw new Error(data.error);
            addMessage('system', data.answer);
        })
        .catch(error => {
            addMessage('system', `Error: ${error.message}`);
        })
        .finally(() => {
            chatInput.disabled = false;
            sendBtn.disabled = false;
            chatInput.focus();
        });
    }

    sendBtn.addEventListener('click', handleSend);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSend();
    });
});
