import math
import time
from copy import deepcopy
import pygame
import sys

class FourPlayerCheckersGUI:
    def __init__(self, game):
        self.game = game
        pygame.init()
        self.WIDTH, self.HEIGHT = 800, 800
        self.WIN = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Four Player Checkers")
        #colors and font
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BROWN = (139, 69, 19)
        self.LIGHT_BROWN = (222, 184, 135)
        self.RED = (255, 0, 0)
        self.BLUE = (0, 0, 255)
        self.GREEN = (0, 255, 0)
        self.YELLOW = (255, 255, 0)
        self.GRAY = (128, 128, 128)
        self.PURPLE = (128, 0, 128)
        self.font = pygame.font.SysFont('Arial', 24)
        #board setup for pieces
        self.SQUARE_SIZE = self.WIDTH // 12
        self.PIECE_RADIUS = self.SQUARE_SIZE // 2 - 5
        self.KING_BORDER_WIDTH = 8
        self.KING_RADIUS = self.PIECE_RADIUS - self.KING_BORDER_WIDTH
        #selection for moves
        self.selected_piece = None
        self.valid_moves = []
        
    def draw_board(self):
        self.WIN.fill(self.BROWN)
        #squares
        for row in range(12):
            for col in range(12):
                if (row + col) % 2 == 0 and (row, col) not in self.game.blocked_positions:
                    pygame.draw.rect(self.WIN, self.LIGHT_BROWN, (col * self.SQUARE_SIZE, row * self.SQUARE_SIZE,self.SQUARE_SIZE, self.SQUARE_SIZE))
        #blocked positions
        for row, col in self.game.blocked_positions:
            pygame.draw.rect(self.WIN, self.GRAY, (col * self.SQUARE_SIZE, row * self.SQUARE_SIZE,self.SQUARE_SIZE, self.SQUARE_SIZE))
        #pieces
        for row in range(12):
            for col in range(12):
                piece = self.game.board[row][col]
                if piece != '.' and piece != 'X':
                    x = col * self.SQUARE_SIZE + self.SQUARE_SIZE // 2
                    y = row * self.SQUARE_SIZE + self.SQUARE_SIZE // 2
                    if piece == 'R':
                        color = self.RED
                        pygame.draw.circle(self.WIN, color, (x, y), self.PIECE_RADIUS)
                    elif piece == 'r':
                        color = self.RED
                        pygame.draw.circle(self.WIN, self.WHITE, (x, y), self.PIECE_RADIUS)
                        pygame.draw.circle(self.WIN, color, (x, y), self.KING_RADIUS)
                    elif piece == 'B':
                        color = self.BLUE
                        pygame.draw.circle(self.WIN, color, (x, y), self.PIECE_RADIUS)
                    elif piece == 'b':
                        color = self.BLUE
                        pygame.draw.circle(self.WIN, self.WHITE, (x, y), self.PIECE_RADIUS)
                        pygame.draw.circle(self.WIN, color, (x, y), self.KING_RADIUS)
                    elif piece == 'G':
                        color = self.GREEN
                        pygame.draw.circle(self.WIN, color, (x, y), self.PIECE_RADIUS)
                    elif piece == 'g':
                        color = self.GREEN
                        pygame.draw.circle(self.WIN, self.WHITE, (x, y), self.PIECE_RADIUS)
                        pygame.draw.circle(self.WIN, color, (x, y), self.KING_RADIUS)
                    elif piece == 'Y':
                        color = self.YELLOW
                        pygame.draw.circle(self.WIN, color, (x, y), self.PIECE_RADIUS)
                    elif piece == 'y':
                        color = self.YELLOW
                        pygame.draw.circle(self.WIN, self.WHITE, (x, y), self.PIECE_RADIUS)
                        pygame.draw.circle(self.WIN, color, (x, y), self.KING_RADIUS)
        #highlight selected piece
        if self.selected_piece:
            row, col = self.selected_piece
            x = col * self.SQUARE_SIZE
            y = row * self.SQUARE_SIZE
            s = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE), pygame.SRCALPHA)
            s.fill((255, 255, 0, 128))
            self.WIN.blit(s, (x, y))
        #highlight valid moves
        for move in self.valid_moves:
            row, col, _ = move
            x = col * self.SQUARE_SIZE
            y = row * self.SQUARE_SIZE
            s = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE), pygame.SRCALPHA)
            s.fill((0, 255, 0, 128))
            self.WIN.blit(s, (x, y))
        #game info
        current_player = self.game.players[self.game.current_player_idx]
        turn_text = f"{current_player['name']}'s turn ({current_player['symbol']})"
        turn_surface = self.font.render(turn_text, True, self.BLACK)
        self.WIN.blit(turn_surface, (10, 10))
        #players statistics
        for i, player in enumerate(self.game.players):
            y_pos = 40 + i * 30
            color = self.RED if player['symbol'] == 'R' else \
                   self.BLUE if player['symbol'] == 'B' else \
                   self.GREEN if player['symbol'] == 'G' else self.YELLOW
            text = f"{player['name']}: {player['pieces']} pieces"
            text_surface = self.font.render(text, True, color)
            self.WIN.blit(text_surface, (10, y_pos))
        pygame.display.update()
    
    def get_row_col_from_pos(self, pos):
        x, y = pos
        row = y // self.SQUARE_SIZE
        col = x // self.SQUARE_SIZE
        return row, col
    
    def handle_click(self, row, col):
        current_player = self.game.players[self.game.current_player_idx]
        if current_player['type'] == "AI":
            return
        piece = self.game.board[row][col]
        #capture moves mandatory
        capture_moves = []
        for x in range(12):
            for y in range(12):
                if self.game.board[x][y] in [current_player['symbol'], current_player['king']]:
                    moves = self.game.get_valid_moves(x, y, self.game.current_player_idx)
                    capture_moves.extend([(x, y, *move) for move in moves if move[2]])
        #enforcing capture moves
        if capture_moves:
            if piece in [current_player['symbol'], current_player['king']]:
                piece_capture_moves = [m for m in capture_moves if m[0] == row and m[1] == col]
                if piece_capture_moves:
                    self.selected_piece = (row, col)
                    self.valid_moves = [m[2:] for m in piece_capture_moves]
                elif self.selected_piece:
                    return
            #selected captured piece
            elif self.selected_piece:
                selected_row, selected_col = self.selected_piece
                for move in self.valid_moves:
                    if move[0] == row and move[1] == col:
                        result = self.game.move_piece(selected_row, selected_col, row, col, move[2])
                        if result:
                            x, y = result
                            self.selected_piece = (x, y)
                            self.valid_moves = [m for m in self.game.get_valid_moves(x, y, self.game.current_player_idx) if m[2]]
                        else:
                            self.selected_piece = None
                            self.valid_moves = []
                            self.game.next_player()
                        return
        else:
            #if no capture then any pieces valid moves
            if self.selected_piece:
                selected_row, selected_col = self.selected_piece
                for move in self.valid_moves:
                    if move[0] == row and move[1] == col:
                        result = self.game.move_piece(selected_row, selected_col, row, col, move[2])
                        if result:
                            x, y = result
                            self.selected_piece = (x, y)
                            self.valid_moves = [m for m in self.game.get_valid_moves(x, y, self.game.current_player_idx) if m[2]]
                        else:
                            self.selected_piece = None
                            self.valid_moves = []
                            self.game.next_player()
                        return
                if piece in [current_player['symbol'], current_player['king']]:
                    self.selected_piece = (row, col)
                    self.valid_moves = self.game.get_valid_moves(row, col, self.game.current_player_idx)
                else:
                    self.selected_piece = None
                    self.valid_moves = []
            else:
                if piece in [current_player['symbol'], current_player['king']]:
                    self.selected_piece = (row, col)
                    self.valid_moves = self.game.get_valid_moves(row, col, self.game.current_player_idx)
    
    def show_message(self, message):
        s = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        self.WIN.blit(s, (0, 0))
        text = self.font.render(message, True, self.WHITE)
        text_rect = text.get_rect(center=(self.WIDTH//2, self.HEIGHT//2))
        self.WIN.blit(text, text_rect)
        pygame.display.update()
        pygame.time.delay(3000)
    
    def run(self):
        clock = pygame.time.Clock()
        while True:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                current_player = self.game.players[self.game.current_player_idx]
                if event.type == pygame.MOUSEBUTTONDOWN and current_player['type'] != "AI":
                    pos = pygame.mouse.get_pos()
                    row, col = self.get_row_col_from_pos(pos)
                    if 0 <= row < 12 and 0 <= col < 12:
                        self.handle_click(row, col)
            #ai move
            current_player = self.game.players[self.game.current_player_idx]
            if current_player['type'] == "AI" and not self.game.check_game_over():
                pygame.time.delay(500)
                move = self.game.ai_move(self.game.current_player_idx)
                if move:
                    x, y, nx, ny, is_capture = move
                    result = self.game.move_piece(x, y, nx, ny, is_capture)
                    #multiple jumps
                    while result:
                        x, y = result
                        moves = self.game.get_valid_moves(x, y, self.game.current_player_idx)
                        capture_moves = [m for m in moves if m[2]]
                        if not capture_moves:
                            break
                        nx, ny, is_capture = capture_moves[0]
                        result = self.game.move_piece(x, y, nx, ny, True)
                self.game.next_player()
            self.draw_board()
            if self.game.check_game_over():
                winner = self.game.get_winner()
                if winner:
                    if self.game.game_mode == 2:
                        human_players = [p for p in self.game.players if p['type'] == 'Human']
                        if len(human_players) > 0 and human_players[0]['pieces'] == 0:
                            self.show_message("All your pieces have been captured! You lose!")
                        else:
                            self.show_message(f"{winner['name']} wins!")
                    else:
                        self.show_message(f"{winner['name']} wins!")
                else:
                    self.show_message("Game ended in a draw!")
                pygame.time.delay(3000)
                return

class FourPlayerCheckers:
    def __init__(self):
        self.board = [['.' for _ in range(12)] for _ in range(12)]
        self.players = []
        self.current_player_idx = 0
        self.difficulty = 3
        self.game_mode = None
        self.ai_count = 0
        self.blocked_positions = set()
        
    def show_setup_dialog(self):
        pygame.init()
        WIDTH, HEIGHT = 600, 600
        WIN = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("4-Player Checkers Setup")
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        GRAY = (200, 200, 200)
        BLUE = (70, 130, 180)
        GREEN = (34, 139, 34)
        RED = (220, 20, 60)
        YELLOW = (218, 165, 32)
        title_font = pygame.font.SysFont('Arial', 32, bold=True)
        font = pygame.font.SysFont('Arial', 24)
        small_font = pygame.font.SysFont('Arial', 20)
        mode = None
        ai_count = 0
        ai_difficulty = 3
        player_names = ["", "", "", ""]
        active_input = None
        mode_text = font.render("Select Game Mode:", True, BLACK)
        human_button = pygame.Rect(50, 100, 250, 40)
        ai_button = pygame.Rect(310, 100, 250, 40)
        ai_count_text = font.render("Number of AIs (1-3):", True, BLACK)
        ai_count_buttons = [pygame.Rect(200 + i*60, 180, 50, 40) for i in range(3)]
        difficulty_text = font.render("AI Difficulty (1-5):", True, BLACK)
        difficulty_slider = pygame.Rect(200, 240, 200, 20)
        slider_knob = pygame.Rect(200 + (ai_difficulty-1)*50, 235, 10, 30)
        player_labels = [font.render(f"Player {i+1} Name ({color}):", True, BLACK) for i, color in enumerate(['R', 'B', 'G', 'Y'])]
        player_inputs = [pygame.Rect(250, 300 + i*50, 200, 32) for i in range(4)]
        start_button = pygame.Rect(WIDTH//2 - 75, HEIGHT - 60, 150, 40)
        clock = pygame.time.Clock()
        running = True
        while running:
            WIN.fill(WHITE)
            title = title_font.render("4-Player Checkers Setup", True, BLACK)
            WIN.blit(title, (WIDTH//2 - title.get_width()//2, 20))
            #game mode selection
            WIN.blit(mode_text, (50, 70))
            #buttons
            pygame.draw.rect(WIN, GREEN if mode == "human" else GRAY, human_button, border_radius=5)
            human_label = font.render("4 Humans", True, BLACK)
            WIN.blit(human_label, (human_button.x + 80, human_button.y + 10))
            pygame.draw.rect(WIN, BLUE if mode == "ai" else GRAY, ai_button, border_radius=5)
            ai_label = font.render("Human vs AIs", True, BLACK)
            WIN.blit(ai_label, (ai_button.x + 70, ai_button.y + 10))
            #ai controls
            if mode == "ai":
                WIN.blit(ai_count_text, (50, 190))
                for i, button in enumerate(ai_count_buttons):
                    pygame.draw.rect(WIN, BLUE if ai_count == i+1 else GRAY, button, border_radius=5)
                    count_label = font.render(str(i+1), True, BLACK)
                    WIN.blit(count_label, (button.x + 20, button.y + 10))
                WIN.blit(difficulty_text, (50, 245))
                pygame.draw.rect(WIN, GRAY, difficulty_slider, border_radius=10)
                pygame.draw.rect(WIN, BLUE, slider_knob, border_radius=5)
                difficulty_value = font.render(str(ai_difficulty), True, BLACK)
                WIN.blit(difficulty_value, (difficulty_slider.x + difficulty_slider.width + 10, difficulty_slider.y))
            # Player name inputs
            for i in range(4):
                if mode == "human" or (mode == "ai" and i < 4 - ai_count):
                    WIN.blit(player_labels[i], (50, 305 + i*50))
                    pygame.draw.rect(WIN, BLACK, player_inputs[i], 2, border_radius=3)
                    name_surface = font.render(player_names[i], True, BLACK)
                    WIN.blit(name_surface, (player_inputs[i].x + 5, player_inputs[i].y + 5))
            #start button
            pygame.draw.rect(WIN, GREEN if self.can_start(mode, player_names, ai_count) else GRAY, start_button, border_radius=5)
            start_label = font.render("Start Game", True, BLACK)
            WIN.blit(start_label, (start_button.x + 30, start_button.y + 10))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if human_button.collidepoint(pos):
                        mode = "human"
                        ai_count = 0
                    elif ai_button.collidepoint(pos):
                        mode = "ai"
                    #ai counts
                    elif mode == "ai":
                        for i, button in enumerate(ai_count_buttons):
                            if button.collidepoint(pos):
                                ai_count = i + 1
                    #difficulty slider
                    elif mode == "ai" and difficulty_slider.collidepoint(pos):
                        rel_x = pos[0] - difficulty_slider.x
                        ai_difficulty = min(5, max(1, round(rel_x / (difficulty_slider.width / 4)) + 1))
                        slider_knob.x = difficulty_slider.x + (ai_difficulty-1)*50
                    #name inputs
                    for i in range(4):
                        if (mode == "human" or (mode == "ai" and i < 4 - ai_count)) and player_inputs[i].collidepoint(pos):
                            active_input = i
                            break
                    else:
                        active_input = None
                    #start button check
                    if start_button.collidepoint(pos) and self.can_start(mode, player_names, ai_count):
                        self.initialize_players(mode, player_names, ai_count, ai_difficulty)
                        running = False
                elif event.type == pygame.MOUSEMOTION:
                    if pygame.mouse.get_pressed()[0] and mode == "ai":
                        pos = pygame.mouse.get_pos()
                        if difficulty_slider.collidepoint(pos):
                            rel_x = pos[0] - difficulty_slider.x
                            ai_difficulty = min(5, max(1, round(rel_x / (difficulty_slider.width / 4)) + 1))
                            slider_knob.x = difficulty_slider.x + (ai_difficulty-1)*50
                elif event.type == pygame.KEYDOWN and active_input is not None:
                    if event.key == pygame.K_BACKSPACE:
                        player_names[active_input] = player_names[active_input][:-1]
                    else:
                        if len(player_names[active_input]) < 10:
                            player_names[active_input] += event.unicode
            clock.tick(60)
        pygame.quit()
        self.initialize_board()
        self.current_player_idx = 0

    def can_start(self, mode, player_names, ai_count):
        if not mode:
            return False
        if mode == "human":
            return all(name for name in player_names)
        else:
            return ai_count > 0 and all(name for i, name in enumerate(player_names) if i < 4 - ai_count)

    def initialize_players(self, mode, player_names, ai_count, ai_difficulty):
        colors = ['R', 'B', 'G', 'Y']
        kings = ['r', 'b', 'g', 'y']
        directions = [
            (1, 1),    #player 1(red)bottom=moves up-right
            (-1, -1),   #player 2(blue)left=moves up-left
            (-1, 1),    #player 3(green)top=moves down-left
            (1, 1)      #player 4(yellow)right=moves down-right
        ]
        self.players = []
        for i in range(4):
            if mode == "human" or (mode == "ai" and i < 4 - ai_count):
                name = player_names[i]
                player_type = "Human"
            else:
                name = f"AI {i+1}"
                player_type = "AI"
            self.players.append({
                'name': name,
                'type': player_type,
                'symbol': colors[i],
                'king': kings[i],
                'pieces': 9,
                'direction': directions[i],
                'position': i
            })
        if mode == "ai":
            self.difficulty = ai_difficulty + 2
            self.ai_count = ai_count
            self.game_mode = 2
        else:
            self.game_mode = 1
            
    def setup(self):
        print("\033[0;32m\t\t\t\tFOUR PLAYER CHECKERS\033[0m")
        print("\033[0;34mGame Modes:\033[0m")
        print("1. 4 Humans")
        print("2. Human vs AIs")
        while True:
            try:
                mode = int(input("Select game mode (1-2): "))
                if 1 <= mode <= 2:
                    self.game_mode = mode
                    break
                print("Please enter 1 or 2")
            except ValueError:
                print("Invalid input")
        if self.game_mode == 2:
            while True:
                try:
                    ai_count = int(input("Number of AIs (1-3): "))
                    if 1 <= ai_count <= 3:
                        self.ai_count = ai_count
                        break
                    print("Please enter 1-3")
                except ValueError:
                    print("Invalid input")
            while True:
                try:
                    level = int(input("Select AI difficulty (1-5, 3 is default): "))
                    if 1 <= level <= 5:
                        self.difficulty = level + 2
                        break
                    print("Please enter a number between 1 and 5")
                except ValueError:
                    print("Invalid input. Please enter a number.")
        colors = ['R', 'B', 'G', 'Y']  # Red, Blue, Green, Yellow
        kings = ['r', 'b', 'g', 'y']
        directions = [(1, 1),(-1, -1),(-1, 1),(1, 1) ]
        for i in range(4):
            if self.game_mode == 1 or (self.game_mode == 2 and i < 4 - self.ai_count):
                name = input(f"Enter name for Player {i+1} ({colors[i]}): ")
                player_type = "Human"
            else:
                name = f"AI {i+1}"
                player_type = "AI"
            self.players.append({
                'name': name,
                'type': player_type,
                'symbol': colors[i],
                'king': kings[i],
                'pieces': 9,
                'direction': directions[i],
                'position': i  # 0=bottom, 1=left, 2=top, 3=right
            })
        self.initialize_board()
        self.current_player_idx = 0

    def initialize_board(self):
        blocked_groups = [
            ['a1', 'a2', 'a3', 'b1', 'b2', 'b3', 'c1', 'c2', 'c3'],
            ['j1', 'j2', 'j3', 'k1', 'k2', 'k3', 'l1', 'l2', 'l3'],
            ['a10', 'a11', 'a12', 'b10', 'b11', 'b12', 'c10', 'c11', 'c12'],
            ['j10', 'j11', 'j12', 'k10', 'k11', 'k12', 'l10', 'l11', 'l12']]
        for group in blocked_groups:
            for pos in group:
                x, y = self.convert_position(pos)
                if x is not None and y is not None:
                    self.board[x][y] = 'X'
                    self.blocked_positions.add((x, y))
        
        start_positions = [
            ['d1', 'f1', 'h1', 'e2', 'g2', 'i2', 'd3', 'f3', 'h3'],  # Player 1 (Red)
            ['l5', 'l7', 'l9', 'k4', 'k6', 'k8', 'j5', 'j7', 'j9'],  # Player 2 (Blue)
            ['e12', 'g12', 'i12', 'd11', 'f11', 'h11', 'e10', 'g10', 'i10'],  # Player 3 (Green)
            ['a4', 'a6', 'a8', 'b5', 'b7', 'b9', 'c4', 'c6', 'c8']]   # Player 4 (Yellow)
        for i, player in enumerate(self.players):
            for pos in start_positions[i]:
                x, y = self.convert_position(pos)
                if x is not None and y is not None:
                    self.board[x][y] = player['symbol']
    def print_board(self):
        #os.system('cls' if os.name == 'nt' else 'clear')
        print("\033[0;37m   A B C D E F G H I J K L")
        print("  +------------------------+")
        
        for row in range(12):
            print(f"{row+1:2}|", end="")
            for col in range(12):
                piece = self.board[row][col]
                color_code = ""
                if piece == 'R' or piece == 'r':
                    color_code = "\033[0;31m"  # Red
                elif piece == 'B' or piece == 'b':
                    color_code = "\033[0;34m"  # Blue
                elif piece == 'G' or piece == 'g':
                    color_code = "\033[0;32m"  # Green
                elif piece == 'Y' or piece == 'y':
                    color_code = "\033[0;33m"  # Yellow
                elif piece == 'X':
                    color_code = "\033[0;37m"  # White for blocked
                
                print(color_code + piece + "\033[0m", end=" ")
            print(f"|{row+1:2}")
        
        print("  +------------------------+")
        print("   A B C D E F G H I J K L")
        
        current_player = self.players[self.current_player_idx]
        print(f"\n{current_player['name']}'s turn ({current_player['symbol']})")
        #player statistics
        for i, player in enumerate(self.players):
            print(f"{player['name']}: {player['pieces']} pieces", end=" | ")
        print()

    def convert_position(self, pos):
        if len(pos) < 2:
            return None, None
        col = pos[0].upper()
        row = pos[1:]
        if col < 'A' or col > 'L' or not row.isdigit():
            return None, None
        x = int(row) - 1
        y = ord(col) - ord('A')
        if 0 <= x < 12 and 0 <= y < 12:
            return x, y
        return None, None

    def get_valid_moves(self, x, y, player_idx=None, board=None):
        if player_idx is None:
            player_idx = self.current_player_idx
        if board is None:
            board = self.board
        player = self.players[player_idx]
        piece = board[x][y]
        moves = []
        if piece not in [player['symbol'], player['king']]:
            return moves
        is_king = (piece == player['king'])
        directions = []
        # Standard movement directions
        if not is_king:
            if player['position'] == 0:  #(Red)
                directions = [(1, -1), (1, 1)] 
            elif player['position'] == 1:  #(Blue)
                directions = [(-1, -1), (1, -1)]  
            elif player['position'] == 2:  #(Green)
                directions = [(-1, -1), (-1, 1)] 
            else:  #(Yellow)
                directions = [(-1, 1), (1, 1)] 
        else:
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]  #kings can move all directions
        
        #mandatory capture rule
        capture_moves = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 12 and 0 <= ny < 12:
                target = board[nx][ny]
                if target != '.' and target != 'X' and self.is_opponent_piece(target, player_idx):
                    nx2, ny2 = x + 2*dx, y + 2*dy
                    if 0 <= nx2 < 12 and 0 <= ny2 < 12 and board[nx2][ny2] == '.':
                        capture_moves.append((nx2, ny2, True))
        if capture_moves:
            return capture_moves
        #regular move
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 12 and 0 <= ny < 12 and board[nx][ny] == '.':
                moves.append((nx, ny, False))
        return moves
    
    def is_opponent_piece(self, piece, player_idx):
        for i, player in enumerate(self.players):
            if i != player_idx and piece in [player['symbol'], player['king']]:
                return True
        return False

    def move_piece(self, x, y, nx, ny, is_capture, player_idx=None):
        if player_idx is None:
            player_idx = self.current_player_idx
        player = self.players[player_idx]
        board = self.board
        piece = board[x][y]
        board[x][y] = '.'
        # King promotion
        if not piece.islower():
            if (player['position'] == 0 and nx == 11) or (player['position'] == 1 and ny == 0) or (player['position'] == 2 and nx == 0) or (player['position'] == 3 and ny == 11):
                piece = player['king']
        board[nx][ny] = piece
        if is_capture:
            cx, cy = (x + nx) // 2, (y + ny) // 2
            captured_piece = board[cx][cy]
            board[cx][cy] = '.'
            #finds which player lost the piece
            for i, p in enumerate(self.players):
                if captured_piece in [p['symbol'], p['king']]:
                    self.players[i]['pieces'] -= 1
                    break
        #additional captures
        if is_capture:
            additional_captures = []
            moves = self.get_valid_moves(nx, ny, player_idx)
            for move in moves:
                if move[2]:
                    additional_captures.append(move)
            if additional_captures:
                return (nx, ny)
        return None

    def get_all_valid_moves(self, player_idx=None, board=None):
        if player_idx is None:
            player_idx = self.current_player_idx
        if board is None:
            board = self.board
        player = self.players[player_idx]
        all_moves = []
        capture_moves = []
        for x in range(12):
            for y in range(12):
                piece = board[x][y]
                if piece in [player['symbol'], player['king']]:
                    moves = self.get_valid_moves(x, y, player_idx, board)
                    for move in moves:
                        nx, ny, is_capture = move
                        if is_capture:
                            capture_moves.append((x, y, nx, ny, True))
                        else:
                            all_moves.append((x, y, nx, ny, False))
        if capture_moves:
            return capture_moves
        return all_moves

    def alpha_beta_search(self, player_idx):
        #filter moves that leave pieces vulnerable
        safe_moves = []
        moves = self.get_all_valid_moves(player_idx)
        for move in moves:
            x, y, nx, ny, _ = move
            new_board, _ = self.ai_move_simulation(move, player_idx, self.board)
            vulnerable = self.count_vulnerable_pieces(new_board, player_idx)
            current_vulnerable = self.count_vulnerable_pieces(self.board, player_idx)
            if vulnerable <= current_vulnerable or move[4]:
                safe_moves.append(move)
        if safe_moves:
            moves = safe_moves
        if not moves:
            return None
        _, best_move = self.max_value(self.board, deepcopy(self.players), self.difficulty, -math.inf, math.inf, player_idx, True)
        if best_move:
            x, y, nx, ny, is_capture = best_move
            new_board, _ = self.ai_move_simulation(best_move, player_idx, self.board)
            vulnerable_after = self.count_vulnerable_pieces(new_board, player_idx)
            current_vulnerable = self.count_vulnerable_pieces(self.board, player_idx)
            if vulnerable_after > current_vulnerable and not is_capture:
                safer_moves = [m for m in moves if not m[4]]  #non-capture moves
                if safer_moves:
                    best_vulnerability = math.inf
                    best_safe_move = None
                    for move in safer_moves:
                        temp_board, _ = self.ai_move_simulation(move, player_idx, self.board)
                        vuln = self.count_vulnerable_pieces(temp_board, player_idx)
                        if vuln < best_vulnerability:
                            best_vulnerability = vuln
                            best_safe_move = move
                    if best_safe_move:
                        return best_safe_move
        return best_move

    def max_value(self, board, players, depth, alpha, beta, player_idx, is_maximizing):
        if depth == 0 or self.is_terminal(board, players, player_idx):
            return self.evaluate(board, players, player_idx), None
        moves = self.get_all_valid_moves(player_idx, board)
        if not moves:
            return -math.inf, None
        best_value = -math.inf
        best_move = None
        for move in moves:
            new_board, new_players = self.ai_move_simulation(move, player_idx, board)
            next_player_idx = (player_idx + 1) % 4
            while new_players[next_player_idx]['pieces'] == 0:
                next_player_idx = (next_player_idx + 1) % 4
            #if this move leads to additional captures then handle them
            x, y, nx, ny, is_capture = move
            if is_capture:
                additional_moves = self.get_valid_moves(nx, ny, player_idx, new_board)
                additional_captures = [m for m in additional_moves if m[2]]
                if additional_captures:
                    additional_move = (nx, ny, additional_captures[0][0], additional_captures[0][1], True)
                    new_board, new_players = self.ai_move_simulation(additional_move, player_idx, new_board)
            if is_maximizing:
                value, _ = self.min_value(new_board, new_players, depth-1, alpha, beta, next_player_idx, not is_maximizing)
            else:
                value, _ = self.max_value(new_board, new_players, depth-1, alpha, beta, next_player_idx, not is_maximizing)
            if value > best_value:
                best_value = value
                best_move = move
                alpha = max(alpha, best_value)
            if best_value >= beta:
                return best_value, best_move
        return best_value, best_move

    def min_value(self, board, players, depth, alpha, beta, player_idx, is_maximizing):
        if depth == 0 or self.is_terminal(board, players, player_idx):
            return self.evaluate(board, players, (player_idx - 1) % 4), None
        moves = self.get_all_valid_moves(player_idx, board)
        if not moves:
            return math.inf, None
        best_value = math.inf
        best_move = None
        for move in moves:
            new_board, new_players = self.ai_move_simulation(move, player_idx, board)
            next_player_idx = (player_idx + 1) % 4
            while new_players[next_player_idx]['pieces'] == 0:
                next_player_idx = (next_player_idx + 1) % 4
            x, y, nx, ny, is_capture = move
            if is_capture:
                additional_moves = self.get_valid_moves(nx, ny, player_idx, new_board)
                additional_captures = [m for m in additional_moves if m[2]]
                if additional_captures:
                    additional_move = (nx, ny, additional_captures[0][0], additional_captures[0][1], True)
                    new_board, new_players = self.ai_move_simulation(additional_move, player_idx, new_board)
            if depth > 1:
                value, _ = self.max_value(new_board, new_players, depth-1, alpha, beta, next_player_idx, not is_maximizing)
            else:
                value = self.evaluate(new_board, new_players, (player_idx - 1) % 4)
            if value < best_value:
                best_value = value
                best_move = move
                beta = min(beta, best_value)
            if best_value <= alpha:
                return best_value, best_move 
        return best_value, best_move

    def evaluate(self, board, players, player_idx):
        player = players[player_idx]
        score = 0
        piece_value = 100
        king_value = 300 
        center_value = 5
        danger_penalty = 150
        king_safety_bonus = 200
        piece_safety_bonus = 20
        opponent_threat_penalty = 50
        player_pieces = 0
        player_kings = 0
        opponent_pieces = 0
        opponent_kings = 0
        for x in range(12):
            for y in range(12):
                piece = board[x][y]
                if piece == player['symbol']:
                    player_pieces += 1
                elif piece == player['king']:
                    player_kings += 1
                elif piece != '.' and piece != 'X':
                    for i, p in enumerate(players):
                        if i != player_idx and piece in [p['symbol'], p['king']]:
                            if piece == p['symbol']:
                                opponent_pieces += 1
                            else:
                                opponent_kings += 1
                            break
        score += (player_pieces * piece_value + player_kings * king_value)
        score -= (opponent_pieces * piece_value * 0.8 + opponent_kings * king_value * 0.8)
        #evaluate board position of piece
        for x in range(12):
            for y in range(12):
                piece = board[x][y]
                if piece == player['symbol']:
                    #piece safety evaluation
                    if self.is_piece_threatened(x, y, player_idx, board):
                        score -= danger_penalty
                    else:
                        score += piece_safety_bonus
                    #advancement bonus
                    if player['position'] == 0:  # Red (bottom)
                        score += x * 2  # Moving up is good
                    elif player['position'] == 2:  # Green (top)
                        score += (11 - x) * 2  # Moving down is good
                    #penalize dangerous positions
                    if self.in_enemy_territory(x, y, player_idx):
                        score -= danger_penalty * 0.5
                elif piece == player['king']:
                    #king safety
                    if self.is_king_in_danger(x, y, player_idx, board):
                        score -= danger_penalty * 2
                    else:
                        score += king_safety_bonus
                    # Center control
                    center_distance = abs(x - 5.5) + abs(y - 5.5)
                    score += (12 - center_distance) * center_value
                elif piece != '.' and piece != 'X':
                    #opponent pieces
                    for i, p in enumerate(players):
                        if i != player_idx and piece in [p['symbol'], p['king']]:
                            #bonus for threatening opponent pieces
                            if self.is_piece_threatened(x, y, i, board):
                                if piece == p['symbol']:
                                    score += piece_value * 0.5
                                else:
                                    score += king_value * 0.5
                            break
        vulnerable_pieces = self.count_vulnerable_pieces(board, player_idx)
        score -= vulnerable_pieces * danger_penalty
        for i in range(4):
            if i != player_idx and players[i]['pieces'] > 0:
                threat_score = self.count_opponent_threats(board, player_idx, i)
                score -= threat_score * opponent_threat_penalty
        piece_diff = player['pieces'] - sum(p['pieces'] for i, p in enumerate(players) if i != player_idx)
        score += piece_diff * piece_value * 0.5  
        return score
    
    def count_opponent_threats(self, board, player_idx, opponent_idx):
        count = 0
        player = self.players[player_idx]
        opponent = self.players[opponent_idx]
        for x in range(12):
            for y in range(12):
                piece = board[x][y]
                if piece in [player['symbol'], player['king']]:
                    #check if any opponent piece can capture this piece
                    for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1)]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < 12 and 0 <= ny < 12:
                            opp_piece = board[nx][ny]
                            if opp_piece in [opponent['symbol'], opponent['king']]:
                                #check if landing spot is empty
                                lx, ly = x - dx, y - dy
                                if 0 <= lx < 12 and 0 <= ly < 12 and board[lx][ly] == '.':
                                    count += 1
                                    break
        return count
    #check if a piece is in danger of being captured next turn
    def is_piece_threatened(self, x, y, player_idx, board):
        for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 12 and 0 <= ny < 12:
                piece = board[nx][ny]
                #opponent piece
                for i, p in enumerate(self.players):
                    if i != player_idx and piece in [p['symbol'], p['king']]:
                        #space
                        nx2, ny2 = x - dx, y - dy
                        if 0 <= nx2 < 12 and 0 <= ny2 < 12 and board[nx2][ny2] == '.':
                            return True
        return False
    #count how many player's pieces are in danger
    def count_vulnerable_pieces(self, board, player_idx):
        count = 0
        for x in range(12):
            for y in range(12):
                piece = board[x][y]
                if piece == self.players[player_idx]['symbol']:
                    if self.is_piece_threatened(x, y, player_idx, board):
                        count += 1
                elif piece == self.players[player_idx]['king']:
                    if self.is_king_in_danger(x, y, player_idx, board):
                        count += 3
        return count

    def is_king_in_danger(self, x, y, player_idx, board):
        for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 12 and 0 <= ny < 12:
                piece = board[nx][ny]
                for i, p in enumerate(self.players):
                    if i != player_idx and piece in [p['symbol'], p['king']]:
                        nx2, ny2 = x - dx, y - dy
                        if 0 <= nx2 < 12 and 0 <= ny2 < 12 and board[nx2][ny2] == '.':
                            return True
        return False

    def in_enemy_territory(self, x, y, player_idx):
        """Check if piece is in enemy territory"""
        player = self.players[player_idx]
        if player['position'] == 0:  #(Red)
            return x < 3  
        elif player['position'] == 1:  #(Blue)
            return y > 8 
        elif player['position'] == 2:  #(Green)
            return x > 8
        else:  #(Yellow)
            return y < 3

    def is_terminal(self, board, players, player_idx):
        active_players = [i for i, p in enumerate(players) if p['pieces'] > 0]
        if len(active_players) <= 1:
            return True
        if not self.get_all_valid_moves(player_idx, board):
            return True  
        return False

    def ai_move_simulation(self, move, player_idx, board):
        x, y, nx, ny, is_capture = move
        new_board = deepcopy(board)
        new_players = deepcopy(self.players)
        player = new_players[player_idx]
        piece = new_board[x][y]
        new_board[x][y] = '.'
        #king promote
        if (not piece.islower() and ((player['direction'] == 1 and nx == 11) or (player['direction'] == -1 and nx == 0))):
            piece = player['king']
        new_board[nx][ny] = piece
        if is_capture:
            cx, cy = (x + nx) // 2, (y + ny) // 2
            captured_piece = new_board[cx][cy]
            new_board[cx][cy] = '.'
            for i, p in enumerate(new_players):
                if captured_piece in [p['symbol'], p['king']]:
                    new_players[i]['pieces'] -= 1
                    break
        return new_board, new_players

    def ai_move(self, player_idx):
        move = self.alpha_beta_search(player_idx)
        if move is None:
            moves = self.get_all_valid_moves(player_idx)
            if moves:
                return moves[0]
        return move

    def check_game_over(self):
        active_players = [p for p in self.players if p['pieces'] > 0]
        
        #human vs ai=end game if human loses all pieces
        if self.game_mode == 2:
            human_players = [p for p in self.players if p['type'] == 'Human']
            if len(human_players) > 0 and human_players[0]['pieces'] == 0:
                return True
        if len(active_players) <= 1:
            return True
        for i, player in enumerate(self.players):
            if player['pieces'] > 0 and not self.get_all_valid_moves(i):
                #check if this player is stuck (game over if only one player left with moves)
                remaining = [p for p in self.players if p['pieces'] > 0 and self.get_all_valid_moves(self.players.index(p))]
                if len(remaining) <= 1:
                    return True
        return False

    def get_winner(self):
        active_players = [p for p in self.players if p['pieces'] > 0]
        if self.game_mode == 2:
            human_players = [p for p in self.players if p['type'] == 'Human']
            if len(human_players) > 0 and human_players[0]['pieces'] == 0:
                ai_players = [p for p in self.players if p['type'] == 'AI']
                if len(ai_players) > 0:
                    return ai_players[0] 
        if len(active_players) == 1:
            return active_players[0]
        return None

    def next_player(self):
        start_idx = (self.current_player_idx + 1) % 4
        for i in range(4):
            next_idx = (start_idx + i) % 4
            if self.players[next_idx]['pieces'] > 0:
                self.current_player_idx = next_idx
                return
        self.current_player_idx = 0

    def play(self):
        #self.setup()
        gui = FourPlayerCheckersGUI(self)
        gui.run()
        while True:
            self.print_board()
            if self.check_game_over():
                winner = self.get_winner()
                if winner:
                    if self.game_mode == 2:
                        human_players = [p for p in self.players if p['type'] == 'Human']
                        if len(human_players) > 0 and human_players[0]['pieces'] == 0:
                            print("\n\nAll your pieces have been captured! You lose!")
                        else:
                            print(f"\n\n{winner['name']} wins!")
                    else:
                        print(f"\n\n{winner['name']} wins!")
                else:
                    print("\n\nGame ended in a draw!")
                break
            current_player = self.players[self.current_player_idx]
            print(f"\nCurrent turn: {current_player['name']} ({current_player['symbol']})")
            if current_player['type'] == "AI":
                print("\nAI is thinking...")
                start_time = time.time()
                move = self.ai_move(self.current_player_idx)
                end_time = time.time()
                if move is None:
                    print(f"{current_player['name']} has no valid moves!")
                    self.next_player()
                    continue
                x, y, nx, ny, is_capture = move
                print(f"{current_player['name']} moves from {chr(y+ord('A'))}{x+1} to {chr(ny+ord('A'))}{nx+1}")
                if is_capture:
                    print(f"Captured piece at {chr((y + ny)//2 + ord('A'))}{(x + nx)//2 + 1}")
                result = self.move_piece(x, y, nx, ny, is_capture)
                #multiple jumps
                while result and is_capture:
                    x, y = result
                    self.print_board()
                    moves = self.get_valid_moves(x, y)
                    capture_moves = [m for m in moves if m[2]]
                    if not capture_moves:
                        break
                    nx, ny, is_capture = capture_moves[0]
                    print(f"{current_player['name']} continues capture to {chr(ny+ord('A'))}{nx+1}")
                    result = self.move_piece(x, y, nx, ny, True)
                
                print(f"AI thinking time: {end_time - start_time:.2f} seconds")
                self.next_player()
            else:
                #human
                moves = self.get_all_valid_moves()
                if not moves:
                    print(f"{current_player['name']} has no valid moves!")
                    self.next_player()
                    continue
                #capture moves
                move_dict = {}
                for move in moves:
                    x, y, nx, ny, is_cap = move
                    if (x, y) not in move_dict:
                        move_dict[(x, y)] = []
                    move_dict[(x, y)].append((nx, ny, is_cap))
                
                capture_pieces = set()
                for move in moves:
                    if move[4]:
                        capture_pieces.add((move[0], move[1]))
                
                if capture_pieces:
                    print("\nYou must make a capture move!")
                    print("Pieces that can capture:", end=" ")
                    for x, y in capture_pieces:
                        print(f"{chr(y+ord('A'))}{x+1}", end=" ")
                    print()
                
                while True:
                    pos = input("\nSelect piece to move (e.g., A3): ")
                    xy = self.convert_position(pos)
                    if xy[0] is not None:
                        x, y = xy
                        piece = self.board[x][y]
                        if piece not in [current_player['symbol'], current_player['king']]:
                            print("That's not your piece!")
                            continue
                        if capture_pieces and (x, y) not in capture_pieces:
                            print("You must select a piece that can capture!")
                            continue
                        if (x, y) in move_dict:
                            available_moves = move_dict[(x, y)]
                            break
                        print("No valid moves for this piece")
                    else:
                        print("Invalid position")
                print("\nAvailable moves:")
                for i, (nx, ny, is_cap) in enumerate(available_moves):
                    print(f"{i+1}: {chr(ny+ord('A'))}{nx+1}", end="")
                    if is_cap:
                        print(" (capture)", end="")
                    print()
                while True:
                    choice = input("Choose move (number): ")
                    if choice.isdigit() and 0 < int(choice) <= len(available_moves):
                        nx, ny, is_capture = available_moves[int(choice)-1]
                        break
                    print("Invalid choice")
                result = self.move_piece(x, y, nx, ny, is_capture)
                #multiple jumps
                while result and is_capture:
                    x, y = result
                    self.print_board()
                    moves = self.get_valid_moves(x, y)
                    capture_moves = [m for m in moves if m[2]]
                    if not capture_moves:
                        break
                    print("\nAdditional captures available:")
                    for i, (nx, ny, _) in enumerate(capture_moves):
                        print(f"{i+1}: {chr(ny+ord('A'))}{nx+1}")
                    while True:
                        choice = input("Choose capture (number): ")
                        if choice.isdigit() and 0 < int(choice) <= len(capture_moves):
                            nx, ny, is_capture = capture_moves[int(choice)-1]
                            break
                        print("Invalid choice")
                    result = self.move_piece(x, y, nx, ny, True)
                self.next_player()

#game = FourPlayerCheckers()
#game.play()