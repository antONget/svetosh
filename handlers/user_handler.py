from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import requests
import asyncio
import logging
from config_data.config import Config, load_config
from services.googlesheets import append_client


router = Router()
# Загружаем конфиг в переменную config
config: Config = load_config()


class User(StatesGroup):
    get_name = State()
    get_phone = State()
    info_user = State()
    report2 = State()


user_dict = {}

def get_telegram_user(user_id, bot_token):
    url = f'https://api.telegram.org/bot{bot_token}/getChat'
    data = {'chat_id': user_id}
    response = requests.post(url, data=data)
    print(response.json())
    return response.json()


@router.message(CommandStart())
async def process_start_command_user(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Запуск бота пользователем /start
    :param message:
    :param state:
    :return:
    """
    logging.info(f'process_start_command_user: {message.chat.id}')
    await message.answer(text=f'Школа «Светоч знания» для детей с большим будущим!\n\n'
                              f'🌟 Учим читать, писать и считать. Развиваем память, логику и мышление🌟\n'
                              f'⬆️ Повышаем у ребёнка уверенность в себе и своих знаниях.\n'
                              f'⬆️ Повышаем успеваемость по всем предметам, за счет развития памяти и логики,'
                              f' ребенок быстро усваивает новую информацию.')
    await asyncio.sleep(2)
    await message.answer(text=f'<b><i>Диагностика интеллекта ребёнка позволит</i></b>:\n'
                              f' ☝️ узнать актуальный уровень его способностей,\n'
                              f' 💪 выявить сильные стороны и зоны роста,\n'
                              f' 👉 понять индивидуальную траекторию развития\n'
                              f' 👍  получить полноценную обратную связь и рекомендации',
                         parse_mode='HTML')
    await asyncio.sleep(2)
    await message.answer(text=f'Для записи оставьте ваши контакты и подпишитесь на наш Телеграм-канал: '
                              f'<a href="{config.tg_bot.channel}">https://t.me/svetoch_znaniya_spb</a>',
                         disable_web_page_preview=True,
                         parse_mode='HTML')

    user_channel_status = await bot.get_chat_member(chat_id=config.tg_bot.channel, user_id=message.from_user.id)

    if user_channel_status.status != 'left':
        await asyncio.sleep(2)
        await message.answer(text=f'Введите ваше имя:')
        await state.set_state(User.get_name)
    else:
        button_1 = KeyboardButton(text='Я подписался')
        keyboard = ReplyKeyboardMarkup(keyboard=[[button_1]], resize_keyboard=True)
        await message.answer(text=f'Для получения диагностики подпишись на канал: '
                                  f'<a href="https://t.me/svetoch_znaniya_spb">https://t.me/svetoch_znaniya_spb</a>',
                             reply_markup=keyboard,
                             parse_mode='HTML')


@router.message(F.text == 'Я подписался')
async def chek_subscription(message: Message, state: FSMContext, bot: Bot) -> None:
    logging.info(f'chek_subscription: {message.chat.id}')
    user_channel_status = await bot.get_chat_member(chat_id=config.tg_bot.channel, user_id=message.from_user.id)
    if user_channel_status.status != 'left':
        await asyncio.sleep(2)
        await message.answer(text=f'Введите ваше имя:')
        await state.set_state(User.get_name)
    else:
        button_1 = KeyboardButton(text='Я подписался')
        keyboard = ReplyKeyboardMarkup(keyboard=[[button_1]], resize_keyboard=True)
        await message.answer(text=f'Вы все еще не подписаны, для получения диагностики подпишись на канал: '
                                  f'<a href="https://t.me/svetoch_znaniya_spb">https://t.me/svetoch_znaniya_spb</a>',
                             reply_markup=keyboard,
                             parse_mode='HTML')


@router.message(F.text, StateFilter(User.get_name))
async def get_name_user(message: Message, state: FSMContext) -> None:
    logging.info(f'get_name_user: {message.chat.id}')
    await state.update_data(name_user=message.text)
    button_1 = KeyboardButton(text='Поделиться контактом ☎️', request_contact=True)
    keyboard = ReplyKeyboardMarkup(keyboard=[[button_1]], resize_keyboard=True)
    await message.answer(text=f'Введите ваш контактный телефон или нажмите «Поделиться контактом» ⤵️',
                         reply_markup=keyboard)
    await state.set_state(User.get_phone)


@router.message(StateFilter(User.get_phone))
async def get_phone_user(message: Message, state: FSMContext) -> None:
    logging.info(f'get_phone_user: {message.chat.id}')
    if message.contact:
        phone = message.contact.phone_number
        print(phone)
    else:
        phone = message.text
    await state.update_data(phone_user=phone)
    inline_btn_1 = InlineKeyboardButton(text='Пропустить', callback_data='pass')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[inline_btn_1]])
    await message.answer(text=f'Вы можете оставить комментарий \n(ФИ ребенка, удобный способ и время для связи и др.) '
                              f'или нажать пропустить.',
                         reply_markup=keyboard)
    await state.set_state(User.info_user)


@router.message(StateFilter(User.info_user))
async def get_info_user(message: Message, state: FSMContext, bot: Bot) -> None:
    logging.info(f'get_info_user: {message.chat.id}')
    await state.update_data(info=message.text)
    user_dict[message.chat.id] = await state.get_data()
    print('id_telegram= ', message.chat.id,
          'user_name= ', message.from_user.username,
          'name= ', user_dict[message.chat.id]['name_user'],
          'phone= ', user_dict[message.chat.id]['phone_user'])
    append_client(id_telegram=message.chat.id,
                  user_name=message.from_user.username,
                  name=user_dict[message.chat.id]['name_user'],
                  phone=user_dict[message.chat.id]['phone_user'],
                  info=user_dict[message.chat.id]['info'])

    channel = get_telegram_user(user_id=config.tg_bot.group_id, bot_token=config.tg_bot.token)
    if 'result' in channel:
        await bot.send_message(chat_id=config.tg_bot.group_id,
                               text=f'Telegram_id: {message.chat.id}\n'
                                    f'@username: {message.from_user.username}\n'
                                    f'Имя: {user_dict[message.chat.id]["name_user"]}\n'
                                    f'Телефон: {user_dict[message.chat.id]["phone_user"]}\n'
                                    f'Комментарий: {user_dict[message.chat.id]["info"]}')

    await message.answer(text=f'Благодарим!\n'
                              f'В ближайшее время с вами свяжутся администраторы нашего центра для согласования'
                              f' удобного времени и записи на диагностику.')

@router.callback_query(StateFilter(User.info_user))
async def get_info_user(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    logging.info(f'get_info_user: {callback.message.chat.id}')
    await state.update_data(info='None')
    user_dict[callback.message.chat.id] = await state.get_data()
    channel = get_telegram_user(user_id=config.tg_bot.group_id, bot_token=config.tg_bot.token)
    if 'result' in channel:
        append_client(id_telegram=callback.message.chat.id,
                      user_name=callback.from_user.username,
                      name=user_dict[callback.message.chat.id]['name_user'],
                      phone=user_dict[callback.message.chat.id]['phone_user'],
                      info=user_dict[callback.message.chat.id]['info'])

    await bot.send_message(chat_id=config.tg_bot.group_id,
                           text=f'Telegram_id: {callback.message.chat.id}\n'
                                f'@username: {callback.from_user.username}\n'
                                f'Имя: {user_dict[callback.message.chat.id]["name_user"]}\n'
                                f'Телефон: {user_dict[callback.message.chat.id]["phone_user"]}\n'
                                f'Комментарий: {user_dict[callback.message.chat.id]["info"]}')

    await callback.message.answer(text=f'Благодарим!\n'
                                       f'В ближайшее время с вами свяжутся администраторы нашего центра для согласования'
                                       f' удобного времени и записи на диагностику.')
