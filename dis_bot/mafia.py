class Mafia:
    def __init__(self, players_nick, role, is_alive=True, don=False, is_doctored=False, is_seduced=False, votes=0):
        self.role = role
        self.votes = votes
        self.nick = players_nick
        self.is_alive = is_alive
        self.don = don
        self.is_doctored = is_doctored
        self.is_seduced = is_seduced

    def kill(self, other_player):
        if self.is_alive:
            if other_player.is_doctored:
                other_player.is_doctored = False
                other_player.is_alive = True
            else:
                if not self.is_seduced:
                    other_player.is_alive = False

    def vote(self, other_player):
        if self.is_alive:
            if not self.is_seduced and self.is_alive:
                other_player.votes += 1

    def checking(self, other_player):
        if self.is_alive:
            if self.don:
                return other_player.role


class Quite:
    def __init__(self, players_nick, role, sheriff=False, doctor=False, is_alive=True, is_doctored=False,
                 is_seduced=False, votes=0):
        self.sheriff = sheriff
        self.doctor = doctor
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

    def checking(self, other_player):
        if self.is_alive:
            if self.sheriff:
                return other_player.role

    def doctoring(self, other_player):
        if self.is_alive:
            if self.doctor:
                other_player.is_doctored = True


class Other:
    def __init__(self, players_nick, role, prostitute, maniac, is_alive=True, is_doctored=False,
                 is_seduced=False, votes=0):
        self.maniac = maniac
        self.prostitute = prostitute
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

    def kill(self, other_player):
        if self.is_alive:
            if self.maniac:
                if other_player.is_doctored:
                    other_player.is_doctored = False
                    other_player.is_alive = True
                else:
                    if not self.is_seduced:
                        other_player.is_alive = False

    def seducing(self, other_player):
        if self.is_alive:
            if self.prostitute:
                if other_player.is_alive:
                    other_player.is_seduced = True
