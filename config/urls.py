from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('backend.core.urls')),
]

# Servir archivos estáticos y multimedia en modo desarrollo
if settings.DEBUG:
    # Archivos estáticos personalizados
    for static_dir in settings.STATICFILES_DIRS:
        urlpatterns += static(settings.STATIC_URL, document_root=static_dir)

    # Archivos multimedia (fotos de usuario, etc.)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
