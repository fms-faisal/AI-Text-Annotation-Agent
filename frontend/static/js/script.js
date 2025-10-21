let currentAnnotations = null;
let currentMode = 'annotate'; // 'annotate' or 'chat'

document.addEventListener('DOMContentLoaded', function() {
    // Annotation mode elements
    const inputText = document.getElementById('inputText');
    const annotateBtn = document.getElementById('annotateBtn');
    const clearBtn = document.getElementById('clearBtn');
    const exampleBtn = document.getElementById('exampleBtn');
    const exportBtn = document.getElementById('exportBtn');
    const outputSection = document.getElementById('outputSection');
    const errorSection = document.getElementById('errorSection');
    
    // Chat mode elements
    const chatInput = document.getElementById('chatInput');
    const sendChatBtn = document.getElementById('sendChatBtn');
    const resetChatBtn = document.getElementById('resetChatBtn');
    const chatMessages = document.getElementById('chatMessages');
    
    // Mode toggle elements
    const annotateModeBtn = document.getElementById('annotateMode');
    const chatModeBtn = document.getElementById('chatMode');
    const annotationView = document.getElementById('annotationView');
    const chatView = document.getElementById('chatView');
    
    // Event listeners - Annotation Mode
    annotateBtn.addEventListener('click', annotateText);
    clearBtn.addEventListener('click', clearAll);
    exampleBtn.addEventListener('click', loadExample);
    exportBtn.addEventListener('click', exportAnnotations);
    
    // Event listeners - Chat Mode
    sendChatBtn.addEventListener('click', sendChat);
    resetChatBtn.addEventListener('click', resetChat);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendChat();
        }
    });
    
    // Event listeners - Mode Toggle
    annotateModeBtn.addEventListener('click', () => switchMode('annotate'));
    chatModeBtn.addEventListener('click', () => switchMode('chat'));
    
    // Example text
    const exampleText = `On October 21, 2025, at 14:30, at City General Hospital Emergency Department (ED), Karim Ullah, a 55-year-old male with a history of Asthma and Hypertension, presented after 12 hours of worsening shortness of breath (SOB) and wheezing. The patient is alert, oriented, speaking full sentences, and in no acute distress. Vital signs are stable: blood pressure 132/86 mmHg, heart rate 92 bpm, and oxygen saturation 92% on room air. Lung exam reveals slightly diminished breath sounds with mild end-expiratory wheezing; no accessory muscle use or cyanosis noted. Cardiac examination shows normal heart sounds (S1 and S2), no murmurs, and no jugular venous distension (JVD). The patient denies fever, chest pain, peripheral edema, or recent infections, and has no recent hospitalizations. He reports having lost his Albuterol inhaler 3 days ago. A chest X-ray was ordered, and initial Troponin levels are pending. Treatment was initiated with 2 grams of Magnesium Sulfate intravenously and Prednisone 40 mg by mouth daily.`;
    
    function switchMode(mode) {
        currentMode = mode;
        
        if (mode === 'annotate') {
            annotateModeBtn.classList.add('active');
            chatModeBtn.classList.remove('active');
            annotationView.style.display = 'block';
            chatView.style.display = 'none';
        } else {
            chatModeBtn.classList.add('active');
            annotateModeBtn.classList.remove('active');
            annotationView.style.display = 'none';
            chatView.style.display = 'block';
        }
        
        errorSection.style.display = 'none';
    }
    function loadExample() {
        inputText.value = exampleText;
        inputText.focus();
    }
    
    async function annotateText() {
        const text = inputText.value.trim();
        
        if (!text) {
            showError('Please enter some text to annotate');
            return;
        }
        
        // Show loading state
        const btnText = annotateBtn.querySelector('.btn-text');
        const loader = annotateBtn.querySelector('.loader');
        btnText.textContent = 'Annotating...';
        loader.style.display = 'inline-block';
        annotateBtn.disabled = true;
        
        // Hide previous results
        outputSection.style.display = 'none';
        errorSection.style.display = 'none';
        
        try {
            const response = await fetch('/api/annotate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text: text })
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                currentAnnotations = data;
                displayAnnotations(data.annotations);
                outputSection.style.display = 'block';
            } else {
                showError(data.error || 'An error occurred during annotation');
            }
        } catch (error) {
            showError('Failed to connect to the server. Make sure the backend is running on port 5000.');
            console.error('Error:', error);
        } finally {
            btnText.textContent = 'Annotate Text';
            loader.style.display = 'none';
            annotateBtn.disabled = false;
        }
    }
    
    function displayAnnotations(annotations) {
        displayEntities(annotations.entities || {});
        displaySentiment(annotations.sentiment || []);
        displayKeywords(annotations.keywords || []);
        displayRelationships(annotations.relationships || []);
    }
    
    function displayEntities(entities) {
        const container = document.getElementById('entitiesOutput');
        container.innerHTML = '';
        
        const entityTypes = Object.keys(entities);
        let hasEntities = false;
        
        entityTypes.forEach(type => {
            if (entities[type] && entities[type].length > 0) {
                hasEntities = true;
                const categoryDiv = document.createElement('div');
                categoryDiv.innerHTML = `<span class="entity-category">${type}:</span>`;
                
                entities[type].forEach(entity => {
                    const tag = document.createElement('span');
                    tag.className = `entity-tag entity-${type}`;
                    tag.textContent = entity;
                    categoryDiv.appendChild(tag);
                });
                
                container.appendChild(categoryDiv);
            }
        });
        
        if (!hasEntities) {
            container.innerHTML = '<p style="color: #999;">No entities found</p>';
        }
    }
    
    function displaySentiment(sentiments) {
        const container = document.getElementById('sentimentOutput');
        container.innerHTML = '';
        
        if (sentiments.length === 0) {
            container.innerHTML = '<p style="color: #999;">No sentiment analysis available</p>';
            return;
        }
        
        sentiments.forEach(item => {
            const div = document.createElement('div');
            div.className = `sentiment-item sentiment-${item.sentiment}`;
            
            const confidence = (item.confidence * 100).toFixed(0);
            
            div.innerHTML = `
                <div>
                    "${item.sentence}"
                    <span class="sentiment-label">${item.sentiment.toUpperCase()}</span>
                    <span class="confidence">${confidence}%</span>
                </div>
            `;
            
            container.appendChild(div);
        });
    }
    
    function displayKeywords(keywords) {
        const container = document.getElementById('keywordsOutput');
        container.innerHTML = '';
        
        if (keywords.length === 0) {
            container.innerHTML = '<p style="color: #999;">No keywords extracted</p>';
            return;
        }
        
        keywords.forEach(kw => {
            const div = document.createElement('div');
            div.className = 'keyword-item';
            
            const score = (kw.importance * 100).toFixed(0);
            
            div.innerHTML = `
                <span class="keyword-term">${kw.term}</span>
                <span class="keyword-score">${score}</span>
            `;
            
            container.appendChild(div);
        });
    }
    
    function displayRelationships(relationships) {
        const container = document.getElementById('relationshipsOutput');
        container.innerHTML = '';
        
        if (relationships.length === 0) {
            container.innerHTML = '<p style="color: #999;">No relationships identified</p>';
            return;
        }
        
        relationships.forEach(rel => {
            const div = document.createElement('div');
            div.className = 'relationship-item';
            
            div.innerHTML = `
                <span class="relationship-subject">${rel.subject}</span>
                <span class="relationship-arrow">→</span>
                <span class="relationship-relation">${rel.relation}</span>
                <span class="relationship-arrow">→</span>
                <span class="relationship-object">${rel.object}</span>
            `;
            
            container.appendChild(div);
        });
    }
    
    function showError(message) {
        const errorMessage = document.getElementById('errorMessage');
        errorMessage.textContent = message;
        errorSection.style.display = 'block';
        
        setTimeout(() => {
            errorSection.style.display = 'none';
        }, 8000);
    }
    
    function clearAll() {
        inputText.value = '';
        outputSection.style.display = 'none';
        errorSection.style.display = 'none';
        currentAnnotations = null;
        inputText.focus();
    }
    
    function exportAnnotations() {
        if (!currentAnnotations) {
            showError('No annotations to export');
            return;
        }
        
        const dataStr = JSON.stringify(currentAnnotations, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        
        // Generate filename with timestamp
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        link.download = `annotations-${timestamp}.json`;
        
        // Trigger download
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }
    
    // CHAT MODE FUNCTIONS
    async function sendChat() {
        const message = chatInput.value.trim();
        
        if (!message) {
            showError('Please enter a message');
            return;
        }
        
        // Add user message to chat
        addChatMessage(message, 'user');
        chatInput.value = '';
        
        // Show loading state
        const btnText = sendChatBtn.querySelector('.btn-text');
        const loader = sendChatBtn.querySelector('.loader');
        btnText.textContent = 'Thinking...';
        loader.style.display = 'inline-block';
        sendChatBtn.disabled = true;
        
        try {
            // Check if user wants to analyze text
            const extractedText = extractTextFromMessage(message);
            
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    message: message,
                    text: extractedText
                })
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                addChatMessage(data.response, 'assistant');
                
                // If annotations were updated, display them
                if (data.annotations && data.has_text) {
                    displayChatAnnotations(data.annotations);
                    currentAnnotations = {
                        status: 'success',
                        annotations: data.annotations
                    };
                }
            } else {
                showError(data.error || 'Chat error occurred');
            }
        } catch (error) {
            showError('Failed to connect to the server');
            console.error('Error:', error);
        } finally {
            btnText.textContent = 'Send';
            loader.style.display = 'none';
            sendChatBtn.disabled = false;
        }
    }
    
    function extractTextFromMessage(message) {
        // Extract text after "analyze:" or "annotate:" prefix
        const patterns = [
            /analyze:\s*(.+)/i,
            /annotate:\s*(.+)/i,
            /analyze this text:\s*(.+)/i,
            /annotate this text:\s*(.+)/i,
            /analyze the following:\s*(.+)/i
        ];
        
        for (const pattern of patterns) {
            const match = message.match(pattern);
            if (match) {
                return match[1].trim();
            }
        }
        
        return null;
    }
    
    function displayChatAnnotations(annotations) {
        const chatAnnotationsPanel = document.getElementById('chatAnnotations');
        chatAnnotationsPanel.style.display = 'block';
        
        // Display entities
        displayChatEntities(annotations.entities || {});
        
        // Display sentiment
        displayChatSentiment(annotations.sentiment || []);
        
        // Display keywords
        displayChatKeywords(annotations.keywords || []);
        
        // Display relationships
        displayChatRelationships(annotations.relationships || []);
    }
    
    function displayChatEntities(entities) {
        const container = document.getElementById('chatEntitiesOutput');
        container.innerHTML = '';
        
        let hasEntities = false;
        
        Object.keys(entities).forEach(type => {
            if (entities[type] && entities[type].length > 0) {
                hasEntities = true;
                const categoryDiv = document.createElement('div');
                categoryDiv.innerHTML = `<span class="entity-category">${type}:</span>`;
                
                entities[type].forEach(entity => {
                    const tag = document.createElement('span');
                    tag.className = `entity-tag entity-${type}`;
                    tag.textContent = entity;
                    categoryDiv.appendChild(tag);
                });
                
                container.appendChild(categoryDiv);
            }
        });
        
        if (!hasEntities) {
            container.innerHTML = '<p style="color: #999; font-size: 0.85rem;">None found</p>';
        }
    }
    
    function displayChatSentiment(sentiments) {
        const container = document.getElementById('chatSentimentOutput');
        container.innerHTML = '';
        
        if (sentiments.length === 0) {
            container.innerHTML = '<p style="color: #999; font-size: 0.85rem;">None found</p>';
            return;
        }
        
        sentiments.forEach(item => {
            const div = document.createElement('div');
            div.className = `sentiment-item sentiment-${item.sentiment}`;
            
            const confidence = (item.confidence * 100).toFixed(0);
            
            div.innerHTML = `
                <div style="font-size: 0.85rem;">
                    "${item.sentence.substring(0, 50)}${item.sentence.length > 50 ? '...' : ''}"
                    <span class="sentiment-label">${item.sentiment.toUpperCase()}</span>
                </div>
            `;
            
            container.appendChild(div);
        });
    }
    
    function displayChatKeywords(keywords) {
        const container = document.getElementById('chatKeywordsOutput');
        container.innerHTML = '';
        
        if (keywords.length === 0) {
            container.innerHTML = '<p style="color: #999; font-size: 0.85rem;">None found</p>';
            return;
        }
        
        keywords.slice(0, 5).forEach(kw => {
            const div = document.createElement('div');
            div.className = 'keyword-item';
            
            const score = (kw.importance * 100).toFixed(0);
            
            div.innerHTML = `
                <span class="keyword-term">${kw.term}</span>
                <span class="keyword-score">${score}</span>
            `;
            
            container.appendChild(div);
        });
    }
    
    function displayChatRelationships(relationships) {
        const container = document.getElementById('chatRelationshipsOutput');
        container.innerHTML = '';
        
        if (relationships.length === 0) {
            container.innerHTML = '<p style="color: #999; font-size: 0.85rem;">None found</p>';
            return;
        }
        
        relationships.forEach(rel => {
            const div = document.createElement('div');
            div.className = 'relationship-item';
            
            div.innerHTML = `
                <span class="relationship-subject">${rel.subject}</span>
                <span class="relationship-arrow">→</span>
                <span class="relationship-relation">${rel.relation}</span>
                <span class="relationship-arrow">→</span>
                <span class="relationship-object">${rel.object}</span>
            `;
            
            container.appendChild(div);
        });
    }
    
    function addChatMessage(content, role) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${role}`;
        
        const label = role === 'user' ? 'You' : 'AI Agent';
        
        messageDiv.innerHTML = `
            <div class="message-content">
                <strong>${label}:</strong>
                ${formatChatMessage(content)}
            </div>
        `;
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    function formatChatMessage(content) {
        // Convert newlines to <br>
        let formatted = content.replace(/\n/g, '<br>');
        
        // Convert **bold** to <strong>
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Convert lists
        formatted = formatted.replace(/^- (.+)$/gm, '<li>$1</li>');
        if (formatted.includes('<li>')) {
            formatted = formatted.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
        }
        
        return formatted;
    }
    
    async function resetChat() {
        if (!confirm('Are you sure you want to reset the conversation?')) {
            return;
        }
        
        try {
            await fetch('/api/chat/reset', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            // Clear chat messages except the first welcome message
            const welcomeMessage = chatMessages.firstElementChild;
            chatMessages.innerHTML = '';
            chatMessages.appendChild(welcomeMessage);
            
            // Hide annotations panel
            document.getElementById('chatAnnotations').style.display = 'none';
            
        } catch (error) {
            showError('Failed to reset chat');
            console.error('Error:', error);
        }
    }
});
