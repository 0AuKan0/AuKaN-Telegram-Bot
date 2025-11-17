#!/usr/bin/env python3
import os
import requests
import asyncio
import threading
from flask import Flask
from telegram import Bot
from telegram.error import TelegramError

print("🚀 INICIANDO BOT AUKAN - CON GROQ...")

# Configuración
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
PORT = int(os.environ.get('PORT', 10000))

print(f"✅ Telegram Token: {'✅' if TELEGRAM_TOKEN else '❌'}")
print(f"✅ Groq API Key: {'✅' if GROQ_API_KEY else '❌'}")

if not TELEGRAM_TOKEN:
    print("❌ ERROR: Falta TELEGRAM_BOT_TOKEN")
    exit(1)
if not GROQ_API_KEY:
    print("❌ ERROR: Falta GROQ_API_KEY")
    exit(1)

# Inicializar bot y Flask
bot = Bot(token=TELEGRAM_TOKEN)
app = Flask(__name__)

print("✅ Bot y servidor inicializados")

@app.route('/')
def home():
    return "🤖 AuKaN Manager Bot - ACTIVO con Groq"

@app.route('/health')
def health():
    return "✅ OK"

async def process_message(update):
    """Procesar un mensaje y responder"""
    try:
        user_message = update.message.text
        chat_id = update.message.chat_id
        
        print(f"📩 Mensaje recibido: '{user_message}'")
        
        # Personalidad del Manager de AuKaN
        system_prompt = """Eres el mánager de AuKaN, un rapero underground de Rubí (Barcelona). 
        Tu tono es callejero, directo y motivador. Hablas en español, usando jerga urbana.
        Eres práctico, leal y siempre buscas oportunidades para que AuKaN crezca.
        Responde como si fueras su mánager de verdad, con actitud y confianza."""
        
        headers = {
            'Authorization': f'Bearer {GROQ_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'llama3-8b-8192',  # Modelo rápido y gratis de Groq
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_message}
            ],
            'max_tokens': 500,
            'temperature': 0.7
        }
        
        print("🔌 Conectando con Groq API...")
        
        response = requests.post(
            'https://api.groq.com/openai/v1/chat/completions', 
            json=data, 
            headers=headers, 
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            bot_response = result['choices'][0]['message']['content']
            print(f"✅ Respuesta obtenida ({len(bot_response)} caracteres)")
            await bot.send_message(chat_id=chat_id, text=bot_response)
        else:
            print(f"❌ Error Groq API: {response.status_code}")
            print(f"❌ Response: {response.text}")
            await bot.send_message(chat_id=chat_id, 
                                text="🎤 Ahora no caigo, jefe. ¿Repites?")
            
    except Exception as e:
        print(f"❌ Error en process_message: {e}")
        await bot.send_message(chat_id=update.message.chat_id, 
                            text="💥 Fallo técnico, herma. Reintenta.")

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
                    print(f"🔄 Procesando nuevo mensaje...")
                    await process_message(update)
            
            await asyncio.sleep(0.5)
            
        except Exception as e:
            print(f"⚠️ Error en bot_loop: {e}")
            await asyncio.sleep(5)

def run_flask():
    """Ejecutar servidor Flask"""
    print(f"🌐 Servidor web en puerto {PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False)

async def main():
    """Función principal"""
    # Iniciar servidor web en segundo plano
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Iniciar el bot
    await bot_loop()

if __name__ == '__main__':
    asyncio.run(main())
