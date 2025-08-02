import os
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class CodeCommenter:
    """Class để tự động tạo comment cho code Java"""
    
    def __init__(self):
        """Khởi tạo client Azure OpenAI"""
        self.client = AzureOpenAI(
            api_version="2024-07-01-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        )
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "GPT-4o-mini")
    
    def read_code_input(self, file_path="code_input.txt"):
        """
        Step 1: Đọc dữ liệu code từ file input
        
        Args:
            file_path (str): Đường dẫn đến file chứa code cần comment
            
        Returns:
            str: Nội dung code từ file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                code_content = file.read()
            print(f"Đã đọc thành công file: {file_path}")
            return code_content
        except FileNotFoundError:
            print(f"Không tìm thấy file: {file_path}")
            return None
        except Exception as e:
            print(f"Lỗi khi đọc file: {e}")
            return None
    
    def process_code(self, code_content):
        """
        Step 2: Xử lý code và tạo comments
        
        Args:
            code_content (str): Nội dung code cần được comment
            
        Returns:
            str: Code đã được thêm comments
        """
        if not code_content:
            return None
            
        prompt = f"""
Bạn là một chuyên gia lập trình Java. Hãy phân tích đoạn code Java sau và thêm các comment tiếng Việt chi tiết:

1. Thêm JavaDoc cho các class, method và constructor
2. Thêm comment giải thích cho các dòng code phức tạp
3. Thêm comment mô tả logic và mục đích của từng phần
4. Giữ nguyên format và cấu trúc code gốc
5. Comment phải rõ ràng, dễ hiểu và hữu ích
6. Sử dụng format comment Java chuẩn (// và /* */)

Code Java cần comment:
```java
{code_content}
```

Trả về code Java đã được comment hoàn chỉnh:
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=4000
            )
            
            commented_code = response.choices[0].message.content.strip()
            
            # Loại bỏ markdown formatting nếu có
            if commented_code.startswith("```java"):
                commented_code = commented_code.replace("```java", "").replace("```", "").strip()
            elif commented_code.startswith("```"):
                commented_code = commented_code.replace("```", "").strip()
            
            print("Đã xử lý và tạo comments thành công")
            return commented_code
            
        except Exception as e:
            print(f"Lỗi khi xử lý code: {e}")
            return None
    
    def save_output(self, commented_code, output_path="code_output.txt"):
        """
        Step 3: Lưu kết quả code đã comment vào file output
        
        Args:
            commented_code (str): Code đã được comment
            output_path (str): Đường dẫn file output
            
        Returns:
            bool: True nếu lưu thành công, False nếu có lỗi
        """
        if not commented_code:
            print("Không có nội dung để lưu")
            return False
            
        try:
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(commented_code)
            print(f"Đã lưu code đã comment vào: {output_path}")
            return True
        except Exception as e:
            print(f"Lỗi khi lưu file: {e}")
            return False
    
    def run_complete_process(self, input_file="code_input.txt", output_file="code_output.txt"):
        """
        Chạy toàn bộ quy trình comment code
        
        Args:
            input_file (str): File chứa code gốc
            output_file (str): File để lưu code đã comment
        """
        print("Bắt đầu quy trình comment code...")
        print("=" * 50)
        
        # Step 1: Đọc code input
        print("Step 1: Đọc dữ liệu code từ file...")
        code_content = self.read_code_input(input_file)
        if not code_content:
            return
        
        print(f"Độ dài code gốc: {len(code_content)} ký tự")
        print()
        
        # Step 2: Xử lý và tạo comments
        print("Step 2: Xử lý và tạo comments...")
        commented_code = self.process_code(code_content)
        if not commented_code:
            return
        
        print(f"Độ dài code đã comment: {len(commented_code)} ký tự")
        print()
        
        # Step 3: Lưu kết quả
        print("Step 3: Lưu kết quả...")
        success = self.save_output(commented_code, output_file)
        
        if success:
            print("=" * 50)
            print("Hoàn thành! Code đã được comment thành công.")
            print(f"File input: {input_file}")
            print(f"File output: {output_file}")
        else:
            print("Có lỗi xảy ra trong quá trình xử lý.")


def main():
    """Hàm main để chạy chương trình"""
    
    # Tạo instance của CodeCommenter
    commenter = CodeCommenter()
    
    # Chạy toàn bộ quy trình
    commenter.run_complete_process()
    
    # Hoặc có thể chạy từng step riêng biệt:
    # code = commenter.read_code_input("code_input.txt")
    # commented = commenter.process_code(code)
    # commenter.save_output(commented, "output.py")


if __name__ == "__main__":
    main()
