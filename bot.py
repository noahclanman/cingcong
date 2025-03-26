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
TOKEN = "7898396898:AAGKFRa-jPLqCqGWQvkTOngVKv9nEL_ClMI"
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
    welcome_message = (
        "👋 Welcome to CC Generator & BIN Checker Bot!\n\n"
        "🔑 Please register using /register before using the commands.\n\n"
        "Available commands:\n"
        "/bin <6-8 digit> - Check BIN details\n"
        "/gen <BIN> - Generate cards (e.g., /gen 424242)\n"
        "/gen <extrap> - Generate with full format (e.g., /gen 424242xxxxxxxxxx|xx|xx|xxx)\n"
        "/help - Show command usage\n"
        "/rules - Show bot rules"
    )
    update.message.reply_text(welcome_message)

def register(update: Update, context: CallbackContext) -> None:
    """Register a new user."""
    user_id = str(update.effective_user.id)
    users = load_users()
    
    if user_id in users:
        update.message.reply_text("You are already registered! 🎉")
        return
    
    save_user(user_id)
    update.message.reply_text(
        "✅ Registration successful!\n"
        "You can now use the bot commands:\n"
        "/bin <6-8 digit> - Check BIN details\n"
        "/gen <bin_extrap> - Generate credit cards"
    )

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    help_text = (
        "🔍 Available Commands:\n\n"
        "/register - Register to use the bot\n"
        "/bin <6-8 digit> - Check BIN details\n"
        "/gen <BIN> - Generate cards with BIN\n"
        "/gen <extrap> - Generate with full format\n"
        "/date <BIN/CC> - Generate only date and CVV\n"
        "/rules - Show bot rules\n"
        "/help - Show this help message\n\n"
        "Example usage:\n"
        "/bin 424242\n"
        "Simple generate:\n"
        "/gen 424242\n"
        "/gen 424242x\n"
        "Full format:\n"
        "/gen 424242xxxxxxxxxx|xx|xx|xxx\n"
        "Date/CVV only:\n"
        "/date 424242\n"
        "/date 4242424242424242"
    )
    update.message.reply_text(help_text)

def rules(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /rules is issued."""
    rules_text = (
        "📜 Bot Rules:\n\n"
        "1. Register before using commands\n"
        "2. Don't spam commands (1-10 sec delay required)\n"
        "3. Use commands properly with correct format\n"
        "4. Don't abuse the bot\n"
        "5. Respect other users\n\n"
        "⚠️ Breaking rules may result in a 24-hour ban"
    )
    update.message.reply_text(rules_text)

def date_command(update: Update, context: CallbackContext) -> None:
    """Handle the /date command"""
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
                "❌ Failed to generate date/CVV. Please check your input."
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
        output = [
            f"🎲 Generated Date/CVV:\n",
            f"Card: {cc}\n",
            f"Brand: {bin_info.get('brand', 'Unknown')}\n",
            "Results:"
        ]
        output.extend(cards)
        
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
            "❌ Please provide a BIN or extrap pattern\n"
            "Examples:\n"
            "Simple: /gen 424242\n"
            "With x: /gen 424242x\n"
            "Full: /gen 424242xxxxxxxxxx|xx|xx|xxx"
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
                "❌ Failed to generate cards. Please check your input format."
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
            "❌ Invalid BIN number or unable to fetch information"
        )

def error_handler(update: Update, context: CallbackContext) -> None:
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    if update.effective_message:
        update.effective_message.reply_text(
            "❌ An error occurred while processing your request"
        )

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
