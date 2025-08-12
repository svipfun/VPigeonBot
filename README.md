# [Readme中文](https://github.com/svipfun/VPigeonBot/releases/tag/Readme中文)
# VPigeonBot

VPigeonBot is a Telegram bot designed to forward messages from users to a designated owner and allow the owner to reply to users by responding to forwarded messages. It includes features for blocking/unblocking users and managing message mappings via a SQLite database.

## Features
- Forwards text, photos, voice messages, videos, documents, and stickers from users to the bot owner.
- Allows the owner to reply to users by responding to forwarded messages.
- Supports commands for blocking (`/block`), unblocking (`/unblock`), and listing blocked users (`/listblocked`).
- Stores message mappings and blocked users in a SQLite database.
- Owner-only commands for administrative control.

## Requirements
- Python 3.7+
- `python-telegram-bot` library (`pip install python-telegram-bot`)
- SQLite3 (included with Python)

## Setup and Deployment

1. **Install Dependencies**:
   ```bash
   pip install python-telegram-bot
   ```

2. **Configure the Bot**:
   - Obtain a Telegram Bot Token from [BotFather](https://t.me/BotFather).
   - Get your Telegram User ID from [UserInfoBot](https://t.me/userinfobot).
   - Update the `TOKEN` and `OWNER_ID` variables in `VPigeonBot.py` with your Bot Token and User ID.

3. **Run the Bot**:
   - Execute the script locally for testing:
     ```bash
     python VPigeonBot.py
     ```
   - The bot uses polling by default (`application.run_polling()`). For production, consider switching to a webhook for better performance (modify the `main()` function accordingly).

4. **Database**:
   - A SQLite database (`VPigeonBot.db`) is automatically created in the same directory as the script to store message mappings and blocked user IDs.

## Usage

### Commands
- `/start`: Displays a welcome message. For the owner, it includes admin command instructions.
- `/help`: Shows help information, similar to `/start`.
- `/block <user_id>`: (Owner-only) Blocks a user by their Telegram User ID.
- `/unblock <user_id>`: (Owner-only) Unblocks a user.
- `/listblocked`: (Owner-only) Lists all blocked user IDs.

### Message Handling
- **Users**: Any message (text, photo, voice, video, document, sticker) sent to the bot is forwarded to the owner with user details (username, ID, first name).
- **Owner**: Reply to a forwarded message to send a response back to the original user. Supported message types include text, photos, voice, videos, documents, and stickers.
- **Blocked Users**: Messages from blocked users are ignored.

## Database Structure
- **mappings**: Stores message ID mappings between forwarded messages and original chat IDs.
  - Columns: `message_id` (primary key), `original_chat_id`.
- **blocked**: Stores IDs of blocked users.
  - Columns: `user_id` (primary key).

## Logging
- The bot uses Python's `logging` module to log events and errors at the INFO level. Logs include timestamps, module names, and messages for debugging.

## Deployment Notes
- For local testing, polling is sufficient. For production, configure a webhook with a public HTTPS URL for better scalability.
- Ensure the `VPigeonBot.db` file is in a persistent storage location if deploying on a server.
- Secure the `TOKEN` and `OWNER_ID` values, as they are sensitive.

## Limitations
- Only the owner can use admin commands (`/block`, `/unblock`, `/listblocked`).
- Non-owner users receive a "You not admin!" message if they attempt to use restricted commands.
- Additional message types (e.g., audio, location) can be added by extending the `message_handler` function.

## Contributing
Feel free to fork this repository, submit issues, or create pull requests for improvements or additional features.

## License
This project is licensed under the GPL License. See the [LICENSE](LICENSE) file for details.
