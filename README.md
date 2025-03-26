# 🎲 CC Generator & BIN Checker Bot

A powerful and flexible Telegram bot for generating valid card numbers and checking BIN information. Built with Python and modern best practices.

## ✨ Features

- 🔄 Generate valid card numbers with:
  - Support for all major card brands (Visa, Mastercard, AMEX, Discover, JCB)
  - Correct length per brand (15/16 digits)
  - Valid CVV length (3/4 digits)
  - Luhn algorithm validation
  - Custom date formats
  
- 🔍 BIN Checking capabilities:
  - Bank information
  - Card brand detection
  - Card type identification
  - Country information
  
- 🛡️ Built-in Security:
  - User registration system
  - Anti-spam protection
  - Rate limiting
  
- 💪 Robust Error Handling:
  - Multiple API retry attempts
  - Smart fallbacks for API failures
  - Comprehensive input validation

## 🚀 Supported Card Formats

```
1. Simple BIN:
   /gen 424242

2. BIN with pattern:
   /gen 424242xxxxxxxxxx

3. Partial number:
   /gen 424242567890xxxx

4. Full format with date/CVV:
   /gen 424242xxxxxxxxxx|mm|yy|cvv

5. Custom date format:
   /gen 424242xxxxxxxxxx|12|25|xxx

6. Date/CVV generation:
   /date 424242
```

## 🛠️ Technical Details

### Card Brand Specifications

```python
Card Patterns:
- Visa:
  • Length: 16
  • CVV: 3
  • Prefix: 4

- Mastercard:
  • Length: 16
  • CVV: 3
  • Prefix: 51-55

- American Express:
  • Length: 15
  • CVV: 4
  • Prefix: 34, 37

- Discover:
  • Length: 16
  • CVV: 3
  • Prefix: 6011, 65, 64, 60

- JCB:
  • Length: 16
  • CVV: 3
  • Prefix: 35
```

## 📦 Project Structure

```
├── bot.py              # Main Telegram bot implementation
├── card_generator.py   # Card generation logic
├── bin_checker.py      # BIN checking functionality
├── requirements.txt    # Project dependencies
├── users.txt          # Registered users storage
├── bins.txt           # Valid BINs storage
└── extrap.txt         # Extrapolation patterns storage
```

## 🔧 Dependencies

```
python-telegram-bot
requests
```

## 🚦 Error Handling

The bot includes comprehensive error handling:
- Input validation for all commands
- Multiple retries for API calls
- Fallback mechanisms for API failures
- Proper error messages for users

## 🔒 Security Features

1. User Registration:
   - Required before using commands
   - Stored in users.txt

2. Rate Limiting:
   - 10-second delay between commands
   - Prevents abuse and spam

3. Input Validation:
   - BIN number validation
   - Pattern format checking
   - Length verification

## 📝 Usage Examples

```python
# Generate cards with simple BIN
/gen 424242
> Generates 10 valid cards with prefix 424242

# Generate with specific pattern
/gen 424242xx7890xxxx
> Generates cards matching the pattern

# Generate with custom date
/gen 424242xxxxxxxxxx|12|25|xxx
> Generates cards with specified expiry date

# Check BIN information
/bin 424242
> Returns detailed BIN information
```

## ⚠️ Disclaimer

This tool is for educational purposes only. Users are responsible for ensuring compliance with applicable laws and regulations.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
