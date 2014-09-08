# -*- coding: utf-8 -*-
from flywheel import Engine

from werewolf.domain.user.models import *
from werewolf.domain.game.models import *


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
