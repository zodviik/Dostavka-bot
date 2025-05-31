import aiogram, sqlite3, config, asyncio
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from keybords import *


connect = sqlite3.connect('courier_db.sqlite')
cursor = connect.cursor()

admin_id = [825885613, 458534902, 658649677, 253848812]

bot = Bot(config.token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

tz = ZoneInfo("Europe/Moscow")

async def orders_autoclear():
    while True:
        cursor.execute(f"SELECT COUNT(*) FROM courier")
        count_orders = cursor.fetchone()[0]
        datetime_format = "%Y-%m-%d %H:%M:%S"
        if count_orders >= 1:
            for i in range(1, 1000):
                try:    
                    cursor.execute(f"SELECT datetime FROM courier WHERE order_id = {i}")
                    time = str(cursor.fetchone())[2:-3]
                    order_time = datetime.strptime(time, datetime_format)
                    current_time = datetime.now(tz).strftime(datetime_format)
                    current_time = datetime.strptime(current_time, datetime_format)
                    if order_time + timedelta(hours=6) < current_time:
                        cursor.execute(f"DELETE FROM courier WHERE order_id = {i}")
                        connect.commit()
                except ValueError as e:
                    pass
        await asyncio.sleep(300)

async def on_startup(dp):
    asyncio.create_task(orders_autoclear())


class Logika(StatesGroup):
    role = State()
    phone_number = State()
    address = State()
    client = State()
    order = State()

class Select_section(StatesGroup):
    sections = State()
    vegetables = State()
    bread = State()
    milk = State()
    drinks = State()


class Check_Courier(StatesGroup):
     role = State()

class Change_data_client(StatesGroup):
    change_name = State()
    change_pnone_number = State()
    change_address = State()

async def get_mainmenu(message:types.Message):
    cursor.execute(f"SELECT user_name, phone_number, address FROM users WHERE id = {message.chat.id}")
    data = cursor.fetchone()
    with open(f"Media/menu.jpg", "br") as photo:
        await bot.send_photo(message.chat.id, photo, f"Главное меню:\n\n✉️Ваш адрес: {data[2]}\n\n📞Ваш номер телефона: {data[1]}\n\n👤Ваше имя: {data[0]}\n\nНаберите продукты в корзину и нажмите  _*🛵Оформить заказ*_ , чтобы отправить заказ курьеру", reply_markup=mainmenu_keyboard, parse_mode="MarkdownV2")


@dp.message_handler(commands=["start", "login"])
async def start(message:types.Message, state:FSMContext):
    cursor.execute(f"SELECT id FROM users WHERE id = {message.chat.id}")
    data = cursor.fetchone()
    if data is None:
        cursor.execute(f"INSERT INTO users(id) VALUES({message.chat.id})")
        cursor.execute(f"INSERT INTO cart(id) VALUES({message.chat.id})")
        connect.commit()
        await bot.send_message(message.chat.id, 'Приветствую, выберите роль!', 
                               reply_markup = role_keyboard)
        await Logika.role.set()
    else:
        await bot.send_message(message.chat.id, 'Вы уже зарегестрированы ✅')
        await get_mainmenu(message)

@dp.message_handler(commands=["delete"])
async def delete(message:types.Message):
    if message.chat.id in admin_id:
        cursor.execute("DELETE FROM users WHERE id = ?", (message.chat.id,))
        cursor.execute("DELETE FROM cart WHERE id = ?", (message.chat.id,))
        connect.commit()
        await bot.send_message(message.chat.id, "Вы успешно удалены из базы данных✅")
    else:
        await bot.send_message(message.chat.id, "Эта команда недоступна для вас🚫")


@dp.message_handler(commands=["changerole"])
async def change_role(message: types.Message):
    if message.chat.id in admin_id:    
        cursor.execute(f"SELECT role FROM users WHERE id = {message.chat.id}")
        role = str(cursor.fetchone())[2:-3]
        if role == "клиент":
            cursor.execute(f"UPDATE users SET role = ? WHERE id = ?", ('курьер', message.chat.id,))
            connect.commit()
        if role == "курьер":
            cursor.execute(f"UPDATE users SET role = ? WHERE id = ?", ('клиент', message.chat.id,))
            connect.commit()
        await bot.send_message(message.chat.id, "Вы успешно сменили роль✅",reply_markup=onlymenu_keyboard)
    else:
        await bot.send_message(message.chat.id, "Эта команда не доступна вам🚫")
        print(message.chat.id)

@dp.message_handler(state=Logika.role)
async def set_role(message: types.Message):
    if message.text == '🚴 Я курьер':
        await bot.send_message(message.chat.id, "Вы выбрали роль курьера, введите пароль!")
        await Check_Courier.role.set()
    else:
        await bot.send_message(message.chat.id, "Вы выбрали роль клиента!✅")
        cursor.execute("UPDATE users SET role = ? WHERE id = ?",('клиент', message.chat.id))
        connect.commit()
        await Logika.client.set()
        await bot.send_message(message.chat.id, "Введите ваше имя")


@dp.message_handler(state=Check_Courier.role)
async def check_courier(message: types.Message, state: FSMContext):
    if message.text == '0000':
        await bot.send_message(message.chat.id, 'Отлично, вы есть в базе данных!✅', reply_markup=courier_keyboard)
        cursor.execute("UPDATE users SET role = ? WHERE id = ?",('курьер', message.chat.id))
        connect.commit()
    await state.finish()


@dp.message_handler(state=Logika.client)
async def check_name(message: types.Message, state: FSMContext):
    cursor.execute("UPDATE users SET user_name = ? WHERE id = ?",(message.text, message.chat.id))
    connect.commit()
    await bot.send_message(message.chat.id, f"Спасибо, {message.text}! Твое имя сохранено✅")
    await bot.send_message(message.chat.id, "Напишите ваш номер телефона в формате: 79*********")
    await Logika.phone_number.set()


@dp.message_handler(state=Logika.phone_number)
async def choose(message:types.Message):
    cursor.execute(f"SELECT 1 FROM users WHERE phone_number = ? LIMIT 1",
            (message.text,))
    data = cursor.fetchone()
    if not(data is None):
        await bot.send_message(message.chat.id, "Ошибка, данный номер уже используется!")
    else:
        if message.text[0] == "7" and message.text[1] == "9" and len(message.text) == 11:
            cursor.execute("UPDATE users SET phone_number = ? WHERE id = ?",(message.text, message.chat.id))
            connect.commit()
            await bot.send_message(message.chat.id, f"Отлично, ваш номер {message.text} сохранён!✅")
            await bot.send_message(message.chat.id, "Напишите ваш адрес в формате: Город, улица, номер дома, квартира.\n" \
            "При неккоректном вводе адреса мы вас не сможем найти :(")
            await Logika.address.set()
        else:
            await bot.send_message(message.chat.id, "Ошибка, неверный формат, попробуйте снова!")
            await Logika.phone_number.set()


@dp.message_handler(state=Logika.address)
async def choose(message:types.Message, state: FSMContext):
    cursor.execute("UPDATE users SET address = ? WHERE id = ?", (message.text, message.chat.id))
    connect.commit()
    await state.finish()
    await bot.send_message(message.chat.id, f"Отлично, ваш адрес сохранён✅")
    await bot.send_message(message.chat.id, f"Успешная регистрация✅")
    await get_mainmenu(message)



@dp.message_handler(state=Select_section.sections)
async def sections(message: types.Message, state: FSMContext):
    if message.text == "🥕Овощи и фрукты🍏":
        await bot.send_message(message.chat.id, "👇Выберите что добавить в корзину", reply_markup=vegetables_keyboard)
        await Select_section.vegetables.set()
    if message.text == "🍞Хлебобулочные изделия":
        await bot.send_message(message.chat.id, "👇Выберите что добавить в корзину",reply_markup=bread_keyboard)
        await Select_section.bread.set()
    if message.text == "🥛Кисломолочные продукты":
        await bot.send_message(message.chat.id, "👇Выберите что добавить в корзину", reply_markup=milk_keybord)
        await Select_section.milk.set()
    if message.text == "🥤Напитки🍹":
        await bot.send_message(message.chat.id, "👇Выберите что добавить в корзину", reply_markup=drinks_keyboard)
        await Select_section.drinks.set()
    if message.text == "Вернуться в главное меню":
        await get_mainmenu(message)
        await state.finish()
@dp.message_handler(state=Select_section.vegetables)
async def vegetables(message: types.Message):
    if message.text != "Вернуться в меню выбора продуктов":
        cursor.execute(f"SELECT vegetables FROM cart WHERE id = {message.chat.id}")
        data = cursor.fetchone()
        new_data = f"{message.text}"
        for i in data:
            if not(i is None):
                new_data = f'{i}, ' + new_data
        cursor.execute("UPDATE cart SET vegetables = ? WHERE id = ?", (new_data, message.chat.id))
        connect.commit()
        await bot.send_message(message.chat.id, f"{message.text} теперь в корзине!")
        await Select_section.vegetables.set()
    else:
        await bot.send_message(message.chat.id, 'Выберите раздел', reply_markup=cart_keyboard)
        await Select_section.sections.set()


@dp.message_handler(state=Select_section.bread)
async def bread(message: types.Message):
    if message.text != "Вернуться в меню выбора продуктов":
        cursor.execute(f"SELECT bread FROM cart WHERE id = {message.chat.id}")
        data = cursor.fetchone()
        new_data = f"{message.text}"
        for i in data:
            if not(i is None):
                new_data = f'{i}, ' + new_data
        cursor.execute("UPDATE cart SET bread = ? WHERE id = ?", (new_data, message.chat.id))
        connect.commit()
        await bot.send_message(message.chat.id, f"{message.text} теперь в корзине!")
        await Select_section.bread.set()
    else:
        await bot.send_message(message.chat.id, 'Выберите раздел', reply_markup=cart_keyboard)
        await Select_section.sections.set()


@dp.message_handler(state=Select_section.milk)
async def milk(message: types.Message):
    if message.text != "Вернуться в меню выбора продуктов":
        cursor.execute(f"SELECT milk FROM cart WHERE id = {message.chat.id}")
        data = cursor.fetchone()
        new_data = f"{message.text}"
        for i in data:
            if not(i is None):
                new_data = f'{i}, ' + new_data
        cursor.execute("UPDATE cart SET milk = ? WHERE id = ?", (new_data, message.chat.id))
        connect.commit()
        await bot.send_message(message.chat.id, f"{message.text} теперь в корзине!")
        await Select_section.milk.set()
    else:
        await bot.send_message(message.chat.id, 'Выберите раздел', reply_markup=cart_keyboard)
        await Select_section.sections.set()


@dp.message_handler(state=Select_section.drinks)
async def drinks(message: types.Message):
    if message.text != "Вернуться в меню выбора продуктов":
        cursor.execute(f"SELECT drinks FROM cart WHERE id = {message.chat.id}")
        data = cursor.fetchone()
        new_data = f"{message.text}"
        for i in data:
            if not(i is None):
                new_data = f'{i}, ' + new_data
        cursor.execute("UPDATE cart SET drinks = ? WHERE id = ?", (new_data, message.chat.id))
        connect.commit()
        await bot.send_message(message.chat.id, f"{message.text} теперь в корзине!")
        await Select_section.drinks.set()
    else:
        await bot.send_message(message.chat.id, 'Выберите раздел', reply_markup=cart_keyboard)
        await Select_section.sections.set()


@dp.message_handler(state=Change_data_client.change_name)
async def change_name(message:types.Message, state: FSMContext):
    cursor.execute("UPDATE users SET user_name = ? WHERE id = ?",(message.text, message.chat.id))
    connect.commit()
    await bot.send_message(message.chat.id, "Имя успешно сохранено!")
    await state.finish()
    await get_mainmenu(message)

@dp.message_handler(state=Change_data_client.change_address)
async def change_name(message:types.Message, state: FSMContext):
    cursor.execute("UPDATE users SET address = ? WHERE id = ?",(message.text, message.chat.id))
    connect.commit()
    await bot.send_message(message.chat.id, "Адрес успешно сохранен")
    await state.finish()
    await get_mainmenu(message)

@dp.message_handler(state=Change_data_client.change_pnone_number)
async def change_name(message:types.Message, state: FSMContext):
    cursor.execute(f"SELECT 1 FROM users WHERE phone_number = ? LIMIT 1",
            (message.text,))
    data = cursor.fetchone()
    if not(data is None):
        await bot.send_message(message.chat.id, "Ошибка, данный номер уже используется!\nПорпробуйте снова")
    else:
        if message.text[0] == "7" and message.text[1] == "9" and len(message.text) == 11:
            cursor.execute("UPDATE users SET phone_number = ? WHERE id = ?",(message.text, message.chat.id))
            connect.commit()
            await bot.send_message(message.chat.id, "Номер телефона успешно сохранен")
            await state.finish()
            await get_mainmenu(message)
        else:
            await bot.send_message(message.chat.id, "Ошибка, неверный формат, попробуйте снова!")
            await Logika.phone_number.set()


@dp.message_handler(state=Logika.order)
async def yes_no(message: types.Message, state: FSMContext):
    if message.text == 'Да✅':
        cursor.execute("SELECT * FROM cart WHERE id = ?", (message.chat.id,))
        data = str(cursor.fetchone()[1:])[1:-1]
        data = data.replace("'", "").replace(",", "").replace("None", "")
        for i in data:
            if i == " ":
                data = data[1:]
            else:
                break
        cursor.execute(f"INSERT INTO courier (cart, user_id, status, datetime) VALUES (?, ?, ?, datetime('now'))", (data, message.chat.id, 'Передан в очередь',))
        connect.commit()
        await bot.send_message(message.chat.id, "Заказ оформлен✅")
        cursor.execute(f"UPDATE cart SET vegetables = NULL, bread = NULL, milk = NULL, drinks = NULL WHERE id = ?", (message.chat.id,))
        connect.commit()
        await asyncio.sleep(1)
        await get_mainmenu(message)
    if message.text == 'Нет❌':
        await get_mainmenu(message)
    await state.finish()

@dp.message_handler(content_types=['text'])
async def choose(message:types.Message):
    cursor.execute(f"SELECT role FROM users WHERE id = {message.chat.id}")
    role = str(cursor.fetchone())[2:-3]
    if role == "клиент":
        if message.text.lower() == "меню":
                await get_mainmenu(message)
        
        if message.text == '👜Выбрать продукты👜':
            with open(f"Media/order.jpg", "br") as photo:
                await bot.send_photo(message.chat.id, photo, 'Выберите раздел', reply_markup=cart_keyboard)
            await Select_section.sections.set()
        
        if message.text == '🧹Очистить корзину':
            cursor.execute(f"UPDATE cart SET vegetables = NULL, bread = NULL, milk = NULL, drinks = NULL WHERE id = ?", (message.chat.id,))
            await bot.send_message(message.chat.id, "Корзина очищена")
        cursor.execute(f"SELECT vegetables FROM cart WHERE id = {message.chat.id}")
        cart_vegetables = str(cursor.fetchone())[2:-3]
        cursor.execute(f"SELECT bread FROM cart WHERE id = {message.chat.id}")
        cart_bread = str(cursor.fetchone())[2:-3]
        cursor.execute(f"SELECT milk FROM cart WHERE id = {message.chat.id}")
        cart_milk = str(cursor.fetchone())[2:-3]
        cursor.execute(f"SELECT drinks FROM cart WHERE id = {message.chat.id}")
        cart_drinks = str(cursor.fetchone())[2:-3]
        if cart_vegetables == 'on':
            cart_vegetables = 'не выбраны'
        if cart_bread == 'on':
            cart_bread = 'не выбраны'
        if cart_milk == 'on':
            cart_milk = 'не выбраны'
        if cart_drinks == 'on':
            cart_drinks = 'не выбраны'
        
        if message.text == '👀Посмотреть корзину':
            if cart_vegetables == 'не выбраны' and cart_bread == 'не выбраны' and cart_milk == 'не выбраны' and cart_drinks == 'не выбраны':
                await bot.send_message(message.chat.id, "Корзина пустая, скорее выберите что-нибудь!")
            else:
                await bot.send_message(message.chat.id, f"Овощи: {cart_vegetables}\n\nХлебобулочные изделия: {cart_bread}\n\nМолочные изделия: {cart_milk}\n\nНапитки: {cart_drinks}")
        
        if message.text == "✉️Изменить адрес":
            await bot.send_message(message.chat.id, "Введите новый адрес")
            await Change_data_client.change_address.set()
        
        if message.text == "📞Изменить номер телефона":
            await bot.send_message(message.chat.id, "Введите новый номер телефона в формате: 79*********")
            await Change_data_client.change_pnone_number.set()
        
        if message.text == "👤Изменить имя":
            await bot.send_message(message.chat.id, "Введите новое имя")
            await Change_data_client.change_name.set()
        
        if message.text == "🛵Оформить заказ":
            await bot.send_message(message.chat.id, f"Ваша корзина👇\n\nОвощи: {cart_vegetables}\n\nХлебобулочные изделия: {cart_bread}\n\nМолочные изделия: {cart_milk}\n\nНапитки: {cart_drinks}\n\nПодтвердите заказ с помощью кнопок внизу👇", reply_markup=yes_or_no_keyboard)
            await Logika.order.set()
    
    elif role == "курьер":
        if message.text == "меню":
            await bot.send_message(message.chat.id, 'Меню:', reply_markup=courier_keyboard)
        if message.text == "Посмотреть свободные заказы":
            await bot.send_message(message.chat.id, 'Свободные заказы:\n')
            cursor.execute("SELECT order_id FROM courier WHERE status = 'Передан в очередь'")
            orders_id = cursor.fetchall()
            for i in range(1, len(orders_id)+1):
                orders_id[i-1] = int(str(orders_id[i-1])[1:-2])
                cursor.execute(f"SELECT datetime, cart, user_id FROM courier WHERE order_id = {orders_id[i-1]}")
                data = cursor.fetchone()
                time, cart, user = data[0], data[1], data[2]
                cursor.execute(f"SELECT phone_number, address, user_name FROM users WHERE id = {user}")
                data = cursor.fetchone()
                phone_number, address, user_name = data[0], data[1], data[2]
                msg = f"Заказ №{i}\nВремя: {time}\n\nЗаказчик: {user_name}\nНомер телефона: +{phone_number}\nАдрес: {address}\nСодержимое заказа:\n{cart}"
                yandex_maps_url = f"https://yandex.ru/maps/?text={address}"
                google_maps_url = f"https://www.google.com/maps/search/?api=1&query={address}"
                twogis_url = f"https://2gis.ru/search?query={address}"
                map_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Яндекс.Карты", url=yandex_maps_url),
                InlineKeyboardButton(text="Google Maps", url=google_maps_url),
                InlineKeyboardButton(text="2ГИС", url=twogis_url)]
                ])
                await bot.send_message(message.chat.id, msg, reply_markup=map_keyboard)


executor.start_polling(dp, skip_updates=True, on_startup=on_startup)