import re

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db import models


router = Router()


EMAIL_REGEX = re.compile(r"[\w\d.!#$%&'*+\\/=?^_`{|}~-]+@[\w\d](?:[\w\d-]{0,61}[\w\d])?(?:\.[\w\d](?:[\w\d-]{0,61}[\w\d])?)+")
PHONE_NUMBER_REGEX = re.compile(r"\+?\d[ -]?\(?\d{3}\)?[ -]?\d{3}(?:[ -]?\d{2}){2}")


class FindEmail(StatesGroup):
    get_input = State()
    add_to_db = State()

class FindPhoneNumber(StatesGroup):
    get_input = State()
    add_to_db = State()

class VerifyPassword(StatesGroup):
    get_input = State()



yes_no_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Да'), KeyboardButton(text='Нет')]
], resize_keyboard=True)


@router.message(Command('find_email'))
async def command_find_email(message: Message, state: FSMContext) -> None:
    await state.set_state(FindEmail.get_input)
    await message.answer("Ведите текст для поиска")


@router.message(FindEmail.get_input)
async def process_find_email(message: Message, state: FSMContext, session: AsyncSession) -> None:
    found = EMAIL_REGEX.findall(message.text)

    if not len(found):
        await state.clear()
        await message.answer("Email не найдены!")
        return

    ans = 'Результат:\n'
    for i, email in enumerate(found):
        ans += f'{i + 1}. {email}\n'

    ans += '\nСохранить найденные email в базе?'

    await state.set_state(FindEmail.add_to_db)
    await state.set_data({'emails': found})
    await message.answer(ans, reply_markup=yes_no_keyboard)


@router.message(FindEmail.add_to_db)
async def process_email_add_to_db(message: Message, state: FSMContext, session: AsyncSession) -> None:
    if message.text == 'Да':
        for email in (await state.get_data())['emails']:
            session.add(models.Email(email=email))
        await session.commit()

        await state.clear()
        await message.answer("Email'ы добавлены в базу!", reply_markup=ReplyKeyboardRemove())
        return

    await state.clear()
    await message.answer("Email'ы не добавлены в базу!", reply_markup=ReplyKeyboardRemove())


@router.message(Command('get_emails'))
async def get_emails(message: Message, state: FSMContext, session: AsyncSession) -> None:
    query = await session.execute(select(models.Email.email))
    res = query.all()

    if not len(res):
        await message.answer("Email'ы в базе отстутсвуют!")
        return

    ans = 'Сохраненные email:\n'
    for i, email in enumerate(res):
        ans += f'{i + 1}. {email.email}\n'

    await message.answer(ans)


@router.message(Command('find_phone_number'))
async def command_find_phone_number(message: Message, state: FSMContext) -> None:
    await state.set_state(FindPhoneNumber.get_input)
    await message.answer("Ведите текст для поиска")


@router.message(FindPhoneNumber.get_input)
async def process_find_phone_number(message: Message, state: FSMContext, session: AsyncSession) -> None:
    await state.clear()
    found = PHONE_NUMBER_REGEX.findall(message.text)

    if not len(found):
        await message.answer("Номера телефонов не найдены!")
        return

    ans = 'Результат:\n'
    for i, phone in enumerate(found):
        ans += f'{i + 1}. {phone}\n'

    ans += '\nСохранить найденные номера в базе?'

    await state.set_state(FindPhoneNumber.add_to_db)
    await state.set_data({'phones': found})
    await message.answer(ans, reply_markup=yes_no_keyboard)


@router.message(FindPhoneNumber.add_to_db)
async def process_phone_number_add_to_db(message: Message, state: FSMContext, session: AsyncSession) -> None:
    if message.text == 'Да':
        for phone_number in (await state.get_data())['phones']:
            session.add(models.PhoneNumber(phone_number=phone_number))
        await session.commit()

        await state.clear()
        await message.answer("Телефоны добавлены в базу!", reply_markup=ReplyKeyboardRemove())
        return

    await state.clear()
    await message.answer("Телефоны не добавлены в базу!", reply_markup=ReplyKeyboardRemove())


@router.message(Command('get_phone_numbers'))
async def get_phone_numbers(message: Message, state: FSMContext, session: AsyncSession) -> None:
    query = await session.execute(select(models.PhoneNumber.phone_number))
    res = query.all()

    if not len(res):
        await message.answer("Номера в базе отстутсвуют!")
        return

    ans = 'Сохраненные номера:\n'
    for i, phone in enumerate(res):
        ans += f'{i + 1}. {phone.phone_number}\n'

    await message.answer(ans)


@router.message(Command('verify_password'))
async def command_verify_password(message: Message, state: FSMContext) -> None:
    await state.set_state(VerifyPassword.get_input)
    await message.answer("Ведите пароль для проверки")

@router.message(VerifyPassword.get_input)
async def process_verify_password(message: Message, state: FSMContext) -> None:
    await state.clear()
    regexs = [r'\d', r'[a-z]', r'[A-Z]', r'[!@#$%^&*\(\)]']

    for regex in regexs:
        if not re.search(regex, message.text):
            await message.answer('Пароль простой')
            return

    await message.answer('Пароль сложный')
