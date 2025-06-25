import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Game, Player, User

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'game_{self.room_id}'
        self.user = self.scope['user']

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Send initial game state
        game = await self.get_game()
        if game:
            players = await self.get_players_info(game)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'send_game_state',
                    'board': game.board,
                    'board_size': game.board_size,
                    'message': self.get_game_status_message(game),
                    'players': players
                }
            )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get('type') == 'make_move':
            await self.make_move(data['row'], data['col'])

    async def make_move(self, row, col):
        game = await self.get_game()
        player = await self.get_player(game)

        # Validation
        if not game or not player:
            return await self.send_error("Game or player not found.")
        if game.status != 'in_progress':
            return await self.send_error("Game is not in progress.")
        if game.current_turn != self.user:
            return await self.send_error("Not your turn.")
        if not isinstance(row, int) or not isinstance(col, int):
            return await self.send_error("Invalid move data (row/col must be integer).")
        if not (0 <= row < 15 and 0 <= col < 15 and game.board[row][col] == ''):
            return await self.send_error("Invalid move.")

        # Apply move
        board = game.board
        board[row][col] = player.symbol

        # Check for winner
        winning_line = self.check_winner(board, player.symbol, row, col, game.block_two_ends)
        if winning_line:
            game.status = 'finished'
            game.winner = self.user
            game.winning_line = winning_line
            message = f"Player {self.user.username} ({player.symbol}) wins!"
        else:
            # Switch turn
            other_player_user = await self.get_other_player_user(game)
            game.current_turn = other_player_user
            game.winning_line = None
            message = self.get_game_status_message(game)

        game.board = board
        await self.save_game(game)

        # Broadcast new state
        players = await self.get_players_info(game)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send_game_state',
                'board': game.board,
                'board_size': game.board_size,
                'message': message,
                'players': players,
                'winning_line': game.winning_line
            }
        )

    def check_winner(self, board, symbol, r, c, allow_blocked_win):
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)] # Horizontal, Vertical, Diag down, Diag up
        for dr, dc in directions:
            line = [(r, c)]
            # Count forward
            for i in range(1, 5):
                nr, nc = r + dr * i, c + dc * i
                if 0 <= nr < 15 and 0 <= nc < 15 and board[nr][nc] == symbol:
                    line.append((nr, nc))
                else:
                    break
            # Count backward
            for i in range(1, 5):
                nr, nc = r - dr * i, c - dc * i
                if 0 <= nr < 15 and 0 <= nc < 15 and board[nr][nc] == symbol:
                    line.insert(0, (nr, nc))
                else:
                    break
            if len(line) >= 5:
                if not allow_blocked_win:
                    end1_r, end1_c = line[-1][0] + dr, line[-1][1] + dc
                    blocked1 = not (0 <= end1_r < 15 and 0 <= end1_c < 15) or (board[end1_r][end1_c] != '' and board[end1_r][end1_c] != symbol)
                    end2_r, end2_c = line[0][0] - dr, line[0][1] - dc
                    blocked2 = not (0 <= end2_r < 15 and 0 <= end2_c < 15) or (board[end2_r][end2_c] != '' and board[end2_r][end2_c] != symbol)
                    if blocked1 and blocked2:
                        continue
                # Trả về danh sách các ô thắng dạng dict
                return [{"row": row, "col": col} for row, col in line]
        return None

    def get_game_status_message(self, game):
        if game.status == 'waiting':
            return "Waiting for another player to join..."
        elif game.status == 'in_progress':
            return f"Turn: {game.current_turn.username}"
        elif game.status == 'finished':
            return f"Game Over! Winner: {game.winner.username}"
        return "Game state unknown."

    # Send game state to the client
    async def send_game_state(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_state',
            'board': event['board'],
            'board_size': event['board_size'],
            'message': event['message'],
            'players': event.get('players', []),
            'winning_line': event.get('winning_line', None)
        }))

    # Send an error message to the client
    async def send_error(self, message):
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message
        }))

    # Database helpers
    @database_sync_to_async
    def get_game(self):
        try:
            return Game.objects.select_related('current_turn', 'winner').prefetch_related('players_info__user').get(id=self.room_id)
        except Game.DoesNotExist:
            return None

    @database_sync_to_async
    def get_player(self, game):
        try:
            return Player.objects.get(game=game, user=self.user)
        except Player.DoesNotExist:
            return None
    
    @database_sync_to_async
    def get_other_player_user(self, game):
        return game.players.exclude(id=self.user.id).first()

    @database_sync_to_async
    def save_game(self, game):
        game.save()

    @database_sync_to_async
    def get_all_players_in_game(self, game):
        return list(game.player_set.select_related('user').all())

    @database_sync_to_async
    def get_players_info(self, game):
        return [
            {"username": p.user.username, "symbol": p.symbol}
            for p in game.players_info.select_related('user').all()
        ]

    @database_sync_to_async
    def get_other_player_user(self, game):
        return game.players.exclude(id=self.user.id).first()

    @database_sync_to_async
    def save_game(self, game):
        game.save()