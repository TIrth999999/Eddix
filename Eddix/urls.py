from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

def empty_favicon(request):
    return HttpResponse(status=204)

urlpatterns = [
    path('favicon.ico', empty_favicon),
    path('admin/', admin.site.urls),
    path('', include('editor.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)