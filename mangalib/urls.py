from django.urls import path

from . import views

app_name = 'mangalib'

urlpatterns = [
    path('', views.home, name = 'home'),
    path('login', views.login_user, name = 'login'),
    path('register', views.register_user, name = 'register'),
    path('logout', views.logout_user, name = 'logout'),
    path('add', views.add_manga, name = 'add'),
    path('save/<str:mangaId>/', views.save_manga, name = 'save'),
    path('delete/<str:mangaId>/', views.delete_manga, name = 'delete'),
    path('gimme', views.gimme, name = 'gimme'),
    path('manga/<str:mangaId>/', views.manga, name = 'manga'),
]