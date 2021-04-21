import discord
import asyncio
from discord.ext import commands
import random
import json
import requests
from translate import Translator
from lists_roles import *
import tracemalloc
import sqlite3

tracemalloc.start()
intents = discord.Intents.default()
intents.members = True


TOKEN = 'тут мог бы быть токен'
MAIN_CHANNEL = 0  # id главного канала
TOWN_N_CHANNEL = 0  # id города-n
DB = sqlite3.connect("db/roles_players.sqlite")  # подключаемся к нужной БД (создание курсоров ниже)

# чтобы "активировать" команду пользователь должен написать ">" перед сообщением
bot = commands.Bot(command_prefix='>')
client = discord.Client()
town_n_channel = bot.get_channel(TOWN_N_CHANNEL)  # определяем канал по id


# в булочную через Китай, здесь обитают все переменные (да, проще было сделать нельзя)
class ToTheBakeryThroughСhina:
    def __init__(self):
        self.flag_new_game = 0  # игра ещё не началась, игроки только набираются, можно брать роль
        self.flag_now_game = 0  # игра идёт прямо сейчас
        self.list_gamers = []  # список игрков
        self.count_id = 0

help_everything = ToTheBakeryThroughСhina()


def color_str(text):  # делает текст жирным
    return f'**{text}**'


def get_quote():  # функция для получения мотивирующих цитат через api
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + "\n -" + json_data[0]['a']
    return quote


async def rule_for_play():  # правила для игры, когда все роли созданы и игра только началась
    await bot.wait_until_ready()
    town_n_channel = bot.get_channel(TOWN_N_CHANNEL)  # определяем нужный нам чат по id
    # отправляем сообщения
    await town_n_channel.send('Итак, все роли разданы, а мафиози познакомились! Мы начинаем!')
    await town_n_channel.send('''```Уважаемые жители, у меня для вас ужасные новости! В городе завелась мафия!!! Ваша 
    цель истребить заразу и снова сделать город безопасным. Цель мафии подчнить себе город, истребив жалких жителей. 
    Наша игра будет состоять из 2 периодов: день и ночь. Ночью активные роли совершают свои действия, а днём мы все 
    дружно решаеим кого повесить ^w^ Все всё поняли? Отлично! Мы начинаем (⌐■_■)```''')

    # начинаем циклы день-ночь, мостик переход(!)


async def distribution(members):  # функция раскидки ролей
    await bot.wait_until_ready()
    town_n_channel = bot.get_channel(TOWN_N_CHANNEL)  # определяем нужный нам чат по id
    # КРАЙНЕ ВАЖНО
    # каждый элемент списка members должен иметь тип данных discord.Member
    # discord.Member выглядит +- так
    # [<Member id=768054429165027359 name='Lymina ^._.^' discriminator='1843' bot=False nick=None guild=<Guild
    # id=829821880549900298 name='Тест сервер для мафии ^w^' shard_id=None chunked=False member_count=3>>]

    length = len(members)
    random.shuffle(members)
    random.shuffle(members)
    random.shuffle(members)
    random.shuffle(members)  # чтоб уж наверняка :D
    # минимальное кол-во 5
    if length < 5:
        # говорим, что не так и возвращаем False
        await town_n_channel.send('Увы, недостаточно игроков.')
        return False
    # если всё получается
    elif length == 5:
        transfer_players(list(zip(members, FIVE_MEMBERS)))  # вводим в БД раскидку на человек-роль
        # list(zip(members, ∞_MEMBERS)) вернёт [(discord.Member, роль)....(discord.Member, роль)]
        bot.loop.create_task(distribution_roles())  # отправляем каждому игроку его роль в лс
        bot.loop.create_task(rule_for_play())  # выводим сообщение, что роли раскиданы, а игра началась, мостик переход
        return True  # возвращаем, что всё хорошо

    # и так для каждого кол-ва игроков, для всех разные сценарии
    elif length == 6:
        transfer_players(list(zip(members, SIX_MEMBERS)))
        bot.loop.create_task(distribution_roles())  # отправляем каждому игроку его роль в лс
        bot.loop.create_task(rule_for_play())
        return True
    elif length == 7:
        transfer_players(list(zip(members, SEVEN_MEMBERS)))
        bot.loop.create_task(distribution_roles())  # отправляем каждому игроку его роль в лс
        bot.loop.create_task(rule_for_play())
        return True
    elif length == 8:
        transfer_players(list(zip(members, EIGHT_MEMBERS)))
        bot.loop.create_task(distribution_roles())  # отправляем каждому игроку его роль в лс
        bot.loop.create_task(rule_for_play())
        return True
    elif length == 9:
        transfer_players(list(zip(members, NINE_MEMBERS)))
        bot.loop.create_task(distribution_roles())  # отправляем каждому игроку его роль в лс
        bot.loop.create_task(rule_for_play())
        return True
    elif length == 10:
        transfer_players(list(zip(members, TEN_MEMBERS)))
        bot.loop.create_task(distribution_roles())  # отправляем каждому игроку его роль в лс
        bot.loop.create_task(rule_for_play())
        return True
    elif length == 11:
        transfer_players(list(zip(members, ELEVEN_MEMBERS)))
        bot.loop.create_task(distribution_roles())  # отправляем каждому игроку его роль в лс
        bot.loop.create_task(rule_for_play())
        return True
    elif length == 12:
        transfer_players(list(zip(members, TWELVE_MEMBERS)))
        bot.loop.create_task(distribution_roles())  # отправляем каждому игроку его роль в лс
        bot.loop.create_task(rule_for_play())
        return True
    elif length == 13:
        transfer_players(list(zip(members, THIRTEEN_MEMBERS)))
        bot.loop.create_task(distribution_roles())  # отправляем каждому игроку его роль в лс
        bot.loop.create_task(rule_for_play())
        return True
    # максимальное кол-во игоров 13
    else:
        # говорим, что не так и возвращаем False
        await town_n_channel.send('Слишком много игроков, будет балаган ._.')
        return False

def transfer_players(spis_of_gamer_and_role):  # записывае в БД (roles_players.sqlite) игрок-роль
    # для справки player выглядит так
    # [<Member id=768054429165027359 name='Lymina ^._.^' discriminator='1843' bot=False nick=None guild=<Guild
    # id=829821880549900298 name='Тест сервер для мафии ^w^' shard_id=None chunked=False member_count=3>>]

    for player, role in spis_of_gamer_and_role:
        cur = DB.cursor() # создаём курсор
        help_everything.count_id += 1 # ведём учет id

        # заносим даные по игроку в БД
        a = (help_everything.count_id, player.name + '#' + player.discriminator, player.id, role)
        cur.execute(f"""INSERT INTO players(id, nick_name, nick_id, role) VALUES(?, ?, ?, ?)""", a)

def say_rule_for_member(name):  # смотрит роль игорка в БД и создаёт текст роль-возможности
    cur = DB.cursor() # создаём курсор
    # получаем роль игрока и отправляем её пользователю с инструкцией
    result = cur.execute("""SELECT * FROM players WHERE nick_name = ?""", (name,)).fetchall()
    return f'{name}, твоя роль {result[0][3]}! ' \
           f'\n {MSG_ROLS[result[0][3]]}'

async def distribution_roles():
    # отправляет запрос для текста про роль игрока и отсылает его в лс, так для каждого кто есть в списке
    await bot.wait_until_ready()

    for memb in help_everything.list_gamers:  # пробегаемся по игрокам
        user_name = await bot.fetch_user(memb.id)  # ищем имя пользователя
        text = say_rule_for_member(user_name)  # определяем какой будем отправлять пользователю текст
        user.send(text)  # отправляем текст


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
     специально для тебя мотивирующую цитату   (ﾉ◕ヮ◕)ﾉ*:･ﾟ✧''')


@bot.command(name='new_game')  # начало новой сессии, открываем комнату ожидания, можно брть роли
async def new_game(ctx):
    help_everything.flag_new_game = 1
    # как вариант для отметки автора сообщения ctx.message.author.mention(c @) или ctx.message.author (без @)
    await ctx.send(f'''Игрок {ctx.message.author.mention} объявил набор в новую игру! Комната ожидания открыта!
    \nВсех желающих присоединиться к игре просим взять у нашего бота роль "Игрок",\
     те кто хотят просто посмотреть за ходом игры пусть возьмут роль "Наблюдатель". 
     Для этого напишите команду (>give @"пользователь" @"роль")
    \nИграть мы будем на нашем текстовом канале {color_str("город-n")}, так что топайте туда ^w^''')


@bot.command()  # начало игры(!), раскидываем персонажей между игроками, роли брять нельзя
async def start_game(ctx):
    help_everything.flag_new_game = 0  # больше роли брать нельзя!
    help_everything.flag_now_game = 1  # игра началась
    await ctx.send('''Комната ожидания закрыта! Кто не успел, тот опоздал! Роли брать нельзя до следующей игровой 
    сессии! Игроки, когда увидете в канале "город-n" сообщение можете начинать! Наблюдатели, следите, чтобы всё было 
    честно!''')
    distribution(help_everything.list_gamers)  # начинаем раскидку ролей, мостик переход


@bot.command(name='i_am_sad')  # вывод мотивирующей цитаты на англиском (в планах перевод)
async def citata(ctx):
    text = get_quote()  # идём к нужной функции
    await ctx.send(f'''{ctx.message.author.mention}, не грусти! Лучше прочитай цитату дня:
    >>> {text}''')


@bot.command()  # раздаёт роли игркам и заносит их в свой список (решить проблему с выводом из списка)
async def give(ctx, member: discord.Member, role: discord.Role):
    if help_everything.flag_new_game:  # делаем проверку, что комната ожидания открыта и роли брать можно
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
        await ctx.send(f'''{ctx.message.author}, рано брать роли мы ещё не начали новую игру!
        \nДля того чтобы начать новую игру введи команду ">new_game"''')


def stop_game():  # завершение сессии игры, обнуляем всё
    # вставить обнуление роли Игрок(!)
    help_everything.flag_game_now = 0  # игра закончилась, опускаем флаг
    help_everything.list_gamers = []  # опустошаем список, игроки расходятся
    help_everything.count_id = 0


bot.run(TOKEN)  # запуск бота через токен

# Ход игры
# 1 - кто-то начинает сессию через new_game
# 2 - игроки берут роли, пока кто-то не пишет start_game
# 3 - идёт раскидка ролей и их занос в БД
#   отправка ролей кажому игроку distribution_roles + say_rule_for_member
# 4 - бот объявляет, что игра начинается - rule_for_play
# 5 ∞ циклы день-ночь
# ночь: бот принимает действия по порядку от: мафии, врача, путаны, маньяка, дона, шерифа (см сценарий игры)
# день: бот говорит кого убили и ждёт решения игроков (условно >команда @Игрок, бот его убивает и говорит его роль)
# после завершения каждого периода проверка на то не выйгра ла ли одна из сторон (сравнение кол-ва игроков на сторонах)
# 6 - объявление результатов
# 7 - чистка всех и вся

# те new_game (+) -> give (+) -> start_game (+) -> внутренние функции(distribution + distribution_roles) ->
# rule_for_play (+) -> циклы день∞ночь∞проверка на выйгрыш -> объявление результатов -> чистка всех и вся
