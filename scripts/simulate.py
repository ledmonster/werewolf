# -*- coding: utf-8 -*-
from pprint import pprint

from flywheel import Engine
from pyramid.paster import bootstrap

from werewolf.app.resource import RootResource
from werewolf.domain.base import Identity
from werewolf.domain.user.models import *
from werewolf.domain.user.repository import *
from werewolf.domain.game.models import *
from werewolf.domain.game.repository import *
from werewolf.domain.game.exception import GameException, GameNotFinished

env = bootstrap('development.ini')

context = RootResource(None)
engine = Engine()
engine.connect_to_host(host='localhost', port=8000, is_secure=False)

# repo_user = UserRepository(engine)
# a = repo_user.get_by_name('COM1')

game = GameService(context, '4db80ce9c0b445728a39d1d47f2cb742')

try:
    game.start()
except GameException as e:
    print e.message

targets = game.execute_night()

pprint(targets)

for k, t in targets.iteritems():
    if t is not None:
        pprint(k)
        if k == BehaviorType.EXECUTION.value:
            print u"{} が吊られました".format(t.user.name)
        elif k == BehaviorType.ATTACK.value:
            print u"{} が襲撃されました".format(t.user.name)
        elif k == BehaviorType.HUNT.value:
            print u"{} が道連れになりました".format(t.user.name)
        elif k == BehaviorType.FORTUNE.value:
            print u"{} が占われました".format(t.user.name)


if game.satisfy_game_end():
    winner = game.get_winner()
    pprint(winner)
    residents = game.village.get_residents()
    village = game.end()
else:
    village = game.execute_morning()
