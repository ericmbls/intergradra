from django.urls import path
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView
from . import views

# Si LogoutConMensaje está definido en views.py
from .views import LogoutConMensaje

urlpatterns = [

    # 🧭 Páginas informativas
    path('', TemplateView.as_view(template_name='bienvenido.html'), name='bienvenida'),
    path('acerca/', TemplateView.as_view(template_name='paginas_bienvenido/acerca_de_nosotros.html'), name='acerca_de_nosotros'),
    path('ayuda/', TemplateView.as_view(template_name='paginas_bienvenido/ayuda.html'), name='ayuda'),
    path('politicas/', TemplateView.as_view(template_name='paginas_bienvenido/politicas.html'), name='politicas'),
    path('contacto/', TemplateView.as_view(template_name='paginas_bienvenido/contactanos.html'), name='contacto'),

    # 🔐 Autenticación
    path('login/', views.login_view, name='login'),
    path('nuevo_usuario/', views.nuevo_usuario, name='nuevo_usuario'),
    path('logout/', LogoutConMensaje.as_view(next_page='bienvenida'), name='logout'),

    # 📊 Dashboard principal
    path('menu/', views.menu, name='menu'),
    path('menu_comida/', views.menu_comida, name='menu_comida'),
    path('mesas/', views.mesas, name='mesas'),
    path('cuentas/', views.cuentas, name='cuentas'),
    path('corte/', views.corte, name='corte'),
    path('ajustes/', views.ajustes, name='ajustes'),

    # ⚙️ Ajustes
    path('ajustes/editar_menu/', views.editar_menu, name='editar_menu'),
    path('ajustes/editar_mesas/', views.editar_mesas, name='editar_mesas'),
    path('ajustes/centro_de_usuarios/', views.centro_de_usuarios, name='centro_de_usuarios'),
    path('ajustes/agregar_usuario/', views.agregar_usuario, name='agregar_usuario'),
    path('ajustes/editar_usuario/<int:usuario_id>/', views.editar_usuario, name='editar_usuario'),
    path('ajustes/eliminar_usuario/<int:usuario_id>/', views.eliminar_usuario, name='eliminar_usuario'),
]