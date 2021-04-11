import discord
import asyncio
from discord.ext import commands
import random
from decoder import decoder
from config import settings
import json, requests

TOKEN = "тут мог бы быть токен"
# чтобы "активировать" команду пользователь должен написать ">" перед сообщением
bot = commands.Bot(command_prefix='>')
client = discord.Client()
flag_expect = 0  # игра ещё не началась, игроки только набираются, можно брать роль
flag_game_now = 0  # игра идёт прямо сейчас

def color_str(text):  # делает текст жирным
    return f'**{text}**'

def get_quote():
  response = requests.get("https://zenquotes.io/api/random")
  json_data = json.loads(response.text)
  quote = json_data[0]['q'] + "\n -" + json_data[0]['a']
  return(quote)

'''def translate(textToTranslate):
    Response = requests.get\
        (f'http://translate.google.ru/translate_a/t?client=x&text={textToTranslate}&hl=en&sl=en&tl=ru')
    print(Response.text)'''


@bot.command()
async def help_me(ctx):
    await ctx.send(f'''Приветик! Я мафия-бот, проект двух лучших женщин в мире: Насти Сарпинской и Гузь Лизы :) 
    Чтобы обратиться ко мне по команде достаточно написать ">твоя команда" (без кавычек) 
    \nВот какие команды я могу выполнить:
    * {color_str(">new_game")} - Начало сбора игроков для новой игры в мафию, открытие комнаты ожидания  (ﾒ￣▽￣)︻┳═一
    * {color_str('>i_am_sad')} - Тебе грустно? Ничего страшного, я выведу
     специально для тебя мотивирующую цитату  (ﾉ◕ヮ◕)ﾉ*:･ﾟ✧''')



@bot.command(name='new_game')
async def new_game(ctx):
    flag_expect = 0
    # как вариант для отметки автора сообщения ctx.message.author.mention(c @) или ctx.message.author (без @)
    await ctx.send(f'''Игрок {ctx.message.author.mention} объявил набор в новую игру! Комната ожидания открыта! 
    \nВсех желающих присоединиться к игре просим взять у нашего бота роль "Игрок".
    \nИграть мы будем на нашем текстовом канале {color_str("город-n")}, так что топайте туда ^w^''')

@bot.command(name='i_am_sad')
async def citata(ctx):
    text = get_quote()
    await ctx.send(f'''{ctx.message.author.mention}, не грусти! Лучше прочитай цитату дня:
    >>> {text}\n
    >>> {translate(text)}''')


def stop_game():
    # вставить обнуление роли Игрок(!)
    flag_game_now = 0 # игра закончилась, опускаем флаг


bot.run(TOKEN)  # запуск бота через токен
