from aiogram import Bot
from aiogram.types import BotCommand


async def set_bot_commands(bot: Bot):
    commands: dict[str, list[BotCommand]] = {}

    commands["en"] = [
        BotCommand(
            command="start",
            description="Start the bot",
        ),
    ]

    await bot.set_my_commands(commands=commands["en"])

    for commands_locale, bot_commands in commands.items():
        await bot.set_my_commands(commands=bot_commands, language_code=commands_locale)
