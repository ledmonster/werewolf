# -*- coding: utf-8 -*-
from flywheel import Engine

from werewolf.domain.base import Identity
from werewolf.domain.user.repository import UserRepository


engine = Engine()
engine.connect_to_host(host='localhost', port=8000, is_secure=False)

repo_user = UserRepository(engine)

identities = [
    'd4d8722d-3c15-4eee-9a76-dcc30bcd272f',
    'c7a7f5fa-8113-40b1-9fd7-a4e07ceb89f2',
    'be5ff2bf-f72f-44ee-a792-15e6f24ebf11',
]

for i in xrange(3):
    repo_user.create(
        identity=Identity(identities[i]),
        name="COM{:d}".format(i+1),
        email="ledmonster+com{:d}@gmail.com".format(i+1),
    )
