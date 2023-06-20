import os

import telebot
from telebot import types
import requests
import dotenv


dotenv.load_dotenv()


TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')
OPEN_WEATHER_APP_ID = os.getenv('OPEN_WEATHER_APP_ID', '')

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    author_button = types.KeyboardButton('Автор')
    news_button = types.KeyboardButton('Новость')
    weather_button = types.KeyboardButton('Погода')
    cats_button = types.KeyboardButton('Котики')
    meme_button = types.KeyboardButton('Мем')
    markup.add(weather_button, news_button, cats_button, meme_button, author_button)
    bot.send_message(message.chat.id, 'Привет! Нажми на кнопку:', reply_markup=markup)


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text == 'Автор':
        bot.send_message(message.chat.id, 'Козлов Дмитрий, МО-221')
    elif message.text == 'Новость':
        bot.send_message(message.chat.id, 'Введите запрос для поиска новостей:')
        bot.register_next_step_handler(message, send_news)
    elif message.text == 'Погода':
        bot.send_message(message.chat.id, 'Введите название города:')
        bot.register_next_step_handler(message, send_weather)
    elif message.text == 'Котики':
        send_cats(message)
    elif message.text == 'Мем':
        send_meme(message)
    else:
        bot.send_message(message.chat.id, 'Я не понимаю...')


def send_news(message):
    query = message.text
    url = f'https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_API_KEY}'
    response = requests.get(url).json()
    try:
        articles = response['articles']
        if len(articles) > 0:
            article = articles[0]
            title = article['title']
            description = article['description']
            url = article['url']
            message_text = f'<b>{title}</b>\n\n{description}\n\n<a href="{url}">Читать далее</a>'
            bot.send_message(message.chat.id, message_text, parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, 'По вашему запросу ничего не найдено.')
    except KeyError:
        bot.send_message(message.chat.id, 'Ошибка при получении новостей.')


def send_weather(message):
    city = message.text
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPEN_WEATHER_APP_ID}&units=metric&lang=ru'
    response = requests.get(url).json()
    try:
        temp = response['main']['temp']
        feels_like = response['main']['feels_like']
        description = response['weather'][0]['description']
        message_text = f'Температура в {city}: {temp}°C\nОщущается как: {feels_like}°C\n{description}'
        bot.send_message(message.chat.id, message_text)
    except KeyError:
        bot.send_message(message.chat.id, 'Ошибка при получении погоды.')


def send_cats(message):
    url = 'https://api.thecatapi.com/v1/images/search'
    response = requests.get(url).json()
    try:
        image_url = response[0]['url']
        bot.send_photo(message.chat.id, image_url)
    except KeyError:
        bot.send_message(message.chat.id, 'Ошибка при получении фото.')


def send_meme(message):
    url = 'https://api.popcat.xyz/meme'
    response = requests.get(url).json()
    try:
        title = response['title']
        media_url = response['url']
        if media_url.endswith('.gif'):
            bot.send_video_note(message.chat.id, media_url, caption=title)
        else:
            bot.send_photo(message.chat.id, media_url, caption=title)
    except KeyError:
        bot.send_message(message.chat.id, 'Произошла ошибка при получении мема.')


bot.polling()
