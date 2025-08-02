"""
Chat API - Xử lý tất cả endpoints liên quan đến chat với AI Assistant

Module này chứa:
- POST /api/chat: Chat với AI Assistant (single request)
- Hỗ trợ both normal chat và quick actions
- Function calling integration
- Context management
"""

from flask import Blueprint, request, jsonify
from flasgger import swag_from
import traceback

# Tạo Blueprint cho chat API
chat_bp = Blueprint('chat', __name__)

def init_chat_api(ai_service):
    """
    Initialize chat API với AI service dependency injection
    
    Args:
        ai_service: Instance của AIService để xử lý AI operations
    """
    global _ai_service
    _ai_service = ai_service

@chat_bp.route('/chat', methods=['POST'])
@swag_from({
    'tags': ['chat'],
    'summary': 'Chat with AI Assistant',
    'description': 'Gửi tin nhắn đến AI Assistant và nhận phản hồi thông minh',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {
                        'type': 'string',
                        'description': 'Tin nhắn gửi đến AI Assistant',
                        'example': 'Xin chào, bạn có thể giúp tôi giải thích đoạn code này không?'
                    },
                    'history': {
                        'type': 'array',
                        'description': 'Lịch sử conversation để maintain context',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'type': {'type': 'string', 'enum': ['user', 'bot']},
                                'content': {'type': 'string'}
                            }
                        }
                    },
                    'is_quick_action': {
                        'type': 'boolean',
                        'description': 'True nếu là quick action (comment, debug, optimize, test)',
                        'example': False
                    }
                },
                'required': ['message']
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'AI response được tạo thành công',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': True},
                    'response': {
                        'type': 'string', 
                        'example': 'Xin chào! Tôi có thể giúp bạn giải thích code. Hãy chia sẻ đoạn code bạn muốn tôi giải thích.'
                    }
                }
            }
        },
        '400': {
            'description': 'Bad request - dữ liệu đầu vào không hợp lệ',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': False},
                    'error': {'type': 'string', 'example': 'Message is required'}
                }
            }
        },
        '500': {
            'description': 'Internal server error',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': False},
                    'error': {'type': 'string', 'example': 'Error processing request'}
                }
            }
        }
    }
})
def chat():
    """
    Chat endpoint - Giao tiếp với AI Assistant thông qua conversation
    
    Hỗ trợ 2 mode:
    1. Quick Actions: Trả về code đã xử lý (comment, debug, optimize, test)
    2. Normal Chat: Trả lời câu hỏi, giải thích code với context đầy đủ
    
    Flow xử lý:
    1. Validate request data
    2. Extract message, history và is_quick_action
    3. Gọi AI service để xử lý
    4. Trả về response hoặc error
    """
    try:
        # Bước 1: Validate request data
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "success": False,
                "error": "Message is required"
            }), 400
        
        # Extract parameters từ request
        message = data['message']
        history = data.get('history', [])                    # Chat history để maintain context
        is_quick_action = data.get('is_quick_action', False) # Flag để phân biệt quick action vs normal chat
        
        if not message.strip():
            return jsonify({
                "success": False,
                "error": "Message cannot be empty"
            }), 400
        
        # Bước 2: Gọi AI service để xử lý
        result = _ai_service.chat_with_ai(
            message=message,
            history=history,
            is_quick_action=is_quick_action
        )
        
        # Bước 3: Trả về response
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
        
    except Exception as e:
        # Xử lý exception và log error để debug
        print(f"Error in chat endpoint: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "error": f"Error processing chat: {str(e)}"
        }), 500


# End of chat.py - Chỉ còn lại single chat endpoint
