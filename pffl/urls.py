from django.conf.urls import include, url
from django.contrib import admin
from pffl import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^login$', auth_views.login, {'template_name':'login.html'}, name='login'),
    url(r'^logout$', auth_views.logout_then_login, name='logout'),
    url(r'^register$', views.register, name='register'),
	url(r'^admin/', include(admin.site.urls), name="admin"),
    url(r'^profile$', views.profile, name='profile'),
    url(r'^auth$', views.authorize, name='auth'),
    url(r'^oauth2callback$', views.auth_return),
    url(r'^auth/success$', views.auth_success, name='auth_success'),
    url(r'^auth/fail$', views.auth_fail, name='auth_fail'),
    url(r'^schedules/view/(?P<schedule_id>[^/]+)$', views.view_schedule, name='view_schedule'),
    url(r'^schedules/export/(?P<schedule_id>[^/]+)$', views.export_schedule, name='export_schedule'),
    url(r'^schedules/new$', views.create_schedule, name='create_schedule'),
    url(r'^import$', views.import_sheet, name='import_sheet'),
    url(r'^generate$', views.generate_schedule, name='generate'),
]