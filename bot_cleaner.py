#!/usr/bin/env python3
"""
Telegram Bot Cleaner
- Delete all bot chats + Block all bots
- Session saved (no re-login if stopped)
- QR login with auto-refresh + terminal QR (using segno)
"""

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.contacts import BlockRequest
from telethon.tl.types import User
from telethon.errors import FloodWaitError, SessionPasswordNeededError
import asyncio
import os
import sys

try:
    import segno
except ImportError:
    print("Installing segno...")
    os.system("pip install -q segno")
    import segno

# ============ CONFIG ============
API_ID = 12345678                  # ← put your real api_id
API_HASH = "your_api_hash_here"    # ← put your real api_hash
SESSION_NAME = "clean_bots"
# ================================


async def safe_block(client, entity):
    while True:
        try:
            await client(BlockRequest(entity))
            return True
        except FloodWaitError as e:
            wait = e.seconds + 5
            print(f"  ⏳ FloodWait {e.seconds}s → sleeping {wait}s...")
            await asyncio.sleep(wait)
        except Exception as e:
            print(f"  ✗ Block failed: {e}")
            return False


def ask_float(prompt, default):
    raw = input(prompt).strip()
    if raw == "":
        return default
    try:
        val = float(raw)
        return val if val >= 0 else default
    except ValueError:
        return default


def show_qr(url: str):
    """Print QR in terminal + save qr.png"""
    qr = segno.make(url)

    print("\n======= SCAN THIS QR =======")
    qr.terminal(compact=True)
    print("============================\n")

    # Save image
    qr.save("qr.png", scale=8)
    print("Also saved as → qr.png  (open it and scan)")
    print("Telegram → Settings → Devices → Link Desktop Device\n")


async def get_client():
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.connect()

    if await client.is_user_authorized():
        print("✓ Already logged in (saved session)")
        return client

    print("""
==============================
   LOGIN METHOD
==============================
1. Session string (paste)
2. Bulk session strings (from file)
3. QR code login
4. Phone number + code
==============================
""")
    choice = input("Choose method [1-4] (default 4): ").strip() or "4"

    try:
        if choice == "1":
            print("\nPaste your session string (Ctrl+C to cancel):")
            s = input().strip()
            if not s:
                print("Cancelled")
                await client.disconnect()
                return None
            await client.disconnect()
            client = TelegramClient(StringSession(s), API_ID, API_HASH)
            await client.connect()

        elif choice == "2":
            path = input("Path to session file (one string per line): ").strip()
            if not path or not os.path.isfile(path):
                print("File not found")
                await client.disconnect()
                return None
            with open(path, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
            if not lines:
                print("File empty")
                await client.disconnect()
                return None
            await client.disconnect()
            for i, s in enumerate(lines, 1):
                try:
                    client = TelegramClient(StringSession(s), API_ID, API_HASH)
                    await client.connect()
                    if await client.is_user_authorized():
                        print(f"✓ Using session #{i} from file")
                        break
                    await client.disconnect()
                except Exception as e:
                    print(f"  Session #{i} failed: {e}")
            else:
                print("No valid session in file")
                return None

        elif choice == "3":
            print("\nQR Login started. Press Ctrl+C to cancel.\n")
            while True:
                try:
                    qr_login = await client.qr_login()
                    show_qr(qr_login.url)

                    print("Waiting for scan... (auto-refresh if expired)")
                    await qr_login.wait(timeout=30)
                    print("✓ QR login successful")
                    break

                except asyncio.TimeoutError:
                    print("Token expired → generating new QR...\n")
                    continue

                except SessionPasswordNeededError:
                    pw = input("2FA password: ")
                    await client.sign_in(password=pw)
                    print("✓ Logged in with 2FA")
                    break

        else:  # 4 - phone
            await client.start()
            print("✓ Phone login successful")

    except (KeyboardInterrupt, asyncio.CancelledError):
        print("\nCancelled by user")
        try:
            await client.disconnect()
        except Exception:
            pass
        return None

    if not await client.is_user_authorized():
        print("Login failed")
        await client.disconnect()
        return None

    # Save string session backup
    try:
        string = StringSession.save(client.session)
        with open(f"{SESSION_NAME}.string", "w") as f:
            f.write(string)
        print(f"Session also saved as {SESSION_NAME}.string")
    except Exception:
        pass

    return client


async def main():
    client = None
    try:
        client = await get_client()
        if client is None:
            return

        me = await client.get_me()
        print(f"\nLogged in as: {me.first_name} (@{me.username or 'no_username'})\n")

        print("==============================")
        print("   DELAY SETTINGS")
        print("==============================")
        print("These delays reduce FloodWait errors.\n")

        delay_delete_to_block = ask_float(
            "Delay AFTER deleting a bot chat, BEFORE blocking it (seconds) [default 1.5]: ",
            1.5
        )
        delay_between_bots = ask_float(
            "Delay BETWEEN finishing one bot and starting the next (seconds) [default 2.0]: ",
            2.0
        )

        print(f"\nUsing:")
        print(f"  • Delete → Block delay : {delay_delete_to_block}s")
        print(f"  • Between bots delay   : {delay_between_bots}s\n")

        bots = []
        async for dialog in client.iter_dialogs():
            entity = dialog.entity
            if isinstance(entity, User) and entity.bot:
                bots.append(dialog)

        print(f"Found {len(bots)} bot chats\n")
        if not bots:
            return

        for i, dialog in enumerate(bots, 1):
            name = dialog.name or "Unknown"
            uid = dialog.entity.id
            print(f"[{i}/{len(bots)}] {name} ({uid})")

            try:
                await client.delete_dialog(dialog.entity)
                print("  ✓ Chat deleted")
            except Exception as e:
                print(f"  ✗ Delete failed: {e}")

            if delay_delete_to_block > 0:
                await asyncio.sleep(delay_delete_to_block)

            if await safe_block(client, dialog.entity):
                print("  ✓ Blocked")

            if i < len(bots) and delay_between_bots > 0:
                await asyncio.sleep(delay_between_bots)
            print()

        print("Done.")

    except (KeyboardInterrupt, asyncio.CancelledError):
        print("\nStopped by user. Session is saved — just run again, no re-login needed.")
    finally:
        if client:
            try:
                await client.disconnect()
            except Exception:
                pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped.")
        sys.exit(0)
