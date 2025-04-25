from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

# Replace these with your own values
API_ID = 3845818 # Your API ID
API_HASH = "95937bcf6bc0938f263fc7ad96959c6d" # Your API Hash
BOT_TOKEN ="7005003917:AAG1GwMAm4uFxMOzvesg1vTWRjVX0hHKStM" # Your bot token




app = Client("message_deleter_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def delete_previous_messages(chat_id, last_message_id):
    deleted_count = 0
    current_message_id = last_message_id - 1  # Start from the message before last
    
    while current_message_id > 0:
        try:
            # Try to get and delete each message sequentially
            message = await app.get_messages(chat_id, current_message_id)
            if message:
                await message.delete()
                deleted_count += 1
                print(f"Deleted message ID {current_message_id}")
                await asyncio.sleep(0.5)  # Rate limiting
            current_message_id -= 1
        except Exception as e:
            print(f"Error deleting message {current_message_id}: {e}")
            current_message_id -= 1  # Continue to next message even if error
    
    return deleted_count

@app.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    await message.reply_text(
        "Add me to a channel as admin with delete permissions, "
        "then send /deleteall in that channel to remove messages."
    )

@app.on_message(filters.command("deleteall") & ~filters.private)
async def trigger_deletion(client: Client, message: Message):
    # Check admin permissions
    try:
        chat_member = await app.get_chat_member(message.chat.id, "me")
        if not chat_member.privileges or not chat_member.privileges.can_delete_messages:
            await message.reply_text("❌ I need admin privileges with delete permission!")
            return
    except Exception as e:
        await message.reply_text(f"❌ Error checking permissions: {e}")
        return

    # Send a marker message to establish our reference point
    marker = await message.reply("🔹 Deletion marker - will be deleted last")
    
    # Create confirmation buttons
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_{message.chat.id}_{marker.id}"),
         InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
    ])
    
    await message.reply_text(
        f"⚠️ This will delete messages up to ID {marker.id-1}.\n"
        "Confirm deletion?",
        reply_markup=keyboard
    )

@app.on_callback_query(filters.regex(r"^confirm_(\d+)_(\d+)$"))
async def process_deletion(client, callback_query):
    chat_id = int(callback_query.matches[0].group(1))
    last_id = int(callback_query.matches[0].group(2))
    
    await callback_query.message.edit_text("⏳ Deleting messages...")
    
    try:
        count = await delete_previous_messages(chat_id, last_id)
        # Delete our marker message
        try:
            await app.delete_messages(chat_id, last_id)
        except:
            pass
            
        await callback_query.message.edit_text(
            f"✅ Deleted {count} messages (up to ID {last_id-1})"
        )
    except Exception as e:
        await callback_query.message.edit_text(f"❌ Error: {str(e)}")
    
    await callback_query.answer()

@app.on_callback_query(filters.regex("^cancel$"))
async def cancel_deletion(client, callback_query):
    await callback_query.message.edit_text("❌ Deletion cancelled")
    await callback_query.answer()

if __name__ == "__main__":
    print("Starting message deletion bot...")
    app.run()
