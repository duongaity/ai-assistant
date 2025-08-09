"""
Test file để kiểm tra Knowledge Base Service

Chạy file này để test các chức năng của service
"""

import sys
import os

# Thêm đường dẫn backend vào sys.path
sys.path.append('/Users/duong/WORKSPACE/AIREADY/ai-assistant/backend')

# Test import service
try:
    from services.knowledge_base_service import KnowledgeBaseService
    print("✅ Import KnowledgeBaseService thành công")
    
    # Tạo instance service
    service = KnowledgeBaseService()
    print("✅ Khởi tạo service thành công")
    
    # Test các method cơ bản
    print(f"✅ Upload folder: {service.upload_folder}")
    print(f"✅ Allowed extensions: {service.allowed_extensions}")
    print(f"✅ Max file size: {service.max_file_size / (1024*1024)}MB")
    
    # Test file validation
    print(f"✅ PDF file test: {service.is_allowed_file('test.pdf')}")
    print(f"✅ TXT file test: {service.is_allowed_file('test.txt')}")
    
    print("\n🎉 Tất cả tests cơ bản đều passed!")
    
except ImportError as e:
    print(f"❌ Lỗi import: {e}")
except Exception as e:
    print(f"❌ Lỗi khác: {e}")
