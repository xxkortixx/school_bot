import asyncpg

from aiogram import Router, F, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards import menu_student,menu_teacher, save_lecture, all_subject, all_subject_del, keyboard_menu_student, keyboard_menu_teacher
from config import user, password, db_name, host, admin

router = Router()

# Обработчик основной команды start
@router.message(CommandStart())
async def command_start(message: types.Message):
    if admin == message.from_user.id:
        conn = await asyncpg.connect(
            user=user,
            password=password,
            database=db_name,
            host=host
        )

        # Создание базы данных
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS lecture_db(
                id SERIAL PRIMARY KEY,
                subject TEXT,
                name_lecture TEXT,
                info_lecture TEXT,
                file_id TEXT
            )''')
        reply_menu = menu_teacher()
        await message.answer(f"Здравствуйте! Меню:",reply_markup=reply_menu)
    else:
        reply_menu= menu_student()
        await message.answer(f"Здравствуйте! Меню:",reply_markup=reply_menu)

class LectureAdd(StatesGroup):
    name = State()
    subject = State()
    info = State()
    file_id = State()

# Обработчик для кнопки "Добавить книгу"
@router.callback_query(F.data == 'add_lecture')
async def add_book(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("📝Введите название лекции")
    await state.set_state(LectureAdd.name)

# Обработчики стейтов
@router.message(LectureAdd.name)
async def state_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text.lower())
    await message.answer("📝Введитеназвание предмета с Заглавной буквы")
    await state.set_state(LectureAdd.subject)

@router.message(LectureAdd.subject)
async def state_autor(message: types.Message, state: FSMContext):
    await state.update_data(subject=message.text.lower())
    await message.answer("📝Напишите описание лекции")
    await state.set_state(LectureAdd.info)

@router.message(LectureAdd.info)
async def state_info(message: types.Message, state: FSMContext):
    await state.update_data(info=message.text.lower())
    await message.answer("📝Отправьте файл лекции")
    await state.set_state(LectureAdd.file_id)

@router.message(LectureAdd.file_id)
async def state_genre(message: types.Message, state: FSMContext):
    await state.update_data(file_id=message.document.file_id)
    reply_keyboard = save_lecture()
    await message.answer("Нажмите на кнопку", reply_markup=reply_keyboard)

#оббработка кнопки созранить
@router.callback_query(F.data == "save")
async def save_lecture_db(callback: types.CallbackQuery,state: FSMContext):
    reply_keyboard = menu_teacher()
    data = await state.get_data()

    conn = await asyncpg.connect(
        user=user,
        password=password,
        database=db_name,
        host=host
    )
    try:
        await conn.execute(
            '''INSERT INTO lecture_db (name_lecture, subject, info_lecture, file_id) 
            VALUES($1, $2, $3, $4)''',
            data['name'], data['subject'], data['info'], data['file_id']
        )
    except Exception as e:
        print(e) 
    await conn.close()
    await state.clear()
    await callback.message.edit_text("Меню:", reply_markup=reply_keyboard)

#обработка кнопки лекции
@router.callback_query(F.data == "lecture")
async def button_lecture(callback: types.CallbackQuery):
    reply_keyboard = await all_subject()
    await callback.message.edit_text("Лекции:",reply_markup=reply_keyboard)

#поиск доступных лекций по предмету
async def search_lecture(subject):
    conn = await asyncpg.connect(
        user=user,
        password=password,
        database=db_name,
        host=host
    )
    books = await conn.fetch('''SELECT name_lecture, id FROM lecture_db WHERE subject ILIKE $1''', f'%{subject}%')
    await conn.close()
    return books

#вывод найденых лекций по предмету
@router.callback_query(F.data.startswith("subject:"))
async def lecture_subject(callback: types.CallbackQuery):
    subject = callback.data.split(":")[1]
    lecture = await search_lecture(subject)

    builder = InlineKeyboardBuilder()

    if lecture:
        builder = InlineKeyboardBuilder()
        for all_lecture_subject in lecture:
            builder.add(types.InlineKeyboardButton(text=f"{all_lecture_subject['name_lecture']}", callback_data=f"lecture:{all_lecture_subject['id']}"))
            builder.add(types.InlineKeyboardButton(text="↩️Главное меню",callback_data="menu:1"))
        
        await callback.message.edit_text("Лекции по этому предмету:", reply_markup=builder.as_markup())
    else:
        await callback.message.answer("Похоже что лекций по данному предмету пока нет!")

#получение информации о какой либо лекции + ее отправка
@router.callback_query(F.data.startswith("lecture:"))
async def handler_lecture(callback: types.CallbackQuery):
    reply_keyboard = keyboard_menu_student()
    lecture = int(callback.data.split(":")[1])
    conn = await asyncpg.connect(
        user=user,
        password=password,
        database=db_name,
        host=host
    )
    lecture_full_info = await conn.fetch(''' SELECT id, subject, name_lecture, info_lecture, file_id FROM lecture_db WHERE id = $1''',lecture)
    lecture_info = lecture_full_info[0]
    await callback.message.edit_text(f"Номер лекции: {lecture_info['id']}\n Название лекции: {lecture_info['name_lecture']}\n Предмет: {lecture_info['subject']}\n Информация о лекции: {lecture_info['info_lecture']}\n Файл:")
    await callback.bot.send_document(document=f"{lecture_info['file_id']}",chat_id=callback.message.chat.id,reply_markup=reply_keyboard)

#кнопка удаления лекций
@router.callback_query(F.data == "del_lecture")
async def button_del_lecture(callback: types.CallbackQuery):
    reply_keyboard = await all_subject_del()
    await callback.message.edit_text("Лекции:",reply_markup=reply_keyboard)

#предметы из бд в котрых есть лекции
@router.callback_query(F.data.startswith("subject_del:"))
async def lecture_subject_del(callback: types.CallbackQuery):
    subject = callback.data.split(":")[1]
    lecture = await search_lecture(subject)

    builder = InlineKeyboardBuilder()

    if lecture:
        builder = InlineKeyboardBuilder()
        for all_lecture_subject in lecture:
            builder.add(types.InlineKeyboardButton(text=f"{all_lecture_subject['name_lecture']}", callback_data=f"lecture_del:{all_lecture_subject['id']}"))
            builder.add(types.InlineKeyboardButton(text="↩️Главное меню",callback_data="menu:2"))
        await callback.message.edit_text("Лекции по этому предмету:", reply_markup=builder.as_markup())
    else:
        await callback.message.answer("Похоже что лекций по данному предмету пока нет!")

#лекции которые можно удалить
@router.callback_query(F.data.startswith("lecture_del:"))
async def list_lecture_del(callback: types.CallbackQuery):
    reply_keyboard = keyboard_menu_teacher()
    conn = await asyncpg.connect(
        user=user,
        password=password,
        database=db_name,
        host=host
    )
    data = int(callback.data.split(":")[1])
    await conn.execute("DELETE FROM lecture_db WHERE id = $1", data)
    await callback.message.edit_text("Меню:",reply_markup=reply_keyboard)

#обратока кнопок меню 
@router.callback_query(F.data.startswith("menu:"))
async def handler_menu(callback:types.CallbackQuery):
    action = int(callback.data.split(":")[1])
    if action == 1:
        reply_keyboard = menu_student()
        await callback.message.edit_text("Меню:",reply_markup=reply_keyboard)
    if action == 2:
        reply_keyboard = menu_teacher()
        await callback.message.edit_text("Меню:",reply_markup=reply_keyboard)

