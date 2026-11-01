# Telegram Bot Cleaner

Delete all bot chats and block every bot on your Telegram account automatically.

No more spam bots filling your chat list.

## Features

- Deletes every bot chat from your account
- Blocks all bots
- Automatic FloodWait handling (waits and continues)
- Custom delays to reduce rate limits
- Session is saved — no need to re-login if the script stops
- Multiple login methods:
  - Session string
  - Bulk session strings from file
  - QR code login (with terminal QR + auto-refresh)
  - Phone number + code

## Requirements

- Python 3.8+
- Telethon
- segno (for QR code in terminal)

```bash
pip install telethon segno
```

## Setup

1. Get `API_ID` and `API_HASH` from [my.telegram.org](https://my.telegram.org)
2. Open `bot_cleaner.py` and fill them in:

```python
API_ID = 12345678
API_HASH = "your_api_hash_here"
```

3. Run the script:

```bash
python bot_cleaner.py
```

## Usage

### First Run – Login

You will see this menu:

```
1. Session string (paste)
2. Bulk session strings (from file)
3. QR code login
4. Phone number + code
```

- **Option 3 (QR)** – Shows QR code directly in the terminal and also saves `qr.png`. Scan it with Telegram → Settings → Devices → Link Desktop Device. Token auto-refreshes if expired.
- **Option 4 (Phone)** – Easiest method. Enter phone number + login code.

After successful login the session is saved as `clean_bots.session`.  
Next time you run the script it will log in automatically (no need to login again).

### Delay Settings

After login the script asks:

```
Delay AFTER deleting a bot chat, BEFORE blocking it (seconds) [default 1.5]:
Delay BETWEEN finishing one bot and starting the next (seconds) [default 2.0]:
```

Just press Enter to use the defaults.

### What it does

1. Finds all bot chats
2. Deletes each chat
3. Blocks each bot
4. Automatically waits if Telegram rate-limits you

## Notes

- Deleting chats only removes them from **your** side
- Blocking prevents the bot from messaging you again
- Use reasonable delays (1.5–3 seconds) to avoid long FloodWaits
- Do not share your session file (`clean_bots.session`) or `.string` file with anyone
- Press `Ctrl+C` anytime to stop safely — session remains saved

## File Structure

```
telegram-bot-cleaner/
├── bot_cleaner.py
├── README.md
├── requirements.txt
└── .gitignore
```

## requirements.txt

```
telethon>=1.34.0
segno>=1.6.0
```

## .gitignore

```
*.session
*.session-journal
*.string
qr.png
__pycache__/
*.py[cod]
.env
.venv/
venv/
.idea/
.vscode/
```

## Support the Project

If this tool saved you time, you can support development:

**Bitcoin (BTC)**  
`bc1qexamplewalletaddressreplace`

**Ethereum (ETH)**  
`0xExampleEthereumWalletAddressReplace`

**USDT (TRC20)**  
`TExampleTronWalletAddressReplace`

**Solana (SOL)**  
`ExampleSolanaWalletAddressReplace`

Thank you.

## Disclaimer

This script is for personal account management only.  
Use responsibly and follow Telegram’s Terms of Service.
