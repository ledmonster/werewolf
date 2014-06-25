from werewolf.domain.user.models import *
from werewolf.domain.game.models import *
from django.contrib import admin

admin.site.register(User)
admin.site.register(UserCredential)
admin.site.register(VillageModel)
admin.site.register(ResidentModel)
admin.site.register(BehaviorModel)
admin.site.register(EventModel)
admin.site.register(ClientSession)
admin.site.register(AccessToken)
admin.site.register(RefreshToken)
