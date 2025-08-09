from flasgger import swag_from
from flask import Blueprint, request, jsonify
import pyttsx3
import base64
import os
import tempfile

tts_bp = Blueprint('tts', __name__)

def text_to_speech(text: str) -> str:
    try:
        engine = pyttsx3.init()
        
        # Configure TTS engine for better compatibility
        # Cấu hình TTS engine để tương thích tốt hơn
        voices = engine.getProperty('voices')
        if voices:
            # Use first available voice
            engine.setProperty('voice', voices[0].id)
        
        # Set speech rate and volume
        engine.setProperty('rate', 150)  # Slower speech rate
        engine.setProperty('volume', 0.9)  # High volume
        
        # Tạo file tạm để lưu audio wav
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tf:
            temp_filename = tf.name
        
        engine.save_to_file(text, temp_filename)
        engine.runAndWait()
        
        # Verify file exists and has content
        if not os.path.exists(temp_filename):
            raise Exception("Audio file was not created")
            
        file_size = os.path.getsize(temp_filename)
        if file_size == 0:
            raise Exception("Audio file is empty")
        
        with open(temp_filename, 'rb') as f:
            audio_bytes = f.read()
        os.remove(temp_filename)  # Xóa file tạm
        
        print(f"Generated audio file size: {len(audio_bytes)} bytes")
        
        audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
        return audio_b64
        
    except Exception as e:
        print(f"Error in text_to_speech function: {str(e)}")
        raise e

@tts_bp.route('/tts', methods=['POST'])
@swag_from({
    'tags': ['tts'],
    'summary': 'Convert text to speech',
    'description': 'Receive text and return audio in base64 encoding',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'text': {
                        'type': 'string',
                        'description': 'Text content to convert to speech',
                        'example': 'Hello, this is a test for TTS API.'
                    }
                },
                'required': ['text']
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'TTS audio generated successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': True},
                    'audio_base64': {
                        'type': 'string',
                        'description': 'Base64 encoded audio data',
                        'example': 'UklGRuYAAABXQVZFZm10IBAAAAABAAEAESsAACJWAAACABAAZGF0YQAAAAA='
                    }
                }
            }
        },
        '400': {
            'description': 'Bad request - missing or invalid text',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': False},
                    'error': {'type': 'string', 'example': 'Text is required'}
                }
            }
        },
        '500': {
            'description': 'Internal server error',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': False},
                    'error': {'type': 'string', 'example': 'Failed to generate audio'}
                }
            }
        }
    }
})
def tts():
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        if not text:
            return jsonify({"success": False, "error": "Text is required"}), 400
        
        audio_b64 = text_to_speech(text)
        
        return jsonify({
            "success": True,
            "audio_base64": audio_b64,
            "format": "wav",
            "mimeType": "audio/wav"
        }), 200
    
    except Exception as e:
        print(f"Error in TTS endpoint: {str(e)}")
        return jsonify({"success": False, "error": "Failed to generate audio"}), 500
 