from django.test import TestCase, RequestFactory, LiveServerTestCase
from django.contrib.auth.models import User
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Create your tests here.

from results.models import CandidateData, CityData, VoteData, VoteResult
from django.core.exceptions import ValidationError

from results.views import index_context
from time import sleep


def initialize_account_data():
    User.objects.create_user(username="admin", password="admin")

def initialize_cadidate_data():
    CandidateData.objects.create(first_name="Marek",
                                 second_name="", last_name="Markowski").clean()
    CandidateData.objects.create(first_name="Jan",
                                 second_name="", last_name="Janowy").clean()


def initialize_city_data():
    CityData.objects.create(town_name="Miasto1", town_type=CityData.TOWN,
                            voivodeship=None, citizen_count=100).clean()
    CityData.objects.create(town_name="Miasto2", town_type=CityData.TOWN,
                            voivodeship=None, citizen_count=10).clean()


def initialize_vote_data():
    VoteData.objects.create(town=CityData.objects.get(town_name="Miasto1"),
                            authorized_citizen_count=50,
                            vote_forms_count=40, vote_count=30).clean()
    VoteData.objects.create(town=CityData.objects.get(town_name="Miasto2"),
                            authorized_citizen_count=10,
                            vote_forms_count=10, vote_count=10).clean()


def initialize_vote_result():
    VoteResult.objects.create(vote_data=VoteData.objects.get(town__town_name="Miasto1"),
                              candidate=CandidateData.objects.get(first_name="Marek"),
                              vote_count=15).clean()
    VoteResult.objects.create(vote_data=VoteData.objects.get(town__town_name="Miasto1"),
                              candidate=CandidateData.objects.get(first_name="Jan"),
                              vote_count=15).clean()


def initialize_database():
    initialize_cadidate_data()
    initialize_city_data()
    initialize_vote_data()
    initialize_vote_result()


class CandidateDataTestCase(TestCase):
    def setUp(self):
        initialize_database()

    def test_add_next_candidate(self):
        with self.assertRaises(ValidationError):
            CandidateData.objects.create(first_name="Lech").clean()

    def test_modify_candidate(self):
        c1 = CandidateData.objects.get(first_name="Marek")
        c1.first_name = "Grzegorz"
        c1.clean()
        c1.save()
        self.assertIsNotNone(CandidateData.objects.get(first_name="Grzegorz"))


class VoteDataTestCase(TestCase):
    def setUp(self):
        initialize_database()

    def test_put_invalid_data(self):
        with self.assertRaises(ValidationError):
            d = VoteData.objects.get(town=CityData.objects.get(town_name="Miasto1"))
            d.authorized_citizen_count = 39
            d.clean()

    def test_more_authorized_citizen_than_citizens(self):
        with self.assertRaises(ValidationError):
            d = VoteData.objects.get(town=CityData.objects.get(town_name="Miasto1"))
            d.authorized_citizen_count = 101
            d.clean()


class VoteResultTestCase(TestCase):
    def setUp(self):
        initialize_database()

    def test_put_invalid_data(self):
        with self.assertRaises(ValidationError):
            vote_data = VoteData.objects.get(town__town_name="Miasto1")
            d = VoteResult.objects.get(vote_data=vote_data,
                                       candidate=CandidateData.objects.get(first_name="Marek"))
            d.vote_count = 14
            try:
                d.clean()
            except:
                raise Exception("Shouldn't throw.")
            d.vote_count = 16
            d.clean()


class ViewTest(TestCase):
    def setUp(self):
        initialize_database()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="admin", password="admin")

    def test_index(self):
        request = self.factory.get("/index")
        request.user = self.user
        context = index_context(request)
        self.assertEqual(context["all_vote_count"], 40)
        self.assertEqual(context["form_count"], 50)
        self.assertEqual(context["citizen_count"], 110)
        self.assertEqual(context["user_name"], "admin")


class SeleniumTestCase(LiveServerTestCase):
    def open(self, url):
        self.wd.get("%s%s" % (self.live_server_url, url))

    def setUp(self):
        self.wd = webdriver.Firefox()

    def tearDown(self):
        self.wd.quit()


class SeleniumTest(SeleniumTestCase):
    def setUp(self):
        SeleniumTestCase.setUp(self)
        initialize_database()
        initialize_account_data()

    def test_workflow(self):
        delay = 1
        timeout = 20

        self.open("")
        assert "Wybory 2005" in self.wd.title

        self.wd.find_element_by_id("username").send_keys("admin")
        self.wd.find_element_by_id("password").send_keys("admin")
        self.wd.find_element_by_id("login_button").click()
        WebDriverWait(self.wd, timeout).until(
            EC.text_to_be_present_in_element((By.ID, "logout_form"), "Zalogowano jako admin"))
        sleep(delay)

        self.wd.find_element_by_id("result_by_town_type_miasto").click()
        WebDriverWait(self.wd, timeout).until(EC.element_to_be_clickable((By.ID, "result_modify_button_1")))

        modify_button = self.wd.find_element_by_id("result_modify_button_1")
        modify_button.click()

        modify_candidate1 = self.wd.find_element_by_id("result_modify_town_candidate1_1")
        modify_candidate1.clear()
        modify_candidate1.send_keys("10")
        sleep(delay)

        modify_button.click()
        sleep(delay)

        WebDriverWait(self.wd, timeout).until(
            EC.element_to_be_clickable((By.ID, "result_modify_confirm_button_1"))
        )
        confirm_button = self.wd.find_element_by_id("result_modify_confirm_button_1")
        confirm_button.click()

        WebDriverWait(self.wd, timeout).until(EC.element_to_be_clickable((By.ID, "result_modify_button_1")))
        sleep(delay)

        self.wd.find_element_by_id("close_button").click()
        sleep(delay)

        self.wd.find_element_by_id("logout_button").click()
        WebDriverWait(self.wd, timeout).until(
            EC.text_to_be_present_in_element((By.ID, "login_form"), "Login")
        )

        sleep(delay)

