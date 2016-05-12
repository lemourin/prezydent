from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.db.models import Q
from django.template import Context, Template
from django.utils import timezone

from .models import CityData, VoteData, VoteResult, CandidateData, HistoryData
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

import json, re, datetime

infinity = 1000000000

color_shades = [
    ("#ffa500", "#0000ff"),
    ("#ffa500", "#1919ff"),
    ("#ffae19", "#3232ff"),
    ("#ffb732", "#4c4cff"),
    ("#ffc04c", "#6666ff"),
    ("#ffc966", "#7f7fff"),
    ("#ffd27f", "#9999ff"),
    ("#ffdb99", "#b2b2ff"),
    ("#ffe4b2", "#ccccff")
]

population_splits = [
    500,
    1000,
    2000,
    3000,
    5000,
    10000,
    20000,
    50000,
    100000
]


class Tuple:
    vote_candidate1 = 0
    vote_candidate2 = 0
    vote_count = 0
    vote_candidate1_percentage = "0"
    vote_candidate2_percentage = "0"


def get_boats_and_abroad(vote_candidate1, vote_candidate2):
    candidate1 = vote_candidate1.all().filter(Q(vote_data__town__town_type=CityData.BOAT) |
                                              Q(vote_data__town__town_type=CityData.ABROAD))

    candidate2 = vote_candidate2.all().filter(Q(vote_data__town__town_type=CityData.BOAT) |
                                              Q(vote_data__town__town_type=CityData.ABROAD))
    t = Tuple()
    for v in candidate1:
        t.vote_candidate1 += v.vote_count
    for v in candidate2:
        t.vote_candidate2 += v.vote_count
    t.vote_count = t.vote_candidate1 + t.vote_candidate2
    t.vote_candidate1_percentage = "%.2f" % (
        100.0 * t.vote_candidate1 / t.vote_count)
    t.vote_candidate2_percentage = "%.2f" % (
        100.0 * t.vote_candidate2 / t.vote_count)
    return t


def get_results_by_population(vote_candidate1, vote_candidate2):
    results_by_population = []
    results_by_population.append(
        ("statki i zagranica", get_boats_and_abroad(vote_candidate1, vote_candidate2)))
    candidate1 = vote_candidate1.all().filter(Q(vote_data__town__town_type=CityData.TOWN) |
                                              Q(vote_data__town__town_type=CityData.VILLAGE))
    candidate2 = vote_candidate2.all().filter(Q(vote_data__town__town_type=CityData.TOWN) |
                                              Q(vote_data__town__town_type=CityData.VILLAGE))
    for i in range(0, len(population_splits) + 1):
        a = population_splits[i - 1] if i > 0 else 0
        b = population_splits[i] if i < len(population_splits) else infinity

        id = "do " + str(b) if i == 0 else \
            "od " + str(a) if i == len(population_splits) else \
            "od " + str(a) + " do " + str(b)
        t = Tuple()
        for v in candidate1. \
                filter(vote_data__town__citizen_count__gt=a). \
                filter(vote_data__town__citizen_count__lte=b):
            t.vote_candidate1 += v.vote_count

        for v in candidate2. \
                filter(vote_data__town__citizen_count__gt=a). \
                filter(vote_data__town__citizen_count__lte=b):
            t.vote_candidate2 += v.vote_count
        t.vote_count = t.vote_candidate1 + t.vote_candidate2
        if t.vote_count == 0:
            continue
        t.vote_candidate1_percentage = "%.2f" % (
            100.0 * t.vote_candidate1 / t.vote_count)
        t.vote_candidate2_percentage = "%.2f" % (
            100.0 * t.vote_candidate2 / t.vote_count)
        results_by_population.append((id, t))
    return results_by_population


def get_results_by_voivodeship(vote_candidate1, vote_candidate2):
    result_by_voivodeship = {}
    vote_result_candidate1 = 0
    vote_result_candidate2 = 0

    for v in vote_candidate1.select_related("vote_data__town__voivodeship"):
        voivodeship = v.vote_data.town.voivodeship
        if voivodeship is None:
            continue
        if voivodeship not in result_by_voivodeship:
            result_by_voivodeship[voivodeship] = Tuple()
        result_by_voivodeship[voivodeship].vote_candidate1 += v.vote_count
        vote_result_candidate1 += v.vote_count

    for v in vote_candidate2.select_related("vote_data__town__voivodeship"):
        voivodeship = v.vote_data.town.voivodeship
        if voivodeship is None:
            continue
        if voivodeship not in result_by_voivodeship:
            result_by_voivodeship[voivodeship] = Tuple()
        result_by_voivodeship[voivodeship].vote_candidate2 += v.vote_count
        vote_result_candidate2 += v.vote_count

    for key, value in result_by_voivodeship.items():
        value.vote_count = value.vote_candidate1 + value.vote_candidate2
        value.vote_candidate1_percentage = "%.2f" % (
            100.0 * value.vote_candidate1 / value.vote_count)
        value.vote_candidate2_percentage = "%.2f" % (
            100.0 * value.vote_candidate2 / value.vote_count)
    return result_by_voivodeship.items(), vote_result_candidate1, vote_result_candidate2


def get_map_colors(result_by_voivodeship):
    lst = []
    for key, value in result_by_voivodeship:
        lst.append((key.name, value))

    lst.sort(key=lambda item: float(item[1].vote_candidate1_percentage))

    color_map = {}
    candidate1_percentages = []
    candidate2_percentages = []
    candidate1_colors = []
    candidate2_colors = []
    idx1 = len(color_shades) - 1
    idx2 = 0
    for key, value in lst:
        if float(value.vote_candidate1_percentage) >= 50.0:
            color_map[key] = color_shades[idx1][1]
            candidate1_colors.append(color_map[key])
            candidate1_percentages.append(value.vote_candidate1_percentage)
            if idx1 - 1 >= 0:
                idx1 -= 1
        else:
            color_map[key] = color_shades[idx2][0]
            candidate2_colors.append(color_map[key])
            candidate2_percentages.append(value.vote_candidate2_percentage)
            if idx2 + 1 < len(color_shades):
                idx2 += 1
    candidate2_colors.reverse()
    candidate2_percentages.reverse()

    lst = []
    for key, value in color_map.items():
        lst.append((key, value))
    lst.sort(key=lambda i: i[0])
    voivodeship_colors = []
    for i in lst:
        voivodeship_colors.append(i[1])
    return voivodeship_colors, candidate1_percentages, \
        candidate2_percentages, candidate1_colors, candidate2_colors


def get_results_by_town_type(vote_candidate1, vote_candidate2):
    results_by_town_type = {}
    for t in CityData.TOWN_TYPE_CHOICES:
        r = Tuple()
        for v in vote_candidate1.filter(vote_data__town__town_type=t[0]):
            r.vote_candidate1 += v.vote_count
        for v in vote_candidate2.filter(vote_data__town__town_type=t[0]):
            r.vote_candidate2 += v.vote_count
        r.vote_count = r.vote_candidate1 + r.vote_candidate2
        if r.vote_count == 0:
            continue
        r.vote_candidate1_percentage = "%.2f" % (
            100.0 * r.vote_candidate1 / r.vote_count)
        r.vote_candidate2_percentage = "%.2f" % (
            100.0 * r.vote_candidate2 / r.vote_count)

        results_by_town_type[t[1]] = r
    return results_by_town_type.items()


def index(request):
    candidate1 = CandidateData.objects.all()[0]
    candidate2 = CandidateData.objects.all()[1]
    vote_candidate1 = VoteResult.objects.all().filter(candidate=candidate1)
    vote_candidate2 = VoteResult.objects.all().filter(candidate=candidate2)

    result_by_voivodeship, \
        vote_result_candidate1, \
        vote_result_candidate2 = get_results_by_voivodeship(vote_candidate1, vote_candidate2)
    vote_count = vote_result_candidate1 + vote_result_candidate2

    voivodeship_colors, \
        candidate1_percentages, \
        candidate2_percentages, \
        candidate1_colors, \
        candidate2_colors =  get_map_colors(result_by_voivodeship)

    results_by_town_type = get_results_by_town_type(
        vote_candidate1, vote_candidate2)

    all_vote_count = 0
    form_count = 0
    authorized_citizen_count = 0
    for v in VoteData.objects.all():
        all_vote_count += v.vote_count
        form_count += v.vote_forms_count
        authorized_citizen_count += v.authorized_citizen_count

    citizen_count = 0
    for v in CityData.objects.all():
        citizen_count += v.citizen_count

    area = 312685
    population_density = "%.0f" % (citizen_count / area)

    context = {
        "user_authenticated": request.user.is_authenticated(),
        "user_name": request.user.username,
        "candidate1": candidate1,
        "candidate2": candidate2,
        "result_by_voivodeship": result_by_voivodeship,
        "vote_count": vote_count,
        "result_candidate1": vote_result_candidate1,
        "result_candidate2": vote_result_candidate2,
        "result_candidate1_percentage": "%.2f" % (100.0 * vote_result_candidate1 / vote_count),
        "result_candidate2_percentage": "%.2f" % (100.0 * vote_result_candidate2 / vote_count),
        "colors": voivodeship_colors,
        "candidate1_percentages": candidate1_percentages,
        "candidate2_percentages": candidate2_percentages,
        "candidate1_colors": candidate1_colors,
        "candidate2_colors": candidate2_colors,
        "all_vote_count": all_vote_count,
        "form_count": form_count,
        "authorized_citizen_count": authorized_citizen_count,
        "citizen_count": citizen_count,
        "area": area,
        "population_density": population_density,
        "results_by_town_type": results_by_town_type,
        "results_by_population": get_results_by_population(vote_candidate1, vote_candidate2)
    }

    return HttpResponse(render(request, "results/index.html", context))


def login_form(request):
    username = request.POST["username"]
    password = request.POST["password"]

    user = authenticate(username=username, password=password)

    response = {}
    if user is not None:
        if not user.is_active:
            response["error"] = "User inactive."
        else:
            response["ok"] = "Logged in as " + username + "."
            login(request, user)
    else:
        response["error"] = "Authentication failed."

    return HttpResponse(json.dumps(response),
                        content_type="application/json")

def logout_form(request):
    logout(request)
    return HttpResponse("")


def modify_entry(request):
    response = {}
    town_id = request.POST["town_id"]
    candidate1 = CandidateData.objects.all()[0]
    candidate2 = CandidateData.objects.all()[1]

    vote_result_candidate1 = VoteResult.objects.get(Q(vote_data__town__id=town_id) &
                                                    Q(candidate=candidate1))
    vote_result_candidate2 = VoteResult.objects.get(Q(vote_data__town__id=town_id) &
                                                    Q(candidate=candidate2))

    try:
        candidate1_result = int(request.POST["candidate1"])
        candidate2_result = int(request.POST["candidate2"])
        vote_result_candidate1.vote_count = candidate1_result
        vote_result_candidate2.vote_count = candidate2_result

        vote_result_candidate1.clean()
        vote_result_candidate2.clean()
        vote_result_candidate1.save()
        vote_result_candidate2.save()

        account = request.user
        m1 = None
        try:
            m1 = HistoryData.objects.get(vote_result=vote_result_candidate1)
        except:
            m1 = HistoryData(vote_result=vote_result_candidate1)
        m2 = None
        try:
            m2 = HistoryData.objects.get(vote_result=vote_result_candidate2)
        except:
            m2 = HistoryData(vote_result=vote_result_candidate2)

        m1.author = m2.author = account
        m1.date = m2.date = timezone.now()
        m1.clean()
        m2.clean()
        m1.save()
        m2.save()
    except Exception as err:
        response["error"] = "Niepoprawne dane: " + str(err)

    return HttpResponse(json.dumps(response), content_type="application/json")


def edit_history(request):
    town_id = request.POST["town_id"]
    response = {}
    author = "admin"
    date = datetime.datetime.min
    for v in HistoryData.objects.filter(vote_result__vote_data__town__id=town_id):
        date = v.date
        author = v.author.username

    response["last_edit_author"] = author
    response["last_edit_time"] = str(date)

    return HttpResponse(json.dumps(response), content_type="application/json")


def edit_form(request):
    filter_request = str(request.POST["filter"])
    candidate1 = CandidateData.objects.all()[0]
    candidate2 = CandidateData.objects.all()[1]
    context = {}
    response = {}

    context["candidate1"] = candidate1.last_name
    context["candidate2"] = candidate2.last_name
    context["user_authenticated"] = request.user.is_authenticated()

    if filter_request.startswith("result_by_voivodeship"):
        voivodeship = str(filter_request.replace("result_by_voivodeship_", ""))
        context["edit_data"] = voivodeship

        data = {}
        for v in VoteResult.objects.select_related("vote_data__town__voivodeship__name",
                                                   "vote_data__town__town_name",
                                                   "vote_data__town",
                                                   "candidate__id").\
                filter(vote_data__town__voivodeship__name=voivodeship):
            if v.vote_data.town not in data:
                data[v.vote_data.town] = {}
            data[v.vote_data.town]["candidate" + str(v.candidate.id)] = v.vote_count

        lst = []
        for key, value in data.items():
            lst.append({
                "id" : key.id,
                "town" : key.town_name,
                "candidate1": value["candidate1"],
                "candidate2": value["candidate2"]})
        lst.sort(key=lambda item: item["town"])
        context["data"] = lst
    elif filter_request.startswith("result_by_town_type"):
        town_type_str = filter_request.replace("result_by_town_type_", "")
        context["edit_data"] = "typ gminy " + town_type_str
        town_type = ""
        for type in CityData.TOWN_TYPE_CHOICES:
            if type[1] == town_type_str:
                town_type = type[0]
        data = {}
        for v in VoteResult.objects.select_related("vote_data__town__town_type",
                                                   "vote_data__town__town_name",
                                                   "vote_data__town",
                                                   "candidate__id").\
                filter(vote_data__town__town_type=town_type):
            if v.vote_data.town not in data:
                data[v.vote_data.town] = {}
            data[v.vote_data.town]["candidate" + str(v.candidate.id)] = v.vote_count

        lst = []
        for key, value in data.items():
            lst.append({
                "id": key.id,
                "town": key.town_name,
                "candidate1": value["candidate1"],
                "candidate2": value["candidate2"]})
        lst.sort(key=lambda item: item["town"])
        context["data"] = lst
    elif filter_request.startswith("result_by_population_statki i zagranica"):
        data = {}
        context["edit_data"] = "statki i zagranica"
        for v in VoteResult.objects.select_related("vote_data__town__town_type",
                                                   "vote_data__town__town_name",
                                                   "vote_data__town",
                                                   "candidate__id"). \
                filter(Q(vote_data__town__town_type=CityData.BOAT) | Q(vote_data__town__town_type=CityData.ABROAD)):
            if v.vote_data.town not in data:
                data[v.vote_data.town] = {}
            data[v.vote_data.town]["candidate" + str(v.candidate.id)] = v.vote_count
        lst = []
        for key, value in data.items():
            lst.append({
                "id": key.id,
                "town": key.town_name,
                "candidate1": value["candidate1"],
                "candidate2": value["candidate2"]})
        lst.sort(key=lambda item: item["town"])
        context["data"] = lst
    elif filter_request.startswith("result_by_population"):
        population_str = filter_request.replace("result_by_population_", "")
        context["edit_data"] = "populacja " + population_str

        a = 0
        b = infinity
        split_data = re.split("\W+", population_str)
        for i in range(len(split_data)):
            if split_data[i] == "od":
                a = int(split_data[i + 1])
            elif split_data[i] == "do":
                b = int(split_data[i + 1])
        data = {}
        for v in VoteResult.objects.select_related("vote_data__town__citizen_count",
                                                   "vote_data__town__town_type",
                                                   "vote_data__town__town_name",
                                                   "vote_data__town",
                                                   "candidate__id").\
                filter(vote_data__town__citizen_count__gte=a).\
                filter(vote_data__town__citizen_count__lt=b).\
                filter(Q(vote_data__town__town_type=CityData.TOWN) | Q(vote_data__town__town_type=CityData.VILLAGE)):
            if v.vote_data.town not in data:
                data[v.vote_data.town] = {}
            data[v.vote_data.town]["candidate" + str(v.candidate.id)] = v.vote_count
        lst = []
        for key, value in data.items():
            lst.append({
                "id": key.id,
                "town": key.town_name,
                "candidate1": value["candidate1"],
                "candidate2": value["candidate2"]})
        lst.sort(key=lambda item: item["town"])
        context["data"] = lst

    response["page"] = Template(open("results/templates/results/edit_form.html").read()).\
        render(Context(context))
    return HttpResponse(json.dumps(response), content_type="application/json")