#!/bin/bash

# Test script cho AI Programming Assistant API v3.0.0
# Kiểm tra tất cả endpoints sau khi restructure

echo "🚀 Testing AI Programming Assistant API v3.0.0"
echo "================================================"

BASE_URL="http://localhost:8888/api"

echo ""
echo "💚 Testing Health API..."
echo "------------------------"

echo "1. Basic health check:"
curl -s "$BASE_URL/health" | jq '.'

echo ""
echo "2. Detailed health check:"
curl -s "$BASE_URL/health/detailed" | jq '.'

echo ""
echo "3. Version information:"
curl -s "$BASE_URL/health/version" | jq '.'

echo ""
echo "🌐 Testing Language API..."
echo "---------------------------"

echo "1. Get all supported languages:"
curl -s "$BASE_URL/languages" | jq '.'

echo ""
echo "2. Get Java language info:"
curl -s "$BASE_URL/languages/java" | jq '.'

echo ""
echo "3. Get Python language info:"
curl -s "$BASE_URL/languages/python" | jq '.'

echo ""
echo "4. Test invalid language:"
curl -s "$BASE_URL/languages/invalid" | jq '.'

echo ""
echo "🤖 Testing Chat API..."
echo "-----------------------"

echo "1. Normal chat:"
curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Xin chào! Bạn có thể giúp tôi không?",
    "is_quick_action": false
  }' | jq '.'

echo ""
echo "2. Quick action - Comment code:"
curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hãy thêm comment vào code này: def hello(): print(\"Hello World\")",
    "is_quick_action": true
  }' | jq '.'

echo ""
echo "3. Chat with history:"
curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Cảm ơn bạn!",
    "history": [
      {"type": "user", "content": "Xin chào"},
      {"type": "bot", "content": "Chào bạn! Tôi có thể giúp gì?"}
    ],
    "is_quick_action": false
  }' | jq '.'

echo ""
echo "🔍 Testing Error Cases..."
echo "--------------------------"

echo "1. Chat without message:"
curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{}' | jq '.'

echo ""
echo "2. Invalid endpoint:"
curl -s "$BASE_URL/invalid" | jq '.'

echo ""
echo "✅ Testing completed!"
echo "Check results above and verify all endpoints work correctly."
echo ""
echo "📊 Swagger Documentation: http://localhost:8888/swagger/"
