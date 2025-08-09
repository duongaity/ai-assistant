# AI Programming Assistant

Ứng dụng web AI hỗ trợ lập trình với khả năng chat, giải thích code và các thao tác nhanh.

## 📋 Overview

AI Programming Assistant là một ứng dụng full-stack giúp lập trình viên:
- **Chat với AI**: Hỏi đáp và tư vấn lập trình
- **Giải thích code**: Phân tích và giải thích đoạn code
- **Quick Actions**: Comment, debug, optimize, test code
- **Multi-language**: Hỗ trợ 9+ ngôn ngữ lập trình
- **API Documentation**: Swagger UI tích hợp

## ⚡ Chức năng ứng dụng

### 🤖 AI Chat Assistant
- **Tư vấn lập trình**: Hỏi đáp về algorithms, data structures, best practices
- **Giải quyết vấn đề**: Debug code, tìm lỗi và đưa ra giải pháp
- **Code review**: Đánh giá và đề xuất cải thiện code
- **Học tập**: Giải thích concepts, patterns và frameworks

### 🔍 Code Analysis
- **Giải thích code**: Phân tích logic và flow của đoạn code
- **Code documentation**: Tự động tạo comments và documentation
- **Security scan**: Phát hiện potential security issues
- **Performance analysis**: Đánh giá hiệu suất và đề xuất optimization

### Quick Actions
- **Add Comments**: Tự động thêm comments cho code
- **Debug Code**: Phát hiện và sửa lỗi trong code
- **Optimize Code**: Cải thiện performance và clean code
- **Generate Tests**: Tạo unit tests cho functions/methods
- **Refactor Code**: Restructure code để dễ đọc và maintain
- **Format Code**: Tự động format theo coding standards

### Real-time Chat
- **Hỏi đáp về code**: Giải thích syntax, functions, và logic của đoạn code
- **Tư vấn architecture**: Thiết kế hệ thống, design patterns, và best practices
- **Debugging support**: Hỗ trợ tìm và sửa lỗi trong code
- **Code review**: Đánh giá chất lượng code và đề xuất cải thiện
- **Learning guidance**: Hướng dẫn học các ngôn ngữ và framework mới
- **Technical discussions**: Thảo luận về algorithms, data structures, performance
- **Project consultation**: Tư vấn về công nghệ, tools, và workflow phù hợp

### 🔊 Text-to-Speech (TTS)
- **Voice synthesis**: Chuyển đổi text thành giọng nói
- **Multiple language support**: Hỗ trợ đọc text bằng nhiều ngôn ngữ
- **Audio streaming**: Trả về audio dưới dạng base64 encoding
- **Real-time processing**: Xử lý TTS nhanh chóng và hiệu quả

### 📚 Knowledge Base
- **Document upload**: Upload và xử lý file PDF
- **Smart search**: Tìm kiếm thông tin trong knowledge base
- **Content extraction**: Trích xuất và lưu trữ nội dung từ documents
- **Vector database**: Sử dụng ChromaDB để tìm kiếm semantic

## 🏗️ Structure

```
ai-assistant/
├── backend/                 # Python Flask API
│   ├── app.py               # Main application
│   ├── requirements.txt     # Dependencies
│   ├── api/                 # API endpoints
│   │   ├── chat.py          # Chat với AI
│   │   ├── health.py        # Health check
│   │   └── language.py      # Language support
│   └── services/
│       └── ai_service.py    # AI service logic
├── frontend/                # React Frontend
│   ├── src/
│   │   ├── App.jsx          # Main component
│   │   ├── components/      # UI components
│   │   └── utils/           # Utilities
│   ├── package.json         # Dependencies
│   └── vite.config.js       # Build config
├── nginx/                   # Load balancer
├── docker-compose.yml       # Container setup
└── README.md
```

## Run Code

### Quick Start với Docker
```bash
# 1. Clone repository
git clone <repository-url>
cd ai-assistant

# 2. Setup environment
# Tạo file backend/.env với Azure OpenAI credentials
echo "AZURE_OPENAI_ENDPOINT=your-endpoint" > backend/.env
echo "AZURE_OPENAI_API_KEY=your-key" >> backend/.env
echo "AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-mini" >> backend/.env

# 3. Start all services
docker-compose up --build

# 4. Access application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8888
# Swagger Docs: http://localhost:8888/swagger/
```

### Development Mode
```bash
# Backend only
cd backend
pip install -r requirements.txt
python app.py

# Frontend only
cd frontend
npm install
npm run dev
```

## Backend

**Tech Stack:**
- **Flask**: Web framework
- **Azure OpenAI**: AI integration
- **pyttsx3**: Text-to-Speech engine
- **ChromaDB**: Vector database
- **PyPDF2**: PDF processing
- **Sentence Transformers**: Text embeddings
- **Flasgger**: Swagger documentation
- **Flask-CORS**: Cross-origin support

**Main Endpoints:**
- `POST /api/chat` - Chat với AI Assistant
- `GET /api/languages` - Danh sách ngôn ngữ hỗ trợ
- `GET /api/health` - Health check
- `POST /api/tts` - Text-to-Speech conversion
- `POST /api/knowledge-base/upload` - Upload PDF documents
- `POST /api/knowledge-base/search` - Search knowledge base

**Key Features:**
- AI chat với context management
- Quick actions (comment, debug, optimize)
- Multi-language programming support
- Text-to-Speech functionality
- Knowledge base with PDF upload
- Vector search với ChromaDB
- Swagger API documentation
- Error handling và logging

## Frontend

**Tech Stack:**
- **React 18**: UI framework
- **Vite**: Build tool
- **CSS Modules**: Styling
- **Axios**: HTTP client

## 🔧 Troubleshooting

### TTS (Text-to-Speech) Issues
If you encounter errors like "Error opening input file temp.wav" or "Invalid data found when processing input":

**macOS:**
```bash
# Install espeak (required for pyttsx3)
brew install espeak

# Or install festival
brew install festival

# Check if TTS engine is working
python3 -c "import pyttsx3; engine = pyttsx3.init(); engine.say('test'); engine.runAndWait()"
```

**Ubuntu/Debian:**
```bash
# Install espeak
sudo apt-get install espeak espeak-data

# Install festival (alternative)
sudo apt-get install festival festvox-kallpc16k
```

**Windows:**
```bash
# Windows có SAPI built-in, nên thường không cần cài thêm
# Nếu vẫn lỗi, thử install Microsoft Speech Platform
```

### Knowledge Base Issues
```bash
# If ChromaDB issues occur, reset the database
rm -rf backend/chroma_db/*

# Restart the application to recreate the database
```

### Environment Setup Issues
```bash
# Make sure all environment variables are set
cp backend/.env.example backend/.env
# Edit .env file with your Azure OpenAI credentials

# Check Python version (requires Python 3.8+)
python3 --version

# Install dependencies
cd backend
pip install -r requirements.txt
```

---

**Happy Coding! 🚀**

