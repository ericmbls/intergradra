from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from backend.core.models import PerfilUsuario

# 🆕 Registro de usuario
class RegistroUsuarioForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'id': 'email',
            'placeholder': 'Correo electrónico',
            'class': 'form-input'
        })
    )

    ROLE_CHOICES = PerfilUsuario.ROLES

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'id': 'role',
            'class': 'form-input'
        })
    )

    foto = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'id': 'platillo-foto',
            'class': 'file-input',
            'accept': 'image/*'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role', 'foto']
        widgets = {
            'username': forms.TextInput(attrs={
                'id': 'fullname',
                'placeholder': 'Nombre de usuario',
                'class': 'form-input'
            }),
            'password1': forms.PasswordInput(attrs={
                'id': 'password',
                'placeholder': 'Contraseña',
                'class': 'form-input'
            }),
            'password2': forms.PasswordInput(attrs={
                'id': 'confirm_password',
                'placeholder': 'Confirmar contraseña',
                'class': 'form-input'
            }),
        }

    def save(self, commit=True):
        user = super().save(commit=commit)
        role = self.cleaned_data['role']
        foto = self.cleaned_data.get('foto')

        perfil, created = PerfilUsuario.objects.get_or_create(user=user)
        perfil.role = role
        if foto:
            perfil.foto = foto
        perfil.save()

        return user

# ✏️ Edición de usuario
class EditarUsuarioForm(forms.ModelForm):
    username = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'id': 'fullname',
            'class': 'form-input',
            'placeholder': 'Nombre de usuario'
        })
    )

    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'id': 'first_name',
            'class': 'form-input',
            'placeholder': 'Nombre'
        })
    )

    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'id': 'last_name',
            'class': 'form-input',
            'placeholder': 'Apellido'
        })
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'id': 'email',
            'class': 'form-input',
            'placeholder': 'Correo electrónico'
        })
    )

    ROLE_CHOICES = PerfilUsuario.ROLES

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'id': 'role',
            'class': 'form-input'
        })
    )

    foto = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'id': 'platillo-foto',
            'class': 'file-input',
            'accept': 'image/*'
        })
    )

    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'id': 'password',
            'class': 'form-input',
            'placeholder': 'Nueva contraseña (opcional)'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)

        if instance:
            perfil = getattr(instance, 'perfilusuario', None)
            if perfil:
                self.fields['role'].initial = perfil.role

    def save(self, commit=True):
        user = super().save(commit=commit)

        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
            user.save()

        perfil, _ = PerfilUsuario.objects.get_or_create(user=user)
        perfil.role = self.cleaned_data['role']
        foto = self.cleaned_data.get('foto')
        if foto:
            perfil.foto = foto
        perfil.save()

        return user