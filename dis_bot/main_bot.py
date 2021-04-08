import discord
import asyncio
from discord.ext import commands
import random

TOKEN = "ODI4NzMyNjY1NjE1ODc2MTE3.YGt3cA.W-Ty1DE9JbQp-lv9iavb-VlLHN0"  # токен бота
# чтобы "активировать" команду пользователь должен написать ">" перед сообщением
bot = commands.Bot(command_prefix='>')


def color_str(text):  # делает текст жирным
    return f'**{text}**'


@bot.command()
async def help_me(ctx):
    await ctx.send(f'Приветик! Я мафия-бот, проект двух лучших женщин в мире: Насти Сарпинской и Гузь Лизы :) \n'
                   f'Чтобы обратиться ко мне по коаманде достаточно написать ">твоя команда" (без кавычек) \n'
                   f'Вот какие команды я могу выполнить: \n'
                   f'{color_str(">new_game")} - Начало сбора игроков для новой игры в мафию, открытие комнаты ожидания')

@bot.command(name='new_game')
async def new_game(ctx):
    # как вариант для отметки автора сообщения ctx.message.author.mention(c @) или ctx.message.author (без @)
    await ctx.send(f'Игрок {ctx.message.author.mention} объявил набор в новую игру! Комната ожидания открыта! \n'
                   f'Всех желающих присоединиться к игре просим написать плюсик (+) \n'
                   f'Захотите выйти из комнаты ожидания поставте (-)')

bot.run(TOKEN) # запуск бота через токен