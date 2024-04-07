import asyncpg

from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import user, password, db_name, host


def menu_student() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="📚Лекции",
        callback_data="lecture")
    )
    builder.adjust(2)
    return builder.as_markup()


def menu_teacher() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="📚Добавить лекцию",
        callback_data="add_lecture")
    )
    builder.add(types.InlineKeyboardButton(
        text="🗑Удалить лекцию",
        callback_data="del_lecture")
    )
    builder.adjust(2)
    return builder.as_markup()

def save_lecture() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="📚Сохранить",
        callback_data="save")
    )
    builder.adjust(2)
    return builder.as_markup()

def keyboard_menu_student() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="↩️Меню",
        callback_data="menu:1")
    )
    builder.adjust(3)
    return builder.as_markup()

def keyboard_menu_teacher() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="↩️Меню",
        callback_data="menu:2")
    )
    builder.adjust(3)
    return builder.as_markup()

async def all_subject() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    conn = await asyncpg.connect(
        user=user,
        password=password,
        database=db_name,
        host=host
    )
    
    for subject in await conn.fetch(''' SELECT DISTINCT subject FROM lecture_db '''):
        builder.add(types.InlineKeyboardButton(
            text=f"{subject['subject']}", callback_data=f"subject:{subject['subject']}"
        )) 
    builder.add(types.InlineKeyboardButton(
        text="↩️Главное меню",
        callback_data="menu:1"
    ))
    await conn.close()
    builder.adjust(1)
    return builder.as_markup()

async def all_subject_del() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    conn = await asyncpg.connect(
        user=user,
        password=password,
        database=db_name,
        host=host
    )
    
    for subject in await conn.fetch(''' SELECT DISTINCT subject FROM lecture_db '''):
        builder.add(types.InlineKeyboardButton(
            text=f"{subject['subject']}", callback_data=f"subject_del:{subject['subject']}"
        ))
    builder.add(types.InlineKeyboardButton(
        text="↩️Главное меню",
        callback_data="menu:2"
    ))
    await conn.close()
    builder.adjust(1)
    return builder.as_markup()



    
