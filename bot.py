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
from config import TOKEN, Delay, menu
import sqlite3
import string
import time
import random
from datetime import datetime
import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials

CREDENTIALS_FILE = 'creds.json'

spreadsheet_id = '11v8cwsDNg8nQoqly9RnW2majX76sgtI_3kkjpHB_rwU'

credentials = ServiceAccountCredentials.from_json_keyfile_name(
    CREDENTIALS_FILE,
    ['https://www.googleapis.com/auth/spreadsheets',
     'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())
service = apiclient.discovery.build('sheets', 'v4', http = httpAuth)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

S=InlineKeyboardButton('Наш сайт', url='https://volgactf.ru/')
V=InlineKeyboardButton('Мы в ВКонтакте', url='https://vk.com/volgactf')
T=InlineKeyboardButton('Мы в Twitter', url='https://twitter.com/volgactf')
G=InlineKeyboardButton('Наш Github', url='https://github.com/volgactf')
Y=InlineKeyboardButton('Мы в Youtube', url='https://www.youtube.com/channel/UCTbjY5Xys-CgMBN8jgLazPA')
kontakt=InlineKeyboardMarkup(row_width=2).add(S,V,T,G,Y)

k1=InlineKeyboardButton('Связаться с организаторами', callback_data='org')
k2=InlineKeyboardButton('Задать вопрос спикеру', callback_data='que')
kom=InlineKeyboardMarkup(row_width=2).add(k1,k2)

button1 = KeyboardButton('Меню')
markup = ReplyKeyboardMarkup(resize_keyboard=True).row(button1)

class Obr(StatesGroup):
        org=State()
        que=State()

class Photo(StatesGroup):
        photo=State()

@dp.message_handler(commands=['start'])
async def process_start_command(msg: types.Message):
    db = sqlite3.connect("databot.db")
    c = db.cursor()
    if msg.from_user.last_name == None:
        name=str(msg.from_user.first_name)
    elif msg.from_user.first_name == None:
        name=str(msg.from_user.last_name)
    else:
        name=str(msg.from_user.first_name+" "+msg.from_user.last_name)
    i = [j[0] for j in c.execute("SELECT id FROM Users")] 
    if msg.from_user.id not in i:
        c.execute('INSERT INTO Users VALUES (?,?)', (msg.from_user.id,name))
        db.commit()
        await bot.send_sticker(msg.from_user.id,'CAACAgIAAxkBAAEC3DBhNQW4ZWueVa7IVZAfjyDG7ZTd6gACAQADkp8eEQpfUwLsF-b2IAQ')
        await msg.answer("<b>Привет </b>"+name+"!\nЯ бот-волонтер который поможет тебе на VolgaCTF.\nЯ буду напоминать тебе о лекциях и других мероприятиях, которые будут проходить во время наших соревнований.\nТакже через меня ты можешь задать вопрос организаторам и спикерам, которые будут выступать.\n<b>Хороших соревнований!</b>\nЕсли ты забудешь, что же я умею, ты всегда можешь ввести команду /help и я напомню.",reply_markup=markup, parse_mode='HTML')
    else:
        await bot.send_sticker(msg.from_user.id,'CAACAgIAAxkBAAEC3DJhNQYZozj6kQ4flQiSo-AUj_b1xQACXgADkp8eEbuhuIbpKqCeIAQ')
        await msg.answer("<b>Мы с тобой уже знакомились!</b>\nЕсли ты хочешь вспомнить, что я умею, то выполним команду /help", parse_mode='HTML')
    c.close()
    db.close()

@dp.message_handler(commands=['help'])
async def process_help_command(msg: types.Message):
        await msg.answer("<b>Давай я тебе напомню что я умею:</b>", reply_markup=kom,parse_mode='HTML')
        await msg.answer("<b>Наши контакты:</b>",reply_markup=kontakt, parse_mode='HTML')
        await bot.send_sticker(msg.from_user.id,'CAACAgIAAxkBAAEC3DRhNQad_42Jq5FJBh74ciRoLKJQPQACvBEAAkedeUmcfVpCt_UYuyAE')

@dp.message_handler(commands=['photos'],state="*")
async def process_photos_command(msg: types.Message, state: FSMContext):
    await msg.answer("Отправь фото")
    await Photo.photo.set()

@dp.message_handler(content_types=['photo'],state=Photo.photo)
async def org(msg: types.Message, state: FSMContext):
    await msg.answer(msg.photo[-1].file_id)
    await state.finish()

@dp.message_handler(content_types=['text'])
async def text(msg: types.Message):
    if msg.text in menu:
        await msg.answer("Меню: ",reply_markup=kom)

@dp.callback_query_handler(lambda c: c.data == 'org', state="*")
async def process_callback_button1(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback_query.from_user.id, 'Напишите ваш вопрос организаторам')
    await Obr.org.set()

@dp.message_handler(state=Obr.org)
async def org(msg: types.Message, state: FSMContext):
    await msg.answer("Спасибо за вопрос, мы обязательно на него скоро ответим")
    db = sqlite3.connect('databot.db')
    c = db.cursor()
    c.execute('SELECT name FROM Users WHERE id = ?',(msg.from_user.id, ))
    name=c.fetchone()
    await bot.send_message(618043018, "<b>Вопрос организаторам от </b>"+str(*name)+": "+msg.text,parse_mode='HTML')
    await state.finish()
    c.close()
    db.close()

@dp.callback_query_handler(lambda c: c.data == 'que', state="*")
async def process_callback_button1(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback_query.from_user.id, 'Напишите ваш вопрос спикеру')
    await Obr.que.set()

@dp.message_handler(state=Obr.que)
async def org(msg: types.Message, state: FSMContext):
    await msg.answer("Спасибо за вопрос, после лекции спикер ответит на ваш вопрос")
    db = sqlite3.connect('databot.db')
    c = db.cursor()
    c.execute('SELECT name FROM Users WHERE id = ?',(msg.from_user.id, ))
    name=c.fetchone()
    await bot.send_message(618043018, "<b>Вопрос спикеру от </b>"+str(*name)+": "+msg.text,parse_mode='HTML')
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
            if current_datetime.hour == int(values['values'][i][2])-4:
                if current_datetime.minute == int(values['values'][i][3])-4:
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

if __name__ == '__main__':
    print('Запускаю бота')
    while True:
        Send()
        executor.start_polling(dp) 
            
