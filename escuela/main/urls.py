from django.conf.urls import url, include
from . import views
from escuela import settings
from django.contrib.auth import views as auth_views
from django.views import(
	static
	)

urlpatterns = [
	url(r'^$', views.index, name='index'),
	
	url(r'^e/(?P<id_equipo>[0-9]+)/$', views.equipo_detail, name='equipo_detail'),
	url(r'^e/(?P<id_equipo>[0-9]+)/blog/$', views.equipo_blog, name='equipo_blog'),
	
	url(r'^a/(?P<id_alumno>[0-9]+)/$', views.alumno_detail, name='alumno_detail'),
	url(r'^a/(?P<id_alumno>[0-9]+)/post$', views.post_add, name='alumno_post_add'),
	url(r'^a/(?P<id_alumno>[0-9]+)/mensaje/$', views.mensaje_add, name='mensaje_add'),

	url(r'^r/(?P<id_reto>[0-9]+)/$', views.reto_detail, name='reto_detail'),

	url(r'^n/add/$', views.NotaFormView.as_view(), name='nota_add'),

	url(r'^p/add$', views.UserFormView.as_view(), name='profile_add'),
	url(r'^p/(?P<id_profile>[0-9]+)/$', views.profile_detail, name='profile_detail'),
	url(r'^p/edit$', views.profile_edit, name='profile_edit'),

	url(r'^tienda/$', views.tienda, name='tienda'),
	url(r'^tienda/comprar/$', views.crear_compra, name='crear_compra'),
	
	url('^login/$', auth_views.login, {'template_name': 'user/login.html', 'extra_context': {'next':'/'}}, name="login"),
    url('^logout/$', auth_views.logout, {'next_page': '/'}, name="logout"),

    url(r'^password_change/$', views.password_change, name='password_change'),

	#url(r'^password_reset/$', auth_views.password_reset, {'template_name': 'user/password_reset.html', 'post_reset_redirect': '/'}, name="password_reset"),
	#url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', auth_views.password_reset_confirm, name='password_reset_confirm'),
	#url(r'^resetpassword/passwordsent/$', 'django.contrib.auth.views.password_reset_done', name='password_reset_done'),

    url(r'^media/(?P<path>.*)$', static.serve, {'document_root': settings.MEDIA_ROOT})
]