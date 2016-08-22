from django.conf.urls import url, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	
	url(r'^e/(?P<id_equipo>[0-9]+)/$', views.equipo_detail, name='equipo_detail'),

	url(r'^r/(?P<id_reto>[0-9]+)/$', views.reto_detail, name='reto_detail'),

	url(r'^n/add/$', views.NotaFormView.as_view(), name='nota_add'),

	url(r'^p/add$', views.UserFormView.as_view(), name='profile_add'),
	url(r'^p/(?P<id_profile>[0-9]+)/$', views.profile_detail, name='profile_detail'),

	url(r'^tienda/$', views.tienda, name='tienda'),
	url(r'^tienda/c/(?P<id_paquete>[0-9]+)/$', views.compra_add, name='compra'),
	
	url('^login/$', auth_views.login, {'template_name': 'user/login.html', 'extra_context': {'next':'/'}}, name="login"),
    url('^logout/$', auth_views.logout, {'next_page': '/'}, name="logout"),
]