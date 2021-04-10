import discord
from discord import utils

import dis_bot.config as config


def color_str(text):  # делает текст жирным
    return f'**{text}**'


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_member_join(self, member):
        await member.create_dm()
        await member.dm_channel.send(
            f'''Приветик! Я мафия-бот, проект двух лучших женщин в мире: Насти Сарпинской и Гузь Лизы :) 
\nЧтобы обратиться ко мне по коаманде достаточно написать ">твоя команда" (без кавычек) \nВот какие команды я могу 
выполнить: \n{color_str(">new_game")} - Начало сбора игроков для новой игры в мафию, открытие комнаты ожидания'''
        )

    async def on_raw_reaction_add(self, payload):
        if payload.message_id == config.POST_ID:
            channel = self.get_channel(payload.channel_id)  # получаем объект канала
            message = await channel.fetch_message(payload.message_id)  # получаем объект сообщения
            member = utils.get(message.guild.members,
                               id=payload.user_id)  # получаем объект пользователя который поставил реакцию
            emoji = str(payload.emoji)  # эмоджик который выбрал юзер
            role = utils.get(message.guild.roles, id=config.ROLES[emoji])  # объект выбранной роли (если есть)
            try:
                if len([i for i in member.roles if i.id not in config.EXCROLES]) <= config.MAX_ROLES_PER_USER:
                    await member.add_roles(role)
                    print('[SUCCESS] User {0.display_name} has been granted with role {1.name}'.format(member, role))
                else:
                    await message.remove_reaction(payload.emoji, member)
                    print('[ERROR] Too many roles for user {0.display_name}'.format(member))

            except KeyError:
                print(f'[ERROR] KeyError, no role found for {emoji}')
            except Exception as e:
                print(repr(e))

    async def on_raw_reaction_remove(self, payload):
        channel = self.get_channel(payload.channel_id)  # получаем объект канала
        message = await channel.fetch_message(payload.message_id)  # получаем объект сообщения
        member = utils.get(message.guild.members,
                           id=payload.user_id)  # получаем объект пользователя который поставил реакцию
        emoji = str(payload.emoji)  # эмоджик который выбрал юзер
        role = utils.get(message.guild.roles, id=config.ROLES[emoji])  # объект выбранной роли (если есть)
        try:
            await member.remove_roles(role)
            print('[SUCCESS] Role {1.name} has been remove for user {0.display_name}'.format(member, role))

        except KeyError:
            print('[ERROR] KeyError, no role found for ' + emoji)
        except Exception as e:
            print(repr(e))


# RUN
client = MyClient()
client.run(config.TOKEN)
