import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'astrobot.settings')
application = get_wsgi_application()

# Django Setup
import django
from django.conf import settings
from django.urls import path, include
from django.contrib import admin
from django.http import JsonResponse
from django.shortcuts import render
from django.db import models
from django.contrib.auth.models import User
import requests
import random
import asyncio
import matplotlib.pyplot as plt
import io
import base64

# Telegram Bot Integration
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
import asyncio

django.setup()

# Database Models
class UserProfile(models.Model):
    class Meta:
        app_label = 'astrobot_app'
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telegram_id = models.CharField(max_length=50, unique=True)
    is_premium = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

# Generate Analytics Graph
def generate_graph():
    users = UserProfile.objects.count()
    premium_users = UserProfile.objects.filter(is_premium=True).count()
    labels = ['Користувачі', 'Преміум-користувачі']
    sizes = [users, premium_users]
    colors = ['blue', 'gold']
    plt.figure(figsize=(5, 5))
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    encoded_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return encoded_image

# Django Views
def home(request):
    graph = generate_graph()
    return render(request, 'dashboard.html', {'graph': graph})

def get_daily_horoscope(sign):
    url = f"https://goroskop.i.ua/{sign}/"
    response = requests.get(url)
    return response.text if response.status_code == 200 else "Не вдалося отримати гороскоп."

def get_tarot_card():
    tarot_url = "https://yoga.co.ua/znachennya-kart-taro/"
    response = requests.get(tarot_url)
    return response.text if response.status_code == 200 else "Не вдалося отримати розклад."

def get_rune_meaning():
    rune_url = "https://esotera.space/runic-meanings/"
    response = requests.get(rune_url)
    return response.text if response.status_code == 200 else "Не вдалося отримати значення рун."

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home),
]

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = "7674458162:AAEkwmjOmYnyNPb-ME32Lh6_EozWYVcWLzg"
bot = Bot(token=TELEGRAM_BOT_TOKEN)
router = Router()
dp = Dispatcher()
dp.include_router(router)

@router.message(Command("start"))
async def start_command(message: Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Гороскоп", "Таро", "Вебінари", "Преміум"]
    keyboard.add(*buttons)
    await message.answer("Привіт! Ласкаво просимо до AstroBot!", reply_markup=keyboard)

@router.message(F.text == "Гороскоп")
async def horoscope_command(message: Message):
    await message.answer("🔮 Зачекайте, гороскоп завантажується...")
    horoscope_text = get_daily_horoscope("aries")
    await message.answer(f"Ваш гороскоп на сьогодні:\n{horoscope_text}")

@router.message(F.text == "Таро")
async def tarot_command(message: Message):
    await message.answer("🔄 Перемішую карти...")
    await asyncio.sleep(2)
    tarot_text = get_tarot_card()
    await message.answer(f"🃏 Вам випала карта:\n{tarot_text}")

@router.message(F.text == "Ворожіння на рунах")
async def rune_command(message: Message):
    await message.answer("✨ Обираю вашу руну...")
    await asyncio.sleep(2)
    rune_text = get_rune_meaning()
    await message.answer(f"🔮 Ваша руна:\n{rune_text}")

@router.message(F.text == "Вебінари")
async def webinars_command(message: Message):
    await message.answer("📅 Ось доступні вебінари:")
    await message.answer("1️⃣ Вебінар: Астропрогноз 2025\n🔗 [Посилання](https://example.com/webinar1)")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
