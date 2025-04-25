from pyrogram import Client, filters
from pyrogram.types import Message
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
    
    # Confirm before proceeding
    confirmation = await message.reply_text(
        "⚠️ WARNING: This will delete ALL messages in this channel. "
        "Are you sure you want to proceed? Reply 'YES' to confirm.",
        reply_markup=None
    )
    
    # Wait for confirmation in the same chat
    try:
        response = await client.listen.Message(
            filters.text & filters.chat(message.chat.id) & filters.user(message.from_user.id),
            timeout=30
        )
        
        if response.text.upper() == "YES":
            processing_msg = await message.reply_text("⏳ Starting deletion process... This may take a while.")
            count = await delete_all_messages(message.chat.id)
            await processing_msg.edit_text(f"✅ Deletion completed! Removed {count} messages.")
        else:
            await message.reply_text("❌ Operation cancelled.")
            
    except asyncio.TimeoutError:
        await message.reply_text("⌛ Confirmation timed out. Operation cancelled.")

if __name__ == "__main__":
    print("Starting bot...")
    app.run()
