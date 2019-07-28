from django.conf.urls import url
from casino import views

app_name = 'casino'

urlpatterns = [
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.login_user, name='login_user'),
    url(r'^deposit/$', views.deposit, name='deposit'),
]
