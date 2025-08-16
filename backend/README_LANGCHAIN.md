# AI Assistant Backend - Langchain Integration

## 🔄 Cập nhật mới: Tích hợp Langchain Framework

Backend này đã được cập nhật để sử dụng **Langchain framework** cho các tác vụ AI nâng cao:

### 🆕 Các thay đổi chính:

#### 1. **LangchainService** - Service mới
- Quản lý **RAG (Retrieval Augmented Generation)** với knowledge base
- **Conversational chains** với memory
- **Agent-based workflows** với tools
- **Vector store operations** với ChromaDB

#### 2. **KnowledgeBaseService** - Cập nhật Langchain
- Sử dụng **Langchain ChromaDB integration**
- **Langchain Document format** cho metadata
- **RecursiveCharacterTextSplitter** cho text chunking
- **SentenceTransformerEmbeddings** cho vector embeddings

#### 3. **AIService** - Hybrid approach
- **Ưu tiên sử dụng Langchain** cho các tác vụ phức tạp
- **Fallback to legacy Azure OpenAI** khi cần thiết
- Tích hợp với **LangchainService** cho RAG capabilities

### 📦 Dependencies mới

```txt
langchain>=0.1.0
langchain-openai>=0.1.0
langchain-chroma>=0.1.0
langchain-community>=0.0.20
```

### 🚀 Cài đặt và chạy

```bash
# 1. Cài đặt dependencies
pip install -r requirements.txt

# 2. Test Langchain integration
python test_langchain_integration.py

# 3. Chạy server
python app.py
```

### 🧪 Test Langchain Integration

Chạy script test để kiểm tra tất cả components:

```bash
python test_langchain_integration.py
```

Script này sẽ test:
- ✅ LangchainService initialization
- ✅ Vector store operations
- ✅ RAG capabilities
- ✅ Tools và agents
- ✅ Integration với AIService

### 🔧 Cấu trúc Service mới

```
services/
├── langchain_service.py      # 🆕 Langchain workflows
├── ai_service.py            # 🔄 Hybrid với Langchain
├── knowledge_base_service.py # 🔄 Langchain vector store
└── ...
```

### 📊 Workflow mới

#### Normal Chat với RAG:
```
User Message → AIService → LangchainService → RAG Chain → Vector Store → Response
```

#### Quick Actions:
```
User Message → AIService → LangchainService → Code Chain → Langchain Tools → Response
```

#### Knowledge Base Search:
```
Query → KnowledgeBaseService → Langchain ChromaDB → Similarity Search → Results
```

### 🎯 Benefits của Langchain Integration

1. **Modular Architecture**: Dễ dàng thêm/sửa chains và tools
2. **Advanced RAG**: Tự động retrieve relevant context từ knowledge base
3. **Memory Management**: Conversation history được quản lý tự động
4. **Tool Integration**: Langchain tools thay vì custom function calling
5. **Scalability**: Dễ dàng mở rộng với nhiều LLM providers

### 🔍 API Endpoints (không đổi)

Tất cả API endpoints giữ nguyên backward compatibility:

- `POST /api/chat` - Chat với AI (giờ sử dụng Langchain RAG)
- `POST /api/knowledge-base/upload` - Upload PDF (Langchain processing)
- `POST /api/knowledge-base/search` - Search (Langchain vector store)
- `GET /api/health` - Health check

### ⚙️ Environment Variables

```env
# Azure OpenAI (vẫn cần cho fallback)
AZURE_OPENAI_ENDPOINT=your-endpoint
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment

# ChromaDB path (không đổi)
CHROMA_DB_PATH=./chroma_db
```

### 🐛 Troubleshooting

#### Nếu gặp lỗi import Langchain:
```bash
pip install --upgrade langchain langchain-openai langchain-chroma langchain-community
```

#### Nếu vector store không hoạt động:
```bash
# Xóa và tạo lại ChromaDB
rm -rf ./chroma_db
python test_langchain_integration.py
```

#### Nếu RAG không trả về kết quả:
1. Check knowledge base có documents không: `GET /api/knowledge-base/files`
2. Upload PDF mới: `POST /api/knowledge-base/upload`
3. Test search: `POST /api/knowledge-base/search`

### 📈 Performance

- **Langchain chains** được cache để tăng tốc
- **Vector similarity search** sử dụng efficient embeddings
- **Conversation memory** được giới hạn để tránh token overflow
- **Fallback mechanisms** đảm bảo service luôn available

### 🔮 Tương lai

Với Langchain integration, backend có thể dễ dàng mở rộng:
- Thêm nhiều LLM providers (Google, Anthropic, etc.)
- Advanced RAG techniques (HyDE, Multi-query, etc.) 
- Custom tools cho specific domains
- Agent workflows phức tạp
- Multi-modal capabilities (text, image, code)

---

**Lưu ý**: Tất cả legacy code được giữ lại để đảm bảo backward compatibility. Langchain được sử dụng như primary choice với fallback mechanisms.
