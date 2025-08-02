# Swagger API Documentation

## 📖 Interactive API Documentation

Ứng dụng **Code Commenter** đã tích hợp **Swagger/OpenAPI** để cung cấp documentation tương tác cho API.

## 🔗 Truy cập Swagger UI

### Development Mode:
- **URL**: http://localhost:5000/swagger/
- **JSON Spec**: http://localhost:5000/apispec_1.json

### Docker Mode:
- **URL**: http://localhost:5000/swagger/
- **Load Balancer**: http://localhost:80/swagger/

## 🎯 Tính năng Swagger

### ✅ Interactive Testing
- 🧪 **Try it out**: Test API endpoints trực tiếp từ browser
- 📝 **Request Builder**: Tự động tạo request payload
- 📊 **Response Viewer**: Xem kết quả real-time với syntax highlighting
- 🔄 **Auto-completion**: Schema validation và suggestions

### ✅ Comprehensive Documentation
- 📋 **All Endpoints**: Danh sách đầy đủ các API endpoints
- 📖 **Request/Response Schemas**: Chi tiết data structures
- 🏷️ **Tags & Categories**: Phân loại endpoints theo chức năng
- 📝 **Parameter Descriptions**: Giải thích chi tiết từng parameter

### ✅ Code Generation
- 🐍 **Python**: `requests` code snippets
- 🌐 **JavaScript**: `fetch()` và `axios` examples  
- 💻 **cURL**: Command-line examples
- 📱 **Multiple Languages**: Java, C#, Go, etc.

## 📚 API Endpoints trong Swagger

### 🏥 Health Check
- **GET** `/api/health`
- **Tag**: `health`
- **Description**: Kiểm tra trạng thái API server
- **Response**: Status, timestamp, version info

### 💬 Code Commenting
- **POST** `/api/comment-code`
- **Tag**: `comment`
- **Description**: Tạo AI-powered comments cho source code
- **Parameters**: 
  - `code` (required): Source code content
  - `language` (optional): Programming language
- **Response**: Commented code với token usage info

### 🌐 Supported Languages
- **GET** `/api/supported-languages`
- **Tag**: `comment`
- **Description**: Lấy danh sách ngôn ngữ lập trình được hỗ trợ
- **Response**: Array của language objects

## 🛠️ Sử dụng Swagger để Test API

### Step 1: Truy cập Swagger UI
```bash
# Mở browser và vào:
http://localhost:5000/swagger/
```

### Step 2: Test Health Check
```bash
1. Expand "health" tag
2. Click GET /api/health
3. Click "Try it out"
4. Click "Execute"
5. Xem response với status 200 và thông tin server
```

### Step 3: Test Code Commenting
```bash
1. Expand "comment" tag  
2. Click POST /api/comment-code
3. Click "Try it out"
4. Input sample request:
   {
     "code": "public class HelloWorld {\n    public static void main(String[] args) {\n        System.out.println(\"Hello World\");\n    }\n}",
     "language": "java"
   }
5. Click "Execute"
6. Xem response với commented code và token info
```

### Step 4: Copy Generated Code
```bash
1. Sau khi execute thành công
2. Scroll xuống "Code samples" section
3. Chọn language (Python, JavaScript, cURL, etc.)
4. Copy code snippet để dùng trong application
```

## 📋 Schema Definitions

### CodeCommentRequest
```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string",
      "description": "Source code to be commented"
    },
    "language": {
      "type": "string", 
      "enum": ["java", "python", "javascript", "typescript", "cpp", "c", "csharp", "go", "rust"],
      "default": "java"
    }
  },
  "required": ["code"]
}
```

### CodeCommentResponse
```json
{
  "type": "object",
  "properties": {
    "success": {"type": "boolean"},
    "commented_code": {"type": "string"},
    "original_length": {"type": "integer"},
    "commented_length": {"type": "integer"},
    "tokens_info": {
      "type": "object",
      "properties": {
        "estimated_input_tokens": {"type": "integer"},
        "max_tokens_used": {"type": "integer"},
        "estimated_output_tokens": {"type": "integer"}
      }
    }
  }
}
```

## 🔧 Configuration

### Swagger Template
```python
swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Code Commenter API",
        "description": "AI-powered code documentation API using Azure OpenAI",
        "version": "1.0.0",
        "contact": {
            "name": "Code Commenter Team",
            "email": "support@codecommenter.com"
        }
    },
    "host": "localhost:5000",
    "basePath": "/api",
    "schemes": ["http", "https"]
}
```

### Tags Organization
- **🏥 health**: Health check operations
- **💬 comment**: Code commenting operations  

## 🚀 Production Swagger

### Security Considerations
```python
# In production, có thể disable Swagger UI:
if os.getenv('FLASK_ENV') == 'production':
    swagger_config['swagger_ui'] = False
```

### Custom Host Configuration
```python
# Update host for production domain
swagger_template['host'] = 'your-domain.com'
swagger_template['schemes'] = ['https']
```

## 🎨 Swagger UI Customization

### Custom CSS (Future Enhancement)
```css
/* Custom Swagger UI styling */
.swagger-ui .topbar { 
    background-color: #1a1a1a; 
}
.swagger-ui .scheme-container {
    background: #f8f9fa;
}
```

## 📊 Benefits của Swagger Integration

### 🏢 For Developers
- ✅ **Self-documenting API**: Code và docs luôn sync
- ✅ **Interactive Testing**: Không cần Postman hay curl
- ✅ **Code Generation**: Auto-generate client code
- ✅ **Schema Validation**: Đảm bảo request/response đúng format

### 👥 For Teams
- ✅ **Collaboration**: Dễ share API specs với team
- ✅ **Onboarding**: New developers hiểu API nhanh hơn
- ✅ **Testing**: QA có thể test API độc lập
- ✅ **Documentation**: Always up-to-date docs

### 🚀 For Production
- ✅ **API Monitoring**: Track usage patterns
- ✅ **Version Control**: API versioning support
- ✅ **Client SDK**: Generate client libraries
- ✅ **Integration**: Easy integration với other tools

---

**🎯 Happy API Testing với Swagger! 🚀**
