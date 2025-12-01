import os
import requests
import time
import schedule
import json
from datetime import datetime, date
from flask import Flask
from threading import Thread

app = Flask(__name__)

# Настройки
BOT_TOKEN = os.environ['BOT_TOKEN']
USER_ID = os.environ['USER_ID']
URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"
LAST_SENT_FILE = "last_sent.json"

# Список заданий
tasks = [
    "Начать украшать квартиру к праздникам",
    "Приготовить горячий шоколад с маршмеллоу и специями", 
    "Разыграть тайного Санту",
    "Составить новогодний плейлист для настроения",
    "Устроить вечер просмотра любимых зимних фильмов",
    "Покататься на коньках под новогоднюю музыку",
    "Сварить авторский глинтвейн по собственному рецепту",
    "Создать фотокнигу уходящего года",
    "Сходить на рождественскую ярмарку за сувенирами",
    "Купить и собрать готовый новогодний венок",
    "Испечь готовое имбирное печенье из набора",
    "Сходить на зимнюю прогулку в парк",
    "Устроить вечер настольных игр при свечах",
    "Написать список достижений за год",
    "Написать письмо самому себе в следующий год",
    "Купить уютный новогодний свитер",
    "Сделать новогодние украшения из готового набора",
    "Сходить в баню или сауну с аромамаслами",
    "Заказать суши и устроить киновечер",
    "Поехать за город на зимнюю прогулку",
    "Сходить в кафе на праздничный десерт",
    "Сходить в кинотеатр на праздничный фильм",
    "Упаковать подарки в красивую бумагу",
    "Сделать благотворительное пожертвование",
    "Посетить новогоднюю ярмарку в центре города",
    "Сделать генеральную уборку",
    "Сходить в гости к друзьям с угощениями",
    "Сходить на новогодний концерт или спектакль",
    "Подвести итоги года и составить планы на следующий",
    "Насладиться спокойным вечером перед праздником",
    "Загадать желание под бой курантов"
]

def get_current_day():
    """Определяет текущий день декабря"""
    return min(datetime.now().day, 31)

def load_last_sent():
    """Загружает дату последней отправки"""
    try:
        with open(LAST_SENT_FILE, 'r') as f:
            data = json.load(f)
            return datetime.strptime(data['last_sent'], '%Y-%m-%d').date()
    except:
        return None

def save_last_sent():
    """Сохраняет сегодняшнюю дату как дату отправки"""
    try:
        with open(LAST_SENT_FILE, 'w') as f:
            json.dump({'last_sent': date.today().isoformat()}, f)
        return True
    except:
        return False

def send_message(chat_id, text):
    """Отправляет сообщение в Telegram"""
    url = URL + "sendMessage"
    params = {"chat_id": chat_id, "text": text}
    try:
        response = requests.post(url, params=params, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Ошибка отправки: {e}")
        return False

def send_daily_task():
    """Отправляет задание если еще не отправляли сегодня"""
    current_month = datetime.now().month
    current_day = datetime.now().day
    
    print(f"🔍 Проверка: месяц={current_month}, день={current_day}")
    
    # Только декабрь
    if current_month != 12 or current_day > 31:
        print(f"⏭️ Не декабрь или день > 31")
        return
    
    last_sent = load_last_sent()
    today = date.today()
    
    # Если еще не отправляли сегодня
    if last_sent != today:
        day = get_current_day()
        task = tasks[day - 1]
        message = f"🎄 Задание на {day} декабря:\n\n{task}\n\nУдачи! 🎅"
        
        if send_message(USER_ID, message):
            save_last_sent()
            print(f"✅ Отправлено задание на {day} декабря")
        else:
            print(f"❌ Ошибка отправки задания")
    else:
        print(f"⏭️ Задание на сегодня уже отправлено")

def send_today_task_manually(chat_id=None):
    """Принудительно отправить сегодняшнее задание"""
    current_month = datetime.now().month
    
    if current_month == 12:
        day = get_current_day()
        task = tasks[day - 1]
        message = f"🎄 Задание на {day} декабря:\n\n{task}\n\nУдачи! 🎅"
        
        target_chat = chat_id if chat_id else USER_ID
        if send_message(target_chat, message):
            save_last_sent()
            print(f"✅ Принудительно отправлено задание на {day} декабря")
            return True
    else:
        if chat_id:
            send_message(chat_id, "❌ Сейчас не декабрь! Задания начнутся с 1 декабря.")
    return False

def process_updates():
    """Обрабатывает входящие сообщения"""
    try:
        url = URL + "getUpdates"
        params = {"timeout": 30, "offset": -1}
        response = requests.get(url, params=params, timeout=10)
        updates = response.json()
        
        if "result" in updates:
            for update in updates["result"]:
                if "message" in update:
                    chat_id = update["message"]["chat"]["id"]
                    text = update["message"].get("text", "").lower()
                    
                    if text == "/start":
                        send_message(chat_id, "🎄 Привет! Я новогодний бот!\n\nС 1 декабря я буду присылать тебе по одному заданию каждый день!\n\nКоманды:\n/today - задание на сегодня\n/sendnow - отправить сейчас\n/help - помощь")
                    
                    elif text == "/today":
                        current_month = datetime.now().month
                        if current_month == 12:
                            day = get_current_day()
                            task = tasks[day - 1]
                            send_message(chat_id, f"🎄 Задание на {day} декабря:\n\n{task}")
                        else:
                            send_message(chat_id, "❄️ Задания начнутся с 1 декабря! Осталось совсем немного!")
                    
                    elif text == "/sendnow":
                        if send_today_task_manually(chat_id):
                            send_message(chat_id, "✅ Сегодняшнее задание отправлено!")
                        else:
                            send_message(chat_id, "❌ Сейчас не декабрь!")
                    
                    elif text == "/help":
                        help_text = "🎅 Новогодний Бот Помощник\n\n"
                        help_text += "Команды:\n"
                        help_text += "/start - начать работу\n"
                        help_text += "/today - задание на сегодня\n"
                        help_text += "/sendnow - отправить задание сейчас\n"
                        help_text += "/help - показать справку\n\n"
                        help_text += "С 1 декабря - каждый день новое задание!"
                        send_message(chat_id, help_text)
    
    except Exception as e:
        print(f"Ошибка process_updates: {e}")

def schedule_checker():
    """Проверяет расписание"""
    while True:
        schedule.run_pending()
        time.sleep(60)

@app.route('/')
def home():
    return "🎄 Новогодний бот работает!"

@app.route('/webhook', methods=['POST'])
def webhook():
    process_updates()
    return "OK"

def main():
    # Настраиваем расписание (для Москвы 8:00 = 5:00 UTC)
    schedule.every().day.at("05:00").do(send_daily_task)
    print("⏰ Расписание: ежедневно в 5:00 UTC (8:00 по Москве)")
    
    # Запускаем проверку расписания в отдельном потоке
    scheduler_thread = Thread(target=schedule_checker)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    # Запускаем обработку сообщений
    def polling_loop():
        while True:
            process_updates()
            time.sleep(5)
    
    polling_thread = Thread(target=polling_loop)
    polling_thread.daemon = True
    polling_thread.start()
    
    print("✅ Бот запущен и ждет 1 декабря!")
    print(f"📅 Всего заданий: {len(tasks)}")
    print(f"👤 USER_ID: {USER_ID}")
    print("📱 Отправьте /sendnow чтобы получить задание сейчас")
    
    # Запускаем Flask
    app.run(host='0.0.0.0', port=3000, debug=False)

if __name__ == '__main__':
    main()
