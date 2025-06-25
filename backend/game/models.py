from django.db import models
from django.contrib.auth.models import User
import uuid

def get_default_board():
    return [['' for _ in range(15)] for _ in range(15)]

class Game(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_games')
    status = models.CharField(max_length=20, default='waiting') # waiting, in_progress, finished
    board = models.JSONField(default=get_default_board)
    board_size = models.IntegerField(default=15)
    current_turn = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    players = models.ManyToManyField(User, through='Player', related_name='games')
    block_two_ends = models.BooleanField(default=False)
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_games')
    winning_line = models.JSONField(null=True, blank=True)
    rematch_requested_by = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_creator(self):
        # Assuming the first player to join is the creator
        player = self.players_info.order_by('created_at').first()
        return player.user if player else None

    def __str__(self):
        return f"Game {self.name} ({self.id})"

class Player(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='players_info')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='players_info')
    symbol = models.CharField(max_length=1) # X or O
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('game', 'user')

# class BoardScenario(models.Model):
#     name = models.CharField(max_length=100)
#     board_state = models.JSONField()
#     description = models.TextField(blank=True)
#
#     def __str__(self):
#         return self.name
