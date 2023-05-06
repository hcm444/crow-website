from django.urls import path, re_path
from django.views.static import serve
from django.conf import settings
from aircraft.views import aircraft_info

urlpatterns = [
    path("crow/", aircraft_info),
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/maps/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]

