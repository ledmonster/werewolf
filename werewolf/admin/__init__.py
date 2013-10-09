from werewolf.models import *
from django.contrib import admin

admin.site.register(User)
admin.site.register(UserCredential)
admin.site.register(Village)
admin.site.register(Resident)
admin.site.register(Event)
admin.site.register(ClientSession)
admin.site.register(AccessToken)
admin.site.register(RefreshToken)
