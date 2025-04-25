from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

# Replace these with your own values
API_ID = 3845818 # Your API ID
API_HASH = "95937bcf6bc0938f263fc7ad96959c6d" # Your API Hash
BOT_TOKEN ="7374311692:AAFJhri3iPUdTc5UPkqMVFIspVVee-VvDgM"  # Your bot token

app = Client(
    "message_deleter_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

async def delete_all_messages(chat_id):
    async with app:
        print(f"Starting deletion in chat {chat_id}...")
        
        # Get all messages from the channel
        messages = app.get_chat_history(chat_id)
        
        deleted_count = 0
        async for message in messages:
            try:
                await message.delete()
                deleted_count += 1
                print(f"Deleted message {deleted_count}")
                await asyncio.sleep(0.5)  # To avoid flood limits
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
        "⚠️ WARNING: This will delete ALL messages in this channel.\n"
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
    
    # Delete all messages
    count = await delete_all_messages(chat_id)
    
    # Update message with result
    await callback_query.message.edit_text(
        f"✅ Deletion completed! Removed {count} messages.",
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
