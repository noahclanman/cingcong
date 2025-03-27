import os
import logging
import time
from telegram import Update, ParseMode
from notes_manager import NotesManager
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
    MessageHandler,
    Filters
)
from bin_checker import BinChecker
from card_generator import CardGenerator

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.WARNING  # Change to WARNING to reduce log spam
)
logger = logging.getLogger(__name__)

# Command cooldown for groups
GROUP_RATE_LIMIT = 3  # seconds
group_last_command = {}

# Bot Token and Configuration
TOKEN = ""
OWNER_ID = ""

# Initialize NotesManager
notes_manager = NotesManager()

def check_bot_permissions(update: Update) -> bool:
    """Check if bot has necessary permissions in the chat"""
    try:
        # Skip checks for private chats
        if update.effective_chat.type == 'private':
            return True
            
        # Get bot member info
        bot_member = update.effective_chat.get_member(update.effective_message.bot.id)
        
        # Check bot's status
        if bot_member.status in ['administrator', 'member']:
            logger.warning(f"Bot status '{bot_member.status}' in chat {update.effective_chat.id}")
            return True
        
        # Bot lacks proper status
        logger.warning(f"Bot needs proper status in chat {update.effective_chat.id}")
        try:
            update.message.reply_text(
                "\n".join([
                    "━━━━━━━━━━━━━━━━",
                    "│ ⚠️ BOT STATUS ERROR",
                    "│ Bot needs to be added",
                    "│ as a member to this chat",
                    "━━━━━━━━━━━━━━━━"
                ])
            )
        except:
            pass
        return False
            
        return True
    except Exception as e:
        logger.error(f"Error checking permissions: {e}")
        return True

def is_admin_or_owner(update: Update, user_id: str) -> bool:
    """Check if user is bot owner or group admin"""
    # Bot owner always has access
    if str(user_id) == OWNER_ID:
        return True
        
    try:
        # Check if command is from a group
        if update.effective_chat.type != 'private':
            # Get user's status in the group
            member = update.effective_chat.get_member(user_id)
            # Return True if user is admin or creator
            return member.status in ['administrator', 'creator']
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        
    return False

# Anti-spam configuration
RATE_LIMIT = 10  # seconds
user_last_command = {}

def check_spam(update: Update) -> bool:
    """Check if command is being spammed"""
    try:
        current_time = time.time()
        user_id = str(update.effective_user.id)
        chat_id = str(update.effective_chat.id)
        
        # Different rate limits for private and group chats
        if update.effective_chat.type == 'private':
            if user_id in user_last_command:
                time_diff = current_time - user_last_command[user_id]
                if time_diff < RATE_LIMIT:
                    return True
            user_last_command[user_id] = current_time
        else:
            # For groups
            if chat_id in group_last_command:
                time_diff = current_time - group_last_command[chat_id]
                if time_diff < GROUP_RATE_LIMIT:
                    return True
            group_last_command[chat_id] = current_time
        
        return False
    except Exception as e:
        logger.error(f"Error in spam check: {e}")
        return False  # Allow message on error

def load_users():
    """Load registered users from users.txt"""
    if not os.path.exists('users.txt'):
        return set()
    with open('users.txt', 'r') as f:
        return set(line.strip() for line in f)

def save_user(user_id):
    """Save a new user to users.txt"""
    with open('users.txt', 'a') as f:
        f.write(f"{user_id}\n")

def check_user_registered(user_id: str) -> bool:
    """Check if user is registered"""
    return user_id in load_users()

def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    separator = "━━━━━━━━━━━━━━━━"
    welcome_message = "\n".join([
        separator,
        "│ 👋 WELCOME TO CC GENERATOR BOT",
        separator,
        "│ 🔑 Register first: /register",
        "│",
        "│ 📌 AVAILABLE COMMANDS:",
        "│ • /bin <6-8 digit> - Check BIN details",
        "│ • /gen <BIN> - Generate cards",
        "│ • /gen <extrap> - Generate with full format",
        "│ • /help - Show command usage",
        "│ • /rules - Show bot rules",
        "│",
        "│ 📝 NOTE COMMANDS:",
        "│ • /notes - List all notes",
        "│ • /get <title> - Get note content",
        separator
    ])
    update.message.reply_text(welcome_message)

def register(update: Update, context: CallbackContext) -> None:
    """Register a new user."""
    user_id = str(update.effective_user.id)
    users = load_users()
    
    separator = "━━━━━━━━━━━━━━━━"
    
    if user_id in users:
        message = "\n".join([
            separator,
            "│ 🎉 ALREADY REGISTERED",
            separator
        ])
        update.message.reply_text(message)
        return
    
    save_user(user_id)
    message = "\n".join([
        separator,
        "│ ✅ REGISTRATION SUCCESSFUL",
        separator,
        "│ 📌 AVAILABLE COMMANDS:",
        "│ • /bin <6-8 digit> - Check BIN details",
        "│ • /gen <bin_extrap> - Generate credit cards",
        separator
    ])
    update.message.reply_text(message)

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    separator = "━━━━━━━━━━━━━━━━"
    help_text = "\n".join([
        separator,
        "│ 🔍 COMMAND GUIDE",
        separator,
        "│ 📌 BASIC COMMANDS:",
        "│ • /start - Start bot & see welcome message",
        "│ • /register - Register to use the bot",
        "│ • /help - Show this help message",
        "│ • /rules - Show bot usage rules",
        separator,
        "│ 💳 CARD COMMANDS:",
        "│ • /bin <6-8 digit> - Check BIN details",
        "│ • /gen <BIN> - Generate cards with BIN",
        "│ • /gen <extrap> - Generate with pattern",
        "│ • /date <BIN/CC> - Generate date and CVV",
        separator,
        "│ 📝 NOTE COMMANDS:",
        "│ • /notes - List all saved notes (All users)",
        "│ • /save <title> <content> - Save note (Group admins & owner)",
        "│ • /remove <title> - Remove note (Group admins & owner)",
        "│ • /get <title> - Get a specific note (All users)",
        separator,
        "│ 💡 EXAMPLES:",
        "│ • Check BIN: /bin 424242",
        "│ • Simple gen: /gen 424242",
        "│ • With pattern: /gen 424242x",
        "│ • Full format: /gen 424242xxxxxxxxxx|xx|xx|xxx",
        "│ • Date only: /date 424242",
        separator,
        "│ ⚡ RATE LIMITS:",
        "│ • Private chat: 10 seconds",
        "│ • Group chat: 3 seconds",
        separator,
        "│ 👥 GROUP USAGE:",
        "│ • Add bot to group",
        "│ • No special permissions needed",
        "│ • Commands work same as private",
        separator
    ])
    update.message.reply_text(help_text)

def rules(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /rules is issued."""
    separator = "━━━━━━━━━━━━━━━━"
    rules_text = "\n".join([
        separator,
        "│ 📜 BOT RULES",
        separator,
        "│ 1. Register before using commands",
        "│ 2. Don't spam commands (10 sec delay)",
        "│ 3. Use commands with correct format",
        "│ 4. Don't abuse the bot",
        "│ 5. Respect other users",
        separator,
        "│ ⚠️  Breaking rules = 24h ban",
        separator
    ])
    update.message.reply_text(rules_text)

def date_command(update: Update, context: CallbackContext) -> None:
    """Handle the /date command"""
    user_id = str(update.effective_user.id)
    
    # Check if user is registered
    if not check_user_registered(user_id):
        update.message.reply_text(
            "\n".join([
                "━━━━━━━━━━━━━━━━",
                "│ ❌ NOT REGISTERED",
                "│ • Use /register command first",
                "━━━━━━━━━━━━━━━━"
            ])
        )
        return
    
    # Check for spam
    if check_spam(update):
        update.message.reply_text(
            "\n".join([
                "━━━━━━━━━━━━━━━━",
                "│ ⚠️ SPAM DETECTED",
                f"│ • Wait {GROUP_RATE_LIMIT if update.effective_chat.type != 'private' else RATE_LIMIT} seconds",
                "━━━━━━━━━━━━━━━━"
            ])
        )
        return
    
    # Check if card number is provided
    if not context.args:
        update.message.reply_text(
            "❌ Please provide a BIN or card number\n"
            "Examples:\n"
            "/date 424242 (BIN)\n"
            "/date 4242424242424242 (Full card)"
        )
        return
    
    cc = context.args[0]
    
    # Initialize generators
    card_gen = CardGenerator()
    bin_checker = BinChecker()
    
    try:
        # Generate date/CVV
        cards = card_gen.generate_cards(cc, mode='datecvv')
        if not cards:
            update.message.reply_text(
                "\n".join([
                    "━━━━━━━━━━━━━━━━",
                    "│ ❌ GENERATION FAILED",
                    "│ • Please check your input format",
                    "━━━━━━━━━━━━━━━━"
                ])
            )
            return
            
        # Get BIN info
        bin_number = cc[:6]
        bin_info = bin_checker.check_bin(bin_number) or {
            'bin': bin_number,
            'brand': 'Unknown',
            'type': 'Unknown',
            'category': 'Unknown',
            'bank': 'Unknown',
            'country': 'Unknown'
        }
        
        # Format output
        separator = "━━━━━━━━━━━━━━━━"
        output = [
            separator,
            "│ 🎲 GENERATED DATE/CVV",
            separator,
            f"│ • CARD     : {cc}",
            f"│ • BRAND    : {bin_info.get('brand', 'Unknown')}",
            separator,
            "│ 📊 RESULTS:"
        ]
        
        # Add each date/cvv with proper formatting
        for i, card in enumerate(cards, 1):
            output.append(f"│ {i}. `{card}`")
        
        output.append(separator)
        
        # Send response
        update.message.reply_text(
            "\n".join(output),
            parse_mode=ParseMode.MARKDOWN
        )
        
    except Exception as e:
        logger.error(f"Error generating date/CVV: {e}")
        update.message.reply_text(
            "❌ Error generating date/CVV. Please check your input."
        )

def gen_command(update: Update, context: CallbackContext) -> None:
    """Handle the /gen command"""
    user_id = str(update.effective_user.id)
    
    # Check if user is registered
    if not check_user_registered(user_id):
        update.message.reply_text(
            "❌ You must register first using /register command"
        )
        return
    
    # Check for spam
    if check_spam(update):
        update.message.reply_text(
            "\n".join([
                "━━━━━━━━━━━━━━━━",
                "│ ⚠️ SPAM DETECTED",
                f"│ • Wait {GROUP_RATE_LIMIT if update.effective_chat.type != 'private' else RATE_LIMIT} seconds",
                "━━━━━━━━━━━━━━━━"
            ])
        )
        return
    
    # Check if extrap pattern is provided
    if not context.args:
        update.message.reply_text(
            "\n".join([
                "━━━━━━━━━━━━━━━━",
                "│ ❌ MISSING INPUT",
                "│ • Provide BIN or extrap pattern",
                "│",
                "│ 📝 EXAMPLES:",
                "│ • Simple: /gen 424242",
                "│ • With x: /gen 424242x",
                "│ • Full: /gen 424242xxxxxxxxxx|xx|xx|xxx",
                "━━━━━━━━━━━━━━━━"
            ])
        )
        return
    
    extrap = context.args[0]
    
    # Initialize generators
    card_gen = CardGenerator()
    bin_checker = BinChecker()
    
    try:
        # Generate cards first
        cards = card_gen.generate_cards(extrap)
        if not cards:
            update.message.reply_text(
                "\n".join([
                    "━━━━━━━━━━━━━━━━",
                    "│ ❌ GENERATION FAILED",
                    "│ • Check your input format",
                    "━━━━━━━━━━━━━━━━"
                ])
            )
            return
            
        # Get BIN info after successful generation
        bin_number = extrap[:6]
        
        # Try multiple times to get BIN info
        max_retries = 3
        bin_info = None
        
        for _ in range(max_retries):
            bin_info = bin_checker.check_bin(bin_number)
            if bin_info:
                break
            time.sleep(1)  # Wait 1 second between retries
            
        # Use fallback only if all retries failed
        if not bin_info:
            brand = card_gen.detect_brand(bin_number)
            bin_info = {
                'bin': bin_number,
                'brand': brand.title(),
                'type': 'Credit',  # Default assumption
                'category': 'Unknown',
                'bank': 'Unknown',
                'country': 'Unknown'
            }
        
        # Save valid extrap and BIN
        card_gen.save_extrap(extrap)
        bin_checker.save_bin(bin_number)
        
        # Format output
        user_info = {
            'user_id': user_id,
            'username': update.effective_user.username or 'Unknown'
        }
        
        output = card_gen.format_output(cards, bin_info, user_info)
        
        # Send response
        update.message.reply_text(
            output,
            parse_mode=ParseMode.MARKDOWN
        )
        
    except Exception as e:
        logger.error(f"Error generating cards: {e}")
        update.message.reply_text(
            "❌ Error generating cards. Please check your input format."
        )

def bin_command(update: Update, context: CallbackContext) -> None:
    """Handle the /bin command"""
    user_id = str(update.effective_user.id)
    
    # Check if user is registered
    if not check_user_registered(user_id):
        update.message.reply_text(
            "❌ You must register first using /register command"
        )
        return
    
    # Check for spam
    if check_spam(update):
        update.message.reply_text(
            "\n".join([
                "━━━━━━━━━━━━━━━━",
                "│ ⚠️ SPAM DETECTED",
                f"│ • Wait {GROUP_RATE_LIMIT if update.effective_chat.type != 'private' else RATE_LIMIT} seconds",
                "━━━━━━━━━━━━━━━━"
            ])
        )
        return
    
    # Check if BIN number is provided
    if not context.args:
        update.message.reply_text(
            "❌ Please provide a BIN number\n"
            "Example: /bin 424242"
        )
        return
    
    bin_number = context.args[0]
    
    # Initialize BIN checker and get information
    checker = BinChecker()
    bin_info = checker.check_bin(bin_number)
    
    # Send response
    if bin_info:
        checker.save_bin(bin_number)  # Save valid BIN
        update.message.reply_text(
            checker.format_bin_info(bin_info),
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        update.message.reply_text(
            "\n".join([
                "━━━━━━━━━━━━━━━━",
                "│ ❌ INVALID BIN",
                "│ • Unable to fetch information",
                "━━━━━━━━━━━━━━━━"
            ])
        )

def error_handler(update: Update, context: CallbackContext) -> None:
    """Log Errors caused by Updates."""
    try:
        # Log the error with full traceback
        logger.error("Exception while handling an update:", exc_info=context.error)
        
        # Log detailed update information
        if update:
            logger.error(
                f"Update info - "
                f"Chat: {update.effective_chat.id if update.effective_chat else 'Unknown'} "
                f"({update.effective_chat.type if update.effective_chat else 'Unknown'}), "
                f"User: {update.effective_user.id if update.effective_user else 'Unknown'}, "
                f"Message: {update.effective_message.text if update.effective_message else 'None'}"
            )
        
        # Notify user about the error
        if update and update.effective_message:
            update.message.reply_text(
                "\n".join([
                    "━━━━━━━━━━━━━━━━",
                    "│ ❌ BOT ERROR",
                    "│ Command processing failed",
                    "│ Error has been logged",
                    "━━━━━━━━━━━━━━━━"
                ])
            )
    except Exception as e:
        logger.error(f"Error in error handler: {e}")

def notes_command(update: Update, context: CallbackContext) -> None:
    """Handle the /notes command - List all notes"""
    separator = "━━━━━━━━━━━━━━━━"
    notes = notes_manager.list_notes()
    
    if not notes:
        message = "\n".join([
            separator,
            "│ 📝 NOTES LIST",
            separator,
            "│ No notes found",
            separator
        ])
    else:
        message = "\n".join([
            separator,
            "│ 📝 NOTES LIST",
            separator,
            *[f"│ • {title}" for title in notes],
            separator
        ])
    
    update.message.reply_text(message)

def save_note_command(update: Update, context: CallbackContext) -> None:
    """Handle the /save command - Save a new note"""
    user_id = str(update.effective_user.id)
    
    if not is_admin_or_owner(update, user_id):
        update.message.reply_text(
            "\n".join([
                "━━━━━━━━━━━━━━━━",
                "│ ❌ ACCESS DENIED",
                "│ Only group admins and bot owner",
                "│ can save notes in groups",
                "━━━━━━━━━━━━━━━━"
            ])
        )
        return
    
    if not context.args or len(context.args) < 2:
        update.message.reply_text(
            "\n".join([
                "━━━━━━━━━━━━━━━━",
                "│ ❌ INVALID FORMAT",
                "│ Use: /save <title> <content>",
                "━━━━━━━━━━━━━━━━"
            ])
        )
        return
    
    title = context.args[0]
    content = " ".join(context.args[1:])
    
    if notes_manager.save_note(title, content):
        update.message.reply_text(
            "\n".join([
                "━━━━━━━━━━━━━━━━",
                "│ ✅ NOTE SAVED",
                f"│ Title: {title}",
                "━━━━━━━━━━━━━━━━"
            ])
        )
    else:
        update.message.reply_text("❌ Failed to save note")

def remove_note_command(update: Update, context: CallbackContext) -> None:
    """Handle the /remove command - Remove a note"""
    user_id = str(update.effective_user.id)
    
    if not is_admin_or_owner(update, user_id):
        update.message.reply_text(
            "\n".join([
                "━━━━━━━━━━━━━━━━",
                "│ ❌ ACCESS DENIED",
                "│ Only group admins and bot owner",
                "│ can remove notes in groups",
                "━━━━━━━━━━━━━━━━"
            ])
        )
        return
    
    if not context.args:
        update.message.reply_text(
            "\n".join([
                "━━━━━━━━━━━━━━━━",
                "│ ❌ INVALID FORMAT",
                "│ Use: /remove <title>",
                "━━━━━━━━━━━━━━━━"
            ])
        )
        return
    
    title = context.args[0]
    
    if notes_manager.remove_note(title):
        update.message.reply_text(
            "\n".join([
                "━━━━━━━━━━━━━━━━",
                "│ ✅ NOTE REMOVED",
                f"│ Title: {title}",
                "━━━━━━━━━━━━━━━━"
            ])
        )
    else:
        update.message.reply_text(
            "\n".join([
                "━━━━━━━━━━━━━━━━",
                "│ ❌ NOTE NOT FOUND",
                f"│ Title: {title}",
                "━━━━━━━━━━━━━━━━"
            ])
        )

def get_note_command(update: Update, context: CallbackContext) -> None:
    """Handle the /get command - Get a specific note"""
    if not context.args:
        update.message.reply_text(
            "\n".join([
                "━━━━━━━━━━━━━━━━",
                "│ ❌ INVALID FORMAT",
                "│ Use: /get <title>",
                "━━━━━━━━━━━━━━━━"
            ])
        )
        return
    
    title = context.args[0]
    content = notes_manager.get_note(title)
    
    if content:
        update.message.reply_text(
            "\n".join([
                "━━━━━━━━━━━━━━━━",
                "│ 📝 NOTE CONTENT",
                f"│ Title: {title}",
                "━━━━━━━━━━━━━━━━",
                f"│ {content}",
                "━━━━━━━━━━━━━━━━"
            ])
        )
    else:
        update.message.reply_text(
            "\n".join([
                "━━━━━━━━━━━━━━━━",
                "│ ❌ NOTE NOT FOUND",
                f"│ Title: {title}",
                "━━━━━━━━━━━━━━━━"
            ])
        )

def wrap_command(func):
    """Wrapper to add permission check to all commands"""
    def wrapped(update: Update, context: CallbackContext):
        if not check_bot_permissions(update):
            return
        return func(update, context)
    return wrapped

def main() -> None:
    """Start the bot."""
    try:
        # Initialize bot with clean updates
        logger.warning("Starting bot...")
        updater = Updater(TOKEN, use_context=True)
        
        # Clean up any existing webhooks
        logger.warning("Cleaning up webhooks...")
        updater.bot.delete_webhook()
        
        dispatcher = updater.dispatcher
        
        # Log bot information
        bot_info = updater.bot.get_me()
        logger.warning(f"Bot Info - ID: {bot_info.id}, Name: {bot_info.first_name}, Username: {bot_info.username}")

        # Debug handler for all messages
        def debug_handler(update: Update, context: CallbackContext) -> None:
            """Debug handler to log all messages"""
            if update.message:
                logger.warning(
                    f"Message received - "
                    f"Chat: {update.effective_chat.id} ({update.effective_chat.type}), "
                    f"User: {update.effective_user.id}, "
                    f"Text: {update.message.text}"
                )

        # Register command handlers
        logger.warning("Registering command handlers...")
        handlers = {
            "start": wrap_command(start),
            "register": wrap_command(register),
            "help": wrap_command(help_command),
            "rules": wrap_command(rules),
            "bin": wrap_command(bin_command),
            "gen": wrap_command(gen_command),
            "date": wrap_command(date_command),
            "notes": wrap_command(notes_command),
            "save": wrap_command(save_note_command),
            "remove": wrap_command(remove_note_command),
            "get": wrap_command(get_note_command)
        }

        # Add handlers with proper filters
        for command, callback in handlers.items():
            # Allow commands in both private chats and groups
            dispatcher.add_handler(CommandHandler(
                command, 
                callback,
                filters=Filters.command & (Filters.chat_type.private | Filters.chat_type.groups)
            ))

        # Add debug handler for all messages
        dispatcher.add_handler(MessageHandler(Filters.all, debug_handler))

        # Register error handler
        dispatcher.add_error_handler(error_handler)

        # Start the Bot
        logger.warning("Starting polling...")
        updater.start_polling(drop_pending_updates=True)
        logger.warning("Bot is running!")
        updater.idle()
    except Exception as e:
        logger.error(f"Critical error starting bot: {e}", exc_info=True)
        raise

if __name__ == '__main__':
    main()
