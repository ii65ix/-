import json

from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Max
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import ProfileForm, RegisterForm
from .models import GameResult, Profile
from .question_data import build_game_data

User = get_user_model()


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
            Profile.objects.get_or_create(user=user)
            messages.success(request, "تم إنشاء الحساب. مرحباً بك!")
            return redirect("home")
    else:
        form = RegisterForm()
    return render(request, "game/register.html", {"form": form})


@login_required
@require_POST
def save_game_result(request):
    try:
        data = json.loads(request.body.decode())
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"ok": False, "error": "invalid_json"}, status=400)
    mode = data.get("mode")
    if mode not in (
        GameResult.MODE_SITUATION,
        GameResult.MODE_TRUEFALSE,
        GameResult.MODE_JOURNEY,
    ):
        return JsonResponse({"ok": False, "error": "invalid_mode"}, status=400)
    try:
        score = int(data.get("score", 0))
        if score < 0 or score > 500_000:
            raise ValueError
    except (TypeError, ValueError):
        return JsonResponse({"ok": False, "error": "invalid_score"}, status=400)
    GameResult.objects.create(user=request.user, mode=mode, score=score)
    return JsonResponse({"ok": True})


@login_required
def dashboard(request):
    recent = GameResult.objects.select_related("user").order_by("-created_at")[:100]
    leaderboard = (
        GameResult.objects.values("user__username", "user_id")
        .annotate(best_score=Max("score"), total_plays=Count("id"))
        .order_by("-best_score", "-total_plays")[:40]
    )
    total_games = GameResult.objects.count()
    total_users_played = User.objects.filter(game_results__isnull=False).distinct().count()
    return render(
        request,
        "game/dashboard.html",
        {
            "recent": recent,
            "leaderboard": leaderboard,
            "total_games": total_games,
            "total_users_played": total_users_played,
        },
    )


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "تم حفظ البروفايل.")
            return redirect("profile")
    else:
        form = ProfileForm(instance=profile)
    results = request.user.game_results.order_by("-created_at")[:60]
    mode_stats = list(
        request.user.game_results.values("mode").annotate(
            plays=Count("id"), best=Max("score")
        )
    )
    return render(
        request,
        "game/profile.html",
        {
            "form": form,
            "profile": profile,
            "results": results,
            "mode_stats": mode_stats,
        },
    )
