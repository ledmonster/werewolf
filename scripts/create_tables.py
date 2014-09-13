# -*- coding: utf-8 -*-
from flywheel import Engine

from werewolf.domain.user import *
from werewolf.domain.game import *
from werewolf.domain.game.repository import *


engine = Engine()
engine.connect_to_host(host='localhost', port=8000, is_secure=False)

engine.register(User)
engine.register(UserCredential)
engine.register(ClientSession)
engine.register(AccessToken)
engine.register(RefreshToken)
engine.register(VillageModel)
engine.register(ResidentModel)
engine.register(BehaviorModel)
engine.register(EventModel)

engine.create_schema()

repo_village = VillageRepository(engine)

repo_village.add(u'PyConJP 村')
repo_village.add(u'ペンギン村')
