from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os
import django
from asgiref.sync import sync_to_async

# Set up the Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_task_project.settings")
django.setup()

from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token = context.args[0] if context.args else None

    if not token:
        await update.message.reply_text("Invalid login attempt! Missing token.")
        return

    # Fetch all sessions asynchronously
    all_sessions = await sync_to_async(lambda: list(Session.objects.all()))()

    for session in all_sessions:
        # Use sync_to_async to safely load session data
        session_store = await sync_to_async(SessionStore)(session_key=session.session_key)
        session_data = await sync_to_async(session_store.load)()

        if session_data.get('telegram_auth_token') == token:
            telegram_id = update.effective_chat.id
            username = update.effective_user.username or update.effective_user.first_name

            # Check if a user already exists for the username
            user = await sync_to_async(
                lambda: User.objects.filter(username=username).first()
            )()

            if not user:
                user = await sync_to_async(User.objects.create_user)(
                    username=username,
                    password=User.objects.make_random_password(),
                )
                print(f"New user registered: {user.username}")

            # Update user details
            user.first_name = username
            await sync_to_async(user.save)()
            print(f"User details updated: {user.username}, Telegram ID: {telegram_id}")

            # Update session data
            session_data['telegram_authenticated'] = True
            session_data['_auth_user_id'] = user.id

            # Save updated session data
            await sync_to_async(session_store.update)(session_data)
            await sync_to_async(session_store.save)()
            print(f"Session saved successfully for session key: {session.session_key}")

            # Notify the user and provide the web app link
            web_app_url = "http://127.0.0.1:8000/"
            await update.message.reply_text(
                f"Welcome, {username}! You are now authenticated. Go to: {web_app_url}"
            )
            return

    # If no session contains the token
    await update.message.reply_text("Authentication failed! Invalid token.")


def main():
    # Replace "YourBotToken" with the actual token from BotFather
    bot_token = "7874802406:AAH0qHJHmNirxrYegKNJyTLv6fMgWmlIAwU"

    # Create the application and add the /start handler
    application = Application.builder().token(bot_token).build()
    application.add_handler(CommandHandler("start", start))

    # Start the bot
    application.run_polling()


if __name__ == "__main__":
    main()
