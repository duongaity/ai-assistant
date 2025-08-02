"""
Health API - Xử lý endpoints liên quan đến health check và monitoring

Module này chứa:
- GET /api/health: Basic health check
"""

from flask import Blueprint, jsonify
from flasgger import swag_from
from datetime import datetime

# Tạo Blueprint cho health API
health_bp = Blueprint('health', __name__)

def init_health_api(ai_service):
    """
    Initialize health API với AI service dependency injection
    
    Args:
        ai_service: Instance của AIService để check AI service health
    """
    global _ai_service
    _ai_service = ai_service

@health_bp.route('/health', methods=['GET'])
@swag_from({
    'tags': ['health'],
    'summary': 'Basic Health Check',
    'description': 'Kiểm tra trạng thái cơ bản của API server',
    'responses': {
        200: {
            'description': 'API đang hoạt động bình thường',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {
                        'type': 'string', 
                        'example': 'healthy',
                        'description': 'Trạng thái tổng quát của API'
                    },
                    'message': {
                        'type': 'string', 
                        'example': 'AI Programming Assistant API is running',
                        'description': 'Thông báo trạng thái'
                    },
                    'timestamp': {
                        'type': 'string', 
                        'example': '2025-08-02T10:30:00Z',
                        'description': 'Thời gian check health'
                    },
                    'version': {
                        'type': 'string', 
                        'example': '3.0.0',
                        'description': 'Version hiện tại của API'
                    }
                }
            }
        }
    }
})
def health_check():
    """
    Basic health check endpoint - Kiểm tra API server có đang chạy không
    
    Endpoint này luôn trả về 200 nếu server đang chạy.
    Được sử dụng bởi load balancer và monitoring tools.
    
    Returns:
        JSON response với basic health information
    """
    return jsonify({
        "status": "healthy",
        "message": "AI Programming Assistant API is running",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "3.0.0"
    })
