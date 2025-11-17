#!/usr/bin/env python3
import os
import requests
from flask import Flask
from telegram import Bot

print("🔧 MODO PRUEBA - BOT AUKAN")

# Configuración
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

print("=== VERIFICACIÓN ===")
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
    return "🤖 Bot AuKaN - PRUEBA"

# Probar Groq directamente
def test_groq():
    print("🧪 TESTEANDO GROQ API...")
    
    headers = {
        'Authorization': f'Bearer {GROQ_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'model': 'llama3-8b-8192',
        'messages': [{'role': 'user', 'content': 'Responde solo con OK si funciona'}],
        'max_tokens': 10
    }
    
    try:
        response = requests.post(
            'https://api.groq.com/openai/v1/chat/completions', 
            json=data, 
            headers=headers, 
            timeout=10
        )
        
        print(f"📊 Status: {response.status_code}")
        print(f"📊 Respuesta: {response.text}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        return False

# Probar Telegram
def test_telegram():
    print("🧪 TESTEANDO TELEGRAM...")
    try:
        bot_info = bot.get_me()
        print(f"✅ Bot: {bot_info.first_name} (@{bot_info.username})")
        return True
    except Exception as e:
        print(f"❌ Error Telegram: {e}")
        return False

# Loop simple de mensajes
def simple_bot_loop():
    print("🔄 INICIANDO BOT SIMPLE...")
    
    last_update_id = 0
    
    while True:
        try:
            updates = bot.get_updates(offset=last_update_id + 1, timeout=10)
            
            for update in updates:
                if update.update_id > last_update_id:
                    last_update_id = update.update_id
                    
                    user_msg = update.message.text
                    chat_id = update.message.chat_id
                    
                    print(f"💬 Mensaje: {user_msg}")
                    
                    # Respuesta fija para probar
                    bot.send_message(
                        chat_id=chat_id, 
                        text="✅ Bot funcionando. Mensaje recibido!"
                    )
                    
        except Exception as e:
            print(f"⚠️ Error en loop: {e}")

if __name__ == '__main__':
    print("🚀 INICIANDO PRUEBAS...")
    
    # Ejecutar tests
    tg_ok = test_telegram()
    groq_ok = test_groq()
    
    print(f"\n📊 RESULTADOS:")
    print(f"Telegram: {'✅' if tg_ok else '❌'}")
    print(f"Groq API: {'✅' if groq_ok else '❌'}")
    
    if tg_ok:
        print("\n🎯 Bot simple activo - Responde con mensaje fijo")
        simple_bot_loop()
    else:
        print("❌ No se puede iniciar bot por errores")
