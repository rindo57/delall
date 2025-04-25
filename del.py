from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import asyncio

# Replace these with your own values
API_ID = 3845818 # Your API ID
API_HASH = "95937bcf6bc0938f263fc7ad96959c6d" # Your API Hash

# Session string will be generated on first run
SESSION_STRING = None  # Will be generated automatically

app = Client(
    "message_deleter_user",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import asyncio

# Replace these with your own values
API_ID = 3845818 # Your API ID
API_HASH = "95937bcf6bc0938f263fc7ad96959c6d" # Your API Hash

# Session string will be generated on first run
SESSION_STRING = None  # Will be generated automatically

app = Client(
    "message_deleter_user",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)
async def delete_all_messages(chat_id):
    print(f"Starting deletion in chat {chat_id}...")
    deleted_count = 0
    
    async for message in app.get_chat_history(chat_id):
        try:
            await message.delete()
            deleted_count += 1
            print(f"Deleted message {deleted_count}")
            await asyncio.sleep(0.5)  # Avoid flood limits
        except Exception as e:
            print(f"Couldn't delete message: {e}")
            continue
    
    print(f"Finished! Deleted {deleted_count} messages.")
    return deleted_count

@app.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    await message.reply_text(
        "Hello! Add me to a channel where I'm admin with delete permissions, "
        "then send /deleteall in that channel to remove all messages."
    )

@app.on_message(filters.command("deleteall") & ~filters.private)
async def delete_all_in_channel(client: Client, message: Message):
    # Check admin permissions
    try:
        me = await app.get_me()
        chat_member = await app.get_chat_member(message.chat.id, me.id)
        if not chat_member.privileges or not chat_member.privileges.can_delete_messages:
            await message.reply_text("❌ I need admin privileges with delete permission!")
            return
    except Exception as e:
        await message.reply_text(f"❌ Error checking permissions: {e}")
        return

    # Ask for confirmation
    confirm = await message.reply_text(
        "⚠️ WARNING: This will delete ALL messages in this channel.\n"
        "Reply with 'YES' to confirm deletion."
    )
    
    try:
        # Wait for "YES" response for 30 seconds
        response = await client.listen.Message(
            filters.text & filters.chat(message.chat.id) & filters.user(message.from_user.id),
            timeout=30
        )
        
        if response.text.upper() == "YES":
            processing = await message.reply_text("⏳ Starting deletion process...")
            count = await delete_all_messages(message.chat.id)
            await processing.edit_text(f"✅ Deletion completed! Removed {count} messages.")
        else:
            await message.reply_text("❌ Operation cancelled.")
            
    except asyncio.TimeoutError:
        await message.reply_text("⌛ Confirmation timed out. Operation cancelled.")

if __name__ == "__main__":
    print("""
    =============================================
    FIRST RUN INSTRUCTIONS:
    1. Run this script
    2. Enter your phone number (with country code)
    3. Enter the login code you receive
    4. After login, your session string will print
    5. Copy it into the SESSION_STRING variable
    6. Run the script again
    =============================================
    """)
    app.run()
