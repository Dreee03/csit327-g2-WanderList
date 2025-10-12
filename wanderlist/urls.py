from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

def home_redirect(request):
    return redirect('home')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('destination/', include('destination.urls')),
    path('', home_redirect),
]

# Serve media files during development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
