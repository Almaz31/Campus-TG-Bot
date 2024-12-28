from aiogram import F,types,Router,Bot
from aiogram.filters import CommandStart,Command
from filters.chat_filter import ChatTypeFilter


admin_group_router=Router()
admin_group_router.message.filter(ChatTypeFilter(["group","supergroup"]))

@admin_group_router.message(Command("admin"))
async def admin_command(message:types.Message,bot:Bot):
    chat_id=message.chat.id
    admins_list=await bot.get_chat_administrators(chat_id)
    admins_list = [
        member.user.id
        for member in admins_list
        if member.status=="creator" or member.status=="administrator"
    ]    
    bot.my_admin_list = admins_list
    if message.from_user.id in admins_list:
        await message.delete()
