import discord
from discord.ext import commands
import aiohttp
import asyncio
from datetime import datetime

# ============================================================================
# CẤU HÌNH - API KEYS & TOKEN
# ============================================================================
DISCORD_TOKEN = "YOUR_DISCORD_BOT_TOKEN_HERE"
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"

# ============================================================================
# THIẾT LẬP BOT
# ============================================================================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# Load system prompt
try:
    with open('prompt.txt', 'r', encoding='utf-8') as f:
        SYSTEM_PROMPT = f.read().strip()
except FileNotFoundError:
    SYSTEM_PROMPT = "Bạn là trợ lý AI thân thiện."

# Lưu trữ lịch sử hội thoại
user_histories = {}

# Gemini API endpoint - sử dụng Gemini 2.0 Flash
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

# ============================================================================
# HÀM GỌI GEMINI API
# ============================================================================
async def get_gemini_response(messages):
    """Gọi Gemini API"""
    try:
        # Chuyển đổi format messages sang Gemini format
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 1024,
            }
        }
        
        start_time = asyncio.get_event_loop().time()
        async with aiohttp.ClientSession() as session:
            async with session.post(GEMINI_API_URL, json=payload) as resp:
                latency = round((asyncio.get_event_loop().time() - start_time) * 1000, 2)
                
                if resp.status == 200:
                    data = await resp.json()
                    if 'candidates' in data and len(data['candidates']) > 0:
                        content = data['candidates'][0]['content']['parts'][0]['text']
                        return content, latency
                    return None, "❌ API không trả về nội dung"
                else:
                    error_text = await resp.text()
                    return None, f"❌ Lỗi API {resp.status}: {error_text[:100]}"
    except Exception as e:
        return None, f"❌ Lỗi: {str(e)}"

# ============================================================================
# HÀM LẤY CONTEXT DISCORD
# ============================================================================
def get_discord_context(message):
    """Lấy thông tin context từ Discord"""
    context = []
    if message.guild:
        context.append(f"Server: {message.guild.name}")
        context.append(f"Số thành viên: {message.guild.member_count}")
        context.append(f"Người hỏi: {message.author.display_name}")
    return "\n".join(context)

# ============================================================================
# HÀM XỬ LÝ TRẢ LỜI
# ============================================================================
async def handle_question(message, question):
    """Xử lý câu hỏi và trả lời"""
    async with message.channel.typing():
        # Chuẩn bị messages
        messages = []
        
        # Thêm system prompt với context
        discord_context = get_discord_context(message)
        full_prompt = f"{SYSTEM_PROMPT}\n\nTHÔNG TIN:\n{discord_context}"
        messages.append({"role": "system", "content": full_prompt})
        
        # Thêm lịch sử hội thoại (3 tin nhắn gần nhất)
        user_id = message.author.id
        if user_id in user_histories:
            for msg in user_histories[user_id][-3:]:
                messages.append(msg)
        
        # Thêm câu hỏi hiện tại
        messages.append({"role": "user", "content": question})
        
        # Gọi API
        response, info = await get_gemini_response(messages)
        
        if not response:
            await message.reply(f"⚠️ {info}")
            return
        
        # Chia response nếu quá dài
        if len(response) > 2000:
            chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
            for i, chunk in enumerate(chunks):
                if i == 0:
                    await message.reply(chunk)
                else:
                    await message.channel.send(chunk)
        else:
            # Tạo embed đẹp
            embed = discord.Embed(
                title="❓ Câu hỏi",
                description=question[:256],
                color=0x5865F2
            )
            embed.add_field(name="💬 Trả lời", value=response[:1024], inline=False)
            embed.set_footer(text=f"Gemini API • {info}ms • {message.author.display_name}")
            
            await message.reply(embed=embed)
        
        # Lưu lịch sử
        if user_id not in user_histories:
            user_histories[user_id] = []
        user_histories[user_id].append({"role": "user", "content": question[:500]})
        user_histories[user_id].append({"role": "assistant", "content": response[:500]})
        
        # Giữ tối đa 6 tin nhắn (3 cặp hỏi-đáp)
        if len(user_histories[user_id]) > 6:
            user_histories[user_id] = user_histories[user_id][-6:]

# ============================================================================
# LỆNH !ASK
# ============================================================================
@bot.command(name='ask')
async def ask_command(ctx, *, question: str = None):
    """
    Hỏi bot câu hỏi
    
    Cách dùng: !ask <câu hỏi>
    Ví dụ: !ask bạn khỏe không?
    """
    if not question:
        embed = discord.Embed(
            title="❓ Cách dùng lệnh !ask",
            description="Sử dụng: `!ask <câu hỏi>`\n\nVí dụ: `!ask bạn khỏe không?`",
            color=0x5865F2
        )
        await ctx.reply(embed=embed)
        return
    
    await handle_question(ctx.message, question)

# ============================================================================
# EVENTS
# ============================================================================
@bot.event
async def on_ready():
    """Khi bot sẵn sàng"""
    print(f'✅ {bot.user} đã kết nối!')
    print(f'🏠 Bot đang ở {len(bot.guilds)} servers')
    
    # Cập nhật status
    activity = discord.Activity(
        type=discord.ActivityType.listening,
        name="!ask | @mention | reply"
    )
    await bot.change_presence(activity=activity, status=discord.Status.online)

@bot.event
async def on_message(message):
    """Xử lý tin nhắn"""
    # Bỏ qua tin nhắn của bot
    if message.author == bot.user:
        return
    
    # 1. Kiểm tra tag bot (@mention)
    if bot.user in message.mentions:
        question = message.content.replace(f'<@{bot.user.id}>', '').replace(f'<@!{bot.user.id}>', '').strip()
        if question:
            await handle_question(message, question)
        return
    
    # 2. Kiểm tra reply tin nhắn bot
    if message.reference and message.reference.message_id:
        try:
            replied_msg = await message.channel.fetch_message(message.reference.message_id)
            # Nếu reply tin nhắn của bot
            if replied_msg.author == bot.user:
                question = message.content.strip()
                if question:
                    await handle_question(message, question)
                return
        except:
            pass
    
    # 3. Xử lý lệnh !ask
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    """Xử lý lỗi lệnh"""
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply("❌ Thiếu tham số! Dùng: `!ask <câu hỏi>`")
    elif isinstance(error, commands.CommandNotFound):
        pass  # Bỏ qua lệnh không tồn tại
    else:
        print(f"[Error] {error}")

# ============================================================================
# CHẠY BOT
# ============================================================================
if __name__ == "__main__":
    print("🚀 Đang khởi động bot...")
    bot.run(DISCORD_TOKEN)
