from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Game, Player
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm
from django.db.models import Count
from django.db import transaction

# Create your views here.

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('game:lobby')
    else:
        form = UserCreationForm()
    return render(request, 'game/signup.html', {'form': form})

@login_required
def lobby_view(request):
    if request.method == "POST":
        room_id = request.POST.get("room_id")
        room_name = request.POST.get("room_name")
        board_size = int(request.POST.get("board_size", 15))
        block_two_ends = request.POST.get("block_two_ends", "off") == "on"

        if room_id:
            # Chỉnh sửa phòng
            game = Game.objects.get(id=room_id)
            if game.creator == request.user and game.status == 'waiting':
                game.name = room_name
                game.board_size = board_size
                game.block_two_ends = block_two_ends
                game.save()
            return redirect('game:lobby')
        else:
            # Tạo phòng mới
            game = Game.objects.create(
                name=room_name,
                creator=request.user,
                board_size=board_size,
                board=[["" for _ in range(board_size)] for _ in range(board_size)],
                block_two_ends=block_two_ends,
                current_turn=request.user
            )
            Player.objects.create(game=game, user=request.user, symbol='X')
            return redirect('game:game_room', room_id=game.id)

    waiting_games = Game.objects.filter(status='waiting').prefetch_related('players_info__user').order_by('-created_at')
    in_progress_games = Game.objects.filter(status='in_progress', players=request.user).prefetch_related('players_info__user').order_by('-updated_at')
    
    def get_guest(game, user):
        # Lấy player khác creator (hoặc khác user hiện tại)
        players = [p.user for p in game.players_info.all()]
        for p in players:
            if p != game.creator:
                return p
        return None

    waiting_games_with_guest = []
    for game in waiting_games:
        guest = get_guest(game, request.user)
        waiting_games_with_guest.append({
            'id': game.id,
            'name': game.name,
            'creator': game.creator,
            'guest': guest,
        })

    in_progress_games_with_guest = []
    for game in in_progress_games:
        guest = get_guest(game, request.user)
        in_progress_games_with_guest.append({
            'id': game.id,
            'name': game.name,
            'creator': game.creator,
            'guest': guest,
        })

    return render(request, "game/index.html", {
        "waiting_games": waiting_games_with_guest,
        "in_progress_games": in_progress_games_with_guest,
    })

@login_required
def game_room(request, room_id):
    game = get_object_or_404(Game, id=room_id)
    
    # Logic to join a game if it's waiting for a player
    if game.status == 'waiting' and not game.players.filter(id=request.user.id).exists():
         with transaction.atomic():
            if game.players.count() < 2:
                Player.objects.create(game=game, user=request.user, symbol='O')
                game.status = 'in_progress'
                game.save()

    context = {
        "game": game,
        'room_name': game.name,
        'room_name_json': str(game.id),
    }
    return render(request, "game/room.html", context)

@login_required
def delete_game(request, room_id):
    if request.method == 'POST':
        game = get_object_or_404(Game, id=room_id)
        if game.creator == request.user:
            game.delete()
    return redirect('game:lobby')

@login_required
def start_from_scenario(request, scenario_id):
    pass
