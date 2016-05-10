from django.db import models
from django.core.exceptions import ValidationError


# Create your models here.


class VoivodeshipData(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class CityData(models.Model):
    TOWN = "town"
    VILLAGE = "village"
    BOAT = "boat"
    ABROAD = "abroad"

    TOWN_TYPE_CHOICES = (
        (TOWN, "miasto"),
        (VILLAGE, "wieś"),
        (BOAT, "statki"),
        (ABROAD, "zagranica")
    )

    town_name = models.CharField(max_length=200, unique=True)
    town_type = models.CharField(max_length=200, db_index=True, choices=TOWN_TYPE_CHOICES)
    voivodeship = models.ForeignKey(VoivodeshipData, on_delete=models.CASCADE, null=True, blank=True)
    citizen_count = models.PositiveIntegerField(db_index=True)

    class Meta:
        unique_together = ('town_name', 'voivodeship')

    def __str__(self):
        return self.town_name


class VoteData(models.Model):
    town = models.OneToOneField(CityData, db_index=True, on_delete=models.CASCADE)
    authorized_citizen_count = models.PositiveIntegerField()
    vote_forms_count = models.PositiveIntegerField()
    vote_count = models.PositiveIntegerField()

    def clean(self):
        if not (self.town.citizen_count >=
                    self.authorized_citizen_count >=
                    self.vote_forms_count >=
                    self.vote_count):
            raise ValidationError("Invalid vote data.")

    def __str__(self):
        return str(self.town) + ", vote count = " + str(self.vote_count)


class CandidateData(models.Model):
    first_name = models.CharField(max_length=200)
    second_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)

    def clean(self):
        cnt = 0
        for v in CandidateData.objects.all():
            if v != self:
                cnt += 1
        if cnt >= 2:
            raise ValidationError("Too many candidates.")

    def __str__(self):
        return self.first_name + " " + self.second_name + " " + self.last_name


class VoteResult(models.Model):
    vote_data = models.ForeignKey(VoteData, on_delete=models.CASCADE)
    candidate = models.ForeignKey(CandidateData, on_delete=models.CASCADE)
    vote_count = models.PositiveIntegerField()

    class Meta:
        unique_together = ('vote_data', 'candidate')

    def clean(self):
        valid_vote_count = 0
        for v in VoteResult.objects.all().filter(vote_data=self.vote_data):
            if v != self:
                valid_vote_count += v.vote_count
        if not (valid_vote_count + self.vote_count <= self.vote_data.vote_count):
            raise ValidationError("Too many votes for a candidate")

    def __str__(self):
        return self.vote_data.town.town_name + " " + self.candidate.last_name + " " + str(self.vote_count)
