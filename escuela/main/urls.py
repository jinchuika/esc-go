from django.conf.urls import url
from . import views
from escuela import settings
from django.contrib.auth import views as auth_views
from django.views import static

urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name='index'),

    url(r'^equipo/list/$', views.EquipoListView.as_view(), name='equipo_list'),
    url(r'^equipo/(?P<pk>[0-9]+)/$', views.EquipoDetailView.as_view(), name='equipo_detail'),

    url(r'^alumno/(?P<pk>[0-9]+)/$', views.AlumnoDetailView.as_view(), name='alumno_detail_'),
    url(r'^alumno/(?P<pk>[0-9]+)/mensaje$', views.MensajeCreateView.as_view(), name='mensaje_add_'),
    
    url(r'^reto/list$', views.RetoListView.as_view(), name='reto_list'),
    url(r'^reto/(?P<pk>[0-9]+)/$', views.RetoDetailView.as_view(), name='reto_detail'),

    url(r'^n/add/$', views.NotaFormView.as_view(), name='nota_add'),

    url(r'^p/add$', views.UserFormView.as_view(), name='profile_add'),
    url(r'^p/inbox$', views.PostAlumnoList.as_view(), name='inbox'),
    url(r'^p/mensaje/(?P<pk>[0-9]+)/$', views.PostAlumnoDetail.as_view(), name='mensaje_detail_'),

    url(r'^perfil/(?P<pk>[0-9]+)/$', views.PerfilDetailView.as_view(), name='perfil_detail'),
    url(r'^perfil/(?P<pk>[0-9]+)/edit$', views.PerfilUpdateView.as_view(), name='perfil_update'),

    url(r'^mensaje/(?P<perfil_id>[0-9]+)/$', views.MensajeDetailView.as_view(), name='mensaje_detail'),

    url(r'^store/$', views.StoreView.as_view(), name='store'),
    url(r'^store/compra$', views.CompraCreateView.as_view(), name='compra_create'),

    url(r'^apoyar/(?P<nota_id>[0-9]+)/$', views.ApuestaCreateView.as_view(), name='apuesta_create'),

    url(r'^login/$', auth_views.login, {'template_name': 'user/login.html'}, name="login"),
    url('^logout/$', auth_views.logout, {'next_page': '/'}, name="logout"),

    url(r'^password_change/$', views.password_change, name='password_change'),

    #url(r'^password_reset/$', auth_views.password_reset, {'template_name': 'user/password_reset.html', 'post_reset_redirect': '/'}, name="password_reset"),
    #url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', auth_views.password_reset_confirm, name='password_reset_confirm'),
    #url(r'^resetpassword/passwordsent/$', 'django.contrib.auth.views.password_reset_done', name='password_reset_done'),

    url(r'^media/(?P<path>.*)$', static.serve, {'document_root': settings.MEDIA_ROOT})
]