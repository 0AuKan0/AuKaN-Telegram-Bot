#!/usr/bin/env python3
import os
import requests
import asyncio
import threading
from flask import Flask
from telegram import Bot
from telegram.error import TelegramError

print("🚀 INICIANDO BOT AUKAN - CON DEPURACIÓN...")

# Configuración
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
PORT = int(os.environ.get('PORT', 10000))

print(f"✅ Telegram Token: {'✅' if TELEGRAM_TOKEN else '❌'}")
print(f"✅ DeepSeek API Key: {'✅' if DEEPSEEK_API_KEY else '❌'}")

if not TELEGRAM_TOKEN or not DEEPSEEK_API_KEY:
    print("❌ ERROR: Faltan variables de entorno")
    exit(1)

# Inicializar bot y Flask
bot = Bot(token=TELEGRAM_TOKEN)
app = Flask(__name__)

print("✅ Bot y servidor inicializados")

@app.route('/')
def home():
    return "🤖 AuKaN Manager Bot - ACTIVO"

async def process_message(update):
    """Procesar un mensaje y responder"""
    try:
        user_message = update.message.text
        chat_id = update.message.chat_id
        
        print(f"📩 Mensaje recibido: '{user_message}'")
        
        # Personalidad del Manager - MÁS CORTA para probar
        system_prompt = "Eres el mánager de AuKaN, rapero de Rubí. Responde con tono callejero."
        
        headers = {
            'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'deepseek-chat',
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_message}
            ],
            'max_tokens': 500
        }
        
        print("🔌 Conectando con DeepSeek API...")
        
        response = requests.post(
            'https://api.deepseek.com/chat/completions', 
            json=data, 
            headers=headers, 
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📊 Response Text: {response.text[:200]}...")
        
        if response.status_code == 200:
            result = response.json()
            bot_response = result['choices'][0]['message']['content']
            print(f"✅ Respuesta obtenida: {bot_response[:50]}...")
            await bot.send_message(chat_id=chat_id, text=bot_response)
        else:
            print(f"❌ Error API: {response.status_code} - {response.text}")
            await bot.send_message(chat_id=chat_id, 
                                text=f"⚠️ Error técnico (Code: {response.status_code})")
            
    except Exception as e:
        print(f"❌ Error en process_message: {e}")
        await bot.send_message(chat_id=update.message.chat_id, 
                            text="💥 Fallo en el servidor.")

async def bot_loop():
    """Loop principal del bot"""
    print("🔥 BOT LISTO - Esperando mensajes...")
    
    # Obtener último ID para ignorar mensajes viejos
    updates = await bot.get_updates()
    last_update_id = updates[-1].update_id if updates else 0
    print(f"📝 Last Update ID: {last_update_id}")
    
    while True:
        try:
            updates = await bot.get_updates(offset=last_update_id + 1, timeout=10)
            
            for update in updates:
                if update.update_id > last_update_id:
                    last_update_id = update.update_id
                    print(f"🔄 Procesando update ID: {update.update_id}")
                    await process_message(update)
            
            await asyncio.sleep(0.5)
            
        except Exception as e:
            print(f"⚠️ Error en bot_loop: {e}")
            await asyncio.sleep(5)

def run_flask():
    """Ejecutar servidor Flask"""
    app.run(host='0.0.0.0', port=PORT, debug=False)

async def main():
    """Función principal"""
    # Iniciar servidor web en segundo plano
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print(f"🌐 Servidor web en puerto {PORT}")
    
    # Iniciar el bot
    await bot_loop()

if __name__ == '__main__':
    asyncio.run(main())
