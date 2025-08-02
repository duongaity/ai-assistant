"""
Cấu hình Swagger Documentation cho AI Programming Assistant API

File này chứa tất cả các cấu hình cho Swagger UI và API documentation
Giúp tách biệt config khỏi main application code
"""

# Cấu hình Swagger UI và API documentation
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,  # Include tất cả routes
            "model_filter": lambda tag: True,  # Include tất cả models
        }
    ],
    "static_url_path": "/flasgger_static",  # Path cho static files của Swagger
    "swagger_ui": True,                     # Enable Swagger UI
    "specs_route": "/swagger/"              # Route để access Swagger UI
}

# Template chứa metadata của API với đường dẫn endpoints chi tiết
swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "AI Programming Assistant API",
        "description": "AI-powered programming assistance API với chat, language support và health monitoring",
        "version": "3.0.0",
        "contact": {
            "name": "AI Programming Assistant Team",
            "email": "support@aiprogrammingassistant.com"
        }
    },
    "host": "localhost:8888",              # Host và port của API
    "basePath": "/api",                    # Base path cho tất cả endpoints
    "schemes": ["http", "https"],          # Supported protocols
    "tags": [
        {
            "name": "chat", 
            "description": "🤖 AI Chat Operations - Giao tiếp với AI Assistant thông qua /api/chat"
        },
        {
            "name": "language",
            "description": "🌐 Language Support - Quản lý ngôn ngữ lập trình qua /api/languages"
        },
        {
            "name": "health",
            "description": "💚 Health Check Operations - Monitoring trạng thái API qua /api/health"
        }
    ],
    "paths": {
        "/chat": {
            "post": {
                "tags": ["chat"],
                "summary": "Chat with AI Assistant",
                "description": "Endpoint chính để chat với AI Assistant - hỗ trợ cả normal chat và quick actions"
            }
        },
        "/languages": {
            "get": {
                "tags": ["language"],
                "summary": "Get supported languages",
                "description": "Lấy danh sách tất cả ngôn ngữ lập trình được hỗ trợ"
            }
        },
        "/languages/{language_code}": {
            "get": {
                "tags": ["language"],
                "summary": "Get specific language info",
                "description": "Lấy thông tin chi tiết về một ngôn ngữ lập trình cụ thể"
            }
        },
        "/health": {
            "get": {
                "tags": ["health"],
                "summary": "Basic health check",
                "description": "Kiểm tra trạng thái cơ bản của API server"
            }
        }
    }
}
