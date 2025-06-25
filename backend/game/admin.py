from django.contrib import admin
from .models import Game, Player #, BoardScenario

class PlayerInline(admin.TabularInline):
    model = Player
    extra = 2  # Show 2 empty player slots by default
    max_num = 2  # A game can have at most 2 players

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'current_turn', 'winner', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'players__username')
    inlines = [PlayerInline]

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'symbol')
    list_filter = ('game__status',)
    search_fields = ('user__username', 'game__id')

# @admin.register(BoardScenario)
# class BoardScenarioAdmin(admin.ModelAdmin):
#     list_display = ('name', 'description')
#     search_fields = ('name',)
