from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'login_form$', views.login_form, name='login_form'),
    url(r'edit_form$', views.edit_form, name='edit_form'),
    url(r'modify_entry$', views.modify_entry, name='modify_entry'),
    url(r'edit_history$', views.edit_history, name='edit_history')
]