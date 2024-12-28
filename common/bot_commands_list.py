from aiogram.types import BotCommand

private=[
    BotCommand(command="menu",description="Відкрити меню"),
    BotCommand(command="check_results",description="Подивитись оцінки"),

]
group=[
    BotCommand(command="post",description="Зробити пост"),
    BotCommand(command="mark_results",description="Поставити оцінки"),
    BotCommand(command="send_survey",description="Надіслати опитування"),
]