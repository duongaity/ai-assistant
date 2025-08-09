"""
Knowledge Base Service - Xử lý logic nghiệp vụ cho knowledge base

Service này chứa:
- Xử lý upload file PDF
- Trích xuất text từ PDF
- Quản lý metadata
- Validation file
"""

import os
import hashlib
import json
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
import PyPDF2
import chromadb
from chromadb.config import Settings
import re

class KnowledgeBaseService:
    """
    Service xử lý các thao tác liên quan đến knowledge base
    """
    
    def __init__(self, upload_folder='uploads', chroma_db_path='./chroma_db'):
        """
        Khởi tạo service
        
        Args:
            upload_folder: Thư mục lưu file upload
            chroma_db_path: Đường dẫn đến ChromaDB
        """
        self.upload_folder = upload_folder
        self.chroma_db_path = chroma_db_path
        self.allowed_extensions = {'pdf'}
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        
        # Tạo thư mục uploads nếu chưa tồn tại
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)
        
        # Khởi tạo ChromaDB client và collection
        self._init_chroma_db()
    
    def is_allowed_file(self, filename):
        """
        Kiểm tra file có được phép upload không
        
        Args:
            filename: Tên file
            
        Returns:
            bool: True nếu file được phép upload
        """
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def validate_file_size(self, file):
        """
        Kiểm tra kích thước file
        
        Args:
            file: File object từ request
            
        Returns:
            tuple: (is_valid, file_size, error_message)
        """
        try:
            file.seek(0, 2)  # Seek to end of file
            file_size = file.tell()
            file.seek(0)  # Reset to beginning
            
            if file_size > self.max_file_size:
                return False, file_size, f"File size must be less than {self.max_file_size // (1024*1024)}MB"
            
            return True, file_size, None
            
        except Exception as e:
            return False, 0, f"Error checking file size: {str(e)}"
    
    def extract_text_from_pdf(self, file_path):
        """
        Trích xuất text từ file PDF
        
        Args:
            file_path: Đường dẫn đến file PDF
            
        Returns:
            tuple: (success, text, pages_count, error_message)
        """
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                pages_count = len(pdf_reader.pages)
                
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            
            return True, text, pages_count, None
            
        except Exception as e:
            return False, "", 0, f"Error extracting text from PDF: {str(e)}"
    
    def calculate_file_hash(self, file_path):
        """
        Tính hash MD5 của file
        
        Args:
            file_path: Đường dẫn đến file
            
        Returns:
            str: Hash MD5 của file
        """
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def generate_unique_filename(self, filename):
        """
        Tạo tên file unique với timestamp
        
        Args:
            filename: Tên file gốc
            
        Returns:
            tuple: (unique_filename, timestamp)
        """
        secure_name = secure_filename(filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{secure_name}"
        return unique_filename, timestamp
    
    def save_file_metadata(self, file_id, metadata):
        """
        Lưu metadata của file
        
        Args:
            file_id: ID của file
            metadata: Dictionary chứa metadata
            
        Returns:
            tuple: (success, metadata_path, error_message)
        """
        try:
            metadata_path = os.path.join(self.upload_folder, f"{file_id}_metadata.json")
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            return True, metadata_path, None
            
        except Exception as e:
            return False, "", f"Error saving metadata: {str(e)}"
    
    def save_extracted_text(self, file_id, text):
        """
        Lưu text đã trích xuất vào file riêng
        
        Args:
            file_id: ID của file
            text: Text đã trích xuất
            
        Returns:
            tuple: (success, text_path, error_message)
        """
        try:
            text_path = os.path.join(self.upload_folder, f"{file_id}_text.txt")
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(text)
            
            return True, text_path, None
            
        except Exception as e:
            return False, "", f"Error saving extracted text: {str(e)}"
    
    def _init_chroma_db(self):
        """
        Khởi tạo ChromaDB client và collection
        
        Tạo connection đến ChromaDB và collection để lưu trữ vector embeddings
        của text đã trích xuất từ PDF files
        """
        try:
            # Tạo thư mục ChromaDB nếu chưa tồn tại
            if not os.path.exists(self.chroma_db_path):
                os.makedirs(self.chroma_db_path)
            
            # Khởi tạo ChromaDB client với persistent storage
            self.chroma_client = chromadb.PersistentClient(path=self.chroma_db_path)
            
            # Tạo hoặc lấy collection cho knowledge base
            # Collection này sẽ lưu trữ text chunks và metadata
            self.collection = self.chroma_client.get_or_create_collection(
                name="knowledge_base",
                metadata={"description": "PDF document knowledge base with text chunks"}
            )
            
            print(f"✅ ChromaDB initialized successfully at: {self.chroma_db_path}")
            
        except Exception as e:
            print(f"❌ Error initializing ChromaDB: {str(e)}")
            self.chroma_client = None
            self.collection = None
    
    def _split_text_into_chunks(self, text, chunk_size=1000, overlap=200):
        """
        Chia text thành các chunks nhỏ để lưu vào vector database
        Cải thiện để xử lý tiếng Việt tốt hơn
        
        Args:
            text: Text cần chia (tiếng Việt hoặc tiếng Anh)
            chunk_size: Kích thước mỗi chunk (số ký tự)
            overlap: Số ký tự overlap giữa các chunk
            
        Returns:
            list: Danh sách các text chunks
        """
        # Làm sạch text: loại bỏ ký tự xuống dòng thừa và khoảng trắng
        cleaned_text = re.sub(r'\n+', '\n', text.strip())
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        
        if len(cleaned_text) <= chunk_size:
            return [cleaned_text]
        
        chunks = []
        start = 0
        
        while start < len(cleaned_text):
            # Tính vị trí kết thúc chunk
            end = start + chunk_size
            
            # Nếu chưa đến cuối text, tìm điểm ngắt tự nhiên (câu, đoạn)
            if end < len(cleaned_text):
                # Tìm điểm ngắt gần nhất với ưu tiên cao cho tiếng Việt
                # Thêm các dấu câu tiếng Việt
                break_chars = ['. ', '\n', '! ', '? ', '; ', ': ', '.\n', '!\n', '?\n']
                
                best_break = -1
                for break_char in break_chars:
                    break_pos = cleaned_text.rfind(break_char, start, end)
                    if break_pos != -1:
                        best_break = break_pos + len(break_char)
                        break
                
                # Nếu không tìm thấy dấu câu, tìm khoảng trắng gần cuối chunk
                if best_break == -1:
                    space_pos = cleaned_text.rfind(' ', start, end)
                    if space_pos != -1 and space_pos > start + chunk_size * 0.7:
                        best_break = space_pos + 1
                
                if best_break != -1:
                    end = best_break
            
            # Lấy chunk text
            chunk = cleaned_text[start:end].strip()
            if chunk:  # Chỉ thêm chunk không rỗng
                chunks.append(chunk)
            
            # Di chuyển start position với overlap
            start = max(start + 1, end - overlap)
            
            # Tránh infinite loop
            if start >= len(cleaned_text):
                break
        
        return chunks
    
    def save_to_vector_db(self, file_id, title, description, extracted_text, metadata):
        """
        Lưu text đã trích xuất vào ChromaDB vector database
        
        Args:
            file_id: UUID của file
            title: Tiêu đề tài liệu
            description: Mô tả tài liệu  
            extracted_text: Text đã trích xuất từ PDF
            metadata: Metadata của file
            
        Returns:
            tuple: (success, chunks_count, error_message)
        """
        try:
            # Kiểm tra ChromaDB đã được khởi tạo chưa
            if not self.collection:
                return False, 0, "ChromaDB not initialized"
            
            # Chia text thành các chunks nhỏ
            text_chunks = self._split_text_into_chunks(extracted_text)
            
            if not text_chunks:
                return False, 0, "No text chunks to save"
            
            # Chuẩn bị dữ liệu cho ChromaDB
            chunk_ids = []
            chunk_documents = []
            chunk_metadatas = []
            
            for i, chunk in enumerate(text_chunks):
                # Tạo unique ID cho mỗi chunk (file_id + chunk_index)
                chunk_id = f"{file_id}_chunk_{i}"
                
                # Phát hiện ngôn ngữ chính của chunk
                language = self._detect_language(chunk)
                
                # Chuẩn hóa nội dung chunk để tìm kiếm tốt hơn
                normalized_chunk = self._normalize_vietnamese_text(chunk)
                
                # Metadata cho mỗi chunk
                # filename_uuid = file_id gốc để có thể nhóm tất cả chunks của cùng 1 file
                chunk_metadata = {
                    "file_id": file_id,
                    "chunk_index": i,
                    "title": title,
                    "description": description,
                    "filename": metadata.get("original_filename", ""),
                    "filename_uuid": file_id,  # Dùng file_id gốc làm filename_uuid để nhóm chunks theo file
                    "upload_time": metadata.get("upload_time", ""),
                    "file_size": metadata.get("file_size", 0),
                    "pages_count": metadata.get("pages_count", 0),
                    "chunk_length": len(chunk),
                    "language": language,
                    "normalized_content": normalized_chunk  # Thêm content đã chuẩn hóa
                }
                
                chunk_ids.append(chunk_id)
                chunk_documents.append(chunk)
                chunk_metadatas.append(chunk_metadata)
            
            # Lưu vào ChromaDB với auto-generated embeddings
            self.collection.add(
                documents=chunk_documents,
                metadatas=chunk_metadatas,
                ids=chunk_ids
            )
            
            print(f"✅ Saved {len(text_chunks)} chunks to ChromaDB for file: {title}")
            return True, len(text_chunks), None
            
        except Exception as e:
            error_msg = f"Error saving to vector DB: {str(e)}"
            print(f"❌ {error_msg}")
            return False, 0, error_msg
    
    def search_in_vector_db(self, query, n_results=5, file_id=None):
        """
        Tìm kiếm trong vector database
        
        Args:
            query: Câu hỏi/từ khóa tìm kiếm
            n_results: Số kết quả trả về
            file_id: Tìm kiếm trong file cụ thể (optional)
            
        Returns:
            tuple: (success, results, error_message)
        """
        try:
            if not self.collection:
                return False, [], "ChromaDB not initialized"
            
            # Chuẩn bị filter nếu cần tìm trong file cụ thể
            where_filter = None
            if file_id:
                where_filter = {"file_id": file_id}
            
            # Thực hiện tìm kiếm vector similarity
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format kết quả trả về
            formatted_results = []
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    result_item = {
                        "content": doc,
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "similarity_score": 1 - results["distances"][0][i] if results["distances"] else 0
                    }
                    formatted_results.append(result_item)
            
            return True, formatted_results, None
            
        except Exception as e:
            error_msg = f"Error searching vector DB: {str(e)}"
            return False, [], error_msg
    
    def delete_from_vector_db(self, file_id):
        """
        Xóa tất cả chunks của một file khỏi vector database
        
        Args:
            file_id: UUID của file cần xóa
            
        Returns:
            tuple: (success, error_message)
        """
        try:
            if not self.collection:
                return False, "ChromaDB not initialized"
            
            # Tìm tất cả chunks của file này
            results = self.collection.get(
                where={"file_id": file_id},
                include=["documents"]
            )
            
            if results["ids"]:
                # Xóa tất cả chunks
                self.collection.delete(ids=results["ids"])
                print(f"✅ Deleted {len(results['ids'])} chunks from ChromaDB for file: {file_id}")
            
            return True, None
            
        except Exception as e:
            error_msg = f"Error deleting from vector DB: {str(e)}"
            return False, error_msg
    
    def process_uploaded_file(self, file, title, description):
        """
        Xử lý file upload hoàn chỉnh
        
        Args:
            file: File object từ request
            title: Tiêu đề tài liệu
            description: Mô tả tài liệu
            
        Returns:
            tuple: (success, result_data, error_message, status_code)
        """
        try:
            # Validate file
            if not file or not file.filename:
                return False, None, "No file selected", 400
            
            if not self.is_allowed_file(file.filename):
                return False, None, "Only PDF files are allowed", 400
            
            # Validate file size
            is_valid_size, file_size, size_error = self.validate_file_size(file)
            if not is_valid_size:
                return False, None, size_error, 413
            
            # Generate unique filename
            unique_filename, timestamp = self.generate_unique_filename(file.filename)
            file_path = os.path.join(self.upload_folder, unique_filename)
            
            # Save file
            file.save(file_path)
            
            # Extract text from PDF
            extract_success, extracted_text, pages_count, extract_error = self.extract_text_from_pdf(file_path)
            if not extract_success:
                # Clean up file if extraction failed
                if os.path.exists(file_path):
                    os.remove(file_path)
                return False, None, extract_error, 500
            
            # Calculate file hash
            file_hash = self.calculate_file_hash(file_path)
            
            # Generate UUID for file_id
            file_id = str(uuid.uuid4())
            
            # Create metadata
            metadata = {
                "file_id": file_id,
                "original_filename": file.filename,
                "title": title,
                "stored_filename": unique_filename,
                "file_path": file_path,
                "file_size": file_size,
                "file_hash": file_hash,
                "pages_count": pages_count,
                "text_length": len(extracted_text),
                "upload_time": datetime.now().isoformat(),
                "description": description,
                "extracted_text": extracted_text
            }
            
            # Save metadata
            metadata_success, metadata_path, metadata_error = self.save_file_metadata(file_id, metadata)
            if not metadata_success:
                # Clean up file if metadata saving failed
                if os.path.exists(file_path):
                    os.remove(file_path)
                return False, None, metadata_error, 500
            
            # Save extracted text
            text_success, text_path, text_error = self.save_extracted_text(file_id, extracted_text)
            if not text_success:
                # Clean up files if text saving failed
                if os.path.exists(file_path):
                    os.remove(file_path)
                if os.path.exists(metadata_path):
                    os.remove(metadata_path)
                return False, None, text_error, 500
            
            # Lưu vào ChromaDB vector database
            # Chức năng này cho phép tìm kiếm semantic trong nội dung PDF
            vector_success, chunks_count, vector_error = self.save_to_vector_db(
                file_id, title, description, extracted_text, metadata
            )
            
            # Ghi log nhưng không fail nếu vector DB có lỗi
            if not vector_success:
                print(f"⚠️ Warning: Could not save to vector DB: {vector_error}")
                # Không return error vì file đã được lưu thành công
            else:
                print(f"✅ Successfully saved {chunks_count} text chunks to vector database")
            
            # Prepare response data (exclude sensitive info)
            response_data = {
                key: value for key, value in metadata.items() 
                if key not in ['extracted_text', 'file_path', 'stored_filename']
            }
            
            # Thêm thông tin về vector DB vào response
            response_data['vector_chunks_count'] = chunks_count if vector_success else 0
            response_data['vector_db_status'] = 'success' if vector_success else 'warning'
            
            return True, response_data, "File uploaded and processed successfully", 200
            
        except Exception as e:
            return False, None, f"Failed to process file: {str(e)}", 500
    
    def get_uploaded_files(self):
        """
        Lấy danh sách các file đã upload
        
        Returns:
            tuple: (success, files_data, error_message)
        """
        try:
            files_list = []
            
            # Kiểm tra thư mục upload tồn tại
            if not os.path.exists(self.upload_folder):
                return True, {"files": [], "total_files": 0}, None
            
            # Duyệt qua các file metadata
            for filename in os.listdir(self.upload_folder):
                if filename.endswith('_metadata.json'):
                    metadata_path = os.path.join(self.upload_folder, filename)
                    try:
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        
                        # Chỉ lấy thông tin cần thiết
                        file_info = {
                            'file_id': metadata.get('file_id'),
                            'filename': metadata.get('original_filename'),
                            'title': metadata.get('title'),
                            'file_size': metadata.get('file_size'),
                            'pages_count': metadata.get('pages_count'),
                            'text_length': metadata.get('text_length'),
                            'upload_time': metadata.get('upload_time'),
                            'description': metadata.get('description', '')
                        }
                        files_list.append(file_info)
                        
                    except Exception as e:
                        # Skip files with invalid metadata
                        continue
            
            # Sắp xếp theo thời gian upload (mới nhất trước)
            files_list.sort(key=lambda x: x.get('upload_time', ''), reverse=True)
            
            result_data = {
                "files": files_list,
                "total_files": len(files_list)
            }
            
            return True, result_data, None
            
        except Exception as e:
            return False, None, f"Failed to list files: {str(e)}"
    
    def get_file_by_id(self, file_id):
        """
        Lấy thông tin chi tiết của một file theo ID
        
        Args:
            file_id: ID của file
            
        Returns:
            tuple: (success, file_data, error_message)
        """
        try:
            metadata_path = os.path.join(self.upload_folder, f"{file_id}_metadata.json")
            
            if not os.path.exists(metadata_path):
                return False, None, "File not found"
            
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Exclude sensitive information
            file_data = {
                key: value for key, value in metadata.items() 
                if key not in ['file_path', 'stored_filename']
            }
            
            return True, file_data, None
            
        except Exception as e:
            return False, None, f"Error retrieving file: {str(e)}"
    
    def delete_file(self, file_id):
        """
        Xóa file và metadata
        
        Args:
            file_id: ID của file
            
        Returns:
            tuple: (success, error_message)
        """
        try:
            # Paths to delete
            metadata_path = os.path.join(self.upload_folder, f"{file_id}_metadata.json")
            text_path = os.path.join(self.upload_folder, f"{file_id}_text.txt")
            
            # Get file path from metadata
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    file_path = metadata.get('file_path')
            else:
                return False, "File not found"
            
            # Xóa khỏi vector database trước
            # Điều này đảm bảo không còn tham chiếu đến file trong vector DB
            vector_success, vector_error = self.delete_from_vector_db(file_id)
            if not vector_success:
                print(f"⚠️ Warning: Could not delete from vector DB: {vector_error}")
                # Tiếp tục xóa file dù vector DB có lỗi
            
            # Delete files from filesystem
            files_to_delete = [metadata_path, text_path]
            if file_path and os.path.exists(file_path):
                files_to_delete.append(file_path)
            
            for file_to_delete in files_to_delete:
                if os.path.exists(file_to_delete):
                    os.remove(file_to_delete)
            
            print(f"✅ Successfully deleted file {file_id} and all associated data")
            return True, None
            
        except Exception as e:
            return False, f"Error deleting file: {str(e)}"
    
    def search_knowledge_base(self, query, max_results=5, file_id=None):
        """
        Tìm kiếm trong knowledge base sử dụng vector similarity
        
        Args:
            query: Câu hỏi hoặc từ khóa tìm kiếm
            max_results: Số kết quả tối đa trả về
            file_id: Tìm kiếm trong file cụ thể (optional)
            
        Returns:
            tuple: (success, search_results, error_message)
        """
        try:
            # Tìm kiếm trong vector database
            vector_success, vector_results, vector_error = self.search_in_vector_db(
                query, max_results, file_id
            )
            
            if not vector_success:
                return False, [], f"Vector search failed: {vector_error}"
            
            # Format kết quả cho API response
            formatted_results = []
            for result in vector_results:
                formatted_result = {
                    "content": result["content"],
                    "similarity_score": round(result["similarity_score"], 4),
                    "source": {
                        "file_id": result["metadata"].get("file_id"),
                        "title": result["metadata"].get("title"),
                        "filename": result["metadata"].get("filename"),
                        "filename_uuid": result["metadata"].get("filename_uuid"),
                        "chunk_index": result["metadata"].get("chunk_index")
                    }
                }
                formatted_results.append(formatted_result)
            
            return True, formatted_results, None
            
        except Exception as e:
            return False, [], f"Search failed: {str(e)}"
    
    def get_vector_db_stats(self):
        """
        Lấy thống kê về vector database
        
        Returns:
            tuple: (success, stats, error_message)
        """
        try:
            if not self.collection:
                return False, {}, "ChromaDB not initialized"
            
            # Lấy số lượng documents trong collection
            count = self.collection.count()
            
            # Lấy thông tin về collection
            stats = {
                "total_chunks": count,
                "collection_name": self.collection.name,
                "db_path": self.chroma_db_path
            }
            
            return True, stats, None
            
        except Exception as e:
            return False, {}, f"Error getting stats: {str(e)}"
    
    # =============================================================================
    # TRUY XUẤT DỮ LIỆU TỪ CHROMADB
    # =============================================================================
    
    def get_all_chunks(self, limit=None):
        """
        Lấy tất cả chunks từ ChromaDB (không cần search query)
        
        Args:
            limit: Giới hạn số lượng chunks trả về (optional)
            
        Returns:
            tuple: (success, chunks_data, error_message)
        """
        try:
            if not self.collection:
                return False, [], "ChromaDB not initialized"
            
            # Lấy tất cả documents trong collection
            results = self.collection.get(
                limit=limit,
                include=["documents", "metadatas"]
            )
            
            # Format kết quả
            chunks_data = []
            if results["documents"]:
                for i, doc in enumerate(results["documents"]):
                    chunk_info = {
                        "id": results["ids"][i],
                        "content": doc,
                        "metadata": results["metadatas"][i] if results["metadatas"] else {}
                    }
                    chunks_data.append(chunk_info)
            
            return True, chunks_data, None
            
        except Exception as e:
            return False, [], f"Error getting all chunks: {str(e)}"
    
    def get_chunks_by_file_id(self, file_id):
        """
        Lấy tất cả chunks của một file cụ thể
        
        Args:
            file_id: UUID của file
            
        Returns:
            tuple: (success, chunks_data, error_message)
        """
        try:
            if not self.collection:
                return False, [], "ChromaDB not initialized"
            
            # Tìm tất cả chunks có file_id cụ thể
            results = self.collection.get(
                where={"file_id": file_id},
                include=["documents", "metadatas"]
            )
            
            # Sắp xếp theo chunk_index
            chunks_data = []
            if results["documents"]:
                for i, doc in enumerate(results["documents"]):
                    chunk_info = {
                        "id": results["ids"][i],
                        "content": doc,
                        "metadata": results["metadatas"][i] if results["metadatas"] else {},
                        "chunk_index": results["metadatas"][i].get("chunk_index", 0) if results["metadatas"] else 0
                    }
                    chunks_data.append(chunk_info)
                
                # Sắp xếp theo chunk_index
                chunks_data.sort(key=lambda x: x["chunk_index"])
            
            return True, chunks_data, None
            
        except Exception as e:
            return False, [], f"Error getting chunks by file ID: {str(e)}"
    
    def get_chunks_by_title(self, title):
        """
        Lấy chunks theo title của document
        
        Args:
            title: Tiêu đề document
            
        Returns:
            tuple: (success, chunks_data, error_message)
        """
        try:
            if not self.collection:
                return False, [], "ChromaDB not initialized"
            
            # Tìm chunks có title cụ thể
            results = self.collection.get(
                where={"title": title},
                include=["documents", "metadatas"]
            )
            
            chunks_data = []
            if results["documents"]:
                for i, doc in enumerate(results["documents"]):
                    chunk_info = {
                        "id": results["ids"][i],
                        "content": doc,
                        "metadata": results["metadatas"][i] if results["metadatas"] else {}
                    }
                    chunks_data.append(chunk_info)
            
            return True, chunks_data, None
            
        except Exception as e:
            return False, [], f"Error getting chunks by title: {str(e)}"
    
    def get_chunk_by_id(self, chunk_id):
        """
        Lấy một chunk cụ thể theo ID
        
        Args:
            chunk_id: ID của chunk (format: file_id_chunk_index)
            
        Returns:
            tuple: (success, chunk_data, error_message)
        """
        try:
            if not self.collection:
                return False, None, "ChromaDB not initialized"
            
            # Lấy chunk theo ID
            results = self.collection.get(
                ids=[chunk_id],
                include=["documents", "metadatas"]
            )
            
            if results["documents"] and len(results["documents"]) > 0:
                chunk_data = {
                    "id": chunk_id,
                    "content": results["documents"][0],
                    "metadata": results["metadatas"][0] if results["metadatas"] else {}
                }
                return True, chunk_data, None
            else:
                return False, None, "Chunk not found"
            
        except Exception as e:
            return False, None, f"Error getting chunk by ID: {str(e)}"
    
    def filter_chunks_by_metadata(self, filters, limit=None):
        """
        Lọc chunks theo metadata
        
        Args:
            filters: Dictionary chứa điều kiện lọc
                    Ví dụ: {"file_size": {"$gte": 1000}, "pages_count": {"$lte": 10}}
            limit: Giới hạn số kết quả
            
        Returns:
            tuple: (success, chunks_data, error_message)
        """
        try:
            if not self.collection:
                return False, [], "ChromaDB not initialized"
            
            # Lọc chunks theo metadata
            results = self.collection.get(
                where=filters,
                limit=limit,
                include=["documents", "metadatas"]
            )
            
            chunks_data = []
            if results["documents"]:
                for i, doc in enumerate(results["documents"]):
                    chunk_info = {
                        "id": results["ids"][i],
                        "content": doc,
                        "metadata": results["metadatas"][i] if results["metadatas"] else {}
                    }
                    chunks_data.append(chunk_info)
            
            return True, chunks_data, None
            
        except Exception as e:
            return False, [], f"Error filtering chunks: {str(e)}"
    
    def get_files_summary_from_chunks(self):
        """
        Lấy tóm tắt thông tin các file từ chunks trong ChromaDB
        
        Returns:
            tuple: (success, files_summary, error_message)
        """
        try:
            if not self.collection:
                return False, [], "ChromaDB not initialized"
            
            # Lấy tất cả chunks
            results = self.collection.get(include=["metadatas"])
            
            if not results["metadatas"]:
                return True, [], None
            
            # Nhóm chunks theo file_id
            files_dict = {}
            for metadata in results["metadatas"]:
                file_id = metadata.get("file_id")
                if file_id not in files_dict:
                    files_dict[file_id] = {
                        "file_id": file_id,
                        "title": metadata.get("title", ""),
                        "filename": metadata.get("filename", ""),
                        "upload_time": metadata.get("upload_time", ""),
                        "file_size": metadata.get("file_size", 0),
                        "pages_count": metadata.get("pages_count", 0),
                        "chunks_count": 0,
                        "total_chunk_length": 0
                    }
                
                # Cập nhật thống kê
                files_dict[file_id]["chunks_count"] += 1
                files_dict[file_id]["total_chunk_length"] += metadata.get("chunk_length", 0)
            
            # Chuyển thành list và sắp xếp
            files_summary = list(files_dict.values())
            files_summary.sort(key=lambda x: x["upload_time"], reverse=True)
            
            return True, files_summary, None
            
        except Exception as e:
            return False, [], f"Error getting files summary: {str(e)}"
    
    def search_chunks_with_filters(self, query, filters=None, n_results=5):
        """
        Tìm kiếm vector similarity với filters metadata
        
        Args:
            query: Câu hỏi tìm kiếm
            filters: Điều kiện lọc metadata (optional)
            n_results: Số kết quả trả về
            
        Returns:
            tuple: (success, results, error_message)
        """
        try:
            if not self.collection:
                return False, [], "ChromaDB not initialized"
            
            # Thực hiện tìm kiếm với filters
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=filters,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format kết quả
            formatted_results = []
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    result_item = {
                        "content": doc,
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "similarity_score": 1 - results["distances"][0][i] if results["distances"] else 0
                    }
                    formatted_results.append(result_item)
            
            return True, formatted_results, None
            
        except Exception as e:
            return False, [], f"Error searching with filters: {str(e)}"

    def search_in_multiple_files(self, query, filename_uuids, max_results=5):
        """
        Tìm kiếm trong nhiều files cụ thể dựa trên list filename_uuid
        Hỗ trợ tìm kiếm tiếng Việt với xử lý văn bản cải tiến
        
        Args:
            query: Câu hỏi tìm kiếm (tiếng Việt hoặc tiếng Anh)
            filename_uuids: List các filename_uuid để tìm kiếm
            max_results: Số kết quả tối đa trả về
            
        Returns:
            tuple: (success, results, error_message)
        """
        try:
            if not self.collection:
                return False, [], "ChromaDB not initialized"
            
            if not filename_uuids or len(filename_uuids) == 0:
                return False, [], "No filename_uuids provided"
            
            # Tạo filter để tìm kiếm trong các files cụ thể
            filters = {
                "filename_uuid": {"$in": filename_uuids}
            }
            
            print(f"🔍 Searching for query: '{query}' in files: {filename_uuids}")
            
            # Chiến lược 1: Tìm kiếm trực tiếp với query gốc
            success, search_results, error_message = self.search_chunks_with_filters(
                query, filters, max_results
            )
            
            if success and len(search_results) > 0:
                print(f"✅ Found {len(search_results)} results with original query")
                return self._format_search_results(search_results, query, filename_uuids, max_results)
            
            # Chiến lược 2: Chuẩn hóa query và thử lại
            normalized_query = self._normalize_vietnamese_text(query)
            if normalized_query != query:
                print(f"🔄 Trying normalized query: '{normalized_query}'")
                success, search_results, error_message = self.search_chunks_with_filters(
                    normalized_query, filters, max_results
                )
                
                if success and len(search_results) > 0:
                    print(f"✅ Found {len(search_results)} results with normalized query")
                    return self._format_search_results(search_results, query, filename_uuids, max_results)
            
            # Chiến lược 3: Tìm kiếm với từ khóa
            keywords = self._extract_keywords_vietnamese(query)
            if keywords:
                keyword_query = " ".join(keywords)
                print(f"🔑 Trying keyword search: '{keyword_query}'")
                success, search_results, error_message = self.search_chunks_with_filters(
                    keyword_query, filters, max_results
                )
                
                if success and len(search_results) > 0:
                    print(f"✅ Found {len(search_results)} results with keyword search")
                    return self._format_search_results(search_results, query, filename_uuids, max_results)
            
            # Chiến lược 4: Tìm kiếm text matching trực tiếp
            print("🔍 Trying direct text matching...")
            text_match_results = self._search_text_matching(query, filename_uuids, max_results)
            if text_match_results:
                print(f"✅ Found {len(text_match_results)} results with text matching")
                return True, text_match_results, f"Found {len(text_match_results)} results using text matching"
            
            # Nếu không tìm thấy gì
            if not success:
                return False, [], error_message
            
            return True, [], "No matching results found"
            
        except Exception as e:
            return False, [], f"Error searching in multiple files: {str(e)}"
    
    def _search_text_matching(self, query, filename_uuids, max_results=5):
        """
        Tìm kiếm bằng text matching trực tiếp (không dùng vector similarity)
        Hữu ích cho các từ khóa cụ thể hoặc khi vector search không hiệu quả
        """
        try:
            # Lấy tất cả chunks của các files được chỉ định
            all_chunks = self.collection.get(
                where={"filename_uuid": {"$in": filename_uuids}},
                include=["documents", "metadatas"]
            )
            
            if not all_chunks["documents"]:
                return []
            
            # Chuẩn hóa query để so sánh
            normalized_query = self._normalize_vietnamese_text(query).lower()
            query_keywords = set(normalized_query.split())
            
            # Tìm kiếm text matching
            matching_results = []
            for i, doc in enumerate(all_chunks["documents"]):
                if not doc:
                    continue
                
                normalized_doc = self._normalize_vietnamese_text(doc).lower()
                doc_words = set(normalized_doc.split())
                
                # Tính điểm dựa trên số từ khóa khớp
                matching_words = query_keywords.intersection(doc_words)
                if matching_words:
                    score = len(matching_words) / len(query_keywords)
                    
                    # Kiểm tra xem có chứa phrase không
                    if normalized_query in normalized_doc:
                        score += 0.5  # Bonus cho exact phrase match
                    
                    metadata = all_chunks["metadatas"][i] if i < len(all_chunks["metadatas"]) else {}
                    
                    result = {
                        "content": doc,
                        "similarity_score": min(score, 1.0),  # Cap at 1.0
                        "metadata": metadata,
                        "matching_words": list(matching_words)
                    }
                    matching_results.append(result)
            
            # Sắp xếp theo điểm số và trả về top results
            matching_results.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            # Format results giống như vector search
            formatted_results = []
            for result in matching_results[:max_results]:
                metadata = result.get("metadata", {})
                formatted_result = {
                    "content": result.get("content", ""),
                    "similarity_score": result.get("similarity_score", 0),
                    "source": {
                        "file_id": metadata.get("filename_uuid", ""),
                        "filename_uuid": metadata.get("filename_uuid", ""),
                        "title": metadata.get("title", ""),
                        "filename": metadata.get("filename", ""),
                        "chunk_index": metadata.get("chunk_index", 0),
                        "chunk_length": len(result.get("content", "")),
                        "search_method": "text_matching",
                        "matching_words": result.get("matching_words", [])
                    }
                }
                formatted_results.append(formatted_result)
            
            return formatted_results
            
        except Exception as e:
            print(f"Error in text matching search: {str(e)}")
            return []
    
    def _format_search_results(self, search_results, original_query, filename_uuids, max_results):
        """
        Format search results cho API response
        """
        formatted_results = []
        for result in search_results:
            metadata = result.get("metadata", {})
            formatted_result = {
                "content": result.get("content", ""),
                "similarity_score": result.get("similarity_score", 0),
                "source": {
                    "file_id": metadata.get("filename_uuid", ""),
                    "filename_uuid": metadata.get("filename_uuid", ""),
                    "title": metadata.get("title", ""),
                    "filename": metadata.get("filename", ""),
                    "chunk_index": metadata.get("chunk_index", 0),
                    "chunk_length": len(result.get("content", "")),
                    "search_method": "vector_similarity"
                }
            }
            formatted_results.append(formatted_result)
        
        return True, formatted_results, f"Found {len(formatted_results)} results in {len(filename_uuids)} files"
    
    def _normalize_vietnamese_text(self, text):
        """
        Chuẩn hóa text tiếng Việt để tìm kiếm tốt hơn
        
        Args:
            text: Text cần chuẩn hóa
            
        Returns:
            str: Text đã được chuẩn hóa
        """
        if not text:
            return text
        
        # Chuyển về lowercase
        normalized = text.lower()
        
        # Loại bỏ dấu câu thừa
        normalized = re.sub(r'[^\w\sàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]', ' ', normalized)
        
        # Loại bỏ multiple spaces
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    def _extract_keywords_vietnamese(self, text):
        """
        Trích xuất từ khóa quan trọng từ query tiếng Việt
        
        Args:
            text: Text cần trích xuất từ khóa
            
        Returns:
            list: Danh sách từ khóa quan trọng
        """
        if not text:
            return []
        
        # Chuẩn hóa text
        normalized = self._normalize_vietnamese_text(text)
        
        # Danh sách stop words tiếng Việt phổ biến
        vietnamese_stop_words = {
            'là', 'của', 'và', 'có', 'trong', 'với', 'để', 'được', 'một', 'các', 'này', 'đó', 
            'như', 'về', 'cho', 'từ', 'khi', 'nào', 'nếu', 'thì', 'sẽ', 'đã', 'đang', 'sao',
            'gì', 'ai', 'đâu', 'bao', 'giờ', 'nào', 'thế', 'tại', 'vì', 'do', 'bởi', 'theo',
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after', 'above',
            'below', 'between', 'among', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'
        }
        
        # Tách từ và loại bỏ stop words
        words = normalized.split()
        keywords = []
        
        for word in words:
            # Giữ lại từ có độ dài >= 3 và không phải stop word
            if len(word) >= 3 and word not in vietnamese_stop_words:
                keywords.append(word)
        
        # Giới hạn số từ khóa trả về
        return keywords[:5]
    
    def _detect_language(self, text):
        """
        Phát hiện ngôn ngữ chính của text (tiếng Việt hoặc tiếng Anh)
        
        Args:
            text: Text cần phân tích
            
        Returns:
            str: 'vi' cho tiếng Việt, 'en' cho tiếng Anh, 'mixed' cho hỗn hợp
        """
        if not text or len(text.strip()) < 10:
            return 'unknown'
        
        # Các ký tự đặc trưng tiếng Việt
        vietnamese_chars = 'àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ'
        
        # Đếm ký tự tiếng Việt
        vietnamese_count = 0
        total_chars = 0
        
        for char in text.lower():
            if char.isalpha():
                total_chars += 1
                if char in vietnamese_chars:
                    vietnamese_count += 1
        
        if total_chars == 0:
            return 'unknown'
        
        vietnamese_ratio = vietnamese_count / total_chars
        
        # Nếu > 5% ký tự là tiếng Việt thì coi là tiếng Việt
        if vietnamese_ratio > 0.05:
            return 'vi'
        elif vietnamese_ratio > 0.01:
            return 'mixed'
        else:
            return 'en'
    
    def debug_chunks_content(self, filename_uuids=None, limit=3):
        """
        Debug method để xem nội dung thực tế của chunks
        Giúp hiểu tại sao tìm kiếm không trả về kết quả mong muốn
        
        Args:
            filename_uuids: List filename_uuid để debug (optional)
            limit: Số chunks tối đa để hiển thị
            
        Returns:
            tuple: (success, debug_info, error_message)
        """
        try:
            if not self.collection:
                return False, {}, "ChromaDB not initialized"
            
            # Tạo filter nếu có filename_uuids
            where_filter = None
            if filename_uuids:
                where_filter = {"filename_uuid": {"$in": filename_uuids}}
            
            # Lấy chunks để debug
            results = self.collection.get(
                where=where_filter,
                limit=limit,
                include=["documents", "metadatas"]
            )
            
            debug_info = {
                "total_chunks": len(results["documents"]) if results["documents"] else 0,
                "chunks_preview": []
            }
            
            if results["documents"]:
                for i, doc in enumerate(results["documents"][:limit]):
                    metadata = results["metadatas"][i] if i < len(results["metadatas"]) else {}
                    
                    chunk_info = {
                        "chunk_index": i,
                        "content_preview": doc[:200] + "..." if len(doc) > 200 else doc,
                        "content_length": len(doc),
                        "language": metadata.get("language", "unknown"),
                        "title": metadata.get("title", ""),
                        "filename": metadata.get("filename", ""),
                        "filename_uuid": metadata.get("filename_uuid", ""),
                        "chunk_metadata_index": metadata.get("chunk_index", 0)
                    }
                    debug_info["chunks_preview"].append(chunk_info)
            
            return True, debug_info, None
            
        except Exception as e:
            return False, {}, f"Error debugging chunks: {str(e)}"
    
    def reset_chromadb(self, confirm_reset=False):
        """
        Reset ChromaDB - Xóa tất cả chunks và tạo lại collection mới
        
        Args:
            confirm_reset: Xác nhận reset (bảo vệ khỏi xóa nhầm)
            
        Returns:
            tuple: (success, reset_info, error_message)
        """
        try:
            if not confirm_reset:
                return False, {}, "Please set confirm_reset=True to confirm reset operation"
            
            if not self.chroma_client:
                return False, {}, "ChromaDB client not initialized"
            
            # Lấy thông tin trước khi reset
            old_collection_info = {}
            if self.collection:
                try:
                    old_data = self.collection.get(include=["documents", "metadatas"])
                    old_collection_info = {
                        "total_chunks_deleted": len(old_data["documents"]) if old_data["documents"] else 0,
                        "collection_name": "knowledge_base"
                    }
                except:
                    old_collection_info = {"total_chunks_deleted": "unknown", "collection_name": "knowledge_base"}
            
            # Xóa collection cũ
            try:
                self.chroma_client.delete_collection(name="knowledge_base")
                print("✅ Deleted old collection 'knowledge_base'")
            except Exception as e:
                print(f"⚠️ Could not delete old collection (might not exist): {str(e)}")
            
            # Tạo collection mới
            self.collection = self.chroma_client.get_or_create_collection(
                name="knowledge_base",
                metadata={"description": "PDF document knowledge base with text chunks - Reset on " + datetime.now().isoformat()}
            )
            
            reset_info = {
                "reset_timestamp": datetime.now().isoformat(),
                "old_collection_info": old_collection_info,
                "new_collection_created": True,
                "db_path": self.chroma_db_path
            }
            
            print(f"🔄 ChromaDB reset completed successfully")
            print(f"📊 Deleted {old_collection_info.get('total_chunks_deleted', 0)} chunks")
            
            return True, reset_info, "ChromaDB reset completed successfully"
            
        except Exception as e:
            return False, {}, f"Error resetting ChromaDB: {str(e)}"
    
    def clear_all_chunks(self):
        """
        Xóa tất cả chunks nhưng giữ nguyên collection
        (Phương thức nhẹ hơn reset_chromadb)
        
        Returns:
            tuple: (success, clear_info, error_message)
        """
        try:
            if not self.collection:
                return False, {}, "ChromaDB collection not initialized"
            
            # Lấy tất cả IDs
            all_data = self.collection.get(include=["documents"])
            total_chunks = len(all_data["ids"]) if all_data["ids"] else 0
            
            if total_chunks == 0:
                return True, {"chunks_cleared": 0, "message": "No chunks to clear"}, "No chunks found"
            
            # Xóa tất cả chunks
            self.collection.delete(ids=all_data["ids"])
            
            clear_info = {
                "chunks_cleared": total_chunks,
                "clear_timestamp": datetime.now().isoformat(),
                "collection_name": "knowledge_base"
            }
            
            print(f"🗑️ Cleared {total_chunks} chunks from ChromaDB")
            
            return True, clear_info, f"Cleared {total_chunks} chunks successfully"
            
        except Exception as e:
            return False, {}, f"Error clearing chunks: {str(e)}"
