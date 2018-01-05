from django.contrib import admin
from pffl.models import *

class CredentialsAdmin(admin.ModelAdmin):
    pass

admin.site.register(CredentialsModel, CredentialsAdmin)
admin.site.register(UserProfile)
admin.site.register(Team)
admin.site.register(Conferance)
admin.site.register(Division)
admin.site.register(Rank)
admin.site.register(Schedule)
admin.site.register(TeamInstance)
admin.site.register(Match)