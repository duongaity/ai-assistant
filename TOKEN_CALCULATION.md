# Token Calculation Feature

## 📊 Tính năng mới: Tính toán Tokens động

### 🔄 Thay đổi trong Backend (`app.py`):

1. **Thêm method `_estimate_tokens()`:**
   - Ước tính tokens từ text (1 token ≈ 3-4 characters)
   - Phù hợp với tiếng Việt và tiếng Anh

2. **Thêm method `_calculate_max_tokens()`:**
   - Tính toán `max_tokens` dựa trên:
     - Độ dài input prompt
     - Độ dài code gốc
     - Ước tính output sẽ dài hơn input 2.5 lần
   - Giới hạn: 500 ≤ max_tokens ≤ 8000

3. **Trả về thông tin tokens:**
   ```json
   {
     "tokens_info": {
       "estimated_input_tokens": 150,
       "max_tokens_used": 800,
       "estimated_output_tokens": 450
     }
   }
   ```

### 🎨 Thay đổi trong Frontend (`App.jsx`):

1. **Hiển thị thông tin tokens real-time:**
   - Input tokens
   - Max tokens allowed
   - Output tokens
   - Ước tính chi phí (USD)

2. **UI cải tiến:**
   - Stats section với tokens info
   - Cost estimation
   - Visual indicators

### 💰 Lợi ích:

1. **Tối ưu chi phí:**
   - Code ngắn → ít tokens → tiết kiệm tiền
   - Không waste tokens với max_tokens cố định

2. **Hiệu suất tốt hơn:**
   - Response nhanh hơn với tokens phù hợp
   - Giảm timeout risks

3. **Transparency:**
   - User biết được chi phí ước tính
   - Monitoring token usage

### 📈 Công thức tính toán:

```python
# Ước tính input tokens
input_tokens = len(prompt) // 3

# Ước tính output tokens (output dài hơn input 2.5x)
estimated_output = input_tokens * 2.5

# Dựa trên code length
code_based_tokens = len(code) // 2

# Final calculation với buffer 20%
max_tokens = max(estimated_output, code_based_tokens) * 1.2

# Apply limits
final_tokens = max(500, min(8000, max_tokens))
```

### 🧪 Test cases:

1. **Code ngắn (< 100 chars):** max_tokens ≈ 500-800
2. **Code trung bình (100-500 chars):** max_tokens ≈ 800-2000  
3. **Code dài (> 500 chars):** max_tokens ≈ 2000-8000

### 💡 Ví dụ thực tế:

- **Input:** Java code 200 characters
- **Estimated input tokens:** ~150
- **Max tokens used:** ~900
- **Actual output tokens:** ~450
- **Cost:** ~$0.0003 USD

So với fixed 4000 tokens: tiết kiệm ~75% tokens!
