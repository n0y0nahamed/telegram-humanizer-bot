import os
import asyncio
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from groq import Groq

# -----------------------
# Environment
# -----------------------
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is missing")

# -----------------------
# Groq client
# -----------------------
client = Groq(api_key=GROQ_API_KEY)

# -----------------------
# Prompt loader
# -----------------------
def load_prompt():
    try:
        with open("WARP.md", "r", encoding="utf-8") as f:
            warp = f.read()
        with open("SKILL.md", "r", encoding="utf-8") as f:
            skill = f.read()
    except FileNotFoundError as e:
        raise RuntimeError(f"Prompt file missing: {e.filename}")

    rules = (
        "IMPORTANT OUTPUT RULES:\n"
        "- Return ONLY the final text.\n"
        "- Do NOT explain reasoning or changes.\n"
        "- Avoid hype, emojis, and marketing language.\n"
        "- Tone must be human, calm, and thoughtful.\n"
        "- Follow the voice and direction defined in SKILL.md.\n"
    )

    return f"{warp}\n\n{skill}\n\n{rules}"

SYSTEM_PROMPT = load_prompt()

# -----------------------
# Typing (1 second)
# -----------------------
async def human_typing(context, chat_id):
    await context.bot.send_chat_action(
        chat_id=chat_id,
        action=ChatAction.TYPING
    )
    await asyncio.sleep(1)

# -----------------------
# /start
# -----------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 Welcome\n\n"
        "This bot helps you rewrite text and draft calm, human replies.\n\n"
        "Choose a command below."
    )

    keyboard = [
        [KeyboardButton("/humanizer ✍️")],
        [KeyboardButton("/comment ✍️")],
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )

    await update.message.reply_text(text, reply_markup=reply_markup)

# -----------------------
# /humanizer
# -----------------------
async def humanizer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "ℹ️ Usage:\n/humanizer Your text here"
        )
        return

    await human_typing(context, update.effective_chat.id)

    user_text = " ".join(context.args)

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text},
            ],
            temperature=0.4,
            max_tokens=800,
        )
        output = response.choices[0].message.content
    except Exception:
        output = "⚠️ Something went wrong. Please try again."

    await update.message.reply_text(output[:4096])

# -----------------------
# /comment
# -----------------------
async def comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "ℹ️ Usage:\n/comment Paste a Twitter/X post"
        )
        return

    await human_typing(context, update.effective_chat.id)

    post_text = " ".join(context.args)

    prompt = (
        "Write a medium-length, thoughtful reply to the following post.\n"
        "Use zero or one crypto-specific term (optional).\n"
        "Sound human, calm, and grounded.\n\n"
        f"{post_text}"
    )

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.45,
            max_tokens=180,
        )
        output = response.choices[0].message.content
    except Exception:
        output = "⚠️ Could not generate a reply right now."

    await update.message.reply_text(output[:4096])

# -----------------------
# Main
# -----------------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("humanizer", humanizer))
    app.add_handler(CommandHandler("comment", comment))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()