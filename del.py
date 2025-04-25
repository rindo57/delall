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
    
    # Create confirmation buttons - IMPORTANT: Use reply_markup parameter correctly
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_delete_{message.chat.id}"),
                InlineKeyboardButton("❌ Cancel", callback_data="cancel_delete")
            ]
        ]
    )
    
    # Send message with buttons - make sure to use reply_markup=keyboard
    await message.reply_text(
        "⚠️ WARNING: This will delete ALL messages in this channel.\n"
        "Are you sure you want to proceed?",
        reply_markup=keyboard
    )

@app.on_callback_query(filters.regex(r"^confirm_delete_"))
async def confirm_deletion(client: Client, callback_query: CallbackQuery):
    chat_id = int(callback_query.data.split("_")[-1])
    
    # Acknowledge the button press first
    await callback_query.answer("Starting deletion...")
    
    # Edit the original message to show processing
    await callback_query.message.edit_text(
        "⏳ Starting deletion process... This may take a while.",
        reply_markup=None
    )
    
    try:
        count = await delete_all_messages(chat_id)
        await callback_query.message.edit_text(
            f"✅ Deletion completed! Removed {count} messages."
        )
    except Exception as e:
        await callback_query.message.edit_text(
            f"❌ Error during deletion: {str(e)}"
        )

@app.on_callback_query(filters.regex(r"^cancel_delete$"))
async def cancel_deletion(client: Client, callback_query: CallbackQuery):
    await callback_query.answer("Operation cancelled")
    await callback_query.message.edit_text(
        "❌ Deletion cancelled.",
        reply_markup=None
    )

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
