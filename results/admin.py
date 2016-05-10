from django.contrib import admin

# Register your models here.

from results.models import CityData, VoivodeshipData, VoteData, CandidateData, VoteResult, AccountData

class CityDataAdmin(admin.ModelAdmin):
    search_fields = [
        "town_name"
    ]

class VoteDataAdmin(admin.ModelAdmin):
    search_fields = [
        "town__town_name"
    ]

class VoteResultAdmin(admin.ModelAdmin):
    search_fields = [
        "vote_data__town__town_name"
    ]

admin.site.register(CityData, CityDataAdmin)
admin.site.register(VoivodeshipData)
admin.site.register(VoteData, VoteDataAdmin)
admin.site.register(CandidateData)
admin.site.register(VoteResult, VoteResultAdmin)
admin.site.register(AccountData)
