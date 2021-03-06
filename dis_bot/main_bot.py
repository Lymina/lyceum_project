import asyncio
import json
import random
import sqlite3
import tracemalloc

import discord
import requests
from discord.ext import commands

from lists_roles import *
from dis_bot.lists_roles import MSG_ROLS

tracemalloc.start()
intents = discord.Intents.default()
intents.members = True

TOKEN = 'здравствуйте, это токен'
MAIN_CHANNEL_ID = 0  # id главного канала
TOWN_N_CHANNEL_ID = 0  # id города-n
MAFIA_CHANNEL_ID = 0  # id чата мафии
GAMER_ID = 0
WATCHER_ID = 0
DB = sqlite3.connect('db/roles_players.sqlite')  # подключаемся к нужной БД (создание курсоров ниже)

# чтобы "активировать" команду пользователь должен написать ">" перед сообщением
bot = commands.Bot(command_prefix='>')
client = discord.Client()


# в булочную через Китай, здесь обитают все переменные (да, проще было сделать нельзя)
class ToTheBakeryThroughChina:
    def __init__(self):
        self.flag_new_game = 0  # игра ещё не началась, игроки только набираются, можно брать роль
        self.flag_now_game = 0  # игра идёт прямо сейчас
        self.list_gamers = []  # список игрков
        self.list_gamers_name = []  # список имён игрков
        self.dikt_gamers = {}  # универсальный список-словарь для учёта игроков вида <номер игрока> - <его id>
        self.spis_night_move = []
        # обнуляется в начале каждой ночи, хранит в себе даннные типа [(id над кем совершено действие, действие),...()]
        self.count_id = 0
        self.votes = dict()  # словарь с голосами


help_everything = ToTheBakeryThroughChina()


def color_str(text):  # делает текст жирным
    return f'**{text}**'


def get_quote():  # функция для получения мотивирующих цитат через api
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + "\n -" + json_data[0]['a']
    return quote


async def night():  # правила для игры, когда все роли созданы и игра только началась
    await bot.wait_until_ready()
    town_n_channel = bot.get_channel(TOWN_N_CHANNEL_ID)  # определяем канал по id
    # отправляем сообщения
    await town_n_channel.send('Горячее солнце заходит в дали, нас ждут неизвестные в ночи пути...')
    await town_n_channel.send('```Город засыпает...```')
    await town_n_channel.send('(просьба всем участникам не писать в ночной эпизод в чат)')
    help_everything.spis_night_move = []

    # начинаем пробег по всем активным в ночи ролям по плану путана -> мафия -> доктор -> шериф -> дон -> маньяк
    # в чём заключается действие каждого игрока см в доп материалах
    # результаты действий игроков записываем в список вида [(имя над кем совершено действие, действие),...()]
    # типы действий: убит, вылечен, отвлёчен. Для дона и шерифа просто сразу говорим правы они или нет

    cur = DB.cursor()  # создаём курсор

    # проверяем есть ли в БД роль "путана"
    result = cur.execute("SELECT * FROM players WHERE role = ?;", ('путана',)).fetchall()
    if result:
        user_name = await bot.fetch_user(result[0][2])  # ищем имя пользователя по id
        await user_name.send('Добрый вечер, дорогая! К кому заглянем на кружечку чая сегодня?)')
        await user_name.send(f'Вот игроки к которым мы можем заглянуть, '
                             f'в качестве ответа напиши команду ">answer "номер игрока""')
        for num in help_everything.dikt_gamers:
            name = await bot.fetch_user(help_everything.dikt_gamers[num])  # ищем имя пользователя по id
            await user_name.send(f'{num}- {name.name}')
    # путана вводит свой ответ, идём дальше..

    # с мафией всё интереснее, тк она может быть не одна, найдём всех мафиози и выберем случайного,
    # напишем ему и он отдавать команду с решением
    result = cur.execute("SELECT * FROM players WHERE role = ?;", ('мафия',)).fetchall()
    maf_gamer = random.choice(result)  # из всего списка выбираем одного мафиози,
    # будет что-то такое (1, 'Gavan_terra#0926', 294121877847277568, 'мафия')
    maf = await bot.fetch_user(maf_gamer[2])  # ищем объект игрока мафии по id

    # а ещё путана может заблокировать действие всего клана мафии,
    # в этом случаее в spis_night_move будет кортэж вида ('мафия', "отвлечен")
    # сделаем проверку на это
    if ('мафия', "отвлечен") in help_everything.spis_night_move:
        await maf.send(
            'К клану мафии сегодня зашла ваша старая знакомая, чтобы выпить чаю, так что сегодня без убийств ^w^')
    else:
        await maf.send('Пиф-паф, сегодня ты мне расскажешь в кого будет стрелять клан мафии!')
        await maf.send(f'Вот игроки в которых можно выстрелить, '
                       f'в качестве ответа напиши команду ">answer "номер игрока""')
        result = cur.execute("SELECT id FROM players WHERE role = ?;", ('мафия',)).fetchall()
        sp_maf_id = []  # создаём список id мафии, чтобы исключить их из вариантов ответа
        for i in result:
            sp_maf_id.append(*i)
        # получаем что-то вроде [3, 4, 5]

        for num in help_everything.dikt_gamers:  # создаём варианты ответов, исключая мафию
            if num not in sp_maf_id:  # если id num нет в списке мафии
                name = await bot.fetch_user(help_everything.dikt_gamers[num])  # ищем имя пользователя по id
                await maf.send(f'{num}- {name.name}')  # предлагаем как вариант
        # мафия делает свой выбор, а мы идём дальше

    result = cur.execute("SELECT * FROM players WHERE role = ?;", ('доктор',)).fetchall()
    if result:
        id_dok = result[0][2]  # определяем id игрока доктора
        user_name = await bot.fetch_user(result[0][2])  # ищем доктора пользователя по id
        if (id, 'отвлечен') in help_everything.spis_night_move:
            await user_name.send('Доктор, к тебе зашла твоя старая знакомая выпить чаю.'
                                 ' Вы допоздна обсуждали свои проблеммы и ты не смог выйти на врачевание это ночью :/')
        else:
            await user_name.send('Док, на улицах творится беспредел, твоя помощь как никогда важна!')
            await user_name.send(
                'Это те, кто могут пострадать. В качестве ответа напиши команду ">answer "номер игрока""')
            for num in help_everything.dikt_gamers:
                name = await bot.fetch_user(help_everything.dikt_gamers[num])  # ищем имя пользователя по id
                await user_name.send(f'{num}- {name.name}')
            # док делает своё выбор, идём дальше

    result = cur.execute("SELECT * FROM players WHERE role = ?;", ('шериф',)).fetchall()
    if result:
        id_sher = result[0][2]
        user_name = await bot.fetch_user(id_sher)  # ищем шерифа по id
        if (id, 'отвлечен') in help_everything.spis_night_move:  # смотрим чаёвничала ли путана с шерифом
            await user_name.send('Старина, к тебе зашла твоя старая знакомая выпить чаю и поболтать :)'
                                 ' Вы так долго обсуждали проблемы, что ты забыл проверить жителей сегодня')
        else:  # если путана не приходила к шерифу выводим ему варианты ответа
            await user_name.send('Ну что дружище, кого будем проверять сегодня?')
            await user_name.send(
                'Это те, кто можно проверить. В качестве ответа напиши команду ">answer "номер игрока""')
            for num in help_everything.dikt_gamers:
                name = await bot.fetch_user(help_everything.dikt_gamers[num])  # ищем имя пользователя по id
                await user_name.send(f'{num}- {name.name}')
            # шриф делает свой выбор, идём дальше

    result = cur.execute("SELECT * FROM players WHERE role = ?;", ('дон',)).fetchall()
    if result:
        id_don = result[0][2]
        user_name = await bot.fetch_user(id_don)  # ищем шерифа по id
        if (id, 'отвлечен') in help_everything.spis_night_move:  # смотрим чаёвничала ли путана с шерифом
            await user_name.send('Сэр, к Вам зашла Ваша старая знакомая выпить чаю и поболтать :) После приятной '
                                 'беседы Вы '
                                 'понимаете, что не хотите сегодня искать шерифа и решаете отдохнуть')
        else:  # если путана не приходила к дону выводим ему варианты ответа
            await user_name.send('Кого проверить сегодня?')
            await user_name.send(
                'Это те, кто можно проверить. В качестве ответа напиши команду ">answer "номер игрока""')
            for num in help_everything.dikt_gamers:
                name = await bot.fetch_user(help_everything.dikt_gamers[num])  # ищем имя пользователя по id
                await user_name.send(f'{num}- {name.name}')
            # дон делает свой выбор, идём дальше

    result = cur.execute("SELECT * FROM players WHERE role = ?;", ('маньяк ',)).fetchall()
    if result:
        id_don = result[0][2]
        user_name = await bot.fetch_user(id_don)  # ищем шерифа по id
        if (id, 'отвлечен') in help_everything.spis_night_move:  # смотрим чаёвничала ли путана с шерифом
            await user_name.send('Сэр, к Вам зашла Ваша старая знакомая выпить чаю и поболтать :) После приятной '
                                 'беседы Вы '
                                 'понимаете, что не хотите сегодня искать шерифа и решаете отдохнуть')
        else:  # если путана не приходила к дону выводим ему варианты ответа
            await user_name.send('Хей-хей! Кого я вижу! Ну что старина, на кого ты направишь свой нож сегодня?')
            await user_name.send(
                'Это те, кто можно кокнуть. В качестве ответа напиши команду ">answer "номер игрока""')
            for num in help_everything.dikt_gamers:
                name = await bot.fetch_user(help_everything.dikt_gamers[num])  # ищем имя пользователя по id
                await user_name.send(f'{num}- {name.name}')
            # маньяк делает свой выбор, идём дальше

    print(help_everything.spis_night_move)
    # все роли отыграли своё действие. на этом период ночь заканчивается,
    # у нас есть spis_night_move с итогами дейсвий ночи вида [(id игрока, действие)...] с его помощю подведём итоги днем
    # те выкинем из БД убитых, обявим того у кого есть алиби (к нему заходила путана пить чай, действие "отвлечен")

    # добавить проверку на выйгрыш одной из сторон (полумостик переход(!))
    # если с проверки вернётся False начинаем период дня (мостик переход(!))


async def day():
    await bot.wait_until_ready()
    town_n_channel = bot.get_channel(TOWN_N_CHANNEL_ID)  # определяем канал по id
    # отправляем сообщения
    await town_n_channel.send('Приятное утреннее солнце вновь встало, прогоняя страшную ночь...')
    await town_n_channel.send('```Город просыпается...```')
    await town_n_channel.send('Сейчас мы подведем итоги прошлой ночи...')
    cur = DB.cursor()
    for elem in help_everything.spis_night_move:
        await town_n_channel.send(f'{discord.Client.fetch_user(elem[0])} был {elem[1]}')
        if elem[1] == 'убит':
            result = cur.execute("SELECT role FROM players WHERE nick_id = ?;", (elem[0],)).fetchall()
            out_role = result[0][0]  # запоминаеи роль
            await town_n_channel.send(f'Он(а) играл(а) прекрасную роль - {out_role}. Помянем.')
            cur.execute("DELETE role FROM players WHERE nick_id = ?;", (elem[0],)).fetchall()
        elif elem[1] == 'отвлечен':
            await town_n_channel.send(f'В эту ночь этого игрока {discord.Client.fetch_user(elem[0])} отвлекла путана. '
                                      f'Он занимался ничегонеделанием')
    await town_n_channel.send('Теперь ваша задача - казнить беспринципных преступников! Сделайте правильный выбор. '
                              'Для этого отправьте мне команду ">punishment @(игрок, которого вы выбрали)". А когда вы '
                              'будете полностью уверены в своем решении, отправьте мне команду ">end_punishment". '
                              'Удачи.')


async def victory(mafia, other, quite):
    await bot.wait_until_ready()
    town_n_channel = bot.get_channel(TOWN_N_CHANNEL_ID)  # определяем канал по id
    if len(mafia) == 0:
        if len(other) == 0 and len(quite) >= 1:
            await town_n_channel.send(
                '''В городе воцарился мир и порядок! Неорганизованная преступность искоренена! Ура!''')
        else:
            await town_n_channel.send('В городе возобладала неорганизованная преступность. Да будет хаос!')
    else:
        await town_n_channel.send('Власть в городе захвачена мафией!')
    stop_game()


@bot.command()  # это бункер казни, если не сработает основная, можно сделать все с помощью этой функции
async def punish(ctx, count_in_spis):
    # count_in_spis - номер игрока в словаре dikt_gamers над которым свершится действие
    count_in_spis = int(count_in_spis)  # ответ от пользователя str преобразовываем в int
    cur = DB.cursor()  # создаём курсор
    id_aut = ctx.message.author.id  # узнаём id автора команды -> роль автора -> тип действия
    result = cur.execute("SELECT role FROM players WHERE nick_id = ?;", (id_aut,)).fetchall()
    aut_role = result[0][0]  # запоминаеи роль автора команды

    chel = await bot.fetch_user(help_everything.dikt_gamers[count_in_spis])  # игрок над которым совершили действие
    # далее идут нюансы действий для каждой роли

    cur.execute('DELETE FROM players WHERE nick_name = ?;',
                (f'{chel.nick}#{chel.discriminator}',))
    DB.commit()
    chel.remove_roles(discord.Guild.get_role(GAMER_ID))
    chel.add_roles(discord.Guild.get_role(WATCHER_ID))


@bot.command()
async def punishment(ctx, member: discord.Member):
    if member in help_everything.votes:  # за игрока уже голосовали
        help_everything.votes[member] += 1
    else:  # за игрока проголосовали впервые
        help_everything.votes[member] = 1


@bot.command()
async def end_punishment(ctx):
    town_n_channel = bot.get_channel(TOWN_N_CHANNEL_ID)  # определяем канал по id
    if help_everything != {}:
        await bot.loop.create_task(back_punishment())
    else:
        await town_n_channel.send('Рано завершать голосование, еще никто не проголосовал!')


async def back_punishment():
    town_n_channel = bot.get_channel(TOWN_N_CHANNEL_ID)  # определяем канал по id
    list_votes = []
    for player, votes in help_everything.votes.items():
        list_votes.append((player, votes))
    sorted(list_votes, key=lambda vote: vote[1])
    candidate = list_votes[-1][0]
    cur = DB.cursor()
    res = cur.execute("""SELECT nick_name, role FROM players WHERE nick_name = ?""",
                      (f'{candidate.nick}#{candidate.discriminator}',)).fetchall()
    player_can = None
    role_can = None
    for elem in res:
        for player, role in elem:
            player_can, role_can = player, role
    await town_n_channel.send(f'Наш Город N покидает {player_can}. Он(а) играл(а) славную роль - {role_can}. Помянем.')
    cur.execute('''DELETE FROM players WHERE nick_name = ?''',
                (f'{candidate.nick}#{candidate.discriminator}',)).fetchall()
    candidate.remove_roles(discord.Guild.get_role(GAMER_ID))
    candidate.add_roles(discord.Guild.get_role(WATCHER_ID))


async def rule_for_play():  # правила для игры, когда все роли созданы и игра только началась
    await bot.wait_until_ready()
    town_n_channel = bot.get_channel(TOWN_N_CHANNEL_ID)  # определяем канал по id
    # отправляем сообщения
    await town_n_channel.send('Итак, все роли розданы, а мафиози познакомились! Мы начинаем!')
    await town_n_channel.send('''```Уважаемые жители, у меня для вас ужасные новости! В городе завелась мафия!!! Ваша 
    цель истребить заразу и снова сделать город безопасным. Цель мафии подчинить себе город, истребив жалких жителей. 
    Наша игра будет состоять из 2 периодов: день и ночь. Ночью активные роли совершают свои действия, а днём мы все 
    дружно решаем, кого повесить ^w^ Все всё поняли? Отлично! Мы начинаем (⌐■_■)```''')
    cur = DB.cursor()  # создаём курсор

    # наполним наш словарь
    for memb in help_everything.list_gamers:
        # получаем id игрока
        result = cur.execute("SELECT id FROM players WHERE nick_id = ?;", (memb.id,)).fetchall()
        # делаем запись в словарь вида номер игрока в БД- его id
        help_everything.dikt_gamers[result[0][0]] = memb.id

    # начинаем циклы день-ночь, мостик переход(!)
    bot.loop.create_task(night())  # активируем ночь, циклы запущены


async def distribution(members):  # функция раскидки ролей
    await bot.wait_until_ready()
    town_n_channel = bot.get_channel(TOWN_N_CHANNEL_ID)  # определяем нужный нам чат по id
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


def transfer_players(list_of_gamer_and_role):  # записывае в БД (roles_players.sqlite) игрок-роль
    # для справки player выглядит так
    # [<Member id=768054429165027359 name='Lymina ^._.^' discriminator='1843' bot=False nick=None guild=<Guild
    # id=829821880549900298 name='Тест сервер для мафии ^w^' shard_id=None chunked=False member_count=3>>]

    for player, role in list_of_gamer_and_role:
        cur = DB.cursor()  # создаём курсор
        help_everything.count_id += 1  # ведём учет id
        name = str(player.name) + '#' + str(player.discriminator)
        player_id = int(player.id)
        # заносим даные по игроку в БД и сохраняем замись комитом
        a = (help_everything.count_id, name, player_id, role)
        cur.execute("INSERT INTO players(id, nick_name, nick_id, role) VALUES(?, ?, ?, ?);", a)
        DB.commit()


def say_rule_for_member(name):  # смотрит роль игорка в БД и создаёт текст роль-возможности
    cur = DB.cursor()  # создаём курсор
    # получаем роль игрока и отправляем её пользователю с инструкцией
    result = cur.execute("SELECT * FROM players WHERE nick_name = ?;", (str(name),)).fetchall()
    # возвращает что-то вроде [(1, 'Lymina ^._.^#1843', 768054429165027359, 'мафия')]
    return [f'{name}, твоя роль {result[0][3]}! ' \
            f'\n {MSG_ROLS[result[0][3]]}', result[0][3]]


async def distribution_roles():
    # отправляет запрос для текста про роль игрока и отсылает его в лс, так для каждого кто есть в списке игроков
    await bot.wait_until_ready()
    for memb in help_everything.list_gamers:  # пробегаемся по игрокам
        user_name = await bot.fetch_user(memb.id)  # ищем имя пользователя по id
        text, role = say_rule_for_member(user_name)  # определяем какой будем отправлять пользователю текст
        await user_name.send(text)  # отправляем текст игроку в лс

        if role == 'мафия':  # если игрок оказался мафией, говорим ему о других мафиозиях

            # нереализованная идея с чатом мафии
            # строки ниже должны создавать приглашение в закрытый чат мафии и отправлять его игроку,
            # но что-то пошло не так...
            '''
            mafia_channel = bot.get_channel(MAFIA_CHANNEL_ID)  # подключаемся к приватному чату мафии
            invitelink = await mafia_channel.create_invite(max_uses=1,unique=True)
            await user_name.send(invitelink)
            '''

            # поэтому мы просто знакомим мафиозия с его семьёй
            cur = DB.cursor()  # создаём курсор
            # смотрим всех мафий и дона
            result = cur.execute("SELECT nick_name FROM players WHERE role = ? OR role = ?;",
                                 ('мафия', 'дон')).fetchall()
            # рассказываем игроку, что он не одинок (или наоборот)
            if result:
                await user_name.send(f'Кстати, вместе с тобой мафией являются: {result}. Не забывайте советоваться,'
                                     f' принимая решения!')
            else:
                await user_name.send('..похоже ты единсвенный представитель клана мафии...')


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
    await distribution(help_everything.list_gamers)  # начинаем раскидку ролей, мостик переход


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
            # добавляем имя пользователя в соответсвующий список
            help_everything.list_gamers_name.append(str(member.name))
            await ctx.send(f'{member} получил(а) роль {role}')  # говорим, что всё получилось
        except Exception:
            # если не нашлось роли/игрка, то говорим об этом
            await ctx.send(f'Неверное имя пользователя или роль! ({member}, {role})')
    else:
        # если что-то пошло не так - говорим об этом чату
        await ctx.send(f'''{ctx.message.author}, рано брать роли мы ещё не начали новую игру!
        \nДля того чтобы начать новую игру введи команду ">new_game"''')


@bot.command()  # используется во время игры, с её помощью игроки делают выбор над кем совершить действие
async def answer(ctx, count_in_spis):
    # count_in_spis - номер игрока в словаре dikt_gamers над которым свершится действие

    count_in_spis = int(count_in_spis)  # ответ от пользователя str преобразовываем в int
    cur = DB.cursor()  # создаём курсор
    id_aut = ctx.message.author.id  # узнаём id автора команды -> роль автора -> тип действия
    result = cur.execute("SELECT role FROM players WHERE nick_id = ?;", (id_aut,)).fetchall()
    aut_role = result[0][0]  # запоминаеи роль автора команды

    chel = await bot.fetch_user(help_everything.dikt_gamers[count_in_spis])  # игрок над которым совершили действие
    # далее идут нюансы действий для каждой роли

    if aut_role == 'мафия' or aut_role == 'маньяк':
        # в список ночных действий передаем кортэж с id убитого и типом действия [(id, "убит")]
        if (help_everything.dikt_gamers[count_in_spis], 'вылечен') not in help_everything.spis_night_move:
            help_everything.spis_night_move.append((help_everything.dikt_gamers[count_in_spis], 'убит'))
            # если игрока посещал доктор, его убить нельзя
        else:
            user_name = await bot.fetch_user(id_aut)  # ищем имя пользователя по id
            await user_name.send('Чувак, его посетил доктор. Придется подождать следующей ночи...')

    if aut_role == 'врач':
        # в список ночных действий передаем кортэж с id выздоровевшего и типом действия [(id, "вылечен")]
        if (help_everything.dikt_gamers[count_in_spis], 'убит') not in help_everything.spis_night_move:
            help_everything.spis_night_move.append((help_everything.dikt_gamers[count_in_spis], 'вылечен'))
        else:
            for i in range(len(help_everything.spis_night_move)):
                if help_everything.spis_night_move[i] == (help_everything.dikt_gamers[count_in_spis], 'убит'):
                    help_everything.spis_night_move[i] = (help_everything.dikt_gamers[count_in_spis], 'вылечен')

    if aut_role == 'путана':
        # у путаны немного особенная роль, поэтому пришлось подзаморочиться
        id_chel = help_everything.dikt_gamers[count_in_spis]  # узнаём id игрока над которым совершено действие
        result = cur.execute("SELECT role FROM players WHERE nick_id = ?;", (id_chel,)).fetchall()
        aut_chel = result[0][0]  # запоминаеи роль игрока над которым совершено действие
        if aut_chel == 'мафия':
            # если путана попадает на одного из мафиозий, то действие блокируется у всего клана (кроме дона конечно)
            # в список ночных действий передаем кортэж [('мафия', "отвлечен")]
            help_everything.spis_night_move.append(('мафия', 'отвлечен'))

        # в список ночных действий передаем кортэж с id отвлеченого и типом действия [(id, "отвлечен")]
        help_everything.spis_night_move.append((id_chel, 'отвлечен'))

    # действия шерифа и дона можно не передовать в список ночных действий, они не влияют
    if aut_role == 'шериф':
        user_name = await bot.fetch_user(id_aut)  # ищем имя пользователя по id
        # проверка на мафию
        result = cur.execute("SELECT * FROM players WHERE id = ? AND role = ?;", (count_in_spis, 'мафия')).fetchall()
        if result:
            await user_name.send(f'Ты оказалмя прав, черт возьми! {chel.name} -'
                                 f' член клана мафии! Будь осторожнее')
        else:
            # проверка на дона
            result = cur.execute("SELECT * FROM players WHERE id = ? AND role = ?;",
                                 (count_in_spis, 'дон')).fetchall()
            if result:
                await user_name.send(f'Ты оказалмя прав, черт возьми! {chel.name} -'
                                     f' глава клана мафии, он дон! Будь осторожнее')

            else:
                await user_name.send(f'Увы старина, сегодня ты в пролёте! '
                                     f'{chel.name} - не является частью клана мафии!')

    if aut_role == 'дон':
        user_name = await bot.fetch_user(id_aut)  # ищем имя пользователя по id
        result = cur.execute("SELECT * FROM players WHERE id = ? AND role = ?;",
                             (count_in_spis, 'шериф')).fetchall()
        if result:
            await user_name.send(f'Поздравляю сер! {chel.name} - шериф!')
        else:
            await user_name.send(f'К сожалению {chel.name} не относится к служителям порядка')


def stop_game():  # завершение сессии игры, обнуляем всё
    # вставить обнуление роли Игрок(!)
    # вставить обнуление БД
    help_everything.flag_game_now = 0  # игра закончилась, опускаем флаг
    help_everything.list_gamers = []  # опустошаем список, игроки расходятся
    help_everything.count_id = 0
    cur = DB.cursor()
    cur.execute('DELETE from players').fetchall()  # в конце игры нужно очистить базу
    DB.commit()


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

# те new_game (+) -> give (+) -> start_game (+) -> внутренние функции(distribution + distribution_roles) (+)->
# rule_for_play (+) -> циклы день∞ночь∞проверка на выйгрыш -> объявление результатов -> чистка всех и вся
