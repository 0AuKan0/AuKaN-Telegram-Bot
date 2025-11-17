#!/usr/bin/env python3
import os
import requests
import asyncio
import threading
from flask import Flask
from telegram import Bot
from telegram.error import TelegramError

print("🚀 INICIANDO BOT AUKAN - CON SERVIDOR WEB...")

# Configuración
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
PORT = int(os.environ.get('PORT', 10000))

print(f"✅ Telegram Token: {'✅' if TELEGRAM_TOKEN else '❌'}")
print(f"✅ DeepSeek API Key: {'✅' if DEEPSEEK_API_KEY else '❌'}")
print(f"✅ Puerto: {PORT}")

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

@app.route('/health')
def health():
    return "✅ OK"

async def get_last_update_id():
    """Obtener el ID del último update procesado"""
    try:
        updates = await bot.get_updates()
        if updates:
            return updates[-1].update_id
        return 0
    except Exception as e:
        print(f"❌ Error obteniendo updates: {e}")
        return 0

async def process_message(update):
    """Procesar un mensaje y responder"""
    try:
        user_message = update.message.text
        user_id = update.message.from_user.id
        chat_id = update.message.chat_id
        
        print(f"📩 Mensaje de {user_id}: {user_message}")
        
        # Personalidad del Manager
        system_prompt = """Eres el mánager de AuKaN, un rapero underground de Rubí (Barcelona). 
        Tu tono es callejero, directo y motivador. Hablas en español, usando jerga urbana.
        Eres práctico, leal y siempre buscas oportunidades para que AuKaN crezca.
        Responde como si fueras su mánager de verdad."""
        
        # Conectar con DeepSeek API
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
        
        response = requests.post('https://api.deepseek.com/chat/completions', 
                               json=data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            bot_response = result['choices'][0]['message']['content']
            print(f"🤖 Enviando respuesta...")
            await bot.send_message(chat_id=chat_id, text=bot_response)
        else:
            print(f"❌ Error API: {response.status_code}")
            await bot.send_message(chat_id=chat_id, 
                           text="🎤 Ahora no caigo, jefe. ¿Repites?")
            
    except Exception as e:
        print(f"❌ Error procesando mensaje: {e}")
        try:
            await bot.send_message(chat_id=update.message.chat_id, 
                           text="💥 Fallo técnico, herma. Reintenta.")
        except:
            pass

async def bot_loop():
    """Loop principal del bot"""
    print("🔥 INICIANDO LOOP DEL BOT...")
    last_update_id = await get_last_update_id()
    
    while True:
        try:
            # Obtener nuevos mensajes
            updates = await bot.get_updates(offset=last_update_id + 1, timeout=60)
            
            for update in updates:
                if update.update_id > last_update_id:
                    last_update_id = update.update_id
                    await process_message(update)
            
            await asyncio.sleep(1)
            
        except TelegramError as e:
            print(f"⚠️ Error de Telegram: {e}")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"❌ Error general: {e}")
            await asyncio.sleep(10)

def run_flask():
    """Ejecutar servidor Flask en un hilo separado"""
    print(f"🌐 Iniciando servidor web en puerto {PORT}...")
    app.run(host='0.0.0.0', port=PORT, debug=False)

async def main():
    """Función principal"""
    # Iniciar servidor web en segundo plano
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Iniciar el bot
    await bot_loop()

if __name__ == '__main__':
    # Ejecutar todo
    asyncio.run(main())
