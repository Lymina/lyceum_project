class Mafia:  # сторона мафии
    def __init__(self, players_nick, role, is_alive=True, don=False, is_doctored=False, is_seduced=False, votes=0):
        self.role = role  # запись роли в формате строки неэффективно, но я поняла, что это может понадобиться для раскрытия роли, строка
        self.votes = votes  # нужны для голосования, число
        self.nick = players_nick  # ник игрока, это очевидно, строка
        self.is_alive = is_alive  # статус: жив или мертв, логика
        self.don = don  # "привилегии" мафиозной стороны, дон, логика
        self.is_doctored = is_doctored  # статус: посещал ли его доктор или нет. обнуляется днем, логика
        self.is_seduced = is_seduced  # статус: посещала ли его путана. обнуляется следующей ночью, то есть возможность голосовать отсутствует, логика

    def kill(self, other_player):  # одна из функций мафии, убийство
        if self.is_alive:
            if other_player.is_doctored:
                other_player.is_doctored = False
                other_player.is_alive = True
            else:
                if not self.is_seduced:
                    other_player.is_alive = False

    def vote(self, other_player):  # голосование
        if self.is_alive:
            if not self.is_seduced:
                other_player.votes += 1

    def checking(self, other_player):  # возможность дона, проверка роли
        if self.is_alive:
            if self.don:
                return other_player.role


class Quite:  # сторона мирных
    def __init__(self, players_nick, role, sheriff=False, doctor=False, is_alive=True, is_doctored=False,
                 is_seduced=False, votes=0):  # в принципе, то же самое, но есть новое
        self.sheriff = sheriff  # "привилегии" мирной стороны, шериф, логика 
        self.doctor = doctor  # "привилегии" мирной стороны, доктор, логика
        self.votes = votes
        self.is_seduced = is_seduced
        self.is_doctored = is_doctored
        self.is_alive = is_alive
        self.role = role
        self.players_nick = players_nick

    def vote(self, other_player):
        if self.is_alive:
            if not self.is_seduced and self.is_alive:
                other_player.votes += 1

    def checking(self, other_player):  # возможность шерифа, проверка роли
        if self.is_alive:
            if self.sheriff:
                return other_player.role

    def doctoring(self, other_player):  # возможность доктора, лечение
        if self.is_alive:
            if self.doctor:
                other_player.is_doctored = True


class Other:  # "серая сторона"
    def __init__(self, players_nick, role, prostitute, maniac, is_alive=True, is_doctored=False,
                 is_seduced=False, votes=0):
        self.maniac = maniac  # тип серой стороны, маньяк, логика
        self.prostitute = prostitute  # тип серой стороны, путана
        self.votes = votes
        self.is_seduced = is_seduced
        self.is_doctored = is_doctored
        self.is_alive = is_alive
        self.role = role
        self.players_nick = players_nick

    def vote(self, other_player):
        if self.is_alive:
            if not self.is_seduced and self.is_alive:
                other_player.votes += 1

    def kill(self, other_player):  # возможность маньяка, убийство
        if self.is_alive:
            if self.maniac:
                if other_player.is_doctored:
                    other_player.is_doctored = False
                    other_player.is_alive = True
                else:
                    if not self.is_seduced:
                        other_player.is_alive = False

    def seducing(self, other_player):  # возможность путаны, совращение
        if self.is_alive:
            if self.prostitute:
                if other_player.is_alive:
                    other_player.is_seduced = True


class Game:
    def __init__(self, list_mafia, list_quite, list_other=None):  # в каждом списке есть объекты соответствующих
        # типов, серая сторона добавляется только при достаточном количестве игроков, поэтому None
        if list_other is None:
            list_other = []
        self.mafia = list_mafia
        self.quite = list_quite
        self.other = list_other

    def night(self):
        pass

    def day(self):
        pass

    def victory(self):
        if len(self.mafia) == 0:
            if len(self.other) == 0:
                return 'В городе воцарился мир и порядок! Неорганизованная преступность искоренена! Ура!'
            else:
                return 'В городе возобладала неорганизованная преступность. Да будет хаос!'
        else:
            return 'Власть в городе захвачена мафией!'
