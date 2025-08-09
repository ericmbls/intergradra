from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

# Modelo para platillos del menú
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

    def __str__(self):
        return f"{self.nombre} ({self.user.username})"


# Perfil extendido del usuario
class PerfilUsuario(models.Model):
    ROLES = [
        ('admin', 'Administrador'),
        ('employee', 'Empleado'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLES, default='employee')
    foto = models.ImageField(upload_to='usuarios/fotos/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"
