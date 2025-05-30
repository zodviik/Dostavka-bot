from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


role_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
r1 = KeyboardButton('🚴 Я курьер')
r2 = KeyboardButton('🛒 Я клиент')
role_keyboard.add(r1, r2)


courier_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
c1 = KeyboardButton("Посмотреть свободные заказы")
courier_keyboard.add(c1)


back_to_mainmenu = KeyboardButton("Вернуться в главное меню")
back_to_choose_menu =  KeyboardButton("Вернуться в меню выбора продуктов")

onlymenu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
onlymenu_keyboard.add(KeyboardButton("меню"))


cart_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
o1 = KeyboardButton("🥕Овощи и фрукты🍏")
o2 = KeyboardButton("🍞Хлебобулочные изделия ")
o3 = KeyboardButton("🥛Кисломолочные продукты")
o4 = KeyboardButton("🥤Напитки🍹")
cart_keyboard.add(o1, o2, o3, o4, back_to_mainmenu)


mainmenu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
m1 = KeyboardButton("👜Выбрать продукты👜")
m2 = KeyboardButton("👀Посмотреть корзину")
m3 = KeyboardButton("🧹Очистить корзину")
m4 = KeyboardButton("✉️Изменить адрес")
m5 = KeyboardButton("📞Изменить номер телефона")
m6 = KeyboardButton("👤Изменить имя")
m7 = KeyboardButton("🛵Оформить заказ")
mainmenu_keyboard.add(m1)
mainmenu_keyboard.add(m2, m3)
mainmenu_keyboard.add(m4, m5, m6)
mainmenu_keyboard.add(m7)


vegetables_keyboard = ReplyKeyboardMarkup(row_width=3)
v1 = KeyboardButton("Огурцы🥒")
v2 = KeyboardButton("Помидоры🍅")
v3 = KeyboardButton("Морковка🥕")
v4 = KeyboardButton("Картофель🥔")
v5 = KeyboardButton("Яблоки🍎")
v6 = KeyboardButton("Бананы🍌")
v7 = KeyboardButton("Груши🍐")
v8 = KeyboardButton("Киви🥝")
v9 = KeyboardButton("Апельсины🍊")
vegetables_keyboard.add(v1, v2, v3, v4, v5, v6, v7, v8, v9)
vegetables_keyboard.add(back_to_choose_menu)
vegetables_list = ["Огурцы🥒", "Помидоры🍅", "Морковка🥕", "Картофель🥔", "Яблоки🍎", "Бананы🍌", "Груши🍐", "Киви🥝", "Апельсины🍊"]


bread_keyboard = ReplyKeyboardMarkup(row_width=2)
b1 = KeyboardButton("Буханка🍞")
b2 = KeyboardButton("Батон🥖")
b3 = KeyboardButton("Круасан🥐")
b4 = KeyboardButton("Пончик🍩")
b5 = KeyboardButton("Сендвич🥪")
b6 = KeyboardButton("Бургер🍔")
bread_keyboard.add(b1, b2, b3, b4, b5, b6)
bread_keyboard.add(back_to_choose_menu)


milk_keybord = ReplyKeyboardMarkup()
mk1 = KeyboardButton("Молоко")
mk2 = KeyboardButton("Кефир")
mk3 = KeyboardButton("Сметана")
mk4 = KeyboardButton("Творог")
mk5 = KeyboardButton("Сгущёнка")
mk6 = KeyboardButton("Сливки")
mk7 = KeyboardButton("Йогурт")
mk8 = KeyboardButton("Сырок")
mk9 = KeyboardButton("Масло")
milk_keybord.add(mk1, mk2)
milk_keybord.add(mk3, mk4, mk5, mk6, mk9)
milk_keybord.add(mk7, mk8)
milk_keybord.add(back_to_choose_menu)


drinks_keyboard = ReplyKeyboardMarkup(row_width=4)
d1 = KeyboardButton("Сок Добрый")
d2 = KeyboardButton("Сок J7 Fresh")
d3 = KeyboardButton("Pulpy")
d4 = KeyboardButton("Rich")
d5 = KeyboardButton("Coca Cola")
d6 = KeyboardButton("Deneb")
d7 = KeyboardButton("Mirinda")
d8 = KeyboardButton("Вода 1л")
d9 = KeyboardButton("Вода 5л")
drinks_keyboard.add(d5, d6, d7)
drinks_keyboard.add(d1, d2, d3, d4)
drinks_keyboard.add(d8, d9)
drinks_keyboard.add(back_to_choose_menu)


yes_or_no_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
yes = KeyboardButton("Да✅")
no = KeyboardButton("Нет❌")
yes_or_no_keyboard.add(yes, no)


accept_keyboard = InlineKeyboardMarkup()
accept = InlineKeyboardButton("Принять в доставку", callback_data="accept")
accept_keyboard.add(accept)