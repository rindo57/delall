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
    # Check if user is admin with delete permissions
    try:
        me = await app.get_me()
        chat_member = await app.get_chat_member(message.chat.id, me.id)
        if not chat_member.privileges or not chat_member.privileges.can_delete_messages:
            await message.reply_text("❌ I need to be an admin with delete permissions!")
            return
    except Exception as e:
        await message.reply_text(f"❌ Error checking permissions: {e}")
        return
    
    # Confirmation buttons
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Confirm", callback_data=f"delete_confirm_{message.chat.id}"),
         InlineKeyboardButton("❌ Cancel", callback_data="delete_cancel")]
    ])
    
    await message.reply_text(
        "⚠️ WARNING: This will delete ALL messages in this channel.\n"
        "Are you sure you want to proceed?",
        reply_markup=keyboard
    )

@app.on_callback_query()
async def handle_callbacks(client, callback_query):
    data = callback_query.data
    
    if data.startswith("delete_confirm_"):
        chat_id = int(data.split("_")[2])
        await callback_query.answer("Starting deletion...")
        await callback_query.message.edit_text("⏳ Starting deletion process...", reply_markup=None)
        
        try:
            count = await delete_all_messages(chat_id)
            await callback_query.message.edit_text(f"✅ Deletion completed! Removed {count} messages.")
        except Exception as e:
            await callback_query.message.edit_text(f"❌ Error during deletion: {str(e)}")
    
    elif data == "delete_cancel":
        await callback_query.answer("Cancelled")
        await callback_query.message.edit_text("❌ Operation cancelled.", reply_markup=None)

if __name__ == "__main__":
    print("""
    =============================================
    FIRST RUN INSTRUCTIONS:
    1. Run this script once
    2. It will ask for your phone number
    3. You'll receive a login code via Telegram
    4. Enter that code when prompted
    5. After successful login, your session string will print
    6. Copy that string into the SESSION_STRING variable
    7. Run the script again
    =============================================
    """)
    app.run()
