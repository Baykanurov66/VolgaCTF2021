#Импорты (возможно тут есть что-то лишнее, но меня не ебет)
import asyncio
import logging
from aiogram import Bot, types
from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ParseMode, InputMediaPhoto, InputMediaVideo, ChatActions
from aiogram.types.message import ContentType
from aiogram.utils.markdown import text, bold, italic, code, pre
from aiogram.utils.emoji import emojize
from aiogram.types import InputFile
from contextlib import suppress
from aiogram.utils.exceptions import (MessageToEditNotFound, MessageCantBeEdited, MessageCantBeDeleted,MessageToDeleteNotFound)
from config import TOKEN, Delay, menu, orgi
import sqlite3
import string
import time
import random
from datetime import datetime
import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
from translate import Translator


#Подключение API для работы с гугл-таблицей
CREDENTIALS_FILE = 'creds.json'

spreadsheet_id = '11v8cwsDNg8nQoqly9RnW2majX76sgtI_3kkjpHB_rwU'

credentials = ServiceAccountCredentials.from_json_keyfile_name(
    CREDENTIALS_FILE,
    ['https://www.googleapis.com/auth/spreadsheets',
     'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())
service = apiclient.discovery.build('sheets', 'v4', http = httpAuth)


#Подключение бота
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())


#Клавиатура для ссылок на контакты
S=InlineKeyboardButton('Cайт🌐', url='https://volgactf.ru/volgactf-2021/final/')
V=InlineKeyboardButton('ВКонтакте🔷', url='https://vk.com/volgactf')
T=InlineKeyboardButton('Twitter📖', url='https://twitter.com/volgactf')
G=InlineKeyboardButton('Github💠', url='https://github.com/volgactf')
Y=InlineKeyboardButton('Youtube🛑', url='https://www.youtube.com/channel/UCTbjY5Xys-CgMBN8jgLazPA')
I=InlineKeyboardButton('Инстраграм💬', url='https://instagram.com/volga_ctf?utm_medium=copy_link')
kontakt=InlineKeyboardMarkup(row_width=2).add(S,V,T,G,Y,I)

S1=InlineKeyboardButton('Website🌐', url='https://volgactf.ru/volgactf-2021/final/')
V1=InlineKeyboardButton('VKontakte🔷', url='https://vk.com/volgactf')
T1=InlineKeyboardButton('Twitter📖', url='https://twitter.com/volgactf')
G1=InlineKeyboardButton('Github💠', url='https://github.com/volgactf')
Y1=InlineKeyboardButton('Youtube🛑', url='https://www.youtube.com/channel/UCTbjY5Xys-CgMBN8jgLazPA')
I1=InlineKeyboardButton('Instagram💬', url='https://instagram.com/volga_ctf?utm_medium=copy_link')
kontakt1=InlineKeyboardMarkup(row_width=2).add(S1,V1,T1,G1,Y1,I1)

k1=InlineKeyboardButton('Связаться с организаторами💌', callback_data='org')
k2=InlineKeyboardButton('Задать вопрос спикеру💬', callback_data='que')
k3=InlineKeyboardButton('Расписание🗓', callback_data='rasp')
kom=InlineKeyboardMarkup(row_width=4).add(k1).add(k2)

k1_1=InlineKeyboardButton('Contact organizers💌', callback_data='org')
k2_1=InlineKeyboardButton('Ask a question to the speaker💬', callback_data='que')
k3_1=InlineKeyboardButton('Schedule🗓', callback_data='rasp')
kom1=InlineKeyboardMarkup(row_width=4).add(k1_1).add(k2_1)

r1=InlineKeyboardButton('Расписание на 14.09.2021', callback_data='r1')
r2=InlineKeyboardButton('Расписание на 15.09.2021', callback_data='r2')
r3=InlineKeyboardButton('Расписание на 16.09.2021', callback_data='r3')
r4=InlineKeyboardButton('Расписание на 17.09.2021', callback_data='r4')
rasp=InlineKeyboardMarkup(row_width=4).add(r1).add(r2).add(r3).add(r4)

l1=InlineKeyboardButton('Русский', callback_data='ru')
l2=InlineKeyboardButton('English', callback_data='eng')
lan=InlineKeyboardMarkup(row_width=4).add(l1).add(l2)

v1=InlineKeyboardButton('Участник🎖', callback_data='gamer')
v2=InlineKeyboardButton('Гость👀', callback_data='guest')
v3=InlineKeyboardButton('Организатор👑', callback_data='orga')
v4=InlineKeyboardButton('Волонтер✋', callback_data='vol')
Vhod=InlineKeyboardMarkup(row_width=2).add(v1,v2,v3,v4)

v1_1=InlineKeyboardButton('Participant🎖', callback_data='gamer')
v2_1=InlineKeyboardButton('Guest👀', callback_data='guest')
v3_1=InlineKeyboardButton('Organizer👑', callback_data='orga')
v4_1=InlineKeyboardButton('Volunteer✋', callback_data='vol')
Vhod1=InlineKeyboardMarkup(row_width=2).add(v1_1,v2_1,v3_1,v4_1)

async def delete_message(message: types.Message, sleep_time: int = 0):
    await asyncio.sleep(sleep_time)
    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await message.delete()
m=0

class Obr(StatesGroup):
        org=State()
        que=State()

class Photo(StatesGroup):
        photo=State()

class Reg(StatesGroup):
        gamer=State()
        orga=State()
        vol=State()

@dp.message_handler(commands=['start'])
async def process_start_command(msg: types.Message, state: FSMContext):
    global m
    db = sqlite3.connect("databot.db")
    c = db.cursor()
    if msg.from_user.last_name == None:
        name=str(msg.from_user.first_name)
    elif msg.from_user.first_name == None:
        name=str(msg.from_user.last_name)
    else:
        name=str(msg.from_user.first_name+" "+msg.from_user.last_name)
    i = [j[0] for j in c.execute("SELECT id FROM Language")] 
    if msg.from_user.id not in i:
        m = await msg.answer("Привет!\nДля начала выбери язык интерфейса\n\n//\n\nHello!\nFirst, select the interface language", reply_markup=lan)
    else:
        await bot.send_sticker(msg.from_user.id,'CAACAgIAAxkBAAEC3DJhNQYZozj6kQ4flQiSo-AUj_b1xQACXgADkp8eEbuhuIbpKqCeIAQ')
        c.execute('SELECT lang FROM Language WHERE id = ?',(msg.from_user.id, ))
        lan1=c.fetchone()
        if str(*lan1) == "ru":
            await msg.answer("<b>Мы с тобой уже знакомились!</b>\nЕсли ты хочешь вспомнить, что я умею, то выполним команду /help", parse_mode='HTML')
        else:
            await msg.answer("Let me remind you how I can help you. Execute command /help", parse_mode='HTML')
    c.close()
    db.close()

@dp.callback_query_handler(lambda c: c.data == 'ru')
async def process_callback_button1(callback_query: types.CallbackQuery):
    global m
    asyncio.create_task(delete_message(m, 0.1))
    db = sqlite3.connect("databot.db")
    c = db.cursor()
    if callback_query.from_user.last_name == None:
        name=str(callback_query.from_user.first_name)
    elif callback_query.from_user.first_name == None:
        name=str(callback_query.from_user.last_name)
    else:
        name=str(callback_query.from_user.first_name+" "+callback_query.from_user.last_name)
    i = [j[0] for j in c.execute("SELECT id FROM Language")]
    if callback_query.from_user.id not in i:
        c.execute('INSERT INTO Language VALUES (?,?)', (callback_query.from_user.id,"ru"))
        db.commit()
        await bot.send_photo(callback_query.from_user.id, 'AgACAgIAAxkBAAICj2E8Xrp-Qmybi1e0hvLu18e6g5JpAAIEtDEbCXrhScSNA-9glO0NAQADAgADeQADIAQ',caption = "<b>\nДобро пожаловать на VolgaCTF 2021 </b>"+name+"!\n\nЯ <b>бот-волонтер</b> который будет помогать тебе ориентироваться на данных соревнованиях.\n\nЯ буду напоминать тебе о лекциях и других мероприятиях, которые будут проходить во время VolgaCTF 2021.\n\n🟡 Узнать обо всех моих возможностях можно вызвав команду /menu\n⚫️ Если ты что-то забудешь, я всегда буду рад напомнить тебе командой /help\n🟠 Посмотреть наши контакты можно командой /kontakt\n\nТеперь давай определимся с твоим статусом на данном мероприятии, выбери один вариант из предложенного списка:", reply_markup=Vhod, parse_mode='HTML')
    else:
        await bot.send_message(callback_query.from_user.id,"<b>Ты уже выбрал язык Русский</b>", parse_mode='HTML')
    c.close()
    db.close()

@dp.callback_query_handler(lambda c: c.data == "eng")
async def process_callback_button1(callback_query: types.CallbackQuery):
    global m
    asyncio.create_task(delete_message(m, 0.1))
    db = sqlite3.connect("databot.db")
    c = db.cursor()
    if callback_query.from_user.last_name == None:
        name=str(callback_query.from_user.first_name)
    elif callback_query.from_user.first_name == None:
        name=str(callback_query.from_user.last_name)
    else:
        name=str(callback_query.from_user.first_name+" "+callback_query.from_user.last_name)
    i = [j[0] for j in c.execute("SELECT id FROM Language")]
    if callback_query.from_user.id not in i:
        c.execute('INSERT INTO Language VALUES (?,?)', (callback_query.from_user.id,"eng"))
        db.commit()
        await bot.send_photo(callback_query.from_user.id, 'AgACAgIAAxkBAAICj2E8Xrp-Qmybi1e0hvLu18e6g5JpAAIEtDEbCXrhScSNA-9glO0NAQADAgADeQADIAQ',caption = "<b>\nWelcome to VolgaCTF 2021 </b>"+name+"!\n\nI am a <b>volunteer bot</b> that will help you navigate during the whole competition.\n\nI will remind you about all the lectures and other events during VolgaCTF 2021.\n\n🟡 tap /menu to check what I can offer you\n⚫️  If you forget anything, I will always be happy to remind with simple command /help\n🟠 Check contacts page with command /contacts\n\nLet’s confirm your status on this competition. Pick an option below:", reply_markup=Vhod1, parse_mode='HTML')
    else:

        await bot.send_message(callback_query.from_user.id,"<b>You have already selected the language English</b>", parse_mode='HTML')
    c.close()
    db.close()

@dp.callback_query_handler(lambda c: c.data == 'gamer', state="*")
async def process_callback_button1(callback_query: types.CallbackQuery, state: FSMContext):
    db = sqlite3.connect("databot.db")
    c = db.cursor()
    i = [j[0] for j in c.execute("SELECT id FROM Users")] 
    if callback_query.from_user.id not in i:
        c.execute('SELECT lang FROM Language WHERE id = ?',(callback_query.from_user.id, ))
        lan=c.fetchone()
        if str(*lan) == "ru":
            await bot.send_message(callback_query.from_user.id,"Введи название своей команды:")
        else:
            await bot.send_message(callback_query.from_user.id,"Enter your team name:")
        await Reg.gamer.set()
    else:
        c.execute('SELECT lang FROM Language WHERE id = ?',(callback_query.from_user.id, ))
        lan=c.fetchone()
        if str(*lan) == "ru":
            await bot.send_message(callback_query.from_user.id,"Ты уже выбрал свой статус!!\n\nПоэтому всё всё....")
        else:
            await bot.send_message(callback_query.from_user.id,"You have already chosen your status !!\n\nSo everything is everything....")
    c.close()
    db.close()

@dp.message_handler(state=Reg.gamer)
async def gamer(msg: types.Message, state: FSMContext):
    db = sqlite3.connect("databot.db")
    c = db.cursor()
    if msg.from_user.last_name == None:
        name=str(msg.from_user.first_name)
    elif msg.from_user.first_name == None:
        name=str(msg.from_user.last_name)
    else:
        name=str(msg.from_user.first_name+" "+msg.from_user.last_name)
    naz="Участник команды: "+ str(msg.text)
    c.execute('INSERT INTO Users VALUES (?,?,?)', (msg.from_user.id,name,naz))
    db.commit()
    c.execute('SELECT lang FROM Language WHERE id = ?',(msg.from_user.id, ))
    lan=c.fetchone()
    if str(*lan) == "ru":
        await bot.send_photo(msg.from_user.id, "AgACAgIAAxkBAAIEmWE9wHto7DbRtSr-OEmurheorrioAALStTEbCXrxSU3P6kjBcZIhAQADAgADeAADIAQ" , caption = "Отлично!\nХороших тебе соревнований❤️\nИ помни: В безопасности сила!\n\nНаши контакты:", reply_markup=kontakt, parse_mode='HTML')
    else:
        await bot.send_photo(msg.from_user.id, "AgACAgIAAxkBAAIEmWE9wHto7DbRtSr-OEmurheorrioAALStTEbCXrxSU3P6kjBcZIhAQADAgADeAADIAQ" , caption = "Great!\nHave a good competition❤️\nPlease check our contacts from the list below:", reply_markup=kontakt1, parse_mode='HTML')
    await state.finish()
    c.close()
    db.close()

@dp.callback_query_handler(lambda c: c.data == 'guest')
async def guest(callback_query: types.CallbackQuery):
    db = sqlite3.connect("databot.db")
    c = db.cursor()
    if callback_query.from_user.last_name == None:
        name=str(callback_query.from_user.first_name)
    elif callback_query.from_user.first_name == None:
        name=str(callback_query.from_user.last_name)
    else:
        name=str(callback_query.from_user.first_name+" "+callback_query.from_user.last_name)
    i = [j[0] for j in c.execute("SELECT id FROM Users")] 
    if callback_query.from_user.id not in i:
        c.execute('INSERT INTO Users VALUES (?,?,?)', (callback_query.from_user.id,name,"Гость"))
        db.commit()
        c.execute('SELECT lang FROM Language WHERE id = ?',(callback_query.from_user.id, ))
        lan=c.fetchone()
        if str(*lan) == "ru":
            await bot.send_photo(callback_query.from_user.id, "AgACAgIAAxkBAAIEmWE9wHto7DbRtSr-OEmurheorrioAALStTEbCXrxSU3P6kjBcZIhAQADAgADeAADIAQ" , caption = "Отлично!\nХороших тебе соревнований❤️\nИ помни: В безопасности сила!\n\nНаши контакты:", reply_markup=kontakt, parse_mode='HTML')
        else:
            await bot.send_photo(callback_query.from_user.id, "AgACAgIAAxkBAAIEmWE9wHto7DbRtSr-OEmurheorrioAALStTEbCXrxSU3P6kjBcZIhAQADAgADeAADIAQ" , caption = "Great!\nHave a good competition❤️\nPlease check our contacts from the list below:", reply_markup=kontakt1, parse_mode='HTML')
    else:
        await bot.send_message(callback_query.from_user.id,"Ты уже выбрал свой статус!!\n\nПоэтому всё всё....")
    c.close()
    db.close()

@dp.callback_query_handler(lambda c: c.data == 'orga', state="*")
async def process_callback_button1(callback_query: types.CallbackQuery, state: FSMContext):
    db = sqlite3.connect("databot.db")
    c = db.cursor()
    i = [j[0] for j in c.execute("SELECT id FROM Users")] 
    if callback_query.from_user.id not in i:
        await bot.send_message(callback_query.from_user.id,"Введи секретный ключ:")
        await Reg.orga.set()
    else:
        await bot.send_message(callback_query.from_user.id,"Ты уже выбрал свой статус!!\n\nПоэтому всё всё....")
    c.close()
    db.close()

@dp.message_handler(state=Reg.orga)
async def gamer(msg: types.Message, state: FSMContext):
    db = sqlite3.connect("databot.db")
    c = db.cursor()
    if msg.from_user.last_name == None:
        name=str(msg.from_user.first_name)
    elif msg.from_user.first_name == None:
        name=str(msg.from_user.last_name)
    else:
        name=str(msg.from_user.first_name+" "+msg.from_user.last_name)
    if str(msg.text) == "JND58-8X4HM-TRY68-HJB6F-TOQCD-FJF9X-96CFR":
        c.execute('INSERT INTO Users VALUES (?,?,?)', (msg.from_user.id,name,"Организатор"))
        db.commit()
        await bot.send_photo(msg.from_user.id, "AgACAgIAAxkBAAIEmWE9wHto7DbRtSr-OEmurheorrioAALStTEbCXrxSU3P6kjBcZIhAQADAgADeAADIAQ" , caption = "Отлично!\nХороших тебе соревнований❤️\nИ помни: В безопасности сила!\n\nНаши контакты:", reply_markup=kontakt, parse_mode='HTML')
    else:
        await msg.answer("Неверный ключ!")
    await state.finish()
    c.close()
    db.close()

@dp.callback_query_handler(lambda c: c.data == 'vol', state="*")
async def process_callback_button1(callback_query: types.CallbackQuery, state: FSMContext):
    db = sqlite3.connect("databot.db")
    c = db.cursor()
    i = [j[0] for j in c.execute("SELECT id FROM Users")] 
    if callback_query.from_user.id not in i:
        await bot.send_message(callback_query.from_user.id,"Введи секретный ключ:")
        await Reg.vol.set()
    else:
        await bot.send_message(callback_query.from_user.id,"Ты уже выбрал свой статус!!\n\nПоэтому всё всё....")
    c.close()
    db.close()

@dp.message_handler(state=Reg.vol)
async def gamer(msg: types.Message, state: FSMContext):
    db = sqlite3.connect("databot.db")
    c = db.cursor()
    if msg.from_user.last_name == None:
        name=str(msg.from_user.first_name)
    elif msg.from_user.first_name == None:
        name=str(msg.from_user.last_name)
    else:
        name=str(msg.from_user.first_name+" "+msg.from_user.last_name)
    if str(msg.text) == "PTIY4-RUNYU-HN7O9-CH37H-PRCS8-QTTHA-5HH6P":
        c.execute('INSERT INTO Users VALUES (?,?,?)', (msg.from_user.id,name,"Волонтер"))
        db.commit()
        await bot.send_photo(msg.from_user.id, "AgACAgIAAxkBAAIEmWE9wHto7DbRtSr-OEmurheorrioAALStTEbCXrxSU3P6kjBcZIhAQADAgADeAADIAQ" , caption = "Отлично!\nХороших тебе соревнований❤️\nИ помни: В безопасности сила!\n\nНаши контакты:", reply_markup=kontakt, parse_mode='HTML')
    else:
        await msg.answer("Неверный ключ!")
    await state.finish()
    c.close()
    db.close()

@dp.message_handler(commands=['help'])
async def process_help_command(msg: types.Message):
    db = sqlite3.connect("databot.db")
    c = db.cursor()
    i = [j[0] for j in c.execute("SELECT id FROM Users")] 
    if msg.from_user.id not in i:
        c.execute('SELECT lang FROM Language WHERE id = ?',(msg.from_user.id, ))
        lan=c.fetchone()
        if str(*lan) == "ru":
            await msg.answer("<b>Выполни для начала команду /start и укажи свой статус с помощью кнопок</b>", parse_mode='HTML')
        else:
            await msg.answer("<b>First run the command /start and indicate your status using the buttons</b>", parse_mode='HTML')
    else:
        c.execute('SELECT lang FROM Language WHERE id = ?',(msg.from_user.id, ))
        lan=c.fetchone()
        if str(*lan) == "ru":
            await bot.send_photo(msg.from_user.id, "AgACAgIAAxkBAAIEgWE9vm3lCZdVy-BrSA8btxBMj2HpAALNtTEbCXrxSc3jZYo4m6eYAQADAgADeQADIAQ" , caption = "⚠️В течении всего времени соревнований я буду напоминать тебе о лекциях и других мероприятиях\n\n🟡Чтобы открыть меню возможностей выполни команду /menu\n\n🟨Узнать всегда о нас и посмотреть наши контакты можно с помощью команды /kontakt\n\n🔆На этом мои полномочия все!\nЕсли тебе есть что предложить или как улучшить мою работу, смело задавай вопрос организаторам!", reply_markup=kom, parse_mode='HTML')
        else:
            await bot.send_photo(msg.from_user.id, "AgACAgIAAxkBAAIJ6GE_lC177zCJveRmAvziuVNamFnFAAKqtjEbcTEBSn_1x9lCK6qjAQADAgADeQADIAQ" , caption = "⚠️During the whole competition I will send reminders of lectures and other events.\n\n🟡To open the options menu, run the command /menu\n\n🟨Check our contacts by using the command /contacts\n\n🔆That’s it!\nIn case you have any suggestions on how to improve my work, feel free to share your ideas by using command /contacts", reply_markup=kom1, parse_mode='HTML')

@dp.message_handler(commands=['contacts'])
async def process_kontakt_command(msg: types.Message):
    db = sqlite3.connect("databot.db")
    c = db.cursor()
    i = [j[0] for j in c.execute("SELECT id FROM Users")] 
    if msg.from_user.id not in i:
        c.execute('SELECT lang FROM Language WHERE id = ?',(msg.from_user.id, ))
        lan=c.fetchone()
        if str(*lan) == "ru":
            await msg.answer("<b>Выполни для начала команду /start и укажи свой статус с помощью кнопок</b>", parse_mode='HTML')
        else:
            await msg.answer("<b>First run the command /start and indicate your status using the buttons</b>", parse_mode='HTML')
    else:
        c.execute('SELECT lang FROM Language WHERE id = ?',(msg.from_user.id, ))
        lan=c.fetchone()
        if str(*lan) == "ru":
            await bot.send_photo(msg.from_user.id, "AgACAgIAAxkBAAIEmWE9wHto7DbRtSr-OEmurheorrioAALStTEbCXrxSU3P6kjBcZIhAQADAgADeAADIAQ" , caption = "Наши контакты везде где мы есть!", reply_markup=kontakt, parse_mode='HTML')
        else:
            await bot.send_photo(msg.from_user.id, "AgACAgIAAxkBAAIEmWE9wHto7DbRtSr-OEmurheorrioAALStTEbCXrxSU3P6kjBcZIhAQADAgADeAADIAQ" , caption = " Please check our contacts from the list below.", reply_markup=kontakt1, parse_mode='HTML')

@dp.message_handler(commands=['photos'],state="*")
async def process_photos_command(msg: types.Message, state: FSMContext):
    await msg.answer("Отправь фото")
    await Photo.photo.set()

@dp.message_handler(content_types=['photo'],state=Photo.photo)
async def org(msg: types.Message, state: FSMContext):
    await msg.answer(msg.photo[-1].file_id)
    await state.finish()

@dp.message_handler(commands=['id'])
async def process_id_command(msg: types.Message):
    await msg.answer(msg.from_user.id)

@dp.message_handler(commands=['bear'])
async def process_id_command(msg: types.Message):
    await bot.send_video(msg.from_user.id, 'http://gifki-gifki.ru/go?http://i.imgur.com/7jws4xS.gif', None, 'Text')

@dp.message_handler(commands=['bear_all'])
async def process_id_command(msg: types.Message):
    db = sqlite3.connect("databot.db")
    c = db.cursor()
    i = [j[0] for j in c.execute("SELECT id FROM Users")]
    for p in range(0,len(i),1):
        await bot.send_video(i[p], 'http://gifki-gifki.ru/go?http://i.imgur.com/7jws4xS.gif', None, 'Text')

@dp.message_handler(commands=['menu'])
async def text(msg: types.Message):
    db = sqlite3.connect("databot.db")
    c = db.cursor()
    i = [j[0] for j in c.execute("SELECT id FROM Users")] 
    if msg.from_user.id not in i:
        c.execute('SELECT lang FROM Language WHERE id = ?',(msg.from_user.id, ))
        lan=c.fetchone()
        if str(*lan) == "ru":
            await msg.answer("<b>Выполни для начала команду /start и укажи свой статус с помощью кнопок</b>", parse_mode='HTML')
        else:
            await msg.answer("<b>First run the command /start and indicate your status using the buttons</b>", parse_mode='HTML')
    else:
        c.execute('SELECT lang FROM Language WHERE id = ?',(msg.from_user.id, ))
        lan=c.fetchone()
        if str(*lan) == "ru":
            await bot.send_photo(msg.from_user.id, "AgACAgIAAxkBAAIEb2E9uxwY971J9yzP_V0wAAFoz85SmwACyrUxGwl68Ul77sScxHKKjQEAAwIAA3kAAyAE" , caption = "🔶 Ты можешь задать вопрос <b>организаторам</b> или <b>спикеру</b>, который ведет лекцию!\n\n🔶 Выбери один из пунктов меню и напиши свой вопрос!", reply_markup=kom, parse_mode='HTML')
        else:
            await bot.send_photo(msg.from_user.id, "AgACAgIAAxkBAAIJ5GE_lAFmWunH52PaRgis3sE4BG61AAKptjEbcTEBSpvcAgksEc48AQADAgADeQADIAQ" , caption = "🔶 Feel free to ask the leading speaker the question or contact the organizer\n\n🔶 Pick any option from the list below and ask a question\nAsk speaker the question", reply_markup=kom1, parse_mode='HTML')

@dp.callback_query_handler(lambda c: c.data == 'org', state="*")
async def process_callback_button1(callback_query: types.CallbackQuery, state: FSMContext):
    db = sqlite3.connect("databot.db")
    c = db.cursor()
    i = [j[0] for j in c.execute("SELECT id FROM Users")] 
    o = [j[0] for j in c.execute("SELECT id FROM Language")] 
    if callback_query.from_user.id not in i and callback_query.from_user.id not in o:
        c.execute('SELECT lang FROM Language WHERE id = ?',(callback_query.from_user.id, ))
        lan=c.fetchone()
        if str(*lan) == "ru":
            await bot.send_message(callback_query.from_user.id,"<b>Выполни для начала команду /start и укажи свой статус с помощью кнопок</b>", parse_mode='HTML')
        else:
            await bot.send_message(callback_query.from_user.id,"<b>First run the command /start and indicate your status using the buttons</b>", parse_mode='HTML')
    else:
        c.execute('SELECT lang FROM Language WHERE id = ?',(callback_query.from_user.id, ))
        lan=c.fetchone()
        if str(*lan) == "ru":
            await bot.send_message(callback_query.from_user.id, 'Напишите ваш вопрос организаторам')
        else:
            await bot.send_message(callback_query.from_user.id, 'ask a question to the organizing team')
        await Obr.org.set()

@dp.message_handler(state=Obr.org)
async def org(msg: types.Message, state: FSMContext):
    db = sqlite3.connect('databot.db')
    c = db.cursor()
    c.execute('SELECT name FROM Users WHERE id = ?',(msg.from_user.id, ))
    name=c.fetchone()
    c.execute('SELECT kom FROM Users WHERE id = ?',(msg.from_user.id, ))
    kom=c.fetchone()
    c.execute('SELECT lang FROM Language WHERE id = ?',(msg.from_user.id, ))
    lan=c.fetchone()
    if str(*lan) == "ru":
        await msg.answer("Вопрос отправлен организаторам, скоро волонтер обязательно подойдет к вам и ответит")
    else:
        await msg.answer("Your question was received, we will answer it as soon as possible.")
    p = [j[0] for j in c.execute("SELECT kom FROM Users")]
    i1 = [j[0] for j in c.execute("SELECT id FROM Users")]
    for i in range(0,len(orgi),1):
        await bot.send_message(orgi[i], "<b>Вопрос организатору от </b>"+str(*name)+" со статусом "+str(*kom)+": "+msg.text,parse_mode='HTML')
        if str(p[i]) == "Волонтер":
            await bot.send_message(i1[i], "<b>Вопрос организатору от </b>"+str(*name)+" со статусом "+str(*kom)+": "+msg.text,parse_mode='HTML')
    await state.finish()
    c.close()
    db.close()

@dp.callback_query_handler(lambda c: c.data == 'que', state="*")
async def process_callback_button1(callback_query: types.CallbackQuery, state: FSMContext):
    db = sqlite3.connect("databot.db")
    c = db.cursor()
    i = [j[0] for j in c.execute("SELECT id FROM Users")] 
    if callback_query.from_user.id not in i:
        c.execute('SELECT lang FROM Language WHERE id = ?',(callback_query.from_user.id, ))
        lan=c.fetchone()
        if str(*lan) == "ru":
            await bot.send_message(callback_query.from_user.id,"<b>Выполни для начала команду /start и укажи свой статус с помощью кнопок</b>", parse_mode='HTML')
        else:
            await bot.send_message(callback_query.from_user.id,"<b>First run the command /start and indicate your status using the buttons</b>", parse_mode='HTML')
    else:
        c.execute('SELECT lang FROM Language WHERE id = ?',(callback_query.from_user.id, ))
        lan=c.fetchone()
        if str(*lan) == "ru":
            await bot.send_message(callback_query.from_user.id, 'Напишите ваш вопрос для спикера')
        else:
            await bot.send_message(callback_query.from_user.id, 'ask a question to the current speaker')
        await Obr.que.set()

@dp.message_handler(state=Obr.que)
async def org(msg: types.Message, state: FSMContext):
    db = sqlite3.connect('databot.db')
    c = db.cursor()
    c.execute('SELECT name FROM Users WHERE id = ?',(msg.from_user.id, ))
    name=c.fetchone()
    c.execute('SELECT kom FROM Users WHERE id = ?',(msg.from_user.id, ))
    kom=c.fetchone()
    c.execute('SELECT lang FROM Language WHERE id = ?',(msg.from_user.id, ))
    lan=c.fetchone()
    if str(*lan) == "ru":
        await msg.answer("Спасибо за вопрос, после лекции спикер ответит на ваш вопрос")
    else:
        await msg.answer("Thank you for your question. The speaker will answer it after the lecture.")
    p = [j[0] for j in c.execute("SELECT kom FROM Users")]
    i1 = [j[0] for j in c.execute("SELECT id FROM Users")]
    for i in range(0,len(orgi),1):
        await bot.send_message(orgi[i], "<b>Вопрос спикеру от </b>"+str(*name)+" со статусом "+str(*kom)+": "+msg.text,parse_mode='HTML')
        if str(p[i]) == "Волонтер":
            await bot.send_message(i1[i], "<b>Вопрос спикеру от </b>"+str(*name)+" со статусом "+str(*kom)+": "+msg.text,parse_mode='HTML')
    await state.finish()
    c.close()
    db.close()

async def time_func():
    current_datetime = datetime.now()
    db = sqlite3.connect("databot.db")
    c = db.cursor()
    ids = [j[0] for j in c.execute("SELECT id FROM Users")]
    values = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id,range='A1:H1000',majorDimension='ROWS').execute()
    lens = int(values['values'][-1][0])
    for i in range(1,int(lens)+1,1):
        if current_datetime.day == int(values['values'][i][1]):
            if current_datetime.hour == int(values['values'][i][2]-4):
                if current_datetime.minute == int(values['values'][i][3]):
                    if str(values['values'][i][4]) == "ожидает":
                        r="E"+str(i+1)
                        values1 = service.spreadsheets().values().batchUpdate(
                            spreadsheetId=spreadsheet_id,body = {
        "valueInputOption": "USER_ENTERED",
        "data": [
            {"range": r,
             "majorDimension": "ROWS",
             "values": [["отправлено"]]},]}
             ).execute()
                        text=str(values['values'][i][5])
                        if str(values['values'][i][6]) == "да":
                            for p in range(0,len(ids),1):
                                await bot.send_photo(ids[p], values['values'][i][7] , caption = text)
                        else:
                            for p in range(0,len(ids),1):
                                await bot.send_message(ids[p],text)
    c.close()
    db.close()
    
def Send():
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(time_func())
    loop.call_later(Delay, Send)


@dp.message_handler(content_types=['text'])
async def text(msg: types.Message):
    db = sqlite3.connect("databot.db")
    c = db.cursor()
    i = [j[0] for j in c.execute("SELECT id FROM Users")] 
    if msg.from_user.id not in i:
        c.execute('SELECT lang FROM Language WHERE id = ?',(msg.from_user.id, ))
        lan=c.fetchone()
        if str(*lan) == "ru":
            await msg.answer("<b>Выполни для начала команду /start и укажи свой статус с помощью кнопок</b>", parse_mode='HTML')
        else:
            await msg.answer("<b>First run the command /start and indicate your status using the buttons</b>", parse_mode='HTML')
    else:
        c.execute('SELECT lang FROM Language WHERE id = ?',(msg.from_user.id, ))
        lan=c.fetchone()
        if str(*lan) == "ru":
            await bot.send_photo(msg.from_user.id, "AgACAgIAAxkBAAIEb2E9uxwY971J9yzP_V0wAAFoz85SmwACyrUxGwl68Ul77sScxHKKjQEAAwIAA3kAAyAE" , caption = "🔶 Ты можешь задать вопрос <b>организаторам</b> или <b>спикеру</b>, который ведет лекцию!\n\n🔶 Выбери один из пунктов меню и напиши свой вопрос!", reply_markup=kom, parse_mode='HTML')
        else:
            await bot.send_photo(msg.from_user.id, "AgACAgIAAxkBAAIJ5GE_lAFmWunH52PaRgis3sE4BG61AAKptjEbcTEBSpvcAgksEc48AQADAgADeQADIAQ" , caption = "🔶 Feel free to ask the leading speaker the question or contact the organizer\n\n🔶 Pick any option from the list below and ask a question\nAsk speaker the question", reply_markup=kom1, parse_mode='HTML')

if __name__ == '__main__':
    print('Запускаю бота')
    while True:
        Send()
        executor.start_polling(dp) 
            
