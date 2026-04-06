from django.contrib.auth import views as auth_views
from django.urls import path

from .forms import StyledLoginForm
from . import views

urlpatterns = [
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(
            template_name="game/login.html",
            authentication_form=StyledLoginForm,
        ),
        name="login",
    ),
    path(
        "accounts/logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),
    path("accounts/register/", views.register, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/", views.profile_view, name="profile"),
    path("api/save-result/", views.save_game_result, name="save_game_result"),
    path("", views.index, name="home"),
]
