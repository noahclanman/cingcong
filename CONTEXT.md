# Telegram CC Generator & BIN Checker Bot

## Overview
This Telegram bot provides a **credit card generator** and **BIN checker** functionality. Users must register before using commands. The bot can be used in private chat or group chat, and it has an anti-spam mechanism to prevent abuse.

## Token and ID
bot token "7898396898:AAGKFRa-jPLqCqGWQvkTOngVKv9nEL_ClMI"
myuserid "1758748981"

## Features
- User registration system
- **BIN Checker** (`/bin <6-8 digit BIN>`)
- **Credit Card Generator** (`/gen <bin_extrap>`)
- Supports multiple card brands: Visa, MasterCard, Amex, JCB, Discover
- Generates valid card numbers using the Luhn algorithm
- Auto-detects correct card length and CVV format based on brand
- Saves user BIN and extrap data secretly
- Works in private messages and group chats
- **Anti-spam mechanism** (bans users flooding commands every 1-10 seconds for 24 hours)
- **Help (`/help`) and Rules (`/rules`) commands**

## Application Flow

### 1. User Registration
- When a user starts the bot (`/start`), they receive a welcome message with available commands.
- Before using commands, they must register with `/register`.
- The bot saves the user ID in `users.txt`.

### 2. BIN Checker (`/bin <6-8 digit BIN>`)
- User enters a BIN (Bank Identification Number).
- The bot fetches information about the BIN:
  - Bank name
  - Card type (Credit/Debit)
  - Country
- Returns BIN details to the user.

### 3. Credit Card Generator (`/gen <bin_extrap>`)
- Users provide a BIN pattern (e.g., `424242xxxxxxxxxx|xx|xx|xxx`).
- The bot generates **10 valid credit card numbers** following the **Luhn algorithm**.
- Supports multiple brands and correct length rules:
  - Visa: 16 digits, CVV 3 digits
  - MasterCard: 16 digits, CVV 3 digits
  - Amex: 15 digits, CVV 4 digits
  - JCB: 16 digits, CVV 3 digits
  - Discover: 16 digits, CVV 3 digits
- Saves generated BIN and extrap in `bins.txt` and `extrap.txt`.
- Output format:
  ```
  Bin: <bin>
  Bank: <bank>
  Type: <type>
  Country: <country>

  cc|mm|yy|cvv
  cc|mm|yy|cvv
  cc|mm|yy|cvv
  cc|mm|yy|cvv
  cc|mm|yy|cvv
  cc|mm|yy|cvv
  cc|mm|yy|cvv
  cc|mm|yy|cvv
  cc|mm|yy|cvv
  cc|mm|yy|cvv

  User: <user_id>
  Owner: <owner_username>
  ```

### 4. Help and Rules Commands
- `/help`: Displays available commands and usage.
- `/rules`: Shows the bot usage rules.

### 5. Anti-Spam Mechanism
- If a user repeatedly sends commands **every 1-10 seconds**, they get banned for **24 hours**.
- The bot automatically blocks further requests from spamming users.

### 6. Group Chat Handling
- The bot works in **both private and group chats**.
- If a user requests `/bin` or `/gen` in a group, the bot **replies directly to their message** instead of sending a separate message.

## Files Used
- `users.txt` → Stores registered user IDs
- `bins.txt` → Stores checked BINs (secretly)
- `extrap.txt` → Stores generated BIN extrap patterns (secretly)

## Command List
| Command         | Description |
|----------------|-------------|
| `/start`       | Starts the bot and shows commands |
| `/register`    | Registers the user before using commands |
| `/bin <6-8 digit>` | Checks BIN details |
| `/gen <bin_extrap>` | Generates credit card numbers |
| `/help`        | Shows command usage |
| `/rules`       | Shows bot rules |

## Notes
- The bot should be hosted on a **secure server**.
- Ensure **no user data leakage**.
- Use a **secure anti-spam mechanism** to prevent bot abuse.

---

**Developer Notes:** Ensure smooth implementation by following the above structure. The bot logic should handle user input carefully, prevent unauthorized access, and implement anti-spam checks efficiently.