from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

# Replace these with your own values
API_ID = 3845818 # Your API ID
API_HASH = "95937bcf6bc0938f263fc7ad96959c6d" # Your API Hash
BOT_TOKEN ="7005003917:AAG1GwMAm4uFxMOzvesg1vTWRjVX0hHKStM" # Your bot token


app = Client(
    "message_deleter_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

async def delete_visible_messages(chat_id):
    print(f"Starting deletion in chat {chat_id}...")
    deleted_count = 0
    
    # Send a marker message
    marker = await app.send_message(chat_id, "🚀 Bot deletion marker - this will be deleted")
    
    while True:
        found_messages = 0
        async for message in app.get_chat_history(chat_id, limit=100):
            # Don't delete messages newer than our marker
            if message.id >= marker.id:
                continue
                
            try:
                await message.delete()
                deleted_count += 1
                found_messages += 1
                print(f"Deleted message {deleted_count}")
                await asyncio.sleep(0.5)  # To avoid flood limits
            except Exception as e:
                print(f"Couldn't delete message: {e}")
                continue
        
        # If no more messages found, break the loop
        if found_messages == 0:
            break
    
    # Delete our marker message
    try:
        await marker.delete()
    except:
        pass
    
    print(f"Finished! Deleted {deleted_count} messages.")
    return deleted_count

@app.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    await message.reply_text(
        "Hello! Add me to a channel where I'm admin with delete permissions, "
        "then send /deleteall in that channel to remove all visible messages."
    )

@app.on_message(filters.command("deleteall") & ~filters.private)
async def delete_all_in_channel(client: Client, message: Message):
    # Check if bot is admin with delete permissions
    chat_member = await app.get_chat_member(message.chat.id, "me")
    if not chat_member.privileges or not chat_member.privileges.can_delete_messages:
        await message.reply_text("❌ I need to be an admin with delete permissions in this channel!")
        return
    
    # Create confirmation buttons
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ Confirm", callback_data=f"delete_confirm_{message.chat.id}"),
                InlineKeyboardButton("❌ Cancel", callback_data="delete_cancel")
            ]
        ]
    )
    
    await message.reply_text(
        "⚠️ WARNING: This will delete all VISIBLE messages in this channel.\n"
        "Note: Bots can only delete messages they can see (usually recent ones).\n"
        "Are you sure you want to proceed?",
        reply_markup=keyboard
    )

@app.on_callback_query(filters.regex(r"^delete_confirm_"))
async def confirm_deletion(client, callback_query):
    chat_id = int(callback_query.data.split("_")[2])
    
    # Edit the original message to show processing
    await callback_query.message.edit_text(
        "⏳ Starting deletion process... This may take a while.",
        reply_markup=None
    )
    
    # Delete visible messages
    try:
        count = await delete_visible_messages(chat_id)
        # Update message with result
        await callback_query.message.edit_text(
            f"✅ Deletion completed! Removed {count} visible messages.\n"
            "Note: Bots can only delete messages they can see (usually recent ones).",
            reply_markup=None
        )
    except Exception as e:
        await callback_query.message.edit_text(
            f"❌ Error during deletion: {str(e)}",
            reply_markup=None
        )
    
    await callback_query.answer()

@app.on_callback_query(filters.regex(r"^delete_cancel$"))
async def cancel_deletion(client, callback_query):
    await callback_query.message.edit_text(
        "❌ Operation cancelled.",
        reply_markup=None
    )
    await callback_query.answer("Deletion cancelled")

if __name__ == "__main__":
    print("Starting bot...")
    app.run()
