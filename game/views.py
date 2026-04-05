from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import RegisterForm
from .question_data import build_game_data


@login_required
def index(request):
    return render(request, "game/index.html", {"game_data": build_game_data()})


def register(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "تم إنشاء الحساب. مرحباً بك!")
            return redirect("home")
    else:
        form = RegisterForm()
    return render(request, "game/register.html", {"form": form})
