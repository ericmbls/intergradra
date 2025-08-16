from django.urls import path
from django.views.generic import TemplateView
from .views import (
    # 🔐 Autenticación
    login_view,
    nuevo_usuario,
    LogoutConMensaje,

    # 📊 Dashboard
    menu,
    menu_comida,
    mesas,
    cuentas_view,
    cerrar_cuenta,
    corte,
    ajustes,

    # 🧾 Pedidos
    procesar_pedido,
    actualizar_pedido,
    crear_orden,

    # ⚙️ Ajustes generales
    editar_menu,
    editar_mesas,
    centro_de_usuarios,

    # 👥 Gestión de usuarios
    agregar_usuario,
    editar_usuario,
    eliminar_usuario,

    # 🍽️ Gestión de platillos
    agregar_platillo,
    editar_platillo,
    eliminar_platillo,
    actualizar_activo,

    # 🪑 Gestión de mesas
    agregar_mesa,
    eliminar_mesa,
)

urlpatterns = [
    # 🌐 Páginas públicas
    path('', TemplateView.as_view(template_name='bienvenido.html'), name='bienvenida'),
    path('acerca/', TemplateView.as_view(template_name='paginas_bienvenido/acerca_de_nosotros.html'), name='acerca_de_nosotros'),
    path('ayuda/', TemplateView.as_view(template_name='paginas_bienvenido/ayuda.html'), name='ayuda'),
    path('politicas/', TemplateView.as_view(template_name='paginas_bienvenido/politicas.html'), name='politicas'),
    path('contacto/', TemplateView.as_view(template_name='paginas_bienvenido/contactanos.html'), name='contacto'),

    # 🔐 Autenticación
    path('login/', login_view, name='login'),
    path('nuevo_usuario/', nuevo_usuario, name='nuevo_usuario'),
    path('logout/', LogoutConMensaje.as_view(next_page='bienvenida'), name='logout'),

    # 📊 Dashboard
    path('menu/', menu, name='menu'),
    path('menu_comida/', menu_comida, name='menu_comida'),
    path('mesas/', mesas, name='mesas'),
    path('cuentas/', cuentas_view, name='cuentas'),
    path('cuentas/cerrar/<int:cuenta_id>/', cerrar_cuenta, name='cerrar_cuenta'),
    path('corte/', corte, name='corte'),
    path('ajustes/', ajustes, name='ajustes'),

    # 🧾 Pedidos
    path('procesar_pedido/', procesar_pedido, name='procesar_pedido'),
    path('ajax/actualizar_pedido/', actualizar_pedido, name='actualizar_pedido'),
    path('crear_orden/', crear_orden, name='crear_orden'),

    # ⚙️ Ajustes generales
    path('ajustes/editar_menu/', editar_menu, name='editar_menu'),
    path('ajustes/editar_mesas/', editar_mesas, name='editar_mesas'),
    path('ajustes/centro_de_usuarios/', centro_de_usuarios, name='centro_de_usuarios'),

    # 👥 Usuarios
    path('ajustes/agregar_usuario/', agregar_usuario, name='agregar_usuario'),
    path('ajustes/editar_usuario/<int:usuario_id>/', editar_usuario, name='editar_usuario'),
    path('ajustes/eliminar_usuario/<int:usuario_id>/', eliminar_usuario, name='eliminar_usuario'),

    # 🍽️ Platillos
    path('ajustes/agregar_platillo/', agregar_platillo, name='agregar_platillo'),
    path('ajustes/editar_platillo/<int:platillo_id>/', editar_platillo, name='editar_platillo'),
    path('ajustes/eliminar_platillo/<int:platillo_id>/', eliminar_platillo, name='eliminar_platillo'),
    path('ajustes/actualizar_activo/<int:id>/', actualizar_activo, name='actualizar_activo'),

    # 🪑 Mesas
    path('ajustes/agregar_mesa/', agregar_mesa, name='agregar_mesa'),
    path('ajustes/eliminar_mesa/<int:numero>/', eliminar_mesa, name='eliminar_mesa'),
]
