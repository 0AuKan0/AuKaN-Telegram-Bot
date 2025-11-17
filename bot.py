#!/usr/bin/env python3
import os
import requests
import asyncio
import threading
from flask import Flask
from telegram import Bot

print("🚀 BOT AUKAN - VERSIÓN CORREGIDA")

# Configuración
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
PORT = int(os.environ.get('PORT', 10000))

print(f"TELEGRAM_TOKEN: {'✅' if TELEGRAM_TOKEN else '❌'}")
print(f"GROQ_API_KEY: {'✅' if GROQ_API_KEY else '❌'}")

if not TELEGRAM_TOKEN or not GROQ_API_KEY:
    print("❌ ERROR: Faltan variables de entorno")
    exit(1)

# Inicializar
bot = Bot(token=TELEGRAM_TOKEN)
app = Flask(__name__)

print("✅ Componentes inicializados")

@app.route('/')
def home():
    return "🤖 AuKaN Manager - ACTIVO"

@app.route('/health')
def health():
    return "✅ OK"

async def process_message(update):
    """Procesar un mensaje y responder"""
    try:
        user_message = update.message.text
        chat_id = update.message.chat_id
        
        print(f"📩 Mensaje: '{user_message}'")
        
        # Personalidad del Manager
        system_prompt = """Eres el mánager de AuKaN, un rapero underground de Rubí (Barcelona). 
        Tu tono es callejero, directo y motivador. Hablas en español, usando jerga urbana.
        Responde como si fueras su mánager de verdad."""
        
        headers = {
            'Authorization': f'Bearer {GROQ_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'llama-3.1-8b-instant',  # ✅ MODELO ACTUALIZADO
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_message}
            ],
            'max_tokens': 500,
            'temperature': 0.7
        }
        
        print("🔌 Conectando con Groq...")
        
        response = requests.post(
            'https://api.groq.com/openai/v1/chat/completions', 
            json=data, 
            headers=headers, 
            timeout=30
        )
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            bot_response = result['choices'][0]['message']['content']
            print(f"✅ Respuesta exitosa")
            await bot.send_message(chat_id=chat_id, text=bot_response)
        else:
            print(f"❌ Error API: {response.status_code} - {response.text[:100]}")
            await bot.send_message(chat_id=chat_id, text="🎤 Ahora no caigo, jefe. ¿Repites?")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        await bot.send_message(chat_id=update.message.chat_id, text="💥 Fallo técnico.")

async def bot_loop():
    """Loop principal del bot"""
    print("🔥 BOT LISTO - Esperando mensajes...")
    
    # Obtener último ID
    updates = await bot.get_updates()
    last_update_id = updates[-1].update_id if updates else 0
    print(f"📝 Last Update ID: {last_update_id}")
    
    while True:
        try:
            updates = await bot.get_updates(offset=last_update_id + 1, timeout=10)
            
            for update in updates:
                if update.update_id > last_update_id:
                    last_update_id = update.update_id
                    print(f"🔄 Nuevo mensaje")
                    await process_message(update)
            
            await asyncio.sleep(0.5)
            
        except Exception as e:
            print(f"⚠️ Error en loop: {e}")
            await asyncio.sleep(5)

def run_flask():
    """Ejecutar servidor Flask"""
    print(f"🌐 Servidor web en puerto {PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False)

async def main():
    """Función principal"""
    # Iniciar servidor web
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Iniciar bot
    await bot_loop()

if __name__ == '__main__':
    # Ejecutar con asyncio
    asyncio.run(main())
