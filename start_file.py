import os
import time
import aiogram
import sqlite3
import telebot
bot = telebot.TeleBot('7119099578:AAF8WP9VJKDRKH0rUYlKs0U9FYPsHqVgeJw')
import subprocess
last_command_time1 = 0

def command_limiter(func):
    def wrapper(message):
        global last_command_time1
        current_time = time.time()

        # Если с момента последней команды прошло меньше секунды, ждем
        while current_time - last_command_time1 < 3:
            time.sleep(0.1)
            current_time = time.time()

        # Обновляем время последней команды
        last_command_time1 = current_time

        # Выполняем команду
        return func(message)
    return wrapper

while True:
    try:
        # Запускаем ваш скрипт
        bot.send_message(-1002102077131, f'перезапуск...')
        # Запускаем программу и читаем ее вывод
        process = subprocess.Popen('python main.py', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        last_command_time1 = 0

        for line in iter(process.stdout.readline, b''):
            # Отправляем каждую строку вывода в Telegram
            current_time = time.time()

            # Если с момента последней команды прошло меньше секунды, ждем
            while current_time - last_command_time1 < 5:
                time.sleep(0.1)
                current_time = time.time()

            # Обновляем время последней команды
            last_command_time1 = current_time
            bot.send_message(-1002102077131, line.decode(errors='ignore'))    
    except telebot.apihelper.ApiTelegramException as e:
        if e.error_code == 429:
            # Подключаемся к вашей базе данных
            conn = sqlite3.connect('kukuruza.sql')
            c = conn.cursor()

            # Создаем таблицу errs, если она еще не существует
            c.execute("CREATE TABLE IF NOT EXISTS errs (timeout BOOLEAN)")

            # Добавляем значение true в столбец timeout таблицы errs
            c.execute("INSERT INTO errs (timeout) VALUES (true)")

            # Сохраняем изменения и закрываем соединение
            conn.commit()
            conn.close()

        # Ждем 15 секунд
        time.sleep(30)

        # Отправляем сообщение о перезапуске
        bot.send_message('1396541072', f'Произошла ошибка: {e}\nПерезапускаем...')

        # Продолжаем цикл
        continue
    except aiogram.utils.exceptions.TerminatedByOtherGetUpdates:
        # Игнорируем исключение и продолжаем цикл
        continue
    except:
        time.sleep(15)
    # тормозит ли этот скипт прийвыполнении расщифровке
    time.sleep(15)


