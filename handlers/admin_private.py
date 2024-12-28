from aiogram import F,types,Router,Bot
from aiogram.filters import Command,or_f,StateFilter

from database.orm_query import orm_add_info, orm_delete_info, orm_get_info, orm_get_one_info, orm_update_info, orm_get_member_by_name,orm_update_member,orm_get_all_members
from filters.chat_filter import ChatTypeFilter,isAdmin
from aiogram.fsm.state import State,StatesGroup
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.reply import get_keyboard
from keyboards.inline import get_callback_btns

admin_private_router=Router()
admin_private_router.message.filter(ChatTypeFilter(["private"]),isAdmin())


KB_ADMIN=get_keyboard(
        "Переглянути інформацію",
        "Оцінити роботу",
        "Додати інформацію про зустріч",
        "Надіслати опитування",
        
        placeholder="Оберіть опцію",
        sizes=(2,2),
        )

class AddInfo(StatesGroup):
    name=State()
    description=State()
    image=State()

    info_for_change = None

    texts={
        "AddInfo:name":"Введіть назву заново",
        "AddInfo:description":"Введіть опис заново",
        "AddInfo:photo":"Це останній стейт",
    }
class AddMark(StatesGroup):
    mark=State()
    save_mark=State()

class AddSurvey(StatesGroup):
    survey=State()



@admin_private_router.message(Command("admin"))
async def start_command(message:types.Message):
    await message.answer("Що вас цікавить?",
        reply_markup=KB_ADMIN
    )

@admin_private_router.message(or_f(Command("send_survey"),F.text.lower()=="надіслати опитування"))
async def survey_command(message:types.Message,state: FSMContext):
    await message.answer("Write a message that must be send")
    await state.set_state(AddSurvey.survey)

@admin_private_router.message(AddSurvey.survey)
async def survey_save(message:types.Message,state: FSMContext,bot: Bot,session:AsyncSession):
    members=await orm_get_all_members(session)
    for user_id in members:
        try:
            await bot.send_message(user_id,"Admin sent a survey:"+"\n"+str(message.text))
            await message.answer("Survey is sending ",reply_markup=KB_ADMIN)
        except Exception as e:
            await message.answer("Error "+str(e),reply_markup=KB_ADMIN)

@admin_private_router.message(or_f(Command("mark_results"),F.text.lower()=="оцінити роботу"))
async def menu_command(message:types.Message,state: FSMContext):
    await message.answer("Write few first letters of member")
    await state.set_state(AddMark.mark)

@admin_private_router.message(AddMark.mark)
async def search_mark_name_(message: types.Message,state:FSMContext,session:AsyncSession):
    for member in await orm_get_member_by_name(session,message.text):
        await message.answer(
            "Name: "+member.name+"\n"+"Surname: "+member.surname+"\n"+"Team: "+member.team,
            reply_markup=get_callback_btns(btns={
                'Mark':f'givemark_{member.id}'
            })
            )
    await message.answer("Choose member that u want to mark")

@admin_private_router.callback_query(F.data.startswith('givemark_'))
async def set_mark_by_id(callback:types.CallbackQuery,state:FSMContext,session:AsyncSession):
    member_id=callback.data.split("_")[-1]
    await state.update_data(id=member_id)
    await callback.message.answer("Enter mark for member that u want to mark")
    await state.set_state(AddMark.save_mark)

@admin_private_router.message(AddMark.save_mark)
async def save_mark_by_id(message: types.Message,state:FSMContext,session:AsyncSession):
    await state.update_data(mark=message.text)
    data= await state.get_data()
    mark = data.get("mark")
    id = data.get("id")
    try:
        await orm_update_member(session,id,int(mark))
        await message.answer("Mark добавлено",reply_markup=KB_ADMIN)
        await state.clear()
    except Exception as e:
        await message.answer("Помилка:\n"+str(e),reply_markup=KB_ADMIN)
        await state.clear()


@admin_private_router.message(or_f(Command("show_info"),F.text.lower()=="переглянути інформацію"))
async def menu_command(message:types.Message,session:AsyncSession):
    for info in await orm_get_info(session):
        await message.answer_photo(
            info.image,
            caption=info.name+"\n"+info.description,
            reply_markup=get_callback_btns(btns={
                'Видалити':f'delete_{info.id}',
                'Редагувати':f'change_{info.id}'
            })
        )
    await message.answer("Ось список зустріч")

@admin_private_router.callback_query(F.data.startswith('delete_'))
async def delete_product(callback:types.CallbackQuery,session:AsyncSession):
    product_id=callback.data.split("_")[-1]
    await orm_delete_info(session,int(product_id))
    await callback.message.answer('Інформацію видалено')

@admin_private_router.callback_query(StateFilter(None), F.data.startswith("change_"))
async def change_info_callback(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    info_id = callback.data.split("_")[-1]

    info_for_change = await orm_get_one_info(session, int(info_id))

    AddInfo.info_for_change = info_for_change

    await callback.answer()
    await callback.message.answer(
        "Введіть назву", reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AddInfo.name)






@admin_private_router.message(StateFilter(None),F.text=="Додати інформацію про зустріч")
async def add_info(message: types.Message,state:FSMContext):
    await message.answer("Введіть назву",reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddInfo.name)

@admin_private_router.message(StateFilter("*"),F.text.casefold()=="назад")
@admin_private_router.message(Command("назад"))
async def add_info_back(message: types.Message,state:FSMContext)->None:
    current_state=await state.get_state()
    if current_state== AddInfo.name:
        await message.answer("Ви на початку! Введіть назву або напишіть 'відмінити'")
        return
    previous = None
    for step in AddInfo.__all_states__:
        if step.state ==current_state:
            await state.set_state(previous)
            await message.answer("Ви повернулись назад \n {AddInfo.texts[previous.state]}")
            return
        previous=step
    

@admin_private_router.message(StateFilter("*"),F.text.casefold()=="відмінити")
@admin_private_router.message(Command("відмінити"))
async def add_info_cancel(message: types.Message,state:FSMContext)->None:
    current_state = await state.get_state()
    if current_state is None:
        return
    if AddInfo.info_for_change:
        AddInfo.info_for_change=None
    await state.clear()
    await message.answer("Всі дії відмінено",reply_markup=KB_ADMIN)

@admin_private_router.message(AddInfo.name, or_f(F.text, F.text == "."))
async def add_info_name(message: types.Message,state:FSMContext):
    if message.text == "." and AddInfo.info_for_change:
        await state.update_data(name=AddInfo.info_for_change.name)
    else:
        await state.update_data(name=message.text)
    await message.answer("Введіть опис")
    await state.set_state(AddInfo.description)

@admin_private_router.message(AddInfo.name)
async def add_info_name_repeat(message: types.Message,state:FSMContext):
    await message.answer("Ви ввели недопустимі дані.Введіть назву корректно")
    
@admin_private_router.message(AddInfo.description,or_f(F.text, F.text == "."))
async def add_info_description(message: types.Message,state:FSMContext):
    if message.text == "." and AddInfo.info_for_change:
        await state.update_data(description=AddInfo.info_for_change.description)
    else:
        await state.update_data(description=message.text)
    await message.answer("Надішліть фото")
    await state.set_state(AddInfo.image)

@admin_private_router.message(AddInfo.description)
async def add_info_description_repeat(message: types.Message,state:FSMContext):
    await message.answer("Ви ввели недопустимі дані.Введіть опис корректно")

    
@admin_private_router.message(AddInfo.image ,or_f(F.photo, F.text == "."))
async def add_info_photo(message: types.Message,state:FSMContext,session:AsyncSession):
     if message.text and message.text == "." and AddInfo.info_for_change:
        await state.update_data(image=AddInfo.info_for_change.image)
     else:
        await state.update_data(image=message.photo[-1].file_id)
     data= await state.get_data()

     try:
        if AddInfo.info_for_change:
            await orm_update_info(session,AddInfo.info_for_change.id,data)
        else:
            await orm_add_info(session,data)
        await message.answer("Інформацію добавлено",reply_markup=KB_ADMIN)
        await state.clear()
     except Exception as e:
        await message.answer("Помилка:\n"+str(e),reply_markup=KB_ADMIN)
        await state.clear()
        AddInfo.info_for_change=None

@admin_private_router.message(AddInfo.image ,F.text)
async def add_info_photo_repeat(message: types.Message,state:FSMContext):
    await message.answer("Ви ввели недопустимі дані.Надішліть фото заново")
