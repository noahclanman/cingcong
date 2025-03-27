import os
import logging
import time
from telegram import Update, ParseMode
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
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot Token and Configuration
TOKEN = "7281838363:AAGUYXXpusQJbHbCkP8-VXXDiv-Jdv3VzaI"
OWNER_ID = "1758748981"

# Anti-spam configuration
RATE_LIMIT = 10  # seconds
user_last_command = {}

def check_spam(user_id: str) -> bool:
    """Check if user is spamming commands"""
    current_time = time.time()
    if user_id in user_last_command:
        time_diff = current_time - user_last_command[user_id]
        if time_diff < RATE_LIMIT:
            return True
    user_last_command[user_id] = current_time
    return False

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
        "│ • /register - Register to use the bot",
        "│ • /bin <6-8 digit> - Check BIN details",
        "│ • /gen <BIN> - Generate cards with BIN",
        "│ • /gen <extrap> - Generate with full format",
        "│ • /date <BIN/CC> - Generate only date and CVV",
        "│ • /rules - Show bot rules",
        "│ • /help - Show this help message",
        separator,
        "│ 💡 EXAMPLES:",
        "│ • BIN check: /bin 424242",
        "│ • Simple gen: /gen 424242",
        "│ • With x: /gen 424242x",
        "│ • Full format: /gen 424242xxxxxxxxxx|xx|xx|xxx",
        "│ • Date only: /date 424242",
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
    if check_spam(user_id):
        update.message.reply_text(
            "\n".join([
                "━━━━━━━━━━━━━━━━",
                "│ ⚠️ SPAM DETECTED",
                "│ • Wait 10 seconds between commands",
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
    if check_spam(user_id):
        update.message.reply_text(
            "⚠️ Please wait a few seconds between commands to avoid spam"
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
    if check_spam(user_id):
        update.message.reply_text(
            "⚠️ Please wait a few seconds between commands to avoid spam"
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
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    try:
        if update and update.effective_message:
            update.effective_message.reply_text(
                "❌ An error occurred while processing your request"
            )
    except:
        pass  # Silently handle any errors in error handler

def main() -> None:
    """Start the bot."""
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    # Register command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("register", register))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("rules", rules))
    dispatcher.add_handler(CommandHandler("bin", bin_command))
    dispatcher.add_handler(CommandHandler("gen", gen_command))
    dispatcher.add_handler(CommandHandler("date", date_command))  # Add new date command

    # Register error handler
    dispatcher.add_error_handler(error_handler)

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
