# Discord Bot - Gemini AI

Bot Discord đơn giản sử dụng Gemini API để trả lời câu hỏi.

## Cài đặt

1. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

2. Cấu hình bot:
   - Mở file `bot.py`
   - Thay `YOUR_DISCORD_BOT_TOKEN_HERE` bằng Discord bot token của bạn
   - Thay `YOUR_GEMINI_API_KEY_HERE` bằng Gemini API key của bạn

3. Chạy bot:
```bash
python bot.py
```

## Cách dùng

Bot chỉ trả lời khi:

1. **Dùng lệnh !ask**
   ```
   !ask bạn khỏe không?
   !ask giải thích về Python
   !ask viết code hello world
   ```

2. **Tag bot (@mention)**
   ```
   @BotName bạn là ai?
   @BotName giúp tôi với
   ```

3. **Reply tin nhắn của bot**
   - Reply bất kỳ tin nhắn nào của bot để tiếp tục hội thoại

## Tính năng

- ✅ Hỏi đáp với Gemini AI
- ✅ Lưu lịch sử hội thoại (3 cặp hỏi-đáp gần nhất)
- ✅ Hiển thị thời gian phản hồi API
- ✅ Tự động chia tin nhắn dài
- ✅ Hỗ trợ 3 cách tương tác: !ask, @mention, reply

## File cấu trúc

- `bot.py` - File chính chứa toàn bộ code
- `prompt.txt` - System prompt cho bot (có thể chỉnh sửa)
- `requirements.txt` - Dependencies

## Lấy API Keys

- **Discord Bot Token**: https://discord.com/developers/applications
- **Gemini API Key**: https://makersuite.google.com/app/apikey
