import os
import asyncio
from dotenv import load_dotenv
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from telegram.constants import ChatAction
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)
from groq import Groq

# Load env
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

def load_prompt():
    with open("WARP.md", "r", encoding="utf-8") as f:
        warp = f.read()
    with open("SKILL.md", "r", encoding="utf-8") as f:
        skill = f.read()

    rules = """
IMPORTANT OUTPUT RULES:
- Return ONLY the final text.
- Do NOT explain reasoning or changes.
- Avoid hype, emojis, and marketing language.
- Tone must be human, calm, and thoughtful.
- Follow the voice and direction defined in SKILL.md.
"""

    return f"{warp}\n\n{skill}\n\n{rules}"

SYSTEM_PROMPT = load_prompt()

# --- Human-like delay (FAST) ---
async def human_delay(context, chat_id):
    # thinking (1 sec)
    await asyncio.sleep(1)

    # typing (1 sec)
    await context.bot.send_chat_action(
        chat_id=chat_id,
        action=ChatAction.TYPING
    )
    await asyncio.sleep(1)

# --- /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 Welcome!\n\n"
        "This bot helps you write and reply in a natural, human tone.\n\n"
        "Choose a command below 👇"
    )

    keyboard = [
        [KeyboardButton("/humanizer")],
        [KeyboardButton("/comment")],
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )

    await update.message.reply_text(text, reply_markup=reply_markup)

# --- /humanizer ---
async def humanizer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Paste your text after the command.\n\n"
            "Example:\n"
            "/humanizer This text sounds robotic."
        )
        return

    await human_delay(context, update.effective_chat.id)

    user_text = " ".join(context.args)

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ],
        temperature=0.4,
        max_tokens=1200,
    )

    await update.message.reply_text(
        completion.choices[0].message.content[:4096]
    )

# --- /comment ---
async def comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Paste a Twitter/X post after the command.\n\n"
            "Example:\n"
            "/comment Long-term adoption comes from products people return to."
        )
        return

    await human_delay(context, update.effective_chat.id)

    post_text = " ".join(context.args)

    comment_prompt = (
        "Write a medium-length, thoughtful reply to the following post.\n"
        "Understand what the post is about and respond insightfully.\n"
        "Use at most ONE crypto-specific term.\n"
        "Sound human, calm, and grounded.\n\n"
        f"{post_text}"
    )

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": comment_prompt},
        ],
        temperature=0.45,
        max_tokens=180,
    )

    await update.message.reply_text(
        completion.choices[0].message.content[:4096]
    )

# --- main ---
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("humanizer", humanizer))
    app.add_handler(CommandHandler("comment", comment))

    app.run_polling()

if __name__ == "__main__":
    main()
    )

    await update.message.reply_text(
        completion.choices[0].message.content[:4096]
    )

# /comment
async def comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Paste a Twitter/X post after the command.\n\n"
            "Example:\n"
            "/comment Adoption comes from products people return to."
        )
        return

    await human_delay(context, update.effective_chat.id)

    post_text = " ".join(context.args)

    comment_prompt = (
        "Write a medium-length, thoughtful reply to the following post.\n"
        "Use at most ONE crypto-specific term.\n"
        "Sound human, calm, and grounded.\n\n"
        f"{post_text}"
    )

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": comment_prompt},
        ],
        temperature=0.45,
        max_tokens=180,
    )

    await update.message.reply_text(
        completion.choices[0].message.content[:4096]
    )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("humanizer", humanizer))
    app.add_handler(CommandHandler("comment", comment))

    app.run_polling()

if __name__ == "__main__":
    main()