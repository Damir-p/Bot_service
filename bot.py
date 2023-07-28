import os
import django
from dotenv import load_dotenv,find_dotenv

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Bot_service.settings')
django.setup()
load_dotenv(find_dotenv())

import requests
import json
import random

from telebot import TeleBot
from bot.models import Message

bot = TeleBot(os.getenv('TOKEN'))
API = os.getenv('OPENWEATHERMAP_API_KEY')
NEWS_API = os.getenv('NEWS_API_KEY')


@bot.message_handler(commands=["start"])
def main(message):
    """
    Обработчик команды /start.

    Бот приветствует пользователя и рассказывает о своих функциях.

    Пример использования:
    /start
    """
    bot.send_message(message.chat.id, f"Здравствуйте, {message.from_user.first_name}. Я бот, который предоставляет информацию о погоде, новостях, \n/help для получения списка доступных команд")


@bot.message_handler(commands=['help'])
def handle_start(message):
    """
    Обработчик команды /help.

    Бот выводит список доступных команд.

    Пример использования:
    /help
    """
    bot.send_message(message.chat.id, "Вот список доступных команд:\n"
                                      "/weather - получить информацию о погоде\n"
                                      "/news - получить последние новости\n"
                                      "/help - показать список команд\n"
                                      "/start - перезапустить бот")

@bot.message_handler(commands=['news'])
def send_random_news(message):
    """
    Обработчик команды /news.

    Бот отправляет пользователю случайную новость.

    Пример использования:
    /news
    """
    try:
        news_data = get_random_news()
        if news_data:
            title = news_data["title"]
            description = news_data["description"]
            url = news_data["url"]
            bot.send_message(message.chat.id, f"{title}\n\n{description}\n\n{url}")
        else:
            bot.reply_to(message, "Извините, не удалось получить новости. Пожалуйста, попробуйте позже.")
    except Exception as e:
        bot.reply_to(message, "Произошла ошибка при получении новостей. Пожалуйста, попробуйте позже.")

def get_random_news():
    """
    Получение случайной новости.

    Возвращает данные о случайной новости из внешнего источника.

    Returns:
        dict: Словарь с данными о случайной новости, содержащий поля "title", "description" и "url".
              В случае ошибки или отсутствия новостей, возвращается None.
    """
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API}"
    response = requests.get(url)
    if response.status_code == 200:
        news_data = response.json()
        articles = news_data.get("articles")
        if articles:
            return random.choice(articles)
    return None

@bot.message_handler(commands=['weather'])
def ask_for_city(message):
    """
    Обработчик команды /weather.

    Бот запрашивает у пользователя название города для получения погоды.

    Пример использования:
    /weather
    """
    bot.send_message(message.chat.id, 'Чтобы узнать погоду, введите ключевые слова "погода" и "название города"')

@bot.message_handler(content_types=['text'])
def handle_weather(message):
    """
    Обработчик погоды.

    Получает от пользователя текстовое сообщение, анализирует его и отправляет погоду в указанном городе.

    Пример использования:
    погода Москва
    """
    text = message.text.strip().lower()

    Message.objects.create(user_id=message.from_user.id, chat_id=message.chat.id, text=text)
    
    if text.startswith("погода"):
        city = text[6:].strip()

        if not city:
            bot.reply_to(message, "Вы не указали название города. Пожалуйста, введите название города после слова 'погода'.")
            return

        res = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API}&units=metric")
        data = json.loads(res.text)

        try:
            temp = data["main"]["temp"]
        except KeyError:
            bot.reply_to(message, "Неправильно указан город. Пожалуйста, проверьте правильность названия города.")
            return

        sunny = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRroEkG0Z1tSw9MlJo41mqB-MkoaW8aDjh5cw&usqp=CAU"
        warm = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR8CyW7cQ6VNVjG0vrcfuClyzC1IwUgUtw8iF1rAtXBcaQjcrY5axboM1YDoA--KzTjCwI&usqp=CAU"
        cold = "https://e7.pngegg.com/pngimages/595/116/png-clipart-winter-smiley-emoji-christmas-emoticon-ice-drawing-cold-thumbnail.png"

        image_url = sunny if temp >= 30.0 else warm if 10.0 <= temp < 30.0 else cold

        bot.send_photo(message.chat.id, image_url)
        bot.reply_to(message, f'Сейчас погода: {temp}°C, \n/help - команды')


bot.polling(none_stop=True)
