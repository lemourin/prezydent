from django.core.management.base import BaseCommand, CommandError
from results.models import CandidateData, VoteData, VoteResult, CityData

class Command(BaseCommand):
    def handle(self, *args, **options):
        for obj in CityData.objects.all():
            t = obj.citizen_count
            tmp = VoteData(town=obj, authorized_citizen_count=int(t * 0.8),
                           vote_forms_count=int(t * 0.7),
                           vote_count=int(t * 0.5))
            try:
                tmp.clean()
                tmp.save()
            except:
                print("failed to save", obj)