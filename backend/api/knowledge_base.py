"""
Knowledge Base API - Xử lý các endpoint liên quan đến quản lý knowledge base

Module này chứa:
- POST /api/knowledge-base/upload: Upload file PDF để xây dựng knowledge base
- GET /api/knowledge-base/files: Lấy danh sách file đã upload
- POST /api/knowledge-base/search: Tìm kiếm trong files cụ thể dựa trên list filename_uuid
- GET /api/knowledge-base/chunks: Lấy tất cả chunks từ ChromaDB
- POST /api/knowledge-base/reset: Reset ChromaDB - xóa tất cả chunks và tạo lại collection
- POST /api/knowledge-base/clear: Xóa tất cả chunks nhưng giữ nguyên collection
"""

from flask import Blueprint, request, jsonify
from flasgger import swag_from
import traceback

# Import service
from services.knowledge_base_service import KnowledgeBaseService

# Tạo Blueprint cho API knowledge base
knowledge_base_bp = Blueprint('knowledge_base', __name__)

# Global service instance
_knowledge_base_service = None

def init_knowledge_base_api():
    """
    Khởi tạo knowledge base API
    """
    global _knowledge_base_service
    _knowledge_base_service = KnowledgeBaseService()

@knowledge_base_bp.route('/knowledge-base/upload', methods=['POST'])
@swag_from({
    'tags': ['knowledge-base'],
    'summary': 'Upload PDF file to knowledge base',
    'description': 'Upload a PDF file to build knowledge base for AI Assistant',
    'consumes': ['multipart/form-data'],
    'parameters': [
        {
            'name': 'file',
            'in': 'formData',
            'type': 'file',
            'required': True,
            'description': 'PDF file to upload (max 10MB)'
        },
        {
            'name': 'title',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': 'Title of the document'
        },
        {
            'name': 'description',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'description': 'Description of the document'
        }
    ],
    'responses': {
        200: {
            'description': 'File uploaded successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'message': {'type': 'string'},
                    'data': {
                        'type': 'object',
                        'properties': {
                            'file_id': {'type': 'string'},
                            'filename': {'type': 'string'},
                            'title': {'type': 'string'},
                            'file_size': {'type': 'integer'},
                            'file_hash': {'type': 'string'},
                            'pages_count': {'type': 'integer'},
                            'text_length': {'type': 'integer'},
                            'upload_time': {'type': 'string'},
                            'description': {'type': 'string'}
                        }
                    }
                }
            }
        },
        400: {
            'description': 'Bad request - Invalid file or missing file',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'error': {'type': 'string'},
                    'message': {'type': 'string'}
                }
            }
        },
        413: {
            'description': 'File too large',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'error': {'type': 'string'},
                    'message': {'type': 'string'}
                }
            }
        },
        500: {
            'description': 'Internal server error',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'error': {'type': 'string'},
                    'message': {'type': 'string'}
                }
            }
        }
    }
})
def upload_file():
    """
    Upload PDF file để xây dựng knowledge base
    """
    try:
        # Kiểm tra có file trong request không
        if 'file' not in request.files:
            return jsonify({
                "success": False,
                "error": "No file provided",
                "message": "Please select a PDF file to upload"
            }), 400
        
        file = request.files['file']
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '')
        
        # Kiểm tra title có được cung cấp không
        if not title:
            return jsonify({
                "success": False,
                "error": "Title is required",
                "message": "Please provide a title for the document"
            }), 400
        
        # Sử dụng service để xử lý file
        success, result_data, error_message, status_code = _knowledge_base_service.process_uploaded_file(
            file, title, description
        )
        
        if success:
            return jsonify({
                "success": True,
                "message": error_message,
                "data": result_data
            }), status_code
        else:
            return jsonify({
                "success": False,
                "error": "Upload failed",
                "message": error_message
            }), status_code
        
    except Exception as e:
        # Log lỗi chi tiết
        error_trace = traceback.format_exc()
        print(f"Error in file upload: {error_trace}")
        
        return jsonify({
            "success": False,
            "error": "Upload failed",
            "message": f"Failed to process file: {str(e)}"
        }), 500

@knowledge_base_bp.route('/knowledge-base/files', methods=['GET'])
@swag_from({
    'tags': ['knowledge-base'],
    'summary': 'List uploaded files',
    'description': 'Get list of all uploaded PDF files in knowledge base',
    'responses': {
        200: {
            'description': 'List of uploaded files',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'message': {'type': 'string'},
                    'data': {
                        'type': 'object',
                        'properties': {
                            'files': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'file_id': {'type': 'string'},
                                        'filename': {'type': 'string'},
                                        'title': {'type': 'string'},
                                        'file_size': {'type': 'integer'},
                                        'pages_count': {'type': 'integer'},
                                        'upload_time': {'type': 'string'},
                                        'description': {'type': 'string'}
                                    }
                                }
                            },
                            'total_files': {'type': 'integer'}
                        }
                    }
                }
            }
        }
    }
})
def list_files():
    """
    Lấy danh sách các file đã upload
    """
    try:
        # Sử dụng service để lấy danh sách file
        success, result_data, error_message = _knowledge_base_service.get_uploaded_files()
        
        if success:
            return jsonify({
                "success": True,
                "message": "Files retrieved successfully",
                "data": result_data
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Failed to list files",
                "message": error_message
            }), 500
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"Error listing files: {error_trace}")
        
        return jsonify({
            "success": False,
            "error": "Failed to list files",
            "message": str(e)
        }), 500

@knowledge_base_bp.route('/knowledge-base/search', methods=['POST'])
@swag_from({
    'tags': ['knowledge-base'],
    'summary': 'Search in specific files',
    'description': 'Search for content in specific files using list of filename_uuid',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'query': {
                        'type': 'string',
                        'description': 'Search query or question',
                        'example': 'What is machine learning?'
                    },
                    'filename_uuids': {
                        'type': 'array',
                        'items': {'type': 'string'},
                        'description': 'List of filename_uuid (file_id) to search in',
                        'example': ['uuid1', 'uuid2', 'uuid3']
                    },
                    'max_results': {
                        'type': 'integer',
                        'description': 'Maximum number of results to return',
                        'default': 5,
                        'example': 5
                    }
                },
                'required': ['query', 'filename_uuids']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Search completed successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'message': {'type': 'string'},
                    'data': {
                        'type': 'object',
                        'properties': {
                            'query': {'type': 'string'},
                            'filename_uuids': {
                                'type': 'array',
                                'items': {'type': 'string'}
                            },
                            'results': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'content': {'type': 'string'},
                                        'similarity_score': {'type': 'number'},
                                        'source': {
                                            'type': 'object',
                                            'properties': {
                                                'file_id': {'type': 'string'},
                                                'filename_uuid': {'type': 'string'},
                                                'title': {'type': 'string'},
                                                'filename': {'type': 'string'},
                                                'chunk_index': {'type': 'integer'},
                                                'chunk_length': {'type': 'integer'}
                                            }
                                        }
                                    }
                                }
                            },
                            'total_results': {'type': 'integer'}
                        }
                    }
                }
            }
        },
        400: {
            'description': 'Bad request - Missing required fields',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'error': {'type': 'string'},
                    'message': {'type': 'string'}
                }
            }
        }
    }
})
def search_in_specific_files():
    """
    Tìm kiếm trong các files cụ thể bằng list filename_uuid
    """
    try:
        # Lấy dữ liệu từ request
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Missing request body",
                "message": "Please provide JSON request body"
            }), 400
        
        query = data.get('query', '').strip()
        filename_uuids = data.get('filename_uuids', [])
        max_results = data.get('max_results', 5)
        
        # Validation
        if not query:
            return jsonify({
                "success": False,
                "error": "Missing query",
                "message": "Please provide a search query"
            }), 400
        
        if not filename_uuids or not isinstance(filename_uuids, list):
            return jsonify({
                "success": False,
                "error": "Missing filename_uuids",
                "message": "Please provide a list of filename_uuid to search in"
            }), 400
        
        if len(filename_uuids) == 0:
            return jsonify({
                "success": False,
                "error": "Empty filename_uuids",
                "message": "filename_uuids list cannot be empty"
            }), 400
        
        # Thực hiện search trong files cụ thể
        success, results, error_message = _knowledge_base_service.search_in_multiple_files(
            query, filename_uuids, max_results
        )
        
        if success:
            return jsonify({
                "success": True,
                "message": "Search in specific files completed successfully",
                "data": {
                    "query": query,
                    "filename_uuids": filename_uuids,
                    "results": results,
                    "total_results": len(results),
                    "max_results": max_results
                }
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Search failed",
                "message": error_message
            }), 500
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"Error in search_in_specific_files: {error_trace}")
        
        return jsonify({
            "success": False,
            "error": "Search failed",
            "message": str(e)
        }), 500

@knowledge_base_bp.route('/knowledge-base/chunks', methods=['GET'])
@swag_from({
    'tags': ['knowledge-base'],
    'summary': 'Get all chunks',
    'description': 'Get all text chunks from ChromaDB',
    'parameters': [
        {
            'name': 'limit',
            'in': 'query',
            'type': 'integer',
            'description': 'Limit number of chunks returned',
            'example': 10
        }
    ],
    'responses': {
        200: {
            'description': 'Chunks retrieved successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'message': {'type': 'string'},
                    'data': {
                        'type': 'object',
                        'properties': {
                            'chunks': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'id': {'type': 'string'},
                                        'content': {'type': 'string'},
                                        'metadata': {'type': 'object'}
                                    }
                                }
                            },
                            'total_chunks': {'type': 'integer'}
                        }
                    }
                }
            }
        }
    }
})
def get_all_chunks():
    """
    Lấy tất cả chunks từ ChromaDB
    """
    try:
        limit = request.args.get('limit', type=int)
        
        success, chunks_data, error_message = _knowledge_base_service.get_all_chunks(limit)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Chunks retrieved successfully",
                "data": {
                    "chunks": chunks_data,
                    "total_chunks": len(chunks_data)
                }
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Failed to get chunks",
                "message": error_message
            }), 500
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"Error getting all chunks: {error_trace}")
        
        return jsonify({
            "success": False,
            "error": "Failed to get chunks",
            "message": str(e)
        }), 500

@knowledge_base_bp.route('/knowledge-base/reset', methods=['POST'])
@swag_from({
    'tags': ['knowledge-base'],
    'summary': 'Reset ChromaDB',
    'description': 'Reset ChromaDB - Delete all chunks and recreate collection',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'confirm_reset': {
                        'type': 'boolean',
                        'description': 'Confirm reset operation (required to prevent accidental deletion)',
                        'example': True
                    }
                },
                'required': ['confirm_reset']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'ChromaDB reset successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'message': {'type': 'string'},
                    'data': {
                        'type': 'object',
                        'properties': {
                            'reset_timestamp': {'type': 'string'},
                            'old_collection_info': {
                                'type': 'object',
                                'properties': {
                                    'total_chunks_deleted': {'type': 'integer'},
                                    'collection_name': {'type': 'string'}
                                }
                            },
                            'new_collection_created': {'type': 'boolean'},
                            'db_path': {'type': 'string'}
                        }
                    }
                }
            }
        },
        400: {
            'description': 'Bad request - Missing confirmation',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'error': {'type': 'string'},
                    'message': {'type': 'string'}
                }
            }
        }
    }
})
def reset_chromadb():
    """
    Reset ChromaDB - Xóa tất cả chunks và tạo lại collection
    """
    try:
        # Lấy dữ liệu từ request
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Missing request body",
                "message": "Please provide JSON request body with confirm_reset field"
            }), 400
        
        confirm_reset = data.get('confirm_reset', False)
        
        if not confirm_reset:
            return jsonify({
                "success": False,
                "error": "Reset not confirmed",
                "message": "Please set confirm_reset=true to confirm reset operation"
            }), 400
        
        # Thực hiện reset
        success, reset_info, error_message = _knowledge_base_service.reset_chromadb(confirm_reset=True)
        
        if success:
            return jsonify({
                "success": True,
                "message": "ChromaDB reset completed successfully",
                "data": reset_info
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Reset failed",
                "message": error_message
            }), 500
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"Error in reset ChromaDB: {error_trace}")
        
        return jsonify({
            "success": False,
            "error": "Reset failed",
            "message": str(e)
        }), 500

@knowledge_base_bp.route('/knowledge-base/clear', methods=['POST'])
@swag_from({
    'tags': ['knowledge-base'],
    'summary': 'Clear all chunks',
    'description': 'Clear all chunks from ChromaDB but keep collection (lighter operation)',
    'responses': {
        200: {
            'description': 'Chunks cleared successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'message': {'type': 'string'},
                    'data': {
                        'type': 'object',
                        'properties': {
                            'chunks_cleared': {'type': 'integer'},
                            'clear_timestamp': {'type': 'string'},
                            'collection_name': {'type': 'string'}
                        }
                    }
                }
            }
        }
    }
})
def clear_all_chunks():
    """
    Xóa tất cả chunks nhưng giữ nguyên collection
    """
    try:
        # Thực hiện clear chunks
        success, clear_info, error_message = _knowledge_base_service.clear_all_chunks()
        
        if success:
            return jsonify({
                "success": True,
                "message": "All chunks cleared successfully",
                "data": clear_info
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Clear failed",
                "message": error_message
            }), 500
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"Error clearing chunks: {error_trace}")
        
        return jsonify({
            "success": False,
            "error": "Clear failed",
            "message": str(e)
        }), 500

@knowledge_base_bp.route('/knowledge-base/chat', methods=['POST'])
@swag_from({
    'tags': ['knowledge-base'],
    'summary': 'Chat with AI using knowledge base',
    'description': 'Chat with AI Assistant using vector database as knowledge source. The AI will search relevant documents and provide answers based on the knowledge base.',
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
                        'description': 'User question or message',
                        'example': 'Explain the coding standards in Java'
                    },
                    'max_results': {
                        'type': 'integer',
                        'description': 'Maximum number of relevant documents to retrieve',
                        'default': 3,
                        'example': 3
                    },
                    'file_ids': {
                        'type': 'array',
                        'items': {'type': 'string'},
                        'description': 'Optional: Search only in specific files (file UUIDs)',
                        'example': ['uuid1', 'uuid2']
                    }
                },
                'required': ['message']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'AI response generated successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': True},
                    'response': {
                        'type': 'string',
                        'description': 'AI generated response based on knowledge base'
                    },
                    'sources': {
                        'type': 'array',
                        'description': 'Relevant documents used to generate the response',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'content': {'type': 'string'},
                                'similarity_score': {'type': 'number'},
                                'source': {
                                    'type': 'object',
                                    'properties': {
                                        'file_id': {'type': 'string'},
                                        'title': {'type': 'string'},
                                        'filename': {'type': 'string'},
                                        'chunk_index': {'type': 'integer'}
                                    }
                                }
                            }
                        }
                    },
                    'search_info': {
                        'type': 'object',
                        'properties': {
                            'query': {'type': 'string'},
                            'results_found': {'type': 'integer'},
                            'search_time': {'type': 'string'}
                        }
                    }
                }
            }
        },
        400: {
            'description': 'Bad request - invalid input',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': False},
                    'error': {'type': 'string'}
                }
            }
        },
        500: {
            'description': 'Internal server error',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': False},
                    'error': {'type': 'string'}
                }
            }
        }
    }
})
def chat_with_knowledge_base():
    """
    Chat với AI Assistant sử dụng knowledge base làm nguồn kiến thức
    """
    try:
        # Bước 1: Xác thực dữ liệu đầu vào
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "success": False,
                "error": "Message is required"
            }), 400
        
        message = data['message'].strip()
        if not message:
            return jsonify({
                "success": False,
                "error": "Message cannot be empty"
            }), 400
        
        max_results = data.get('max_results', 3)
        file_ids = data.get('file_ids', None)
        
        # Bước 2: Tìm kiếm trong knowledge base
        import time
        search_start = time.time()
        
        if file_ids:
            # Tìm kiếm trong các file cụ thể
            search_success, search_results, search_error = _knowledge_base_service.search_in_multiple_files(
                query=message,
                filename_uuids=file_ids,
                max_results=max_results
            )
        else:
            # Tìm kiếm trong toàn bộ knowledge base
            search_success, search_results, search_error = _knowledge_base_service.search_knowledge_base(
                query=message,
                max_results=max_results
            )
        
        search_time = round(time.time() - search_start, 3)
        
        if not search_success:
            return jsonify({
                "success": False,
                "error": f"Search failed: {search_error}"
            }), 500
        
        # Bước 3: Tạo context từ các tài liệu tìm được
        if not search_results:
            # Không tìm thấy tài liệu liên quan
            ai_response = f"""Xin lỗi, tôi không tìm thấy thông tin liên quan đến câu hỏi "{message}" trong knowledge base hiện tại.
            
Có thể bạn muốn:
- Kiểm tra lại từ khóa tìm kiếm
- Upload thêm tài liệu liên quan
- Đặt câu hỏi cụ thể hơn

Bạn có thể upload file PDF chứa thông tin bạn cần thông qua trang Knowledge Base."""

            return jsonify({
                "success": True,
                "response": ai_response,
                "sources": [],
                "search_info": {
                    "query": message,
                    "results_found": 0,
                    "search_time": f"{search_time}s"
                }
            }), 200
        
        # Bước 4: Tạo context cho AI từ các tài liệu tìm được
        context_parts = []
        for i, result in enumerate(search_results[:max_results], 1):
            source_info = f"[Nguồn {i}: {result['source']['title']}]"
            content = result['content']
            context_parts.append(f"{source_info}\n{content}")
        
        context = "\n\n".join(context_parts)
        
        # Bước 5: Tạo prompt cho AI
        ai_prompt = f"""Bạn là một AI Assistant thông minh và thân thiện. Hãy trả lời câu hỏi của người dùng CHÍNH XÁC dựa trên thông tin từ các tài liệu được cung cấp.

Câu hỏi: {message}

Thông tin từ tài liệu:
{context}

**QUAN TRỌNG - QUY TẮC TRẢ LỜI:**
- CHỈ trả lời dựa trên thông tin có trong các tài liệu được cung cấp ở trên
- KHÔNG bịa đặt, suy đoán hoặc thêm thông tin không có trong tài liệu
- Nếu thông tin không đủ hoặc không có trong tài liệu, hãy nói rõ "Thông tin này không có trong tài liệu được cung cấp"
- Khi trích dẫn thông tin, hãy đề cập nguồn cụ thể (ví dụ: "Theo tài liệu X...")

Hãy trả lời một cách tự nhiên, thân thiện và dễ hiểu. Sử dụng format markdown để trình bày đẹp mắt:
- Sử dụng **in đậm** cho từ khóa quan trọng
- Dùng `code` cho các thuật ngữ kỹ thuật
- Chia thành các đoạn ngắn, dễ đọc
- Sử dụng bullet points (•) hoặc số thứ tự khi liệt kê
- Thêm emoji phù hợp để làm sinh động (📝, 💡, ⚠️, ✅, etc.)

Sử dụng tiếng Việt.

Câu trả lời:"""

        # Bước 6: Sử dụng AI service để tạo câu trả lời
        from services.ai_service import AIService
        ai_service = AIService()
        
        ai_result = ai_service.chat_with_ai(
            message=ai_prompt,
            history=[],
            is_quick_action=False
        )
        
        if not ai_result["success"]:
            return jsonify({
                "success": False,
                "error": f"AI processing failed: {ai_result.get('error', 'Unknown error')}"
            }), 500
        
        # Bước 7: Trả về kết quả
        return jsonify({
            "success": True,
            "response": ai_result["response"],
            "sources": search_results,
            "search_info": {
                "query": message,
                "results_found": len(search_results),
                "search_time": f"{search_time}s"
            }
        }), 200
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"Error in knowledge base chat: {error_trace}")
        
        return jsonify({
            "success": False,
            "error": f"Chat processing failed: {str(e)}"
        }), 500
