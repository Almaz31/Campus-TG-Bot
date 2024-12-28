from aiogram import F,Bot,Router,types
from aiogram.filters import CommandStart,Command,or_f

from database.orm_query import orm_get_info,orm_add_member,orm_get_member_mark
from filters.chat_filter import ChatTypeFilter
from keyboards.reply import get_keyboard
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.state import State,StatesGroup
from aiogram.fsm.context import FSMContext

user_private_router=Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))

class AddMember(StatesGroup):
    name=State()
    surname=State()
    team=State()
    mark=State()
    id_user=State()


@user_private_router.message(CommandStart())
async def start_command(message:types.Message,state:FSMContext):
    await message.answer("Введіть своє ім`я")
    await state.set_state(AddMember.name)

    """ await message.answer("Start",
        reply_markup=get_keyboard("Подивитись оцінку",
        "Інформація про зустрічі",
        placeholder="Що вас цікавить?",
        sizes=(2,)
        ),
    ) """

@user_private_router.message(AddMember.name,F.text)
async def add_member_name(message: types.Message,state:FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введіть прізвище")
    await state.set_state(AddMember.surname)

@user_private_router.message(AddMember.surname,F.text)
async def add_member_surname(message: types.Message,state:FSMContext):
    await state.update_data(surname=message.text)
    await message.answer("Введіть команду")
    await state.set_state(AddMember.team)

@user_private_router.message(AddMember.team,F.text)
async def add_member_team(message: types.Message,state:FSMContext,session:AsyncSession):
    await state.update_data(team=message.text.lower())
    await state.update_data(id_user=message.from_user.id)
    data= await state.get_data()
    try:
        await orm_add_member(session,data)
        await message.answer("Реєстрація успішно завершена",
            reply_markup=get_keyboard("Подивитись оцінку",
            "Інформація про зустрічі",
            placeholder="Що вас цікавить?",
            sizes=(2,)
            ),)
        await state.clear()
    except Exception as e:
        await message.answer("Помилка:\n"+str(e),reply_markup=get_keyboard("Подивитись оцінку",
            "Інформація про зустрічі",
            placeholder="Що вас цікавить?",
            sizes=(2,)
            ),)
        await state.clear()
    



@user_private_router.message(or_f(Command("info"),F.text.lower()=="інформація про зустрічі"))
async def menu_command(message:types.Message,session:AsyncSession):
    for info in await orm_get_info(session):
        await message.answer_photo(
            info.image,
            caption=info.name+"\n"+info.description
        )
    await message.answer("Ось інформація про зустрічі")

@user_private_router.message(or_f(Command("check_results"),F.text.lower()=="подивитись оцінку"))
async def menu_command(message:types.Message,session:AsyncSession):
    data = await orm_get_member_mark(session,message.from_user.id)
    try:
        await message.answer("U have "+str(data.mark))
    except Exception as e:
        await message.answer("U have not mark ")