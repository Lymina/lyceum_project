import discord
import asyncio
from discord.ext import commands
import random
import json
import requests
from translate import Translator
from lists_roles import *

TOKEN = 'тут мог бы быть токен'
# чтобы "активировать" команду пользователь должен написать ">" перед сообщением
bot = commands.Bot(command_prefix='>')
client = discord.Client()


# в булочную через Китай, здесь обитают все переменные (да, проще было сделать нельзя)
class ToTheBakeryThroughСhina:
    def __init__(self):
        self.flag_new_game = 0  # игра ещё не началась, игроки только набираются, можно брать роль
        self.flag_now_game = 0  # игра идёт прямо сейчас
        self.list_gamers = []


help_everything = ToTheBakeryThroughСhina()


def distribution(members):  # пока просто функция. можно связать с основной прогой
    length = len(members)
    random.shuffle(members)
    random.shuffle(members)
    random.shuffle(members)
    random.shuffle(members)  # чтоб уж наверняка :D
    if length < 5:
        return False, 'Увы, недостаточно игроков.'
    elif length == 5:
        return True, zip(members, FIVE_MEMBERS)
    elif length == 6:
        return True, zip(members, SIX_MEMBERS)
    elif length == 7:
        return True, zip(members, SEVEN_MEMBERS)
    elif length == 8:
        return True, zip(members, EIGHT_MEMBERS)
    elif length == 9:
        return True, zip(members, NINE_MEMBERS)
    elif length == 10:
        return True, zip(members, TEN_MEMBERS)
    elif length == 11:
        return True, zip(members, ELEVEN_MEMBERS)
    elif length == 12:
        return True, zip(members, TWELVE_MEMBERS)
    elif length == 13:
        return True, zip(members, THIRTEEN_MEMBERS)
    else:
        return False, 'Слишком много игроков, будет балаган ._.'


def color_str(text):  # делает текст жирным
    return f'**{text}**'


def get_quote():  # функция для получения мотивирующих цитат через api
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + "\n -" + json_data[0]['a']
    return quote


def translate(text_to_translate):  # функция перевода цитат (не работает)
    translator = Translator(from_lang='en', to_lang='ru')  # обоз
    end_text = translator.translate(text_to_translate)
    return text_to_translate


@bot.command()  # помогалка, тут всё понятно
async def help_me(ctx):
    await ctx.send(f'''Приветик! Я мафия-бот, проект двух лучших женщин в мире: Насти Сарпинской и Гузь Лизы :) 
    Чтобы обратиться ко мне по команде достаточно написать ">твоя команда" (без кавычек) 
    \nВот какие команды я могу выполнить:
    * {color_str(">new_game")} - Начало сбора игроков для новой игры в мафию, открытие комнаты ожидания  (ﾒ￣▽￣)︻┳═一
    * {color_str('>give @"пользователь" @"роль"')} - Начинайте новую игру? Возьмите себе роли "Игрок"\
    (чтобы писать в канале "город-n") или "Наблюдатель" (чтобы следить за игрой в канале "город-n") (>ω^)
    * {color_str(">start_game")} - Все игроки готовы? Отлично, введи эту команду и мы начнём!  
    ᄽὁȍ ̪ őὀᄿ

    * {color_str('>i_am_sad')} - Тебе грустно? Ничего страшного, я выведу
     специально для тебя мотивирующую цитату  (ﾉ◕ヮ◕)ﾉ*:･ﾟ✧''')


@bot.command(name='new_game')  # начало новой сессии, открываем комнату ожидания, можно брть роли
async def new_game(ctx):
    help_everything.flag_new_game = 1
    # как вариант для отметки автора сообщения ctx.message.author.mention(c @) или ctx.message.author (без @)
    await ctx.send(f'''Игрок {ctx.message.author.mention} объявил набор в новую игру! Комната ожидания открыта! 

    \nВсех желающих присоединиться к игре просим взять у нашего бота роль "Игрок",\
     те кто хотят просто посмотреть за ходом игры пусть возьмут роль "Наблюдатель". 
     Для этого напишите команду (>give @"пользователь" @"роль")
    \nИграть мы будем на нашем текстовом канале {color_str("город-n")}, так что топайте туда ^w^''')


@bot.command()
async def start_game(ctx):  # начало игры(!), раскидываем персонажей между игроками, роли брять нельзя
    help_everything.flag_new_game = 0  # больше роли брать нельзя!
    help_everything.flag_now_gane = 1  # игра началась
    await ctx.send(
        f'Комната ожидания закрыта! Кто не успел, тот опоздал! Роли брать нельзя до следующей игровой сессии!'
        f'Игроки, когда увидете в канале "город-n" сообщение можете начинать!'
        f'Наблюдатели, следите, чтобы всё было честно!')


@bot.command(name='i_am_sad')  # вывод мотивирующей цитаты на англиском (в планах перевод)
async def citata(ctx):
    text = get_quote()  # идём к нужной функции
    await ctx.send(f'''{ctx.message.author.mention}, не грусти! Лучше прочитай цитату дня:
    >>> {text}''')


@bot.command()  # раздаёт роли игркам и заносит их в свой список (решить проблему с выводом из списка)
async def give(ctx, member: discord.Member, role: discord.Role):
    if help_everything.flag_new_game == 1:  # делаем проверку, что комната ожидания открыта и роли брать можно
        try:
            get_role = discord.utils.get(ctx.guild.roles, id=role.id)
            await member.add_roles(get_role)  # выдаём роль
            help_everything.list_gamers.append(member)  # добавляем пользователя в список
            await ctx.send(f'{member} получил(а) роль {role}')  # говорим, что всё получилось
        except Exception:
            # если не нашлось роли/игрка, то говорим об этом
            await ctx.send(f'Неверное имя пользователя или роль! ({member}, {role})')
    else:
        # если что-то пошло не так - говорим об этом чату
        await ctx.send(f'''{ctx.message.author}, рано брать роли, мы ещё не начали новую игру!
        \nДля того, чтобы начать новую игру введи команду ">new_game"''')


def stop_game():  # завершение сессии игры, обнуляем всё
    # вставить обнуление роли Игрок(!)
    help_everything.flag_game_now = 0  # игра закончилась, опускаем флаг
    help_everything.list_gamers = []  # опустошаем список, игроки расходятся


bot.run(TOKEN)  # запуск бота через токен
