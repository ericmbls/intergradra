from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone

# 🍽️ Platillo del menú
class Platillo(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='platillos'
    )
    nombre = models.CharField(max_length=100)
    ingredientes = models.TextField()
    precio = models.DecimalField(max_digits=6, decimal_places=2)
    activo = models.BooleanField(default=True)
    foto = models.ImageField(upload_to='platillos/', blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} — ${self.precio:.2f} ({self.user.username})"

    @property
    def ingredientes_list(self):
        return [i.strip() for i in self.ingredientes.split(',') if i.strip()]

    class Meta:
        verbose_name = "Platillo"
        verbose_name_plural = "Platillos"
        ordering = ['nombre']


# 👤 Perfil extendido del usuario
class PerfilUsuario(models.Model):
    ROLES = [
        ('admin', 'Administrador'),
        ('employee', 'Empleado'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLES, default='employee')
    foto = models.ImageField(upload_to='usuarios/fotos/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} — {self.get_role_display()}"

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"


# 🪑 Mesa del restaurante
class Mesa(models.Model):
    numero = models.PositiveIntegerField(unique=True)
    color = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"Mesa {self.numero}"

    class Meta:
        verbose_name = "Mesa"
        verbose_name_plural = "Mesas"
        ordering = ['numero']


# 💳 Cuenta activa (puede o no tener mesa)
class Cuenta(models.Model):
    mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE, null=True, blank=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    platillos = models.ManyToManyField(Platillo, blank=True)
    total = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    activa = models.BooleanField(default=True)
    creada = models.DateTimeField(auto_now_add=True)
    cerrada = models.DateTimeField(null=True, blank=True)  # Agregado para corte

    def __str__(self):
        mesa_info = f"Mesa {self.mesa.numero}" if self.mesa else "Para llevar"
        return f"Cuenta #{self.id} — {mesa_info} — ${self.total:.2f}"

    def calcular_total(self):
        self.total = sum(p.precio for p in self.platillos.all())
        self.save(update_fields=['total'])

    def cerrar(self):
        self.calcular_total()
        self.activa = False
        self.cerrada = timezone.now()
        self.save(update_fields=['activa', 'total', 'cerrada'])

    class Meta:
        verbose_name = "Cuenta"
        verbose_name_plural = "Cuentas"
        ordering = ['-creada']


# 🧾 Orden dentro de una cuenta
class Orden(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En proceso'),
        ('servida', 'Servida'),
        ('cancelada', 'Cancelada'),
    ]

    cuenta = models.ForeignKey(Cuenta, on_delete=models.CASCADE, related_name='ordenes')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    platillos = models.ManyToManyField(Platillo)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    nota = models.TextField(blank=True, null=True)
    creada = models.DateTimeField(auto_now_add=True)
    actualizada = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Orden #{self.id} — Cuenta #{self.cuenta.id} — {self.get_estado_display()}"

    def total(self):
        return sum(p.precio for p in self.platillos.all())

    class Meta:
        verbose_name = "Orden"
        verbose_name_plural = "Órdenes"
        ordering = ['-creada']


# 💸 Gasto extra del día
class GastoExtra(models.Model):
    fecha = models.DateField()
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.CharField(max_length=255)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.fecha} — ${self.monto:.2f} — {self.descripcion}"

    class Meta:
        verbose_name = "Gasto Extra"
        verbose_name_plural = "Gastos Extras"
        ordering = ['-fecha']


# 📊 Corte de caja diario
class CorteCaja(models.Model):
    fecha = models.DateField(unique=True)
    efectivo_inicial = models.DecimalField(max_digits=10, decimal_places=2)
    ventas_totales = models.DecimalField(max_digits=10, decimal_places=2)
    gastos_totales = models.DecimalField(max_digits=10, decimal_places=2)
    monto_extra = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    dinero_en_caja = models.DecimalField(max_digits=10, decimal_places=2)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Corte {self.fecha} — ${self.dinero_en_caja:.2f}"

    class Meta:
        verbose_name = "Corte de Caja"
        verbose_name_plural = "Cortes de Caja"
        ordering = ['-fecha']
