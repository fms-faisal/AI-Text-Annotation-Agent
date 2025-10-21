from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from agent import GeminiAnnotator, BatchAnnotator, ConversationalAgent
import os
import secrets

# Initialize Flask app
app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')

# Secret key for sessions
app.secret_key = secrets.token_hex(16)

# Enable CORS for API requests
CORS(app)

# Initialize annotators
annotator = GeminiAnnotator()
batch_annotator = BatchAnnotator()

# Store conversational agents per session
agents = {}

@app.route('/')
def index():
    """Render the main web interface."""
    return render_template('index.html')


@app.route('/api/annotate', methods=['POST'])
def annotate():
    """
    API endpoint for single text annotation.
    
    Request JSON:
        {
            "text": "Text to annotate"
        }
    
    Response JSON:
        {
            "status": "success|error",
            "original_text": "...",
            "annotations": {...},
            "model": "gemini-1.5-flash"
        }
    """
    try:
        # Get request data
        data = request.get_json()
        
        # Validate input
        if not data:
            return jsonify({
                'status': 'error',
                'error': 'No JSON data provided'
            }), 400
        
        if 'text' not in data:
            return jsonify({
                'status': 'error',
                'error': 'Missing "text" field in request'
            }), 400
        
        text = data['text']
        
        # Check if text is empty
        if not text or len(text.strip()) == 0:
            return jsonify({
                'status': 'error',
                'error': 'Empty text provided'
            }), 400
        
        # Check text length (Gemini has limits)
        if len(text) > 10000:
            return jsonify({
                'status': 'error',
                'error': 'Text too long. Maximum 10,000 characters.'
            }), 400
        
        # Perform annotation
        result = annotator.annotate(text)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': f'Server error: {str(e)}'
        }), 500


@app.route('/api/batch-annotate', methods=['POST'])
def batch_annotate():
    """
    API endpoint for batch text annotation.
    
    Request JSON:
        {
            "texts": ["text1", "text2", ...]
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'texts' not in data:
            return jsonify({
                'status': 'error',
                'error': 'Missing "texts" field in request'
            }), 400
        
        texts = data['texts']
        
        if not isinstance(texts, list):
            return jsonify({
                'status': 'error',
                'error': '"texts" must be a list'
            }), 400
        
        if len(texts) == 0:
            return jsonify({
                'status': 'error',
                'error': 'Empty texts list'
            }), 400
        
        # Limit batch size
        if len(texts) > 10:
            return jsonify({
                'status': 'error',
                'error': 'Maximum 10 texts per batch'
            }), 400
        
        # Process batch
        results = batch_annotator.annotate_batch(texts)
        
        return jsonify({
            'status': 'success',
            'count': len(results),
            'results': results
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': f'Server error: {str(e)}'
        }), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'AI Text Annotation Agent',
        'model': 'Google Gemini 2.5 Flash',
        'version': '1.0.0'
    })


@app.route('/api/stats', methods=['GET'])
def stats():
    """Get API statistics."""
    return jsonify({
        'model': 'gemini-2.5-flash',
        'capabilities': [
            'Named Entity Recognition',
            'Sentiment Analysis',
            'Keyword Extraction',
            'Relationship Extraction'
        ],
        'entity_types': [
            'PERSON', 'ORGANIZATION', 'LOCATION', 'DATE',
            'TIME', 'MONEY', 'PRODUCT', 'EVENT'
        ]
    })


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Conversational AI endpoint for interactive annotation refinement.
    
    Request JSON:
        {
            "message": "User's message",
            "text": "Optional text to annotate"
        }
    """
    try:
        # Get or create session ID
        if 'session_id' not in session:
            session['session_id'] = secrets.token_hex(8)
        
        session_id = session['session_id']
        
        # Get or create agent for this session
        if session_id not in agents:
            agents[session_id] = ConversationalAgent()
        
        agent = agents[session_id]
        
        # Get request data
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'status': 'error',
                'error': 'Missing "message" field in request'
            }), 400
        
        message = data['message']
        text = data.get('text', None)
        
        # Process chat
        result = agent.chat(message, text)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': f'Chat error: {str(e)}'
        }), 500


@app.route('/api/chat/reset', methods=['POST'])
def reset_chat():
    """Reset the conversation for the current session."""
    try:
        if 'session_id' in session:
            session_id = session['session_id']
            if session_id in agents:
                agents[session_id].reset()
        
        return jsonify({
            'status': 'success',
            'message': 'Chat reset successfully'
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': f'Reset error: {str(e)}'
        }), 500


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'status': 'error', 'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'status': 'error', 'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("=" * 50)
    print("AI Text Annotation Agent Starting...")
    print("=" * 50)
    print("Server: http://localhost:5000")
    print("Model: Google Gemini 2.5 Flash")
    print("Ready to annotate text!")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
