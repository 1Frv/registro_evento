from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("guardar/", views.guardar, name="guardar"),
    path("anular/<int:pk>/", views.anular, name="anular"),
    path("salir/", LogoutView.as_view(), name="salir"),
    path("exportar/", views.exportar, name="exportar"),
]