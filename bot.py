import os
from telegram.ext import Updater, CommandHandler
from dotenv import load_dotenv
import openai

# Load .env file
load_dotenv()

# Get keys from environment
openai.api_key = os.getenv("OPENAI_API_KEY")
TOKEN = os.getenv("BOT_TOKEN")

if not openai.api_key:
    raise ValueError("OPENAI_API_KEY not found in environment")

if not TOKEN:
    raise ValueError("BOT_TOKEN not found in environment")

def load_prompt():
    with open("WARP.md", "r", encoding="utf-8") as f:
        warp = f.read()
    with open("SKILL.md", "r", encoding="utf-8") as f:
        skill = f.read()

    return f"{warp}\n\n{skill}"

SYSTEM_PROMPT = load_prompt()

def humanizer(update, context):
    if not context.args:
        update.message.reply_text(
            "Paste text like this:\n\n/humanizer your text here"
        )
        return

    text = " ".join(context.args)

    try:
        res = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ],
            temperature=0.7
        )

        reply = res.choices[0].message.content
        update.message.reply_text(reply[:4096])

    except Exception as e:
        update.message.reply_text(f"Error: {e}")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("humanizer", humanizer))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()