#!/usr/bin/env python3
import os
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

print("🚀 INICIANDO BOT AUKAN...")

# VERIFICACIÓN SEGURA DE VARIABLES
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')

print(f"✅ Telegram Token: {'✅' if TELEGRAM_TOKEN else '❌'}")
print(f"✅ DeepSeek API Key: {'✅' if DEEPSEEK_API_KEY else '❌'}")

if not TELEGRAM_TOKEN:
    print("❌ ERROR: TELEGRAM_BOT_TOKEN no configurado")
    exit(1)
if not DEEPSEEK_API_KEY:
    print("❌ ERROR: DEEPSEEK_API_KEY no configurado")
    exit(1)

print("✅ TODAS LAS VARIABLES CONFIGURADAS CORRECTAMENTE")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    print(f"📩 Mensaje recibido: {user_message}")
    
    try:
        # Personalidad del Manager
        system_prompt = "Eres el mánager de AuKaN, rapero de Rubí. Tono callejero, directo y motivador. Usa jerga urbana."
        
        headers = {
            'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'deepseek-chat',
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_message}
            ]
        }
        
        response = requests.post('https://api.deepseek.com/chat/completions', json=data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            bot_response = result['choices'][0]['message']['content']
            print(f"🤖 Respondiendo: {bot_response[:50]}...")
            await update.message.reply_text(bot_response)
        else:
            error_msg = f"⚠️ Error API: {response.status_code}"
            print(error_msg)
            await update.message.reply_text("🎤 Ahora no caigo, jefe. ¿Repites?")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        await update.message.reply_text("💥 Fallo técnico, herma. Reintenta.")

def main():
    print("🔥 CONFIGURANDO BOT...")
    try:
        app = Application.builder().token(TELEGRAM_TOKEN).build()
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("✅ BOT LISTO - INICIANDO...")
        app.run_polling()
        
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        exit(1)

if __name__ == '__main__':
    main()
