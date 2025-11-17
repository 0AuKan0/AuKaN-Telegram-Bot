import os
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# Configuración
TELEGRAM_TOKEN = os.environ.get(8527474513:AAG8MaKqe6nJFbEqgU_3b3BJCATBIaMcUwo)
DEEPSEEK_API_KEY = os.environ.get(sk-769d1f91eed24eeb90b2e592af597c67)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    # Conectar con DeepSeek API
    headers = {
        'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'model': 'deepseek-chat',
        'messages': [
            {'role': 'system', 'content': 'Eres el mánager de AuKaN, un rapero underground de Rubí (Barcelona). Tu tono es callejero, directo y motivador. Hablas en español, usando jerga urbana.'},
            {'role': 'user', 'content': user_message}
        ]
    }
    
    try:
        response = requests.post('https://api.deepseek.com/chat/completions', json=data, headers=headers)
        result = response.json()
        bot_response = result['choices'][0]['message']['content']
        
        await update.message.reply_text(bot_response)
    except Exception as e:
        await update.message.reply_text("⚠️ Hermano, ahora no puedo pensar claro. Inténtalo otra vez.")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == '__main__':
    main()
