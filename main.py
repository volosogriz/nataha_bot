# -*- coding: utf-8 -*-
from aiogram import Bot, Dispatcher, executor, types
import asyncio
API_TOKEN = '6693646126:AAG8ubQrQ8Rgx_zcAdRCRD_ad6WtRC5VVLY'
bot = Bot(API_TOKEN)
dp = Dispatcher(bot)
import random
import sqlite3
import requests
from requests.exceptions import ReadTimeout
from telebot import types
from datetime import timedelta
from datetime import datetime
import threading
import time
import psutil
import speech_recognition as sr
import subprocess
import os
import subprocess


# Время, когда команда была последний раз выполнена (может быть сохранено в базе данных или файле)
last_execution_time = None  # Здесь должно быть реальное значение

# текущее время
current_time = time.time()

user_response = None

last_command_time1 = 0
last_command_time2 = 0

async def insert_user_message(userid, username, name, improvement_param, number, set_value):
    conn = sqlite3.connect('kukuruza.sql')
    cur = conn.cursor()
    
    # Создание таблицы, если она еще не существует
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            userid INTEGER,
            username TEXT NOT NULL,
            name TEXT NOT NULL,
            message_time TEXT NOT NULL,
            improvement_param TEXT,
            number INTEGER,
            set_value INTEGER                       
        )        
    """)
    conn.commit()
    cur.close()
    conn.close()

    current_time1 = datetime.now().strftime("%H:%M %d.%m.%y")
    if username is None:
        username = 'n/a'
    if not name:
        print("Ошибка: Поле 'name' не может быть пустым.")
        return

    try:
        conn = sqlite3.connect('kukuruza.sql')
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO user_messages (userid, username, name, message_time, improvement_param, number, set_value)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (userid, username, name, current_time1, improvement_param, number, set_value))
        conn.commit()

        # Получаем id последней вставленной строки
        last_id = cur.lastrowid

        # Выбираем эту строку из базы данных
        cur.execute("SELECT * FROM user_messages WHERE id = ?", (last_id,))
        row = cur.fetchone()

        if row is None:
            print("Ошибка: Не удалось найти вставленную запись.")
            return None

        # Возвращаем строку в виде словаря
        return {
            'id': row[0],
            'userid': row[1],
            'username': row[2],
            'name': row[3],
            'message_time': row[4],
            'improvement_param': row[5],
            'number': row[6],
            'set_value': row[7]
        }
    except sqlite3.InterfaceError as e:
        print(f"Ошибка при вставке данных: {e}")
        print(f"Некорректные данные: userid={userid}, username={username}, name={name}, improvement_param={improvement_param}, number={number}, set_value={set_value}")
        # Получаем id последней вставленной строки
        last_id = cur.lastrowid

        # Выбираем эту строку из базы данных
        cur.execute("SELECT * FROM user_messages WHERE id = ?", (last_id,))
        row = cur.fetchone()

        conn.close()

        # Возвращаем строку в виде словаря
    cur.close()
    conn.close()


@dp.message_handler(commands=["stop"])
async def stop_command(message: types.Message):
    print('stop')
    # Отправляем файл profile.db
    with open("kukuruza.sql", "rb") as file:
        await bot.send_document(message.chat.id, file)




@dp.message_handler(lambda message: 'good_night' in message.text.lower(), state='*')
async def sccsd(message: types.Message,):
    await message.answer('Good night!')
    os.system("shutdown /s /t 0")





























@dp.message_handler(commands=['adm'])
async def handle_admin_command(message: types.Message):
    if message.sender_chat:
        username123 = message.sender_chat.id
    else:
        username123 = message.from_user.id
    if message.chat.type == "private":
        #  ID пользователя из сообщения
        user_id = message.text.split()[1] if len(message.text.split()) > 1 else None
        if user_id:
            conn = sqlite3.connect('kukuruza.sql')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM admins WHERE id=?", (user_id,))
            admin = cursor.fetchone()
            if admin:
                cursor.execute("DELETE FROM admins WHERE id=?", (user_id,))
                await message.reply(f'Пользователь {user_id} удален из списка администраторов')
            else:
                cursor.execute("INSERT INTO admins (id, username) VALUES (?, ?)", (user_id, username123)) 
                await message.reply(f'Пользователь {user_id} добавлен в список администраторов')
            conn.commit()
        else:
            await message.reply ('Вы не указали ID пользователя')
    else:
        await message.reply('Эта команда доступна только в личных сообщениях')


channel_id = 1001848826330
with open('texts.txt', 'r', encoding='utf-8') as f:
    random_texts = f.read().splitlines()



@dp.message_handler(commands=['getrandomphoto'])
async def get_random_photo(message):
    # Получаем все медиа сообщения из канала
    channel_id = 1001848826330
    media = bot.get_chat_media(channel_id)

    # Фильтруем только фотографии
    photos = [m for m in media if m.content_type == 'photo']

    # Выбираем случайную фотографию
    random_photo = random.choice(photos)

    # ПЕРЕИСАТЬ НА АИОГРАММ ЭТО ВОЗМОНО!!!
    bot.send_photo(message.chat.id, random_photo.photo.file_id)


def command_limiter(func):
    async def wrapper(message: types.Message):
        global last_command_time1
        current_time = time.time()
        while current_time - last_command_time1 < 1:
            await asyncio.sleep(0.1)
            current_time = time.time()
        last_command_time1 = current_time
        return await func(message)
    return wrapper



def command_limiter2(func):
    async def wrapper(message: types.Message):
        global last_command_time2
        current_time = time.time()
        global sec
        if message.sender_chat:
            username123 = message.sender_chat.id
        else:
            username123 = message.from_user.id
        conn = sqlite3.connect('kukuruza.sql')
        cur = conn.cursor()
        cur.execute('SELECT wait_time_seconds FROM users WHERE username = ?', (username123,))
        result = cur.fetchone()
        if result is not None:
            wait_time_seconds = result[0]
        else:
            wait_time_seconds = 0  # или любое другое значение по умолчанию
        cur.execute('SELECT last_execution_time FROM users WHERE username = ?', (username123,))
        result = cur.fetchone()
        if result is not None:
            last_execution_time = result[0]
        else:
            last_execution_time = 0  # или любое другое значение по умолчанию
        cur.close()
        conn.close()
        if last_execution_time is None or current_time - last_execution_time >= wait_time_seconds:
            sec = 10
        else:
            sec = 3
        if current_time - last_command_time2 < 5:
            msg = await bot.send_message(message.chat.id, "Пожалуйста, подождите")
            while current_time - last_command_time2 < sec:
                await asyncio.sleep(0.1)
                current_time = time.time()
            await bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        last_command_time2 = current_time
        return await func(message)
    return wrapper


async def get_gpu_usage():
    """Get the current gpu usage.

    Returns:
        dict: The keys are the ids of the gpus and the values are the gpu usage.
    """
    # NVIDIA GPUs
    result = subprocess.check_output(
        [
            'nvidia-smi', '--query-gpu=utilization.gpu',
            '--format=csv,nounits,noheader'
        ], encoding='utf-8')
    # Each line in the result corresponds to one GPU.
    gpu_usage = [int(x) for x in result.strip().split('\\n')]
    gpu_ids = range(len(gpu_usage))
    usage_dict = dict(zip(gpu_ids, gpu_usage))

    # AMD GPUs
    try:
        result = subprocess.check_output(
            [
                'radeontop', '-d', '-',
                '-l', '1'
            ], encoding='utf-8')
        # Parse the output to get the GPU usage
        for line in result.split('\\n'):
            if 'gpu' in line:
                usage = int(line.split(':')[1].strip().replace('%', ''))
                usage_dict['AMD'] = usage
    except:
        #print("Radeontop not found. Skipping AMD GPUs.")
        pass
    return usage_dict
food_smileys = ["😀", "😋", "😊", "🥵", "😁", "🤣", "😃", "😄", "😅", "😆", "😉", "😊", "😋", "😎", "😍", "😘", "🥰", "😗", "😙", "🥲", "😚", "☺️", "🙂", "🤗", "🤩", "🤔", "🫡", "🤨", "😐", "🫥", "😶‍🌫️", "🙄", "😏", "😣", "😥", "😮", "😯", "😪", "🥱", "😴", "😌", "😛", "😜", "😝", "🤤", "🙃", "🫠", "😲", "😧", "😦", "😨", "🤯", "😬", "😮‍💨", "😳", "🤪", "😠", "🥺", "🫨", "🤫", "🤭", "🫢", "🫣", "🧐", "🤓", "😈"]
file_url = 'https://lh3.googleusercontent.com/u/0/drive-viewer/AKGpihbQL5VpC5lLYPOBKY6L43S5jabz-tu632mBZJiPAZpyHY3k1U_lNPZxhyeqAEdsbe8IUcihnDAncAl1IGT4RXHYcQu-FA=w2512-h1292'

@dp.message_handler(lambda message: 'кукуруза' in message.text.lower())
async def info(message: types.Message):
    random_smiley = random.choice(food_smileys)
    await bot.send_message(message.chat.id, f'{random_smiley}')
    await bot.send_document(message.chat.id, file_url)

@dp.message_handler(commands=['words_filter'])
async def main(message: types.Message):
    conn = sqlite3.connect('kukuruza.sql')
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM bad_words WHERE chat_id = '{message.chat.id}'")
    rows = cur.fetchall()
    if rows:
        cur.execute(f"DELETE FROM bad_words WHERE chat_id = '{message.chat.id}'")
        await bot.send_message(message.chat.id, 'Удаление ненормативной лексики отключенно')
    else:
        cur.execute(f"INSERT INTO bad_words (chat_id) VALUES ('{message.chat.id}')")
        await bot.send_message(message.chat.id, 'В чате теперь удаляются сообщения с ненормативной лексикой!')
    conn.commit()
    cur.close()
    conn.close()

@dp.message_handler(commands=['speech_recognition'])
async def main(message: types.Message):
    conn = sqlite3.connect('kukuruza.sql')
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM speech_recognition WHERE chat_id = '{message.chat.id}'")
    rows = cur.fetchall()
    if rows:
        cur.execute(f"DELETE FROM speech_recognition WHERE chat_id = '{message.chat.id}'")
        await bot.send_message(message.chat.id, 'Распознование текста в гс отключенно')
    else:
        cur.execute(f"INSERT INTO speech_recognition (chat_id) VALUES ('{message.chat.id}')")
        await bot.send_message(message.chat.id, 'Распознование текста в гс включенно')
    conn.commit()
    cur.close()
    conn.close()


@dp.message_handler(commands=['gg2'])
async def main(message) :
    conn = sqlite3.connect('kukuruza.sql')
@dp.message_handler(commands=['serverinfo'])
@command_limiter2
async def serverinfo(message: types.Message):
    msg = await bot.send_message(message.chat.id, 'Инициализация...')
    start_time = time.time()
    while True:
        # Проверяем, прошло ли уже 10 секунд
        if time.time() - start_time > 10:
            break

        cpu_usage = psutil.cpu_percent()
        memory_info = psutil.virtual_memory()
        memory_usage = memory_info.percent
        gpu_usage = await get_gpu_usage()
        gpu_usage_text = ', '.join(f'GPU {i}: {usage}%' for i, usage in gpu_usage.items())
        text = f'Использование CPU: {cpu_usage}%\nИспользование {gpu_usage_text}\nИспользование RAM: {memory_usage}%'
        await bot.edit_message_text(text, message.chat.id, msg.message_id)
        await asyncio.sleep(1)  # Обновляем информацию каждую секунду

@dp.message_handler(commands=['gg'])
async def main(message: types.Message):
    # Подключение к базе данных
    conn = sqlite3.connect('kukuruza.sql')
    cur = conn.cursor()

    # Удаление таблицы
    #cur.execute("DELETE FROM users WHERE id=?", (21,))
    cur.execute('UPDATE users SET username = ? WHERE id = ?', (-1001844622449, 4))

    conn.commit()

    # Закрытие соединения с базой данных
    conn.close()

user_states = {}

@dp.message_handler(commands=['pg0'])
async def main(message: types.Message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(f'да, сбросить прогресс', callback_data='pg0')
    markup.row(btn1)
    btn2 = types.InlineKeyboardButton(f'отмеа', callback_data='cancel')
    markup.row(btn2)
    await message.reply(f'вы действительно хотите сбросить прогресс? ', reply_markup=markup)
@dp.message_handler(commands=['id'])
async def main(message: types.Message):
    if message.sender_chat:
        username123 = message.sender_chat.id
    else:
        username123 = message.from_user.id
    await bot.send_message(username123, str(username123))
        
@dp.message_handler(commands=['start'])
async def main(message: types.Message):
    try:
        conn = sqlite3.connect('kukuruza.sql')
        cur = conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, nickname TEXT NOT NULL, progress INTEGER DEFAULT 0, last_execution_time REAL)')
        conn.commit()
        cur.close()
        conn.close()
        msg_set = 'creating sql table'
        msg = await bot.send_message(message.chat.id, msg_set )
        conn = sqlite3.connect('kukuruza.sql')
        cur = conn.cursor()
        username = message.from_user.username
        try:
            cur.execute('ALTER TABLE users ADD COLUMN wait_time_seconds INTEGER DEFAULT 86400')
            cur.execute('ALTER TABLE users ADD COLUMN range INTEGER DEFAULT 0' )
            cur.execute('ALTER TABLE statistics ADD COLUMN otrezat_send INTEGER DEFAULT 0' )
            cur.execute('ALTER TABLE statistics ADD COLUMN otrezat_received INTEGER DEFAULT 0' )
            conn.commit()
            cur.close()
            conn.close()
            msg_set= msg_set + 'done!'
            await bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=msg_set)
        except:
            msg_set= msg_set + " all libraries from 11.03.24 update are alredy exist!"
            await bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=msg_set)
        try:
            conn = sqlite3.connect('kukuruza.sql')
            cur = conn.cursor()
            conn = sqlite3.connect('kukuruza.sql')
            cur = conn.cursor()
            cur.execute('ALTER TABLE users ADD COLUMN name TEXT')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS user_chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                chat_id INTEGER,
                FOREIGN KEY(user_id) REFERENCES users(id)
                )
            ''')
            conn.commit()
            cur.close()
            conn.close()
            msg_set = msg_set + 'Updated to 12.03.24 update!'
            await bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=msg_set)
        except:
            msg_set = msg_set + ' all libraries from 12.03.24 update are alredy exist!'
            await bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=msg_set)
        conn = sqlite3.connect('kukuruza.sql')
        cur = conn.cursor()
        try:
            cur.execute('ALTER TABLE statistics ADD COLUMN otrezat_send INTEGER DEFAULT 0' )
            cur.execute('ALTER TABLE statistics ADD COLUMN otrezat_received INTEGER DEFAULT 0' )
            conn.commit()
            cur.close()
            conn.close()
            msg_set= msg_set + 'done!'
            await bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=msg_set)
        except:
            msg_set= msg_set + " ntc alredy exist! "
            await bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=msg_set)
        cur.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_entry_date TEXT DEFAULT "11.03.2024",
                kukuruza_commands_count INTEGER DEFAULT 2,
                commands_count INTEGER DEFAULT 2
            )
        ''')
        conn.commit()
        cur.close()
        conn.close()
        conn = sqlite3.connect('kukuruza.sql')
        cur = conn.cursor()
        try:
            cur.execute('ALTER TABLE users ADD COLUMN username INTEGER')
            conn.commit()
            cur.close()
            conn.close()
            msg_set= msg_set + 'done!'
            await bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=msg_set)
        except:
            conn.commit()
            cur.close()
            conn.close()
    except sqlite3.Error as e:
        await message.answer('err!')
    await message.answer(f'hi, <a href="https://t.me/{message.from_user.username}"> {message.from_user.first_name}</a>! давай растить член! \n /kukuruza' , parse_mode='html', disable_web_page_preview=True)
@dp.message_handler(commands=['pr0'])
async def main(message: types.Message):
    nickname = message.from_user.username
    conn = sqlite3.connect('kukuruza.sql')
    cur = conn.cursor()
    cur.execute('UPDATE users SET progress = ? WHERE nickname = ?', (0, nickname))
    conn.commit()
    cur.close()
    conn.close()
    await bot.send_message(message.chat.id, 'ddd')

@dp.message_handler(commands=['kd0'])
async def main(message: types.Message):
    if message.sender_chat:
        nickname = message.reply_to_message.sender_chat.id
    else:
        nickname = message.from_user.id
    await bot.send_message(message.chat.id, 'ало') 
    conn = sqlite3.connect('kukuruza.sql')
    cur = conn.cursor()
    cur.execute('UPDATE users SET wait_time_seconds = ? WHERE username = ?', (0, nickname))
    conn.commit()
    cur.close()
    conn.close()
    await bot.send_message(message.chat.id, 'ваш кд установлен в 0')

@dp.message_handler(commands=['kd24'])
async def main(message: types.Message):
    if message.sender_chat:
        nickname = message.sender_chat.id
    else:
        nickname = message.from_user.id
    await bot.send_message(message.chat.id, 'ало') 
    conn = sqlite3.connect('kukuruza.sql')
    cur = conn.cursor()
    cur.execute('UPDATE users SET wait_time_seconds = ? WHERE username = ?', (86400, nickname))
    conn.commit()
    cur.close()
    conn.close()
    await bot.send_message(message.chat.id, 'ваш кд установлен в 24часа')

@dp.message_handler(commands=['range1'])
async def main(message: types.Message):
    nickname = message.from_user.username
    await bot.send_message(message.chat.id, 'ало') 
    conn = sqlite3.connect('kukuruza.sql')
    cur = conn.cursor()
    cur.execute('SELECT range FROM users WHERE nickname = ?', (nickname,))
    range2 = cur.fetchone()[0] + 1
    cur.execute('UPDATE users SET range = ? WHERE nickname = ?', (range2, nickname))
    conn.commit()
    cur.close()
    conn.close()
    await bot.send_message(message.chat.id, f'разброс установлен в {range2}')

@dp.message_handler(commands=['range0'])
async def main(message: types.Message):
    nickname = message.from_user.username
    await bot.send_message(message.chat.id, 'ало') 
    conn = sqlite3.connect('kukuruza.sql')
    cur = conn.cursor()
    cur.execute('SELECT range FROM users WHERE nickname = ?', (nickname,))
    range2 = cur.fetchone()[0] - 1
    cur.execute('UPDATE users SET range = ? WHERE nickname = ?', (range2, nickname))
    conn.commit()
    cur.close()
    conn.close()
    await bot.send_message(message.chat.id, f'разброс установлен в {range2}')
 
@dp.message_handler(commands=['stats'])
async def main(message: types.Message):
    #КУКУРУЗА КОУНТ
    conn = sqlite3.connect('kukuruza.sql')
    cur = conn.cursor()
    if message.sender_chat:
        username123 = message.sender_chat.id
    else:
        username123 = message.from_user.id
    if message.sender_chat:
        user_id = message.sender_chat.id
    else:
        user_id = message.from_user.id

    cur.execute("UPDATE statistics SET commands_count = commands_count + 1 WHERE id = ?", (username123,))
    conn.commit()
    cur.close()
    conn.close()

    conn = sqlite3.connect('kukuruza.sql')
    cur = conn.cursor()
    cur.execute('SELECT rangeupup FROM users WHERE username = ?', (username123,))
    result = cur.fetchone()
    if result is None:
        rangeupup = 0
    else:
        rangeupup = result[0]
    if message.reply_to_message:
        if message.reply_to_message.sender_chat:
            user_id = message.reply_to_message.sender_chat.id
        else:
            user_id = message.reply_to_message.from_user.id
    else:
        if message.sender_chat:
            nickname = message.sender_chat.id
        else:
            nickname = message.from_user.id

    try:
        cur.execute("SELECT first_entry_date, kukuruza_commands_count, commands_count FROM statistics WHERE id = ?", (user_id,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        conn = sqlite3.connect('kukuruza.sql')
        cur = conn.cursor()
        cur.execute('SELECT name FROM users WHERE username = ?', (user_id,))
        name = cur.fetchone()[0]
        cur.execute('SELECT nickname FROM users WHERE username = ?', (user_id,))
        nickname = cur.fetchone()[0]
        cur.execute('SELECT wait_time_seconds FROM users WHERE username = ?', (user_id,))
        wait_time_seconds = cur.fetchone()[0]
        cur.execute('SELECT range FROM users WHERE username = ?', (user_id,))
        range2 = cur.fetchone()[0]
        cur.execute("SELECT progress FROM users WHERE username = ?", (user_id,))
        progress = cur.fetchone()[0]
        cur.execute("SELECT otrezat_send FROM statistics WHERE id = ?", (user_id,))
        otrezat_send = cur.fetchone()[0]
        cur.execute("SELECT otrezat_received FROM statistics WHERE id = ?", (user_id,))
        otrezat_received = cur.fetchone()[0]

        msg = await bot.send_message(message.chat.id, 'статистика')

        if result is not None:
            hours, remainder = divmod(wait_time_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            cooldown = f"{hours}часа {minutes}мин {seconds}сек"
            dispersion = f"от {-5-range2} до {10+range2}"
            first_entry_date, kukuruza_commands_count, commands_count = result
            msg_set = f'<a href="https://t.me/{nickname}">{name}</a> {progress} см \n'
            msg_set = msg_set + f"C кулдауном {cooldown} \nС разбросом {dispersion}\nДата первого входа: {first_entry_date}\nОтрезанно писюнов:{otrezat_send} \nПолученно отрезаний: {otrezat_received} \nКоличество команд /kukuruza: {kukuruza_commands_count}\nКолличество взаимодействий с ботом: {commands_count} \n"
            msg_set = msg_set + f"Разброс при получении очко: от 1 до {rangeupup + 5} баллов\n"
            msg_set = msg_set + f"айди для отрезания пиписи: `{user_id}`"
            await bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=msg_set,  parse_mode='html', disable_web_page_preview=True)
        else:
            await bot.send_message(message.chat.id, f"нет статистики")
        cur.close()
        conn.close()
    except:
        await bot.send_message(message.chat.id, f"Пусто")








last_command_time = {}


#1001523096357

@dp.message_handler(commands=['kukurusa', 'kukuruza'])
@command_limiter2
async def main(message: types.Message) :
    conn = sqlite3.connect('updates.db')
    cur = conn.cursor()
    # Проверка, было ли обновление уже обработано
    cur.execute('SELECT update_id FROM updates WHERE update_id = ?', (message.message_id,))
    if cur.fetchone():
        return  # Если обновление уже было обработано, пропустить его

    # Добавление ID обновления в базу данных
    cur.execute('INSERT INTO updates VALUES (?)', (message.message_id,))
    conn.commit()

    if message.sender_chat:
        user_id = message.sender_chat.id
    else:
        user_id = message.from_user.id

    # Если пользователь уже отправлял команду
    #if user_id in last_command_time:
        # Проверяем, прошла ли секунда с момента последней команды
        #if time.time() - last_command_time[user_id] < 10:
            #bot.reply_to(message, "Слишком частая отправка команды. Повторите через некоторое время")
            #return
    last_command_time[user_id] = time.time()
    conn = sqlite3.connect('kukuruza.sql')
    cur = conn.cursor()
    if message.sender_chat:
        user_id = message.sender_chat.id
    else:
        user_id = message.from_user.id
    username = message.from_user.username
    if username == None:
        username = 'N/A'
    cur.execute(f"UPDATE users SET nickname = '{username}' WHERE id = '{user_id}' AND nickname != '{username}'")
    conn.commit()
    conn.close()
    conn = sqlite3.connect('kukuruza.sql')
    cur = conn.cursor()

    # айди пользователя
    if message.sender_chat:
        username123 = message.sender_chat.id
    else:
        username123 = message.from_user.id
    cur.execute("SELECT * FROM statistics WHERE id = ?", (username123,))
    user123 = cur.fetchone()
    if user123 is None:
        cur.execute("INSERT INTO statistics (id, first_entry_date) VALUES (?, ?)", (username123, datetime.now().strftime("%d.%m.%Y")))
    conn.commit()
    cur.close()
    conn.close()
   #КУКУРУЗА КОУНТ
    conn = sqlite3.connect('kukuruza.sql')
    cur = conn.cursor()
    if message.sender_chat:
        username123 = message.sender_chat.id
    else:
        username123 = message.from_user.id
    cur.execute("UPDATE statistics SET commands_count = commands_count + 1 WHERE id = ?", (username123,))
    conn.commit()
    cur.close()
    conn.close()
    conn = sqlite3.connect('kukuruza.sql')
    cur = conn.cursor()
    if message.sender_chat:
        username = message.sender_chat.id
    else:
        username = message.from_user.id
    nickname1 = message.from_user.username
    cur.execute(f"SELECT COUNT(*) FROM users WHERE username = '{username}'")
    existing_count = cur.fetchone()[0]
    if nickname1 == None:
        nickname1 = 'N/A'
    if existing_count == 0:
        cur.execute("SELECT id FROM users ORDER BY id DESC LIMIT 1")
        last_id = cur.fetchone()[0] + 1
        cur.execute(f"INSERT INTO users (nickname, last_execution_time, wait_time_seconds, range, username, id) VALUES ('{nickname1}', 0, 86400, 0, '{username}', {last_id})")
        conn.commit()
        await bot.send_message(message.chat.id, "Добро пожаловать! Сейчас твой член равен 0см. Сечас мы бросим кубик и увеличим или уменьшим твой член! ") 
    cur.close()
    conn.close()
    conn = sqlite3.connect('kukuruza.sql')
    cur = conn.cursor()
    cur.execute('SELECT wait_time_seconds FROM users WHERE username = ?', (username,))
    wait_time_seconds = cur.fetchone()[0]
    cur.execute('SELECT range FROM users WHERE username = ?', (username,))
    range1 = cur.fetchone()[0]
    register(message)
    first_name = message.from_user.first_name
    conn = sqlite3.connect('kukuruza.sql')
    cur = conn.cursor()
    cur.execute('UPDATE users SET name = ? WHERE username = ?', (first_name, username))
    cur.execute("SELECT name FROM users WHERE username = ?", (username,))
    name = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()
    current_time = time.time()
    conn = sqlite3.connect('kukuruza.sql')
    cur = conn.cursor()
    nickname = message.from_user.username
    cur.execute('SELECT last_execution_time FROM users WHERE username = ?', (username,))
    result = cur.fetchone()
    last_execution_time = result[0]
    cur.execute('SELECT progress FROM users WHERE username = ?', (username,))
    result = cur.fetchone()[0]
    if result == None:
        result = 0
    conn.commit()
    if last_execution_time is None or wait_time_seconds is None:
       cur.execute('UPDATE users SET wait_time_seconds = ? WHERE username = ?', (86400, username)) 
       cur.execute('UPDATE users SET range = ? WHERE username = ?', (0, username)) 
       await message.answer('added 2 new columns: range; wait_time_seconds')
    cur.close()
    conn.close()
    if last_execution_time is None or current_time - last_execution_time >= wait_time_seconds:

         #КУКУРУЗА КОУНТ
        msg = await message.answer(f'растим ваш член! текущий разброс равен от {-5 -range1} до {10 + range1}') 
        await asyncio.sleep(3)
        conn = sqlite3.connect('kukuruza.sql')
        cur = conn.cursor()
        if message.sender_chat:
            username123 = message.sender_chat.id
        else:
            username123 = message.from_user.id
        cur.execute("UPDATE statistics SET kukuruza_commands_count = kukuruza_commands_count + 1 WHERE id = ?", (username123,))
        conn.commit()
        cur.close()
        conn.close()




        new_text = 0
        new_number = 0
        uprange = 10 + range1
        dwnrange = -5 - range1
        #for _ in range(10):
            
            #time.sleep(0.7)
            #new_number = random.randint(dwnrange, uprange)
            #if new_number != new_text:
                #new_text = new_number
                #bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text = f'{new_text} см')
                
        if result == 0:
            random_number = random.randint(0, uprange)
        else:
            random_number = random.randint(dwnrange, uprange)
        if random_number == 0:
            random_number = 1
        result = result + random_number
        if result < 0:
            result = 0
        conn = sqlite3.connect('kukuruza.sql')
        cur = conn.cursor()
        cur.execute('UPDATE users SET progress = ? WHERE username = ?', (result, username))
        conn.commit()
        cur.close()
        conn.close()
        if random_number < 0:
            msg_set = f'⏬Ваш член уменьшился на {abs(random_number)} см! теперь он равен {result} см.'
            await bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=msg_set)
            row = await insert_user_message(username123, nickname, name, "kukuruza", f'{random_number}', result)
            await bot.send_message(-1002021859893, f"Добавлена строка: {row}")


        else:
            msg_set = f'⏫Ваш член увеличился на {random_number} см! теперь он равен {result} см.'
            await bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=msg_set)
            row = await insert_user_message(username123, nickname, name, "kukuruza", f'{random_number}', result)
            await bot.send_message(-1002021859893, f"Добавлена строка: {row}")

        conn = sqlite3.connect('kukuruza.sql')
        cur = conn.cursor()

        # Никнейм пользователя
        

        # Выборка всех пользователей по прогрессу
        cur.execute("SELECT username, progress FROM users ORDER BY progress DESC")
        all_users = cur.fetchall()

        # Поиск места пользователя в топе
        user_rank = None
        for i, user in enumerate(all_users):
            if user[0] == username:
                user_rank = i + 1
                break

        cur.close()
        conn.close()

        if user_rank is not None:
            msg_set = msg_set + f"\nТы №{user_rank} в топе!"
            #bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text = msg_set)
        else:
            msg_set = msg_set + f'\nты не в топе.((('
            #bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text = msg_set)

        last_execution_time = current_time
        conn = sqlite3.connect('kukuruza.sql')
        cur = conn.cursor()
        cur.execute('UPDATE users SET last_execution_time = ? WHERE username = ?', (last_execution_time, username))
        conn.commit()
        cur.close()
        conn.close()
        await asyncio.sleep(2)
        timenotfomated = wait_time_seconds - (current_time - last_execution_time)
        hours = timenotfomated // 3600
        minutes = (timenotfomated % 3600) // 60
        seconds = timenotfomated % 60
        hours = round(hours)
        minutes = round(minutes)
        seconds = round(seconds)
        formatted_time = f"{hours:02} часов {minutes:02} минут"
        #bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        msg_set =  msg_set + f'\nCледущая попытка через { formatted_time}'
        await bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text = msg_set)
        if random.random() < 0.5:
            await abgrade(message)
        await asyncio.sleep(2)


        

    else:
        timenotfomated = wait_time_seconds - (current_time - last_execution_time)
        hours = timenotfomated // 3600
        minutes = (timenotfomated % 3600) // 60
        seconds = timenotfomated % 60
        hours = round(hours)
        minutes = round(minutes)
        seconds = round(seconds)
        formatted_time = f"{hours:02} часов {minutes:02} минут"
        await message.reply(f'подождите еще { formatted_time}')
rangeupnum = None

@dp.message_handler(commands=['clear'])
async def abgrade(message: types.Message) :
    conn = sqlite3.connect('kukuruza.sql')
    cur = conn.cursor()
    cur.execute('DELETE FROM otrezat;')
    conn.commit()
    cur.close()
    conn.close()
    await message.answer("done!")


@dp.message_handler(commands=['abgrade'])
async def abgrade(message: types.Message) :
     #КУКУРУЗА КОУНТ
    
    
    if message.sender_chat:
        username123 = message.sender_chat.id
    else:
        username123 = message.from_user.id
    
    if message.sender_chat:
        userid = message.sender_chat.id
    else:
        userid = message.from_user.id
    if message.sender_chat:
        conn = sqlite3.connect('kukuruza.sql')
        cur = conn.cursor()
        cur.execute("UPDATE statistics SET commands_count = commands_count + 1 WHERE id = ?", (username123,))
        msg_id = message.message_id
        cur.execute('SELECT rangeupup FROM users WHERE username = ?', (userid,))
        result = cur.fetchone()
        if result is None:
            rangeupup = 0
        else:
            rangeupup = result[0]
        ruu_num = rangeupup + 5
        rangeupnum = random.randint(1, ruu_num)
        cur.execute("INSERT INTO otrezat (id, rangeupnum, id_message, otrezat, id_chat) VALUES (?, ?, ?, ?, ?)", (message.sender_chat.id, rangeupnum, msg_id, False, message.chat.id))

        conn.commit()
        cur.close()
        conn.close()
        await message.reply (f'<a href="https://t.me/{message.sender_chat.id}"> {message.from_user.first_name}</a>! ты заработал <b>{rangeupnum}</b> очков улушения! ты можешь что-то улучшить!' , parse_mode='html', disable_web_page_preview=True)

        await message.answer(f'1. увеличить разброс рулетки на {rangeupnum}!!! \n2. уменьшить кд на {rangeupnum} мин!!! \n3.отрезат пиписа сопернику на {rangeupnum} см!!! \n4. увеличить рандом баллов улучшения на 1!!! \n5. подарить {rangeupnum}см своей пиписи... ')
        await message.answer(f'Вы пишете от лица канала или чата, поэтому отправьте выбранный вариант ответом на это сообщение')
        await message.answer(message.sender_chat.id)

        return

    conn = sqlite3.connect('kukuruza.sql')
    cur = conn.cursor()
    cur.execute("UPDATE statistics SET commands_count = commands_count + 1 WHERE id = ?", (username123,))
    conn.commit()
    cur.close()
    conn.close()

    conn = sqlite3.connect('kukuruza.sql')
    cur = conn.cursor()

        # Создание таблицы, если она еще не существует
    cur.execute("""
        CREATE TABLE IF NOT EXISTS otrezat (
            id INTEGER,
            rangeupnum INTEGER,
            id2 INTEGER,
            id_message INTEGER,
            otrezat BOOLEAN DEFAULT 0,
            id_chat INTEGER
        )
    """)
    if message.sender_chat:
        userid = message.sender_chat.id
    else:
        userid = message.from_user.id
    msg_id = message.message_id
    cur.execute('SELECT rangeupup FROM users WHERE username = ?', (userid,))
    result = cur.fetchone()
    if result is None:
        rangeupup = 0
    else:
        rangeupup = result[0]
    ruu_num = rangeupup + 5
    rangeupnum = random.randint(1, ruu_num)
    cur.execute("INSERT INTO otrezat (id, rangeupnum, id_message, otrezat, id_chat) VALUES (?, ?, ?, ?, ?)", (userid, rangeupnum, msg_id, False, message.chat.id))

    conn.commit()
    cur.close()
    conn.close()

    
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(f'увеличить разброс рулетки на {rangeupnum}!!!', callback_data='rangeup')
    markup.row(btn1)
    btn2 = types.InlineKeyboardButton(f'уменьшить кд на {rangeupnum} мин!!!', callback_data='kddwn')
    markup.row(btn2)
    btn3 = types.InlineKeyboardButton(f'отрезат пиписа сопернику на {rangeupnum} см!!!', callback_data='otrezat')
    markup.row(btn3)
    btn4 = types.InlineKeyboardButton(f'увеличить рандом баллов улучшения на 1!!! ', callback_data='rangeupup')
    markup.row(btn4)
    btn5 = types.InlineKeyboardButton(f'подарить {rangeupnum}см своей пиписи... ', callback_data='present')
    markup.row(btn5)





    await message.reply (f'<a href="https://t.me/{message.from_user.username}"> {message.from_user.first_name}</a>! ты заработал <b>{rangeupnum}</b> очков улушения! ты можешь что-то улучшить!' , parse_mode='html', disable_web_page_preview=True, reply_markup=markup)




userid = None
msg_id = None
@dp.callback_query_handler(lambda call: True)
async def callbackmessage(call: types.CallbackQuery):
    
    global rangeupnum
    global userid
    global msg_id
    if call.data == 'rangeup':
        # Получаем имя пользователя, который нажал кнопку
        callback_username = call.from_user.id
        #bot.send_message(call.message.chat.id, callback_username)
        # Проверяем, есть ли сообщение, на которое нужно ответить
        if call.message.reply_to_message is not None:
            # Получаем имя пользователя, которому было адресовано первоначальное сообщение
            #message_username = call.message.reply_to_message.from_user.id
            if call.message.sender_chat:
                message_username = call.message.reply_to_message.sender_chat.id
            else:
                message_username = call.message.reply_to_message.from_user.id
            # Проверяем, являются ли они одним и тем же пользователем
            if callback_username == message_username:
                
                conn = sqlite3.connect('kukuruza.sql')
                cur = conn.cursor()
                #bot.send_message(call.message.chat.id, callback_username)
                cur.execute('SELECT rangeupnum FROM otrezat WHERE id = ?', (callback_username,))
                rangeupnum = cur.fetchone()[0]
                cur.execute('SELECT range FROM users WHERE username = ?', (callback_username,))
                range2 = cur.fetchone()[0] + rangeupnum

                cur.execute('UPDATE users SET range = ? WHERE username = ?', (range2, callback_username))
                cur.execute("DELETE FROM otrezat WHERE id = ?",(callback_username,))
                conn.commit()
                cur.close()
                conn.close()
                await call.message.reply(f'разброс при увелечении члена теперь от {-5 - range2} до {10 + range2} см!!!')
                row = await insert_user_message(message_username, 'nickname', 'name', f"установил разброс при увелечении члена теперь от {-5 - range2} до {10 + range2} см", f'{rangeupnum}', 0)
                await bot.send_message(-1002102077131, f"Добавлена строка: {row}")
                await bot.delete_message(call.message.chat.id, call.message.message_id)
                
            else:
                await bot.answer_callback_query(call.id, "Вы не можете использовать эту кнопку!")
        else:
            await bot.answer_callback_query(call.id, "Сообщение, на которое вы пытаетесь ответить, не существует!")
    elif call.data == 'kddwn':
         # Получаем имя пользователя, который нажал кнопку
        callback_username = call.from_user.id

        # Проверяем, есть ли сообщение, на которое нужно ответить
        if call.message.reply_to_message is not None:
            # Получаем имя пользователя, которому было адресовано первоначальное сообщение
            if call.message.sender_chat:
                message_username = call.message.reply_to_message.sender_chat.id
            else:
                message_username = call.message.reply_to_message.from_user.id
            # Проверяем, являются ли они одним и тем же пользователем
            if callback_username == message_username:
                
                conn = sqlite3.connect('kukuruza.sql')
                cur = conn.cursor()
                #bot.send_message(call.message.chat.id, callback_username)
                cur.execute('SELECT rangeupnum FROM otrezat WHERE id = ?', (callback_username,))
                rangeupnum = cur.fetchone()[0]
                cur.execute('SELECT wait_time_seconds FROM users WHERE username = ?', (callback_username,))
                result = cur.fetchone()
                #bot.send_message(call.message.chat.id, rangeupnum)
                range2 = result[0] - rangeupnum * 60
                await bot.delete_message(call.message.chat.id, call.message.message_id)

                if range2 < 0:
                    range2 = 0
                cur.execute('UPDATE users SET wait_time_seconds = ? WHERE username = ?', (range2, callback_username))
                cur.execute("DELETE FROM otrezat WHERE id = ?",(callback_username,))

                conn.commit()
                cur.close()
                conn.close()
                timenotfomated = range2
                hours = timenotfomated // 3600
                minutes = (timenotfomated % 3600) // 60
                seconds = timenotfomated % 60
                hours = round(hours)
                minutes = round(minutes)
                seconds = round(seconds)
                formatted_time = f"{hours:02} часов {minutes:02} минут {seconds:02} секунд "
                await call.message.reply_to_message.reply(f'Ваш кд теперь {formatted_time}')
                row = await insert_user_message(message_username, 'nickname', 'name', f"установил кд теперь {formatted_time}", f'{rangeupnum}', 0)
                await bot.send_message(-1002102077131, f"Добавлена строка: {row}")
            else:
                await bot.answer_callback_query(call.id, "Вы не можете использовать эту кнопку!")
        else:
            await bot.answer_callback_query(call.id, "Сообщение, на которое вы пытаетесь ответить, не существует!")
    elif call.data == 'otrezat':

         # Получаем имя пользователя, который нажал кнопку
        callback_username = call.from_user.id

        # Проверяем, есть ли сообщение, на которое нужно ответить
        if call.message.reply_to_message is not None:
            # Получаем имя пользователя, которому было адресовано первоначальное сообщение
            if call.message.sender_chat:
                message_username = call.message.reply_to_message.sender_chat.id
            else:
                message_username = call.message.reply_to_message.from_user.id
            # Проверяем, являются ли они одним и тем же пользователем
            if callback_username == message_username:
                await bot.delete_message(call.message.chat.id, call.message.message_id)
                
                conn = sqlite3.connect('kukuruza.sql')
                cur = conn.cursor()


                cur.execute("UPDATE otrezat SET otrezat = ? WHERE id = ?", (True, call.message.reply_to_message.from_user.id))

                conn.commit()
                cur.close()
                conn.close()
        

                
                await call.message.reply_to_message.reply("Отправьте юзернэйм пользователя ответом на это сообщение")

                
            else:
                await bot.answer_callback_query(call.id, "Вы не можете использовать эту кнопку!")
        else:
            await bot.answer_callback_query(call.id, "Сообщение, на которое вы пытаетесь ответить, не существует!")

    elif call.data == 'pg0':
        # Получаем имя пользователя, который нажал кнопку
        callback_username = call.from_user.id

        # Проверяем, есть ли сообщение, на которое нужно ответить
        if call.message.reply_to_message is not None:
            # Получаем имя пользователя, которому было адресовано первоначальное сообщение
            if call.message.sender_chat:
                message_username = call.message.reply_to_message.sender_chat.id
            else:
                message_username = call.message.reply_to_message.from_user.id
            # Проверяем, являются ли они одним и тем же пользователем
            if callback_username == message_username:
                username_to_delete = call.from_user.id
                conn = sqlite3.connect('kukuruza.sql')
                cur = conn.cursor()
# Выполнение SQL-запроса
                cur.execute("SELECT name FROM users WHERE username = ?", (username_to_delete,))
                result = cur.fetchone()
                if result is None:
                    name = "anonim"
                else:
                    name = result[0]
                #bot.send_message(call.message.chat.id, username_to_delete)
                cur.execute("SELECT nickname FROM users WHERE username = ?", (username_to_delete,))
                result = cur.fetchone()
                if result is None:
                    nickname = "Анонимный пользователь"
                else:
                    nickname = result[0]
                cur.execute("DELETE FROM users WHERE username = ?", (username_to_delete,))
                cur.execute("DELETE FROM statistics WHERE id = ?", (username_to_delete,))
                cur.execute("DELETE FROM user_chats WHERE id = ?", (username_to_delete,))
                conn.commit()
                cur.close()
                conn.close()
                await bot.delete_message(call.message.chat.id, call.message.message_id)
                await bot.send_message(call.message.chat.id, f'{nickname} сбросил свой прогресс')
                row = await insert_user_message(message_username, 'nickname', 'name', f"сбросил прогресс {formatted_time}", f'{rangeupnum}', 0)
                await bot.send_message(-1002102077131, f"Добавлена строка: {row}")
            else:
                await bot.answer_callback_query(call.id, "Вы не можете использовать эту кнопку!")
        else:
            await bot.answer_callback_query(call.id, "Сообщение, на которое вы пытаетесь ответить, не существует!")
    elif call.data == 'cancel':
        # Получаем имя пользователя, который нажал кнопку
        callback_username = call.from_user.id

        # Проверяем, есть ли сообщение, на которое нужно ответить
        if call.message.reply_to_message is not None:
            # Получаем имя пользователя, которому было адресовано первоначальное сообщение
            if call.message.sender_chat:
                message_username = call.message.reply_to_message.sender_chat.id
            else:
                message_username = call.message.reply_to_message.from_user.id
            # Проверяем, являются ли они одним и тем же пользователем
            if callback_username == message_username:
                
                await bot.delete_message(call.message.chat.id, call.message.message_id)
                
            else:
                await bot.answer_callback_query(call.id, "Вы не можете использовать эту кнопку!")
        else:
            await bot.answer_callback_query(call.id, "Сообщение, на которое вы пытаетесь ответить, не существует!")
    elif call.data == 'rangeupup':
        # Получаем имя пользователя, который нажал кнопку
        callback_username = call.from_user.id

        # Проверяем, есть ли сообщение, на которое нужно ответить
        if call.message.reply_to_message is not None:
            # Получаем имя пользователя, которому было адресовано первоначальное сообщение
            if call.message.sender_chat:
                message_username = call.message.reply_to_message.sender_chat.id
            else:
                message_username = call.message.reply_to_message.from_user.id
            # Проверяем, являются ли они одним и тем же пользователем
            if callback_username == message_username:
                conn = sqlite3.connect('kukuruza.sql')
                cur = conn.cursor()
                #bot.send_message(call.message.chat.id, callback_username)
                cur.execute('SELECT rangeupup FROM users WHERE username = ?', (callback_username,))
                result = cur.fetchone()
                if result is None:
                    rangeupup = 0
                else:
                    rangeupup = result[0]
                cur.execute('SELECT rangeupnum FROM otrezat WHERE id = ?', (callback_username,))
                rangeupnum = cur.fetchone()[0]
                #bot.send_message(call.message.chat.id, rangeupnum)
                new_ruu = rangeupup + 1

                cur.execute('UPDATE users SET rangeupup = ? WHERE username = ?', (new_ruu, callback_username))
                cur.execute("DELETE FROM otrezat WHERE id = ?",(callback_username,))

                conn.commit()
                cur.close()
                conn.close()
                await call.message.reply_to_message.reply(f'разброс очков улучшения теперь теперь от 1 до {5 + new_ruu} баллов!!!')
                row = await insert_user_message(message_username, 'nickname', "name", f"установил разброс очков улучшения теперь теперь от 1 до {5 + new_ruu} баллов", f'{rangeupnum}', 0)
                await bot.send_message(-1002102077131, f"Добавлена строка: {row}")

                await bot.delete_message(call.message.chat.id, call.message.message_id)
  
                
            else:
                await bot.answer_callback_query(call.id, "Вы не можете использовать эту кнопку!")
        else:
            await bot.answer_callback_query(call.id, "Сообщение, на которое вы пытаетесь ответить, не существует!")
    elif call.data == 'present':

         # Получаем имя пользователя, который нажал кнопку
        callback_username = call.from_user.id

        # Проверяем, есть ли сообщение, на которое нужно ответить
        if call.message.reply_to_message is not None:
            # Получаем имя пользователя, которому было адресовано первоначальное сообщение
            if call.message.sender_chat:
                message_username = call.message.reply_to_message.sender_chat.id
            else:
                message_username = call.message.reply_to_message.from_user.id
            # Проверяем, являются ли они одним и тем же пользователем
            if callback_username == message_username:
                await bot.delete_message(call.message.chat.id, call.message.message_id)
                
                conn = sqlite3.connect('kukuruza.sql')
                cur = conn.cursor()


                cur.execute("UPDATE otrezat SET otrezat = ? WHERE id = ?", (True, call.message.reply_to_message.from_user.id))

                conn.commit()
                cur.close()
                conn.close()
        

                
                await call.message.reply_to_message.reply("Отправьте юзернэйм пользователя с кем поделиться пиписей ответом на это сообщение")
                
            else:
                await bot.answer_callback_query(call.id, "Вы не можете использовать эту кнопку!")
        else:
            await bot.answer_callback_query(call.id, "Сообщение, на которое вы пытаетесь ответить, не существует!")












from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

class ReplyToMessageFilter(BoundFilter):
    key = 'reply_to_message'

    def __init__(self, reply_to_message):
        self.reply_to_message = reply_to_message

    async def check(self, message: types.Message):
        return message.reply_to_message is not None and message.reply_to_message.text == self.reply_to_message

# Регистрация фильтра
dp.filters_factory.bind(ReplyToMessageFilter)

@dp.message_handler(reply_to_message='Отправьте юзернэйм пользователя ответом на это сообщение')
async def handle_username_reply(message: types.Message):
    # ваш код здесь
    # ваш код здесь
  
    chat_id = message.chat.id
    replied_message_id = message.reply_to_message.message_id
    #bot.delete_message(chat_id, replied_message_id)

    global rangeupnum
    global userid
    global msg_id
    conn = sqlite3.connect('kukuruza.sql')
    cur = conn.cursor()
    if message.sender_chat:
        userid1 = message.sender_chat.id
    else:
        userid1 = message.from_user.id
    await bot.send_message(-1002102077131, f"{userid1}")
    #await bot.reply (userid1)
    cur.execute("SELECT otrezat FROM otrezat WHERE id = ?", (userid1,))
    result = cur.fetchone()
    if result is not None:
        otresat = result[0]
        if otresat == True:
            username = message.text.replace('@', '')
            if check_user_in_db(username):
                #bot.reply_to(message, username)
                conn = sqlite3.connect('kukuruza.sql')
                cur = conn.cursor()
                cur.execute("SELECT rangeupnum FROM otrezat WHERE id = ?", (userid1,))
                rangeupnum1 = cur.fetchone()[0]
                cur.execute("SELECT progress FROM users WHERE nickname = ?", (username,))
                prgrs = cur.fetchone()[0] 
                if message.from_user.username != username:
                    if prgrs != 0:
                        #bot.reply_to(message, prgrs)
                        cur.execute(f"UPDATE users SET progress = progress - {rangeupnum1} WHERE nickname = ?", (username,))
                        conn.commit()
                        cur.execute("SELECT progress FROM users WHERE nickname = ?", (username,))
                        prgrs2 = cur.fetchone()[0]
                        cur.execute("SELECT name FROM users WHERE username = ?", (userid1,))
                        name = cur.fetchone()[0]
                        cur.execute("SELECT name FROM users WHERE nickname = ?", (username,))
                        name2 = cur.fetchone()[0]
                        cur.execute("SELECT username FROM users WHERE nickname = ?", (username,))
                        id_otrezat = cur.fetchone()[0]
                        cur.execute(f"UPDATE statistics SET otrezat_send = otrezat_send + 1 WHERE id = ?", (userid1,))
                        cur.execute(f"UPDATE statistics SET otrezat_received = otrezat_received + 1 WHERE id = ?", (id_otrezat,))



                        if prgrs2 < 0:
                            cur.execute(f"UPDATE users SET progress = 0 WHERE nickname = ?", (username,))
                            prgrs2 = 0
                            await message.answer(f"<a href='https://t.me/{message.from_user.username}'> {name}</a> отрезает {rangeupnum1}см у <a href='https://t.me/{username}'> {name2}</a>! теперь у него 0см!", parse_mode='html', disable_web_page_preview=True)
                            #bot.delete_message(chat_id, replied_message_id)

                        else:   
                            await message.reply_to_message.reply(f"<a href='https://t.me/{message.from_user.username}'> {name}</a> отрезает {rangeupnum1}см у <a href='https://t.me/{username}'> {name2}</a>! теперь у него {prgrs2}см!", parse_mode='html', disable_web_page_preview=True)


                            cur.execute("SELECT id_message FROM otrezat WHERE id = ?", (userid1,))
                            id_msg = cur.fetchone()[0] 
                            cur.execute("SELECT id_chat FROM otrezat WHERE id = ?", (userid1,))
                            id_chat = cur.fetchone()[0] 
                        conn.commit()
                        cur.close()
                        conn.close()
                        row = await insert_user_message(userid1, message.from_user.username, name, f"отрезает {rangeupnum1}см у {name2}</a>! теперь у него {prgrs2}см!", f'{rangeupnum1}', prgrs2)
                        await bot.send_message(-1002102077131, f"Добавлена строка: {row}")
                        conn = sqlite3.connect('kukuruza.sql')
                        cur = conn.cursor()

                        await bot.delete_message(chat_id, replied_message_id)
                        cur.execute("DELETE FROM otrezat WHERE id = ?",(userid1,))
                        conn.commit()
                        cur.close()
                        conn.close()
                    else:
                        await message.reply_to_message.reply(f"он без писюна! выбери еще раз")
                else:
                    await message.reply_to_message.reply(f"Себе нельзя отрезать пипися.🤨 попробуй еще раз")
            elif check_user_in_db2:
                #bot.reply_to(message, username)
                conn = sqlite3.connect('kukuruza.sql')
                cur = conn.cursor()
                cur.execute("SELECT rangeupnum FROM otrezat WHERE id = ?", (userid1,))
                rangeupnum1 = cur.fetchone()[0]
                cur.execute("SELECT progress FROM users WHERE username = ?", (username,))
                re = cur.fetchone() 
                if re:
                    prgrs = re[0]
                else:
                    prgrs = 0
                if userid1 != username:
  
                    #bot.reply_to(message, prgrs)
                    if re - rangeupnum1 < 0:
                        cur.execute(f"UPDATE users SET progress = 0 WHERE username = ?", (username,))
                    else:


                        cur.execute(f"UPDATE users SET progress = progress - {rangeupnum1} WHERE username = ?", (username,))
                    conn.commit()
                    cur.execute("SELECT progress FROM users WHERE username = ?", (username,))
                    prgrs2 = cur.fetchone()[0]
                    cur.execute("SELECT name FROM users WHERE username = ?", (userid1,))
                    name = cur.fetchone()[0]
                    cur.execute("SELECT name FROM users WHERE username = ?", (username,))
                    name2 = cur.fetchone()[0]
                    cur.execute("SELECT username FROM users WHERE username = ?", (username,))
                    id_otrezat = cur.fetchone()[0]
                    cur.execute(f"UPDATE statistics SET otrezat_send = otrezat_send + 1 WHERE id = ?", (userid1,))
                    cur.execute(f"UPDATE statistics SET otrezat_received = otrezat_received + 1 WHERE id = ?", (id_otrezat,))

                    if prgrs2 < 0:
                        cur.execute(f"UPDATE users SET progress = 0 WHERE username = ?", (username,))
                        prgrs2 = 0
                        await message.answer(f"<a href='https://t.me/{message.from_user.username}'> {name}</a> отрезает {rangeupnum1}см у <a href='https://t.me/{username}'> {name2}</a>! теперь у него 0см!", parse_mode='html', disable_web_page_preview=True)
                        #bot.delete_message(chat_id, replied_message_id)
                    else:   
                        await message.reply_to_message.reply(f"<a href='https://t.me/{message.from_user.username}'> {name}</a> отрезает {rangeupnum1}см у <a href='https://t.me/{username}'> {name2}</a>! теперь у него {prgrs2}см!", parse_mode='html', disable_web_page_preview=True)
                        cur.execute("SELECT id_message FROM otrezat WHERE id = ?", (userid1,))
                        id_msg = cur.fetchone()[0] 
                        cur.execute("SELECT id_chat FROM otrezat WHERE id = ?", (userid1,))
                        id_chat = cur.fetchone()[0] 
                    conn.commit()
                    cur.close()
                    conn.close()
                    row = await insert_user_message(userid1, message.from_user.username, name, f"отрезает {rangeupnum1}см у {name2}</a>! теперь у него {prgrs2}см!", f'{rangeupnum1}', result)
                    await bot.send_message(-1002102077131, f"Добавлена строка: {row}")
                    conn = sqlite3.connect('kukuruza.sql')
                    cur = conn.cursor()
                    await bot.delete_message(chat_id, replied_message_id)
                    cur.execute("DELETE FROM otrezat WHERE id = ?",(userid1,))
                    conn.commit()
                    cur.close()
                    conn.close()            
            else:
                        # пользователя нет в базе данных
                await message.reply_to_message.reply(f"Пользователь не найден")
        else:
            await message.reply_to_message.reply(f"у тебя нет очков улучшения")
    else:
        await message.reply_to_message.reply(f"у тебя нет очков улучшения")
@dp.message_handler(reply_to_message='Вы пишете от лица канала или чата, поэтому отправьте выбранный вариант ответом на это сообщение')
async def handle_username_reply(message: types.Message):
    # ваш код здесь
    # ваш код здесь

    #bot.delete_message(chat_id, replied_message_id)
    await message.answer(message.sender_chat.id)

    global rangeupnum
    global userid
    global msg_id
    conn = sqlite3.connect('kukuruza.sql')
    cur = conn.cursor()

    userid1 = message.sender_chat.id

    cur.execute("SELECT otrezat FROM otrezat WHERE id = ?", (userid1,))
    result = cur.fetchone()
    await message.answer(result)

    otresat = result[0]
    if otresat == True:
        text = message.text
        if text == '1':
            await message.answer('1')
        elif text == '2':
            await message.answer('2')

        else:
            await message.answer('такого варианта нет')
    else:
        await message.answer('у вас нет очков улучшения')



@dp.message_handler(reply_to_message='Отправьте юзернэйм пользователя с кем поделиться пиписей ответом на это сообщение')
async def handle_username_reply(message: types.Message):
    # ваш код здесь
    # ваш код здесь

    chat_id = message.chat.id
    replied_message_id = message.reply_to_message.message_id
    #bot.delete_message(chat_id, replied_message_id)

    global rangeupnum
    global userid
    global msg_id
    conn = sqlite3.connect('kukuruza.sql')
    cur = conn.cursor()
    if message.sender_chat:
        userid1 = message.sender_chat.id
    else:
        userid1 = message.from_user.id
    cur.execute("SELECT otrezat FROM otrezat WHERE id = ?", (userid1,))
    result = cur.fetchone()
    
    otresat = result[0]
    if otresat == True:
        username = message.text.replace('@', '')
        if check_user_in_db(username):
            #bot.reply_to(message, username)
            conn = sqlite3.connect('kukuruza.sql')
            cur = conn.cursor()
            cur.execute("SELECT rangeupnum FROM otrezat WHERE id = ?", (userid1,))
            rangeupnum1 = cur.fetchone()[0]
            cur.execute("SELECT progress FROM users WHERE nickname = ?", (username,))
            prgrs = cur.fetchone()[0] 
            cur.execute("SELECT progress FROM users WHERE username = ?", (userid1,))
            pg = cur.fetchone()[0]

            if message.from_user.username != username:
                #bot.reply_to(message, prgrs)
                if pg - rangeupnum1<0:
                    cur.execute(f"UPDATE users SET progress = progress + {pg} WHERE nickname = ?", (username,))
                    cur.execute(f"UPDATE users SET progress = 0 WHERE username = ?", (userid1,))
                else:
                    cur.execute(f"UPDATE users SET progress = progress + {rangeupnum1} WHERE nickname = ?", (username,))
                    cur.execute(f"UPDATE users SET progress = progress - {rangeupnum1} WHERE username = ?", (userid1,))
                conn.commit()
                cur.execute("SELECT progress FROM users WHERE nickname = ?", (username,))
                prgrs2 = cur.fetchone()[0]
                cur.execute("SELECT name FROM users WHERE username = ?", (userid1,))
                name = cur.fetchone()[0]
                cur.execute("SELECT name FROM users WHERE nickname = ?", (username,))
                name2 = cur.fetchone()[0]
                cur.execute("SELECT username FROM users WHERE nickname = ?", (username,))
                id_otrezat = cur.fetchone()[0]
                #await message.answer (rangeupnum1)
                cur.execute(f"UPDATE statistics SET otrezat_send = otrezat_send + 1 WHERE id = ?", (userid1,))
                cur.execute(f"UPDATE statistics SET otrezat_received = otrezat_received + 1 WHERE id = ?", (id_otrezat,))
                conn.commit()
                cur.close()
                conn.close()    
                await message.reply_to_message.reply(f"<a href='https://t.me/{message.from_user.username}'> {name}</a> дарит {rangeupnum1}см <a href='https://t.me/{username}'> {name2}</a>! теперь у них: \n⏫<a href='https://t.me/{username}'> {name2}</a> - {prgrs2}см!\n⏬<a href='https://t.me/{message.from_user.username}'> {name}</a> - {pg}см", parse_mode='html', disable_web_page_preview=True)
                row = await insert_user_message(userid1, message.from_user.username, name, f"отрезает {rangeupnum1}см у {name2}</a>! теперь у него {prgrs2}см!", f'{rangeupnum1}', prgrs2)
                conn = sqlite3.connect('kukuruza.sql')
                cur = conn.cursor()
                await bot.send_message(-1002102077131, f"Добавлена строка: {row}")
                cur.execute("SELECT id_message FROM otrezat WHERE id = ?", (userid1,))
                id_msg = cur.fetchone()[0] 
                cur.execute("SELECT id_chat FROM otrezat WHERE id = ?", (userid1,))
                id_chat = cur.fetchone()[0] 
                await bot.delete_message(chat_id, replied_message_id)
                cur.execute("DELETE FROM otrezat WHERE id = ?",(userid1,))
                conn.commit()
                cur.close()
                conn.close()
            else:
                await message.reply_to_message.reply(f"Себе нельзя подарить пипися.🤨 попробуй еще раз")
        elif check_user_in_db2:
            #bot.reply_to(message, username)
            conn = sqlite3.connect('kukuruza.sql')
            cur = conn.cursor()
            cur.execute("SELECT rangeupnum FROM otrezat WHERE id = ?", (userid1,))
            rangeupnum1 = cur.fetchone()[0]
            cur.execute("SELECT progress FROM users WHERE username = ?", (username,))
            prgrs = cur.fetchone()[0] 
            if userid1 != username:
                
                #bot.reply_to(message, prgrs)
                if message.from_user.username != username:
                    #bot.reply_to(message, prgrs)
                    if pg - rangeupnum1<0:
                        cur.execute(f"UPDATE users SET progress = progress + {pg} WHERE nickname = ?", (username,))
                        cur.execute(f"UPDATE users SET progress = 0 WHERE username = ?", (userid1,))
                    else:
                        cur.execute(f"UPDATE users SET progress = progress + {rangeupnum1} WHERE nickname = ?", (username,))
                        cur.execute(f"UPDATE users SET progress = progress - {rangeupnum1} WHERE username = ?", (userid1,))
                conn.commit()
                cur.execute("SELECT progress FROM users WHERE username = ?", (username,))
                prgrs2 = cur.fetchone()[0]
                cur.execute("SELECT name FROM users WHERE username = ?", (userid1,))
                name = cur.fetchone()[0]
                cur.execute("SELECT name FROM users WHERE username = ?", (username,))
                name2 = cur.fetchone()[0]
                cur.execute("SELECT username FROM users WHERE username = ?", (username,))
                id_otrezat = cur.fetchone()[0]
                cur.execute(f"UPDATE statistics SET otrezat_send = otrezat_send + 1 WHERE id = ?", (userid1,))
                cur.execute(f"UPDATE statistics SET otrezat_received = otrezat_received + 1 WHERE id = ?", (id_otrezat,))
                cur.execute("SELECT progress FROM users WHERE username = ?", (userid1,))
                pg = cur.fetchone()[0]
                await message.reply_to_message.reply(f"<a href='https://t.me/{message.from_user.username}'> {name}</a> дарит {rangeupnum1}см <a href='https://t.me/{username}'> {name2}</a>! теперь у них: \n⏫<a href='https://t.me/{username}'> {name2}</a> - {prgrs2}см!\n⏬<a href='https://t.me/{message.from_user.username}'> {name}</a> - {pg}см", parse_mode='html', disable_web_page_preview=True)
                row = await insert_user_message(userid1, message.from_user.username, name, f"дарит {rangeupnum1}сm {name2}! теперь у них: \n⏫{name2} - {prgrs2}см!\n⏬{name} - {pg}см", f'{rangeupnum1}', result)
                await bot.send_message(-1002102077131, f"Добавлена строка: {row}")
                cur.execute("SELECT id_message FROM otrezat WHERE id = ?", (userid1,))
                id_msg = cur.fetchone()[0] 
                cur.execute("SELECT id_chat FROM otrezat WHERE id = ?", (userid1,))
                id_chat = cur.fetchone()[0] 
                await bot.delete_message(chat_id, replied_message_id)
                cur.execute("DELETE FROM otrezat WHERE id = ?",(userid1,))
                conn.commit()
                cur.close()
                conn.close()

            
        else:
                    # пользователя нет в базе данных
            await message.reply_to_message.reply(f"Пользователь не найден")
    else:
        await message.reply_to_message.reply(f"у тебя нет очков улучшения")

        

def check_user_in_db(username):
    conn = sqlite3.connect('kukuruza.sql')  # подключение к вашей базе данных
    cursor = conn.cursor()
    cursor.execute(f"SELECT progress FROM users WHERE nickname = '{username}'")  # выполнение SQL-запроса
    user = cursor.fetchone()  # получение результата запроса
    conn.close()  # закрытие соединения с базой данных
    return user is not None  # возвращает True, если пользователь найден, иначе False
def check_user_in_db2(username):
    conn = sqlite3.connect('kukuruza.sql')  # подключение к вашей базе данных
    cursor = conn.cursor()
    cursor.execute(f"SELECT progress FROM users WHERE username = '{username}'")  # выполнение SQL-запроса
    user = cursor.fetchone()  # получение результата запроса
    conn.close()  # закрытие соединения с базой данных
    return user is not None  # возвращает True, если пользователь найден, иначе False

@dp.message_handler(commands=['top'])
async def top(message) :
     #КУКУРУЗА КОУНТ
    
    conn = sqlite3.connect('kukuruza.sql')
    cur = conn.cursor()
    if message.sender_chat:
        username123 = message.sender_chat.id
    else:
        username123 = message.from_user.id
    cur.execute("UPDATE statistics SET commands_count = commands_count + 1 WHERE id = ?", (username123,))
    conn.commit()
    cur.close()
    conn.close()




    conn = sqlite3.connect('kukuruza.sql')
    cur = conn.cursor()
    #msg = bot.send_message(message.chat.id, 'Топ данного чата')
    # Выборка всех пользователей по прогрессу
    cur.execute("SELECT nickname, progress, wait_time_seconds, range FROM users ORDER BY progress DESC")
    all_users = cur.fetchall()

    # Форматирование и отправка сообщения
    message1 = "<b>Топ данного чата</b> \n"
    medals = ["🥇", "🥈", "🥉"]
    count = 0
    for user in all_users:
        
        if count >= 10:
            break
        nickname, progress, wait_time_seconds, range2 = user
        
        conn = sqlite3.connect('kukuruza.sql')
        cur = conn.cursor()
        cur.execute("SELECT name FROM users WHERE nickname = ?", (nickname,))
        firstname = cur.fetchone()[0]


        # Получение списка ID чатов для данного пользователя
        user_chats = get_user_chats(nickname)

        # Если пользователь находится в текущем чате
        if message.chat.id in user_chats:
            #time.sleep(0.5)
            hours, remainder = divmod(wait_time_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            cooldown = f"{hours}часа {minutes}мин {seconds}сек"
            dispersion = f"от {-5-range2} до {10+range2}"
            medal = medals[count] if count < 3 else f"{count+1} -"
            message1 += f"\n{medal} <a href='https://t.me/{nickname}'> {firstname}</a>! {progress}см "
            count += 1
            #bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text = f'{message1}...', parse_mode='html', disable_web_page_preview=True)

    # Если в топе меньше 10 пользователей, добавляем пустые места
    if count < 10:
        for i in range(count, 10):
            message1 += f"\n{i+1} - нет пользователя"
            #time.sleep(0.1)
            #bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text = f'{message1}...', parse_mode='html', disable_web_page_preview=True)
        
    #bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text = f'{message1}', parse_mode='html', disable_web_page_preview=True)
    await bot.send_message(message.chat.id, f'{message1}', parse_mode='html', disable_web_page_preview=True)


@dp.message_handler(commands=['topwrld'])
async def top(message) :
     #КУКУРУЗА КОУНТ

    conn = sqlite3.connect('kukuruza.sql')
    cur = conn.cursor()
    if message.sender_chat:
        username123 = message.sender_chat.id
    else:
        username123 = message.from_user.id
    cur.execute("UPDATE statistics SET commands_count = commands_count + 1 WHERE id = ?", (username123,))
    conn.commit()
    cur.close()
    conn.close()













    conn = sqlite3.connect('kukuruza.sql')
    cur = conn.cursor()
    #msg = bot.send_message(message.chat.id, 'Топ')
    # Выборка всех пользователей по прогрессу
    cur.execute("SELECT nickname, progress, wait_time_seconds, range FROM users ORDER BY progress DESC")
    all_users = cur.fetchall()

    # Форматирование и отправка сообщения
    message1 = "<b>Топ бота</b> \n"
    medals = ["🥇", "🥈", "🥉"]
    count = 0
    for user in all_users:
        
        if count >= 10:
            break
        nickname, progress, wait_time_seconds, range2 = user
        
        conn = sqlite3.connect('kukuruza.sql')
        cur = conn.cursor()
        cur.execute("SELECT name FROM users WHERE nickname = ?", (nickname,))
        firstname = cur.fetchone()[0]


        # Получение списка ID чатов для данного пользователя
        user_chats = get_user_chats(nickname)

        # Если пользователь находится в текущем чате
        if True:
            #time.sleep(0.5)
            hours, remainder = divmod(wait_time_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            cooldown = f"{hours}часа {minutes}мин {seconds}сек"
            dispersion = f"от {-5-range2} до {10+range2}"
            medal = medals[count] if count < 3 else f"{count+1} -"
            #message1 += f"\n{medal} <a href='https://t.me/{nickname}'> {firstname}</a>! {progress}см \nс кулдауном {cooldown} \nс разбросом {dispersion}\n"
            message1 += f"\n{medal} <a href='https://t.me/{nickname}'> {firstname}</a>! {progress}см "
            
            count += 1
            #bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text = f'{message1}...', parse_mode='html', disable_web_page_preview=True)

    # Если в топе меньше 10 пользователей, добавляем пустые места
    if count < 10:
        for i in range(count, 10):
            message1 += f"\n{i+1} - нет пользователя"
            #time.sleep(0.1)
            #bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text = f'{message1}...', parse_mode='html', disable_web_page_preview=True)
        #message1 += f"если какие то данные отображаются как None не волнуйтесь они скоро появятся!"
    await bot.send_message(message.chat.id, f'{message1}', parse_mode='html', disable_web_page_preview=True)

@dp.message_handler(commands=['topgg'])
async def top(message) :
     #КУКУРУЗА КОУНТ

    conn = sqlite3.connect('kukuruza.sql')
    cur = conn.cursor()
    if message.sender_chat:
        username123 = message.sender_chat.id
    else:
        username123 = message.from_user.id
    cur.execute("UPDATE statistics SET commands_count = commands_count + 1 WHERE id = ?", (username123,))
    conn.commit()
    cur.close()
    conn.close()













    conn = sqlite3.connect('kukuruza.sql')
    cur = conn.cursor()
    #msg = bot.send_message(message.chat.id, 'Топ')
    # Выборка всех пользователей по прогрессу
    cur.execute("SELECT nickname, progress, wait_time_seconds, range FROM users ORDER BY progress DESC")
    all_users = cur.fetchall()

    # Форматирование и отправка сообщения
    message1 = "<b>Топ бота</b> \n"
    medals = ["🥇", "🥈", "🥉"]
    count = 0
    for user in all_users:
        
        if count >= 100:
            break
        nickname, progress, wait_time_seconds, range2 = user
        
        conn = sqlite3.connect('kukuruza.sql')
        cur = conn.cursor()
        cur.execute("SELECT name FROM users WHERE nickname = ?", (nickname,))
        firstname = cur.fetchone()[0]


        # Получение списка ID чатов для данного пользователя
        user_chats = get_user_chats(nickname)

        # Если пользователь находится в текущем чате
        if True:
            #time.sleep(0.5)
            hours, remainder = divmod(wait_time_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            cooldown = f"{hours}часа {minutes}мин {seconds}сек"
            dispersion = f"от {-5-range2} до {10+range2}"
            medal = medals[count] if count < 3 else f"{count+1} -"
            #message1 += f"\n{medal} <a href='https://t.me/{nickname}'> {firstname}</a>! {progress}см \nс кулдауном {cooldown} \nс разбросом {dispersion}\n"
            message1 += f"\n{medal} <a href='https://t.me/{nickname}'> {firstname}</a>! {progress}см "
            
            count += 1
            #bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text = f'{message1}...', parse_mode='html', disable_web_page_preview=True)

    # Если в топе меньше 10 пользователей, добавляем пустые места
    if count < 10:
        for i in range(count, 10):
            message1 += f"\n{i+1} - нет пользователя"
            #time.sleep(0.1)
            #bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text = f'{message1}...', parse_mode='html', disable_web_page_preview=True)
        #message1 += f"если какие то данные отображаются как None не волнуйтесь они скоро появятся!"
    await message.aswer (f'{message1}', parse_mode='html', disable_web_page_preview=True)






def get_user_chats(username):
    conn = sqlite3.connect('kukuruza.sql')
    cur = conn.cursor()

    # Получение ID пользователя
    cur.execute("SELECT id FROM users WHERE nickname = ?", (username,))
    user_id = cur.fetchone()[0]

    # Получение ID чатов
    cur.execute("SELECT chat_id FROM user_chats WHERE user_id = ?", (user_id,))
    chat_ids = [row[0] for row in cur.fetchall()]

    cur.close()
    conn.close()

    return chat_ids


@dp.message_handler(commands=['reg2'])
def register(message):
    conn = sqlite3.connect('kukuruza.sql')
    cur = conn.cursor()

    # Получение ID чата
    chat_id = message.chat.id

    # Получение имени пользователя
    if message.sender_chat:
        username = message.sender_chat.id
    else:
        username = message.from_user.id

    # Добавление пользователя в таблицу users, если его там еще нет
    #cur.execute("INSERT OR IGNORE INTO users (nickname, name) VALUES (?, ?)", (username, message.from_user.first_name))

    # Получение ID пользователя

    cur.execute("SELECT id FROM users WHERE username = ?", (username,))
    result = cur.fetchone()
    user_id = result[0]


    # Проверка на наличие связи пользователя и чата в таблице user_chats
    cur.execute("SELECT 1 FROM user_chats WHERE user_id = ? AND chat_id = ?", (user_id, chat_id))
    exists = cur.fetchone() is not None

    # ееее
    if not exists:
        cur.execute("INSERT INTO user_chats (user_id, chat_id) VALUES (?, ?)", (user_id, chat_id))
    
        conn.commit()
        cur.close()
        conn.close()
        row = insert_user_message(username, 'n/a', 'n/a', f'зареган в чате {chat_id}', result, 'n/a')
        bot.send_message(-1002102077131, f"Добавлена строка: {row}")



# Считываем файл и создаем словарь с матерными словами и пояснениями
with open('bad_words.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()
bad_words_dict = {}
for line in lines:
    if ' — ' in line:  # Проверяем, что строка содержит ' — '
        word, explanation = line.lower().strip().split(' — ', maxsplit=1)
        if word not in bad_words_dict:  # Проверяем, что слово еще не добавлено в словарь
            bad_words_dict[word] = explanation

print(f"Добавлено {len(bad_words_dict)} уникальных слов")

@dp.message_handler()
async def handle_message(message: types.Message):
    # ваш код здесь

    global user_states
    conn = sqlite3.connect('kukuruza.sql')
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL
    )
    """)
    if message.sender_chat:
        username123 = message.sender_chat.id
    else:
        username123 = message.from_user.id
    conn.commit()
    cur.execute("SELECT 1 FROM admins WHERE id = ?", (username123,))
    exists = cur.fetchone() is not None



    cur.close()
    conn.close()

    # Получаем список администраторов чата
    if message.chat.type != "private":
        admins = [admin.user.username for admin in await bot.get_chat_administrators(message.chat.id)]

        # Если сообщение содержит "БАМ" и отправитель является администратором
        if message.text.startswith("БАМ") and ((message.from_user.username in admins or exists) or (message.from_user.username in admins and exists) ):

            # Если сообщение является ответом на другое сообщение, берем имя пользователя из этого сообщения
            if message.reply_to_message:
                username = message.reply_to_message.from_user.username
            # Иначе берем имя пользователя из текста сообщения
            elif len(message.text.split()) == 2:
                username = message.text.split()[1].replace('@', '')  # Удаляем символ '@' из имени пользователя
            else:
                return

            # Если пользователь уже в списке, удаляем его
            if username in user_states and user_states[username] == message.from_user.username:
                del user_states[username]
                await bot.send_message(message.chat.id, f'порча снята с {username}')
            # Иначе добавляем пользователя в список
            else:
                user_states[username] = message.from_user.username
                await bot.send_message(message.chat.id, f'насылаю порчу на {username}')
        elif message.from_user.username not in admins and message.text.startswith("БАМ"):
            await message.reply ('ИДИ НАХУЙ')

        # Если сообщение от пользователя, который находится в списке, удаляем сообщение
        elif message.from_user.username in user_states:
            await bot.delete_message(message.chat.id, message.message_id)
        elif message.text.startswith("БЛЯ БАМ") and message.from_user.username in admins:
            user_states.clear()

            await bot.send_message(message.chat.id, 'Порча снята со всех')
    words = message.text.lower().split()
    conn = sqlite3.connect('kukuruza.sql')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS bad_words (
            chat_id INTEGER
            )
        ''')

    conn.commit()


    cur.execute(f"SELECT * FROM bad_words WHERE chat_id = '{message.chat.id}'")
    rows = cur.fetchall()
    if rows:


        cur.close()
        conn.close()
        #print(bad_words_dict)
        for word in words:
            if word in bad_words_dict:

                await bot.delete_message(message.chat.id, message.message_id)
                msg = await bot.send_message(message.chat.id, f'<a href="https://t.me/{message.from_user.username}"> {message.from_user.first_name}</a>! отправил матершинное слово!!! \n{word} - {bad_words_dict[word]} \nсообщение удаленно!' , parse_mode='html', disable_web_page_preview=True)
                await asyncio.sleep(10)
                await bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=f'<a href="https://t.me/{message.from_user.username}"> {message.from_user.first_name}</a>! отправил матершинное слово!!! \n \nсообщение удаленно!' , parse_mode='html', disable_web_page_preview=True)
#ооо посхалко!
                break
@dp.message_handler(content_types=['voice'])
@command_limiter
async def voice_processing(message):
    conn = sqlite3.connect('updates.db')
    cur = conn.cursor()
    # Проверка, было ли обновление уже обработано
    cur.execute('SELECT update_id FROM updates WHERE update_id = ?', (message.message_id,))
    if cur.fetchone():
        return  # Если обновление уже было обработано, пропустить его

    # Добавление ID обновления в базу данных
    cur.execute('INSERT INTO updates VALUES (?)', (message.message_id,))
    conn.commit()

    text = None


    conn = sqlite3.connect('kukuruza.sql')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS speech_recognition (
            chat_id INTEGER
            )
        ''')

    conn.commit()
    cur.execute(f"SELECT * FROM speech_recognition WHERE chat_id = '{message.chat.id}'")
    rows1 = cur.fetchall()
    cur.execute(f"SELECT * FROM bad_words WHERE chat_id = '{message.chat.id}'")
    rows = cur.fetchall()
    if rows1:
        msg123 = await message.reply ('Распознование речи🧐....')
        await asyncio.sleep(1)
    if (rows1 or rows) or (rows1 and rows):




        file_info = await bot.get_file(message.voice.file_id)
        downloaded_file = await bot.download_file(file_info.file_path)
        try:
            with open('voice.ogg', 'wb') as new_file:
                new_file.write(downloaded_file.read())
        except:
            await bot.delete_message(message.chat.id, msg123.message_id)

        src_filename = 'voice.ogg'
        dest_filename = 'voice.wav'
        process = subprocess.run(['ffmpeg', '-y', '-i', src_filename, dest_filename])
        if process.returncode != 0:
            await bot.edit_message_text(chat_id=message.chat.id, message_id=msg123.message_id, text='error!')
            asyncio.sleep(5)
            await bot.delete_message(message.chat.id, msg123.message_id)

            raise Exception("Error converting ogg to wav.")

        r = sr.Recognizer()
        with sr.AudioFile(dest_filename) as source:
            audio_data = r.record(source)
        
            try:
                text = r.recognize_google(audio_data, language='ru-RU')

                if rows1:
                    if text:
                        await bot.edit_message_text(chat_id=message.chat.id, message_id=msg123.message_id, text=text)
                    else:
                        text = "Бро ничего не сказал🤷"
                        if rows1:
                            await bot.edit_message_text(chat_id=message.chat.id, message_id=msg123.message_id, text=text)
                            await asyncio.sleep(5)
                            await bot.delete_message(message.chat.id, msg123.message_id)
            except:
                text = "Неудалось распознать🤷"
                if rows1:
                    await bot.edit_message_text(chat_id=message.chat.id, message_id=msg123.message_id, text=text)
                    await asyncio.sleep(5)
                    await bot.delete_message(message.chat.id, msg123.message_id)

            
    text2 = text.lower()
    words = text2.split()
    conn = sqlite3.connect('kukuruza.sql')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS bad_words (
            chat_id INTEGER
            )
        ''')

    conn.commit()



    if rows:


        cur.close()
        conn.close()
        #print(bad_words_dict)
        for word in words:
            if word in bad_words_dict:

                await bot.delete_message(message.chat.id, message.message_id)
                msg = bot.send_message(message.chat.id, f'<a href="https://t.me/{message.from_user.username}"> {message.from_user.first_name}</a>! сказал матершинное слово!!! \n{word} - {bad_words_dict[word]} \nсообщение удаленно!' , parse_mode='html', disable_web_page_preview=True)
                time.sleep(10)
                await bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=f'<a href="https://t.me/{message.from_user.username}"> {message.from_user.first_name}</a>! отправил матершинное слово!!! \n \nсообщение удаленно!' , parse_mode='html', disable_web_page_preview=True)
                if rows:                 
                    await asyncio.sleep(5)
                    await bot.delete_message(message.chat.id, msg123.message_id)
                break
        
        




@dp.message_handler(content_types=['video'])
@command_limiter
async def video_processing(message):
    conn = sqlite3.connect('updates.db')
    cur = conn.cursor()
    # Проверка, было ли обновление уже обработано
    cur.execute('SELECT update_id FROM updates WHERE update_id = ?', (message.message_id,))
    if cur.fetchone():
        return  # Если обновление уже было обработано, пропустить его

    # Добавление ID обновления в базу данных
    cur.execute('INSERT INTO updates VALUES (?)', (message.message_id,))
    conn.commit()

    text = None

    conn = sqlite3.connect('kukuruza.sql')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS speech_recognition (
            chat_id INTEGER
            )
        ''')
    conn.commit()
    cur.execute(f"SELECT * FROM speech_recognition WHERE chat_id = '{message.chat.id}'")
    rows1 = cur.fetchall()
    cur.execute(f"SELECT * FROM bad_words WHERE chat_id = '{message.chat.id}'")
    rows = cur.fetchall()
    if rows1:
        msg123 = await message.reply ('Распознование речи🧐....')
        await asyncio.sleep(1)
    if (rows1 or rows) or (rows1 and rows):
        file_info = await bot.get_file(message.video.file_id)
        downloaded_file = await bot.download_file(file_info.file_path)
        try:
            with open('video.mp4', 'wb') as new_file:
                new_file.write(downloaded_file.read())        
        except:
            await bot.delete_message(message.chat.id, msg123.message_id)

        src_filename = 'video.mp4'
        dest_filename = 'audio.wav'
        process = subprocess.run(['ffmpeg', '-y', '-i', src_filename, '-vn', '-f', 'wav', dest_filename])
        if process.returncode != 0:
            await bot.delete_message(message.chat.id, msg123.message_id)

            #raise Exception("Error converting video to audio.")
            pass


        r = sr.Recognizer()
        with sr.AudioFile(dest_filename) as source:
            audio_data = r.record(source)
            try:

                text = r.recognize_google(audio_data, language='ru-RU')
                
                if rows1:
                    if text:
                        await bot.edit_message_text(chat_id=message.chat.id, message_id=msg123.message_id, text=text)

                    else:
                        text = "Бро ничего не сказал🤷"
                        if rows1:
                            await bot.edit_message_text(chat_id=message.chat.id, message_id=msg123.message_id, text=text)
                            await asyncio.sleep(5)
                            await bot.delete_message(message.chat.id, msg123.message_id)
                    

            except:
                text = "Не удалось распознать🤷"
                if rows1:
                    await bot.edit_message_text(chat_id=message.chat.id, message_id=msg123.message_id, text=text)
                    await asyncio.sleep(5)
                    await bot.delete_message(message.chat.id, msg123.message_id)        
    text2 = text.lower()
    words = text2.split()
    conn = sqlite3.connect('kukuruza.sql')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS bad_words (
            chat_id INTEGER
            )
        ''')
    conn.commit()
    if rows:
        cur.close()
        conn.close()
        for word in words:
            if word in bad_words_dict:
                await bot.delete_message(message.chat.id, message.message_id)

                msg = await bot.send_message(message.chat.id, f'<a href="https://t.me/{message.from_user.username}"> {message.from_user.first_name}</a>! сказал матершинное слово!!! \n{word} - {bad_words_dict[word]} \nсообщение удаленно!' , parse_mode='html', disable_web_page_preview=True)
                await asyncio.sleep(10)
                await bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=f'<a href="https://t.me/{message.from_user.username}"> {message.from_user.first_name}</a>! отправил матершинное слово!!! \n \nсообщение удаленно!' , parse_mode='html', disable_web_page_preview=True)
                if rows:                 
                    await asyncio.sleep(5)
                    await bot.delete_message(message.chat.id, msg123.message_id)
                break



@dp.message_handler(content_types=['video_note'])
@command_limiter
async def video_note_processing(message):
    conn = sqlite3.connect('updates.db')
    cur = conn.cursor()
    # Проверка, было ли обновление уже обработано
    cur.execute('SELECT update_id FROM updates WHERE update_id = ?', (message.message_id,))
    if cur.fetchone():
        return  # Если обновление уже было обработано, пропустить его

    # Добавление ID обновления в базу данных
    cur.execute('INSERT INTO updates VALUES (?)', (message.message_id,))
    conn.commit()

    text = None
    conn = sqlite3.connect('kukuruza.sql')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS speech_recognition (
            chat_id INTEGER
            )
        ''')
    conn.commit()
    cur.execute(f"SELECT * FROM speech_recognition WHERE chat_id = '{message.chat.id}'")
    rows1 = cur.fetchall()
    cur.execute(f"SELECT * FROM bad_words WHERE chat_id = '{message.chat.id}'")
    rows = cur.fetchall()
    if rows1:
        msg123 = await message.reply ('Распознование речи🧐....')
        await asyncio.sleep(1)
    if (rows1 or rows) or (rows1 and rows):
        file_info = await bot.get_file(message.video_note.file_id)
        downloaded_file = await bot.download_file(file_info.file_path)
        with open('video_note.mp4', 'wb') as new_file:
            new_file.write(downloaded_file.read())
        src_filename = 'video_note.mp4'
        dest_filename = 'audio.wav'
        process = subprocess.run(['ffmpeg', '-y', '-i', src_filename, '-vn', '-f', 'wav', dest_filename])
        if process.returncode != 0:
            await bot.delete_message(message.chat.id, msg123.message_id)

            raise Exception("Error converting video to audio.")
        r = sr.Recognizer()
        with sr.AudioFile(dest_filename) as source:
            audio_data = r.record(source)
            try:

                text = r.recognize_google(audio_data, language='ru-RU')
                
                if rows1:
                    if text:
                        await bot.edit_message_text(chat_id=message.chat.id, message_id=msg123.message_id, text=text)
                    else:
                        text = "Бро ничего не сказал🤷"
                        if rows1:
                            await bot.edit_message_text(chat_id=message.chat.id, message_id=msg123.message_id, text=text)
                            await asyncio.sleep(5)
                            await bot.delete_message(message.chat.id, msg123.message_id)

            except:
                text = "Не удалось распознать🤷"
                if rows1:
                    await bot.edit_message_text(chat_id=message.chat.id, message_id=msg123.message_id, text=text)
                    await asyncio.sleep(5)
                    await bot.delete_message(message.chat.id, msg123.message_id)
                


        text2 = text.lower()
        words = text2.split()
    conn = sqlite3.connect('kukuruza.sql')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS bad_words (
            chat_id INTEGER
            )
        ''')
    conn.commit()
    if rows:
        cur.close()
        conn.close()
        for word in words:
            if word in bad_words_dict:
                await bot.delete_message(message.chat.id, message.message_id)
                msg = await bot.send_message(message.chat.id, f'<a href="https://t.me/{message.from_user.username}"> {message.from_user.first_name}</a>! сказал матершинное слово!!! \n{word} - {bad_words_dict[word]} \nсообщение удаленно!' , parse_mode='html', disable_web_page_preview=True)
                await asyncio.sleep(10)
                await bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=f'<a href="https://t.me/{message.from_user.username}"> {message.from_user.first_name}</a>! отправил матершинное слово!!! \n \nсообщение удаленно!' , parse_mode='html', disable_web_page_preview=True)
                if rows:                 
                    await asyncio.sleep(5)
                    await bot.delete_message(message.chat.id, msg123.message_id)
                break
@dp.message_handler(commands=["stop"])
async def stop_command(message: types.Message):
    print('stop')
    # Отправляем файл profile.db
    with open("kukurusa.sql", "rb") as file:
        await bot.send_document(message.chat.id, file)

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
    
