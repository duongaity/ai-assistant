# NOTE

## AI (Artificial Intelligence)
- Lĩnh vực nghiên cứu phát triển các hệ thống có khả năng thực hiện các tác vụ mà trước đây chỉ con người mới làm được như nhận diện hình ảnh, xử lý ngôn ngữ tự nhiên, ra quyết định...

## LLM (Large Language Model)
- Mô hình ngôn ngữ lớn, được huấn luyện trên lượng dữ liệu văn bản khổng lồ.
- Có khả năng sinh văn bản, trả lời câu hỏi, tóm tắt, dịch thuật, lập trình...
- Ví dụ: GPT-3, GPT-4, Llama, Claude, Gemini...

## RAG (Retrieval-Augmented Generation)
- Kỹ thuật kết hợp giữa truy xuất thông tin (retrieval) và sinh văn bản (generation).
- Mô hình sẽ tìm kiếm thông tin liên quan từ kho dữ liệu, sau đó dùng LLM để tổng hợp và trả lời.
- Giúp tăng độ chính xác, cập nhật thông tin mới, giảm ảo giác (hallucination).

## Các khái niệm liên quan

### Prompt Engineering
- Nghệ thuật thiết kế câu lệnh đầu vào để LLM trả lời đúng ý muốn.

### Fine-tuning
- Tinh chỉnh lại mô hình AI trên tập dữ liệu nhỏ, chuyên biệt cho một nhiệm vụ cụ thể.

### Embedding
- Biểu diễn văn bản, hình ảnh, âm thanh... dưới dạng vector số để phục vụ tìm kiếm, phân loại, so sánh.

### Vector Database
- Cơ sở dữ liệu lưu trữ các vector embedding, hỗ trợ tìm kiếm tương tự (similarity search).
- Ví dụ: Pinecone, Milvus, Weaviate, Chroma...

### Hallucination
- Hiện tượng mô hình AI "bịa" ra thông tin không đúng sự thật.

### Zero-shot, Few-shot Learning
- Zero-shot: Mô hình thực hiện nhiệm vụ chưa từng được huấn luyện trực tiếp.
- Few-shot: Mô hình học từ một vài ví dụ mẫu.

### Agent
- Hệ thống AI có khả năng tự động thực hiện chuỗi hành động để đạt mục tiêu, có thể sử dụng LLM, công cụ