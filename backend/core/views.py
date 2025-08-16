from functools import wraps
import json
from decimal import Decimal, InvalidOperation

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseBadRequest
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView

from .models import Platillo, PerfilUsuario, Mesa, Cuenta, Orden
from .forms import RegistroUsuarioForm, EditarUsuarioForm
import logging

logger = logging.getLogger(__name__)

# 🔐 Decorador para restringir acceso solo a administradores
def solo_admin(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        perfil = getattr(request.user, 'perfilusuario', None)
        if request.user.is_authenticated and perfil and perfil.role == 'admin':
            return view_func(request, *args, **kwargs)
        messages.error(request, '⛔ No tienes permisos para realizar esta acción.')
        return redirect('menu')
    return _wrapped_view

# 🌐 Página de bienvenida
def bienvenido(request):
    return render(request, 'bienvenido.html')

# 🔑 Login
def login_view(request):
    if request.method == 'POST':
        input_usuario = request.POST.get('username')
        password = request.POST.get('password')

        if '@' in input_usuario:
            user_obj = User.objects.filter(email=input_usuario).first()
            if not user_obj:
                return render(request, 'inicioSesion.html', {'error': 'Correo no registrado'})
            username = user_obj.username
        else:
            username = input_usuario

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            perfil = getattr(user, 'perfilusuario', None)
            request.session['user_role'] = perfil.role if perfil else 'employee'
            return redirect('menu')

        return render(request, 'inicioSesion.html', {'error': 'Credenciales inválidas'})

    return render(request, 'inicioSesion.html')

# 🆕 Registro de usuario
def nuevo_usuario(request):
    form = RegistroUsuarioForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        perfil = getattr(user, 'perfilusuario', None)
        request.session['user_role'] = perfil.role if perfil else 'employee'
        return redirect('login')
    return render(request, 'nuevo_usuario.html', {'form': form})

# 🚪 Logout con mensaje
class LogoutConMensaje(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "Sesión finalizada correctamente. Gracias por utilizar Cuenta Clara.")
        return super().dispatch(request, *args, **kwargs)

# 📊 Dashboard principal
@login_required
def menu(request):
    return render(request, 'menu.html')

@login_required
def ajustes(request):
    return render(request, 'ajustes.html')

@login_required
def menu_comida(request):
    platillos = Platillo.objects.filter(activo=True)
    return render(request, 'menu_comida.html', {'platillos': platillos})

@login_required
def mesas(request):
    mesas = Mesa.objects.order_by('numero')
    # Ejemplo temporal
    ordenes = [
        {
            'id': 1,
            'nombre_mesa': 'Mesa 3',
            'items': ['2x Hamburguesa Clásica', '1x Refresco Grande', '1x Ensalada César'],
            'para_llevar': False
        },
        {
            'id': 2,
            'nombre_mesa': 'Para Llevar',
            'items': ['3x Tacos al Pastor', '2x Agua Mineral', '1x Flan Napolitano'],
            'para_llevar': True
        }
    ]
    return render(request, 'mesas.html', {'mesas': mesas, 'ordenes': ordenes})

@login_required
def corte(request):
    return render(request, 'corte.html')

@login_required
def cuentas_view(request):
    mesa_filtro = request.GET.get('mesa')
    fecha_filtro = request.GET.get('fecha')

    cuentas = Cuenta.objects.prefetch_related(
        'ordenes__platillos',
        'mesa'
    ).order_by('-creada')

    if mesa_filtro:
        cuentas = cuentas.filter(mesa__numero=mesa_filtro)

    if fecha_filtro:
        cuentas = cuentas.filter(creada__date=fecha_filtro)

    return render(request, 'cuentas.html', {'cuentas': cuentas})

@login_required
def cerrar_cuenta(request, cuenta_id):
    cuenta = get_object_or_404(Cuenta, id=cuenta_id, activa=True)

    if request.method == 'POST':
        cuenta.activa = False
        cuenta.calcular_total()
        cuenta.save()
        messages.success(request, f'Cuenta de mesa {cuenta.mesa.numero} cerrada correctamente.')
        return redirect('cuentas')

    return render(request, 'cuentas.html', {'cuentas': Cuenta.objects.filter(activa=True)})

# 👥 Gestión de usuarios
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
    form = RegistroUsuarioForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        if not hasattr(user, 'perfilusuario'):
            PerfilUsuario.objects.create(user=user, role='employee')
        messages.success(request, '✅ Usuario agregado correctamente')
        return redirect('centro_de_usuarios')
    return render(request, 'Ajustes/agregar_usuario.html', {'form': form})

@login_required
@solo_admin
def editar_usuario(request, usuario_id):
    usuario = get_object_or_404(User, id=usuario_id)

    if not request.user.is_superuser and request.user != usuario:
        messages.error(request, '❌ No tienes permiso para editar este usuario.')
        return redirect('centro_de_usuarios')

    if request.method == 'POST':
        form = EditarUsuarioForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            form.save()
            if request.user == usuario:
                update_session_auth_hash(request, usuario)
            messages.success(request, '✅ Datos actualizados correctamente.')
            return redirect('centro_de_usuarios')
        else:
            messages.error(request, '❌ Por favor corrige los errores del formulario.')
    else:
        form = EditarUsuarioForm(instance=usuario)

    return render(request, 'Ajustes/editar_usuario.html', {
        'form': form,
        'usuario': usuario
    })

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

# 🍽️ Gestión de platillos
@login_required
@solo_admin
def editar_menu(request):
    platillos = Platillo.objects.all()
    return render(request, 'Ajustes/editar_menu.html', {'platillos': platillos})

@login_required
@solo_admin
def agregar_platillo(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        precio_raw = request.POST.get('precio', '').strip()
        ingredientes = request.POST.getlist('ingredientes')
        foto = request.FILES.get('foto')

        try:
            precio = Decimal(precio_raw)
            if precio < 0:
                raise InvalidOperation("Precio negativo")
        except (InvalidOperation, TypeError, ValueError):
            messages.error(request, '❌ El precio ingresado no es válido.')
            return redirect('agregar_platillo')

        ingredientes_str = ', '.join([i.strip() for i in ingredientes if i.strip()])

        Platillo.objects.create(
            user=request.user,
            nombre=nombre,
            precio=precio,
            ingredientes=ingredientes_str,
            foto=foto
        )
        messages.success(request, '✅ Platillo agregado correctamente.')
        return redirect('editar_menu')

    return render(request, 'Ajustes/agregar_platillo.html')

@login_required
@solo_admin
def editar_platillo(request, platillo_id):
    platillo = get_object_or_404(Platillo, id=platillo_id)

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        precio_raw = request.POST.get('precio', '').strip()
        ingredientes = request.POST.getlist('ingredientes[]')  

        if not nombre or not precio_raw:
            messages.error(request, '❌ El nombre y el precio son obligatorios.')
            return redirect('editar_platillo', platillo_id=platillo.id)

        try:
            precio = float(precio_raw)
        except ValueError:
            messages.error(request, '❌ El precio debe ser un número válido.')
            return redirect('editar_platillo', platillo_id=platillo.id)

        platillo.nombre = nombre
        platillo.precio = precio
        platillo.ingredientes = ', '.join([i.strip() for i in ingredientes if i.strip()])

        if request.FILES.get('foto'):
            platillo.foto = request.FILES['foto']

        platillo.save()
        messages.success(request, '✅ Platillo actualizado correctamente.')
        return redirect('editar_menu')

    ingredientes_list = [i.strip() for i in platillo.ingredientes.split(',')] if platillo.ingredientes else []
    campos_vacios = range(max(0, 10 - len(ingredientes_list)))

    return render(request, 'Ajustes/editar_platillo.html', {
        'platillo': platillo,
        'ingredientes_list': ingredientes_list,
        'campos_vacios': campos_vacios
    })

@login_required
@solo_admin
def eliminar_platillo(request, platillo_id):
    platillo = get_object_or_404(Platillo, id=platillo_id)
    platillo.delete()
    messages.success(request, '🗑️ Platillo eliminado correctamente.')
    return redirect('editar_menu')

@login_required
@solo_admin
def actualizar_activo(request, id):
    platillo = get_object_or_404(Platillo, id=id)
    platillo.activo = not platillo.activo
    platillo.save()
    messages.success(request, f"Estado de '{platillo.nombre}' actualizado.")
    return redirect('editar_menu')

# 🧾 Procesar pedido (ejemplo con formulario clásico)
@login_required
def procesar_pedido(request):
    if request.method == 'POST':
        ids_str = request.POST.get('platillos[]', '')
        ids = ids_str.split(',') if ids_str else []
        if not ids:
            messages.error(request, '⚠️ No seleccionaste ningún platillo.')
            return redirect('menu_comida')

        messages.success(request, '✅ Pedido enviado correctamente.')
        return redirect('menu_comida')

    messages.error(request, '⛔ Método no permitido.')
    return redirect('menu_comida')

@login_required
def crear_orden(request):
    if request.method == "POST":
        try:
            platillos_data = request.POST.get("platillos_seleccionados")
            mesa_id = request.POST.get("mesa")

            if not platillos_data:
                return HttpResponseBadRequest("No se recibieron platillos")

            platillo_ids = json.loads(platillos_data)

            if not platillo_ids:
                return HttpResponseBadRequest("Debes seleccionar al menos un platillo")

            # Buscar o crear cuenta activa según la mesa
            cuenta = None
            if mesa_id:
                try:
                    mesa = Mesa.objects.get(id=mesa_id)
                except Mesa.DoesNotExist:
                    return HttpResponseBadRequest("Mesa no encontrada")

                cuenta, _ = Cuenta.objects.get_or_create(
                    mesa=mesa,
                    activa=True,
                    defaults={"usuario": request.user}
                )
            else:
                # "Para llevar": una sola cuenta activa por usuario
                cuenta, _ = Cuenta.objects.get_or_create(
                    mesa=None,
                    activa=True,
                    usuario=request.user
                )

            # Crear la orden dentro de la cuenta
            orden = Orden.objects.create(
                cuenta=cuenta,
                usuario=request.user
            )
            orden.platillos.set(Platillo.objects.filter(id__in=platillo_ids))
            orden.save()

            # Agregar platillos a la cuenta
            cuenta.platillos.add(*orden.platillos.all())
            cuenta.calcular_total()

            return redirect("cuentas")  # Ajusta al nombre real de tu URL

        except json.JSONDecodeError:
            return HttpResponseBadRequest("Error en los datos de platillos")
        except Exception as e:
            return HttpResponseBadRequest(f"Error inesperado: {str(e)}")

    return HttpResponseBadRequest("Método no permitido")

# 🔄 AJAX: actualizar pedido
@csrf_exempt
def actualizar_pedido(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            return JsonResponse({"success": True, "data": data})
        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON inválido"}, status=400)

@login_required
@solo_admin
def editar_mesas(request):
    mesas = Mesa.objects.order_by('numero')
    return render(request, 'Ajustes/editar_mesas.html', {'mesas': mesas})

@login_required
@solo_admin
def agregar_mesa(request):
    if request.method == 'POST':
        numero = request.POST.get('numero')
        color = request.POST.get('color')

        if not numero or Mesa.objects.filter(numero=numero).exists():
            messages.error(request, '⚠️ Número inválido o ya existe.')
            return redirect('agregar_mesa')

        Mesa.objects.create(numero=numero, color=color)
        return redirect('editar_mesas')  

    return render(request, 'Ajustes/agregar_mesa.html')

@require_POST
@login_required
def eliminar_mesa(request, numero):
    try:
        mesa = Mesa.objects.get(numero=numero)
        mesa.delete()
        return JsonResponse({'success': True})
    except Mesa.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Mesa no encontrada'})
