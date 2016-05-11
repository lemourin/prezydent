from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'login_form$', views.login_form, name='login_form'),
    url(r'edit_form$', views.edit_form, name='edit_form'),
]