from django.urls import path
from . import views

urlpatterns = [
    path('all', views.list_view),
    path('add_note', views.add_view),
    path('mod_note/<int:pg>', views.mod_view)
]