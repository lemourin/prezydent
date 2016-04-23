from django.core.management.base import BaseCommand, CommandError
from results.models import CandidateData, VoteData, VoteResult

import random

class Command(BaseCommand):
    def voivodeship_winner(self, name):
        sum = 0
        for c in name:
            sum += ord(c)
        return sum % 2 == 0

    def handle(self, *args, **options):
        VoteResult.objects.all().delete()

        candidate1 = CandidateData.objects.all()[0]
        candidate2 = CandidateData.objects.all()[1]

        for obj in VoteData.objects.all():
            t = obj.vote_count
            candidate1_count = int(t * (random.randint(20, 80) / 100.0))
            candidate2_count = int(t - 1.05 * candidate1_count)

            if self.voivodeship_winner(obj.town.town_name):
                if candidate1_count < candidate2_count:
                    candidate1_count, candidate2_count = candidate2_count, candidate1_count
            else:
                if candidate1_count > candidate2_count:
                    candidate1_count, candidate2_count = candidate2_count, candidate1_count

            tmp1 = VoteResult(vote_data=obj, candidate=candidate1, vote_count=candidate1_count)
            tmp2 = VoteResult(vote_data=obj, candidate=candidate2, vote_count=candidate2_count)
            try:
                tmp1.clean()
                tmp1.save()
                tmp2.clean()
                tmp2.save()
            except:
                print("failed to save", obj.town.town_name, candidate1_count, candidate2_count, t)
