import os
import openai
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
openai.api_key = os.getenv("OPENAI_API_KEY")

def load_prompt():
    with open("WARP.md", "r", encoding="utf-8") as f:
        warp = f.read()
    with open("SKILL.md", "r", encoding="utf-8") as f:
        skill = f.read()
    return f"{warp}\n\n{skill}"

SYSTEM_PROMPT = load_prompt()

async def humanizer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Usage:\n/humanizer your text"
        )
        return

    user_text = " ".join(context.args)

    try:
        res = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text},
            ],
            temperature=0.4,
        )

        await update.message.reply_text(
            res.choices[0].message.content[:4096]
        )

    except Exception as e:
        await update.message.reply_text("❌ Error processing text")
        print(e)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("humanizer", humanizer))
    app.run_polling()

if __name__ == "__main__":
    main()