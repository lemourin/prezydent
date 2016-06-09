from django.conf.urls import url, include
from rest_framework import routers, serializers, viewsets
from django.http import HttpResponse

from .models import CityData, VoteResult, VoteData, CandidateData
from . import views

class CitySerializer(serializers.ModelSerializer):
    voivodeship = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
     )

    vote_count = serializers.SerializerMethodField()
    candidate1_result = serializers.SerializerMethodField()
    candidate2_result = serializers.SerializerMethodField()

    def get_vote_count(self, f):
        return VoteData.objects.get(town=f).vote_count

    def get_candidate1_result(self, f):
        return VoteResult.objects.get(vote_data__town=f, candidate=1).vote_count

    def get_candidate2_result(self, f):
        return VoteResult.objects.get(vote_data__town=f, candidate=2).vote_count

    class Meta:
        model = CityData
        fields = (
            'town_name',
            'town_type',
            'voivodeship',
            'citizen_count',
            'vote_count',
            'candidate1_result',
            'candidate2_result'
        )

class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateData
        fields = (
            "first_name",
            "second_name",
            "last_name"
        )


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'login_form$', views.login_form, name='login_form'),
    url(r'logout_form$', views.logout_form, name='logout_form'),
    url(r'edit_form$', views.edit_form, name='edit_form'),
    url(r'modify_entry$', views.modify_entry, name='modify_entry'),
    url(r'edit_history$', views.edit_history, name='edit_history'),
    url(r'summary$', views.summary, name='summary'),
    url(r'city/list/(?P<filter_name>([\w+\-]*))/(?P<filter_argument>([\w+\-]*)$)', views.city, name='city'),
    url(r'city/modify/(?P<town_id>(\d+))/(?P<candidate_id>(\d+))/(?P<vote_count>(\d+))$',
        views.modify, name='modify')
]