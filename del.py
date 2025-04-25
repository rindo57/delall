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

async def delete_recent_messages(chat_id):
    """
    Deletes recent messages that the bot can see (new messages since bot joined)
    """
    deleted_count = 0
    last_message_id = 25
    
    while True:
        # Get the most recent message in the channel
        try:
            messages = await app.get_messages(chat_id)
            if not messages:
                break
                
            message = messages[0] if isinstance(messages, list) else messages
            
            # Stop if we've reached a message we've already processed
            if message.id == last_message_id:
                break
                
            last_message_id = message.id
            
            # Delete the message
            try:
                await message.delete()
                deleted_count += 1
                print(f"Deleted message {deleted_count}")
                await asyncio.sleep(0.5)  # Rate limiting
            except Exception as e:
                print(f"Couldn't delete message {message.id}: {e}")
                continue
                
        except Exception as e:
            print(f"Error getting messages: {e}")
            break
    
    return deleted_count

@app.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    await message.reply_text(
        "Hello! Add me to a channel where I'm admin with delete permissions, "
        "then send /deleteall in that channel to remove recent messages."
    )

@app.on_message(filters.command("deleteall") & ~filters.private)
async def delete_in_channel(client: Client, message: Message):
    # Check if bot is admin with delete permissions
    try:
        chat_member = await app.get_chat_member(message.chat.id, "me")
        if not chat_member.privileges or not chat_member.privileges.can_delete_messages:
            await message.reply_text("❌ I need to be an admin with delete permissions in this channel!")
            return
    except Exception as e:
        await message.reply_text(f"❌ Error checking permissions: {e}")
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
        "⚠️ WARNING: This will delete RECENT messages in this channel.\n"
        "Note: Bots can only delete messages sent after they joined.\n"
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
    
    # Delete messages
    try:
        count = await delete_recent_messages(chat_id)
        # Update message with result
        await callback_query.message.edit_text(
            f"✅ Deletion completed! Removed {count} recent messages.\n"
            "Note: Bots can only delete messages sent after they joined.",
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
