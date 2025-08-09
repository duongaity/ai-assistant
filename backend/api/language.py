"""
Language API - Các endpoint liên quan đến ngôn ngữ lập trình

Chứa:
- GET /api/languages: Lấy danh sách ngôn ngữ lập trình được hỗ trợ
"""

from flask import Blueprint, jsonify
from flasgger import swag_from

# Tạo Blueprint cho API ngôn ngữ
language_bp = Blueprint('language', __name__)

@language_bp.route('/languages', methods=['GET'])
@swag_from({
    'tags': ['language'],
    'summary': 'Get supported programming languages',
    'description': 'Get list of programming languages supported by AI Assistant',
    'responses': {
        200: {
            'description': 'List of languages returned successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': True},
                    'languages': {
                        'type': 'array',
                        'description': 'List of languages with value and label',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'value': {
                                    'type': 'string', 
                                    'description': 'Language code value',
                                    'example': 'java'
                                },
                                'label': {
                                    'type': 'string',
                                    'description': 'Language display name', 
                                    'example': 'Java'
                                },
                                'description': {
                                    'type': 'string',
                                    'description': 'Brief language description',
                                    'example': 'Object-oriented programming language'
                                }
                            }
                        }
                    },
                    'total': {
                        'type': 'integer',
                        'description': 'Total number of supported languages',
                        'example': 9
                    }
                }
            }
        }
    }
})
def get_supported_languages():
    """
    Lấy danh sách các ngôn ngữ lập trình được hỗ trợ bởi AI Assistant
    
    Returns:
        JSON response chứa danh sách ngôn ngữ, mỗi ngôn ngữ bao gồm:
        - value: Mã code để gọi API
        - label: Tên hiển thị cho giao diện
        - description: Mô tả ngắn gọn về ngôn ngữ
    """
    # Danh sách ngôn ngữ được hỗ trợ với metadata đầy đủ
    languages = [
        {
            "value": "java", 
            "label": "Java",
            "description": "Object-oriented programming language"
        },
        {
            "value": "python", 
            "label": "Python",
            "description": "High-level programming language"
        },
        {
            "value": "javascript", 
            "label": "JavaScript",
            "description": "Dynamic programming language"
        },
        {
            "value": "typescript", 
            "label": "TypeScript",
            "description": "JavaScript with static typing"
        },
        {
            "value": "c", 
            "label": "C",
            "description": "Low-level programming language"
        },
        {
            "value": "csharp", 
            "label": "C#",
            "description": "Microsoft programming language"
        },
        {
            "value": "go", 
            "label": "Go",
            "description": "Google programming language"
        }
    ]
    
    return jsonify({
        "success": True,
        "languages": languages,
        "total": len(languages)
    })
