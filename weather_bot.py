import telebot
import requests
import json
from datetime import datetime

TELEGRAM_TOKEN = 'YOUR_TELEGRAM_TOKEN'
WEATHER_API_KEY = 'YOUR_OPENWEATHERMAP_API_KEY'

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def is_russian(text):
    return any('а' <= char <= 'я' or char == 'ё' for char in text.lower())

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,"Привет! Я WeatherBot ⛅\nНапиши название города и я покажу погоду")

@bot.message_handler(content_types=['text'])
def get_city(messege):
    city = messege.text
    lang = 'ru' if is_russian(city) else 'en'
    weather_data = get_weather(city,lang)
    if weather_data:
        bot.send_message(messege.chat.id, weather_data)
    else:
        bot.send_message(messege.chat.id, "Город не найден, попробуй еще раз")


def get_weather(city, lang):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city},&appid={WEATHER_API_KEY}&units=metric&lang={lang}"
    response = requests.get(url)
    if response.status_code == 200:
        data = json.loads(response.text)
        if lang == 'ru':
            current = f"Текущая погода в {city}:\nТемпература: {data['main']['temp']}°C\nОписание: {data['weather'][0]['description']}\nВлажность: {data['main']['humidity']}%\nВетер: {data['wind']['speed']} м/с"
        else:
            current = f"Current weather in {city}:\nTemperature: {data['main']['temp']}°C\nDescription: {data['weather'][0]['description']}\nHumidity: {data['main']['humidity']}%\nWind: {data['wind']['speed']} m/s"

        forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city},&appid={WEATHER_API_KEY}&units=metric&lang={lang}&cnt=8" 
        forecast_response = requests.get(forecast_url)
        if forecast_response.status_code == 200:
            forecast_data = json.loads(forecast_response.text)['list']

            forecast = "\n\nПочасовой прогноз на день:\n" if lang == 'ru' else "\n\nHourly forecast for the day:\n"
            for item in forecast_data:
                time = datetime.fromtimestamp(item['dt']).strftime('%H:%M')
                forecast += f"{time}: {item['main']['temp']}°C, {item['weather'][0]['description']}\n"
            return current + forecast
    return None

bot.polling()

