from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.db.models import Q

from .models import CityData, VoteData, VoteResult, CandidateData

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
    t.vote_candidate1_percentage = "%.2f" % (100.0 * t.vote_candidate1 / t.vote_count)
    t.vote_candidate2_percentage = "%.2f" % (100.0 * t.vote_candidate2 / t.vote_count)
    return t

def get_results_by_population(vote_candidate1, vote_candidate2):
    results_by_population = []
    results_by_population.append(("statki i zagranica", get_boats_and_abroad(vote_candidate1, vote_candidate2)))
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
        t.vote_candidate1_percentage = "%.2f" % (100.0 * t.vote_candidate1 / t.vote_count)
        t.vote_candidate2_percentage = "%.2f" % (100.0 * t.vote_candidate2 / t.vote_count)
        results_by_population.append((id, t))
    return results_by_population

def get_results_by_voivodeship(vote_candidate1, vote_candidate2):
    result_by_voivodeship = {}
    vote_result_candidate1 = 0
    vote_result_candidate2 = 0
    for v in vote_candidate1:
        voivodeship = v.vote_data.town.voivodeship
        if voivodeship is None:
            continue
        if voivodeship not in result_by_voivodeship:
            result_by_voivodeship[voivodeship] = Tuple()
        result_by_voivodeship[voivodeship].vote_candidate1 += v.vote_count
        vote_result_candidate1 += v.vote_count

    for v in vote_candidate2:
        voivodeship = v.vote_data.town.voivodeship
        if voivodeship is None:
            continue
        if voivodeship not in result_by_voivodeship:
            result_by_voivodeship[voivodeship] = Tuple()
        result_by_voivodeship[voivodeship].vote_candidate2 += v.vote_count
        vote_result_candidate2 += v.vote_count

    for key, value in result_by_voivodeship.items():
        value.vote_count = value.vote_candidate1 + value.vote_candidate2
        value.vote_candidate1_percentage = "%.2f" % (100.0 * value.vote_candidate1 / value.vote_count)
        value.vote_candidate2_percentage = "%.2f" % (100.0 * value.vote_candidate2 / value.vote_count)
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
        r.vote_candidate1_percentage = "%.2f" % (100.0 * r.vote_candidate1 / r.vote_count)
        r.vote_candidate2_percentage = "%.2f" % (100.0 * r.vote_candidate2 / r.vote_count)

        results_by_town_type[t[1]] = r
    return results_by_town_type.items()

def index(request):
    candidate1 = CandidateData.objects.all()[0]
    candidate2 = CandidateData.objects.all()[1]
    vote_candidate1 = VoteResult.objects.all().filter(candidate=candidate1)
    vote_candidate2 = VoteResult.objects.all().filter(candidate=candidate2)
    vote_data = VoteData.objects.all()
    city_data = CityData.objects.all()

    result_by_voivodeship, \
    vote_result_candidate1,\
    vote_result_candidate2 = get_results_by_voivodeship(vote_candidate1, vote_candidate2)
    vote_count = vote_result_candidate1 + vote_result_candidate2

    voivodeship_colors, \
    candidate1_percentages, \
    candidate2_percentages, \
    candidate1_colors, \
    candidate2_colors = get_map_colors(result_by_voivodeship)

    results_by_town_type = get_results_by_town_type(vote_candidate1, vote_candidate2)

    all_vote_count = 0
    form_count = 0
    authorized_citizen_count = 0
    for v in vote_data:
        all_vote_count += v.vote_count
        form_count += v.vote_forms_count
        authorized_citizen_count += v.authorized_citizen_count

    citizen_count = 0
    for v in city_data:
        citizen_count += v.citizen_count

    area = 312685
    population_density = "%.0f" % (citizen_count / area)

    context = {
        "candidate1" : candidate1,
        "candidate2" : candidate2,
        "result_by_voivodeship" : result_by_voivodeship,
        "vote_count" : vote_count,
        "result_candidate1" : vote_result_candidate1,
        "result_candidate2" : vote_result_candidate2,
        "result_candidate1_percentage" : "%.2f" % (100.0 * vote_result_candidate1 / vote_count),
        "result_candidate2_percentage" : "%.2f" % (100.0 * vote_result_candidate2 / vote_count),
        "colors" : voivodeship_colors,
        "candidate1_percentages" : candidate1_percentages,
        "candidate2_percentages" : candidate2_percentages,
        "candidate1_colors" : candidate1_colors,
        "candidate2_colors" : candidate2_colors,
        "all_vote_count" : all_vote_count,
        "form_count" : form_count,
        "authorized_citizen_count" : authorized_citizen_count,
        "citizen_count" : citizen_count,
        "area" : area,
        "population_density" : population_density,
        "results_by_town_type" : results_by_town_type,
        "results_by_population" : get_results_by_population(vote_candidate1, vote_candidate2)
    }

    return HttpResponse(render(request, "results/index.html", context))