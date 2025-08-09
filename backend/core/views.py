from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView
from django.contrib import messages
from functools import wraps

from .forms import RegistroUsuarioForm, EditarUsuarioForm
from .models import PerfilUsuario

# 🔐 Decorador para restringir acceso solo a administradores
def solo_admin(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        perfil = getattr(request.user, 'perfilusuario', None)
        if perfil and perfil.role == 'admin':
            return view_func(request, *args, **kwargs)
        messages.error(request, '⛔ No tienes permisos para realizar esta acción.')
        return redirect('menu')
    return _wrapped_view

# 🏠 Página de bienvenida
def bienvenido(request):
    return render(request, 'bienvenido.html')

# 🔑 Login (por usuario o correo)
def login_view(request):
    if request.method == 'POST':
        input_usuario = request.POST.get('username')
        password = request.POST.get('password')

        # Autenticación por correo
        if '@' in input_usuario and '.' in input_usuario:
            try:
                user_obj = User.objects.get(email=input_usuario)
                username = user_obj.username
            except User.DoesNotExist:
                return render(request, 'inicioSesion.html', {'error': 'Correo no registrado'})
        else:
            username = input_usuario

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            perfil = getattr(user, 'perfilusuario', None)
            role = perfil.role if perfil else 'employee'
            request.session['user_role'] = role
            return redirect('menu')

        return render(request, 'inicioSesion.html', {'error': 'Credenciales inválidas'})

    return render(request, 'inicioSesion.html')

# 🆕 Registro de usuario
def nuevo_usuario(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            perfil = getattr(user, 'perfilusuario', None)
            request.session['user_role'] = perfil.role if perfil else 'employee'
            return redirect('login')
    else:
        form = RegistroUsuarioForm()
    return render(request, 'nuevo_usuario.html', {'form': form})

# 📂 Menús principales
@login_required
def menu(request):
    return render(request, 'menu.html')

@login_required
def ajustes(request):
    return render(request, 'ajustes.html')

@login_required
def menu_comida(request):
    return render(request, 'menu_comida.html')

@login_required
def mesas(request):
    return render(request, 'mesas.html')

@login_required
def corte(request):
    return render(request, 'corte.html')

@login_required
def cuentas(request):
    return render(request, 'cuentas.html')

# ⚙️ Módulo Ajustes
@login_required
def editar_menu(request):
    return render(request, 'Ajustes/editar_menu.html')

@login_required
def editar_mesas(request):
    return render(request, 'Ajustes/editar_mesas.html')

@login_required
@solo_admin
def centro_de_usuarios(request):
    rol = request.GET.get('rol')
    usuarios = User.objects.select_related('perfilusuario')
    if rol:
        usuarios = usuarios.filter(perfilusuario__role=rol)
    return render(request, 'Ajustes/centro_de_usuarios.html', {
        'usuarios': usuarios,
        'rol_seleccionado': rol
    })

@login_required
@solo_admin
def agregar_usuario(request):
    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            if not hasattr(user, 'perfilusuario'):
                PerfilUsuario.objects.create(user=user, role='mesero')  # Rol por defecto
            messages.success(request, '✅ Usuario agregado correctamente')
            return redirect('centro_de_usuarios')
    else:
        form = RegistroUsuarioForm()
    return render(request, 'Ajustes/agregar_usuario.html', {'form': form})

@login_required
@solo_admin
def editar_usuario(request, usuario_id):
    usuario = get_object_or_404(User, id=usuario_id)
    form = EditarUsuarioForm(request.POST or None, request.FILES or None, instance=usuario)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, '✅ Datos actualizados correctamente')
        return redirect('centro_de_usuarios')

    return render(request, 'Ajustes/editar_usuario.html', {'form': form})

# 🗑️ Eliminar usuario
@login_required
@solo_admin
def eliminar_usuario(request, usuario_id):
    usuario_a_eliminar = get_object_or_404(User, id=usuario_id)

    if usuario_a_eliminar == request.user:
        messages.error(request, '⛔ No puedes eliminar tu propio usuario.')
        return redirect('centro_de_usuarios')

    perfil = getattr(usuario_a_eliminar, 'perfilusuario', None)
    if perfil and perfil.role == 'admin':
        admins = User.objects.filter(perfilusuario__role='admin')
        if admins.count() <= 1:
            messages.error(request, '⛔ No puedes eliminar al único administrador.')
            return redirect('centro_de_usuarios')

    usuario_a_eliminar.delete()
    messages.success(request, '🗑️ Usuario eliminado correctamente.')
    return redirect('centro_de_usuarios')

# 🚪 Logout con mensaje
class LogoutConMensaje(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "Sesión finalizada correctamente. Gracias por utilizar Cuenta Clara.")
        return super().dispatch(request, *args, **kwargs)