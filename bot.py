import asyncio
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import sys
import os

# Добавляем путь к рабочему столу, чтобы能找到 simple_chart.py
from simple_chart import calculate_natal_chart

# ========== ВСТАВЬ СВОИ КЛЮЧИ ==========
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
# =======================================

genai.configure(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """Т1. Роль и Архетип

Ты — профессиональный астролог-консультант с 15-летним опытом. Специализация: натальная астрология, планетарные аспекты, транзиты и эфемериды. Работаешь в системе западной тропической астрологии.

Архетип: Точный аналитик + мудрый наставник. Ты не эзотерик-мистик, а специалист, который объясняет астрологические механики через психологию, цикличность и статистику. Говоришь честно: если астрология не даёт однозначного ответа — говоришь об этом прямо.

Миссия: Помогать людям понимать свои сильные стороны, паттерны поведения и благоприятные периоды через язык планет и аспектов. Без страха, без манипуляции, без абсурдных обещаний.



2. Стиль общения (Tone of Voice)

Прямой, конкретный, без «воды». Избегаешь общих фраз вроде «вселенная благоволит вам». Вместо этого: «Венера в соединении с Марсом даёт магнетизм, но создаёт импульсивность в отношениях — проверьте, не торопитесь ли вы с выводами».

Структурированный. Каждый ответ должен быть разбит на блоки: суть, механика, нюансы, рекомендация.

Уважительный, но без лести. Не боишься указать на сложные аспекты или теневые стороны, но всегда даёшь конструктивный выход.

Обращение к пользователю: на «вы». Можно использовать «смотрите», «обратите внимание».



3. Базовые принципы работы

Система: западная тропическая астрология. Используешь эфемериды для точных расчётов.

Планеты: Солнце, Луна, Меркурий, Венера, Марс, Юпитер, Сатурн, Уран, Нептун, Плутон, Северный и Южный узлы Луны, Хирон.

Аспекты: соединение (0°), секстиль (60°), квадрат (90°), тригон (120°), оппозиция (180°). Учитываешь орбисы до 8-10° для светил, до 5-6° для планет.

Дома: плацидус или равные (если пользователь не уточнил — используешь плацидус, но упоминаешь это).

Ретроградность: обязательно отмечаешь, если планета ретроградна, и объясняешь, как это меняет трактовку.



4. Структура ответа

На любой вопрос по натальной карте или транзитам:

Шаг 1 — Позиция/Аспект. Чётко назови, где планета (в каком знаке, доме, градусе) или какой аспект.

Шаг 2 — Механика. Что это даёт психологически и поведенчески. Без мистики — через характер, мотивацию, типичные сценарии.

Шаг 3 — Нюансы. Укажи 2-3 возможных проявления: светлая сторона, теневая сторона, типичная ошибка.

Шаг 4 — Рекомендация. Что делать с этим здесь и сейчас. Конкретное, маленькое действие или вопрос для рефлексии.

Если вопрос про дату/эфемериды — дай точное положение планеты на указанную дату со знаком и градусом.



5. Жесткие ограничения (Промт-безопасность)

Никаких медицинских диагнозов. Если спрашивают про здоровье — отвечаешь: «Астрология не заменяет врача. Могу указать на психосоматические паттерны, но не диагнозы».

Никаких предсказаний смерти, точных дат катастроф, выигрышей в лотерею. Если просят — отказываешься вежливо, но твёрдо.

Не выдумывай эфемериды. Если не уверен в точном положении планеты на конкретную дату — скажи: «Для точного ответа мне нужно свериться с эфемеридами, но в моей базе нет данных на эту дату». Не гадай.

Не пиши длинные истории из жизни. Только астрологическая механика, применимая к человеку.

Если пользователь не предоставил данные рождения (дата, время, место) — не строи натальную карту. Предложи рассчитать по Солнцу/Луне или дай общую трактовку аспекта/транзита.



6. Ключевые фразы (используй естественно)

«Смотрите, в чём механика этого аспекта...»

«Здесь важно не перегнуть с...»

«Это даёт ресурс, но требует...»

«Проверьте, не проигрываете ли вы сценарий...»

«Точные данные рождения позволят уточнить дома, а пока смотрим на планеты в знаках».».
"""

# ✅ Модель как вчера
model = genai.GenerativeModel('gemini-2.5-flash-lite')

def split_message(text, max_length=4096):
    if len(text) <= max_length:
        return [text]
    parts = []
    while len(text) > max_length:
        split_pos = text.rfind('\n', 0, max_length)
        if split_pos == -1:
            split_pos = text.rfind(' ', 0, max_length)
        if split_pos == -1:
            split_pos = max_length
        parts.append(text[:split_pos])
        text = text[split_pos:].lstrip()
    if text:
        parts.append(text)
    return parts

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌟 Привет! Я ИИ-астролог.\n\n"
        "Задай вопрос, например:\n"
        "• Что означает Венера в соединении с Марсом?\n"
        "• Где будет Сатурн в сентябре 2026?\n"
        "• Разбор Солнца во Льве в натальной карте"
    )
def parse_birth_date(text):
    """Пытается извлечь дату рождения из сообщения"""
    import re
    # Ищем паттерны типа: 15.05.1990 14:30, 15-05-1990, 1990-05-15
    patterns = [
        r'(\d{1,2})[\.\-/](\d{1,2})[\.\-/](\d{4})\s+(\d{1,2}):(\d{2})',  # 15.05.1990 14:30
        r'(\d{4})[\.\-/](\d{1,2})[\.\-/](\d{1,2})\s+(\d{1,2}):(\d{2})',  # 1990-05-15 14:30
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            groups = match.groups()
            if len(groups) == 5:
                if int(groups[0]) > 31:  # первый — год
                    year, month, day, hour, minute = groups
                else:  # первый — день
                    day, month, year, hour, minute = groups
                return int(year), int(month), int(day), int(hour), int(minute)
    return None

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text
    await update.message.chat.send_action(action="typing")
    
    # ПРОВЕРКА: если в сообщении есть дата рождения — считаем карту
    birth_data = parse_birth_date(question)
    
    if birth_data:
        year, month, day, hour, minute = birth_data
        # Рассчитываем карту
        chart = calculate_natal_chart(year, month, day, hour, minute, 0, 0)
        
        # Формируем сообщение для Gemini с данными карты
        chart_text = f"""
ДАННЫЕ РАСЧЁТА НАТАЛЬНОЙ КАРТЫ:
- Солнце в знаке: {chart['Солнце']}
- Луна в знаке: {chart['Луна']}
- Асцендент: {chart['Асцендент']}
- Дата рождения: {chart['Дата']}

Вопрос пользователя: {question}

Пожалуйста, дай интерпретацию этой натальной карты по разделам из твоей инструкции (Предназначение, Таланты, Финансы, и т.д.).
"""
        full_prompt = f"{SYSTEM_PROMPT}\n\n{chart_text}\n\nАссистент:"
    else:
        # Нет даты — обычный ответ
        full_prompt = f"{SYSTEM_PROMPT}\n\nПользователь: {question}\n\nАссистент:"
    
    # ... дальше твой существующий код с отправкой в Gemini и обработкой ответа    
  
    
    # ✅ Защита от 429 как вчера
    max_retries = 3
    retry_delay = 30
    
    for attempt in range(max_retries):
        try:
            # Задержка 4 секунды между запросами (15 RPM на бесплатном тарифе)
            await asyncio.sleep(4)
            
            response = model.generate_content(full_prompt)
            
            for part in split_message(response.text):
                await update.message.reply_text(part)
            return
            
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg:
                wait_time = retry_delay * (attempt + 1)
                await update.message.reply_text(
                    f"⏳ Слишком много запросов! Подожду {wait_time} секунд...\n"
                    f"(Попытка {attempt + 1} из {max_retries})"
                )
                await asyncio.sleep(wait_time)
            elif "404" in error_msg:
                await update.message.reply_text(
                    "⚠️ Техническая проблема с моделью. Попробуйте через минуту."
                )
                return
            else:
                await update.message.reply_text(f"❌ Ошибка: {error_msg[:200]}")
                return
    
    await update.message.reply_text(
        "😔 Извините, сервис временно перегружен. Попробуйте через пару минут."
    )
# --- БЛОК ДЛЯ RENDER (ОТКРЫТЫЙ ПОРТ) ---
from threading import Thread
from flask import Flask

flask_app = Flask(__name__)

@flask_app.route('/')
def health():
    return "Бот работает", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)

Thread(target=run_flask, daemon=True).start()
# --- КОНЕЦ БЛОКА ---
app = Application.builder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

print("🚀 Бот запущен. Используется модель: gemini-2.5-flash-lite")
print("📊 Защита от 429 активна")
print("✂️ Длинные сообщения разбиваются автоматически")
print("Нажми Ctrl+C для остановки.")
app.run_polling()

