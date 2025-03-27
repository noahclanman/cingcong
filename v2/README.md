# 🎲 CC Generator & BIN Checker Bot

A powerful and flexible Telegram bot for generating valid card numbers and checking BIN information. Built with Python and modern best practices.

## 🚀 Commands

### Basic Commands
- `/start` - Start bot & see welcome message
- `/register` - Register to use the bot
- `/help` - Show detailed command guide
- `/rules` - Show bot usage rules

### Card Commands
- `/bin <6-8 digit>` - Check BIN information
- `/gen <BIN>` - Generate cards from BIN
- `/gen <extrap>` - Generate with pattern
- `/date <BIN/CC>` - Generate date and CVV

### Note Commands
- `/notes` - List all saved notes (All users)
- `/save <title> <content>` - Save a note (Group admins & owner)
- `/remove <title>` - Remove note (Group admins & owner)
- `/get <title>` - Get a specific note (All users)

## 💡 Examples

```
BIN Check:
/bin 424242

Simple Generation:
/gen 424242

With Pattern:
/gen 424242x

Full Format:
/gen 424242xxxxxxxxxx|xx|xx|xxx

Date Only:
/date 424242
```

## 🔒 Group Usage

The bot works in both private chats and groups:
1. Add the bot to your group
2. No special permissions needed - works as regular member
3. Commands work the same as in private chat

## ⚠️ Rate Limits

- Private Chat: 10 seconds between commands
- Group Chat: 3 seconds between commands

## 🛡️ Security Features

1. User Registration:
   - Required before using commands
   - Stored securely

2. Rate Limiting:
   - Prevents spam and abuse
   - Different limits for private/group

3. Admin System:
   - Protected note management
   - Group admins and owner can save/remove notes
   - Regular users can only view notes

## 📝 Notes System

- Save important information as notes
- Quick access with /get command
- List all notes with /notes
- Admin-controlled note management
- All users can view notes

## ⚠️ Disclaimer

This tool is for educational purposes only. Users are responsible for ensuring compliance with applicable laws and regulations.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
