import math
import time
from copy import deepcopy
import pygame
import sys

class CheckersGUI:
    def __init__(self, game):
        self.game = game
        pygame.init()
        self.WIDTH, self.HEIGHT = 800, 800
        self.WIN = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Checkers")
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BROWN = (139, 69, 19)
        self.LIGHT_BROWN = (222, 184, 135)
        self.RED = (255, 0, 0)
        self.BLUE = (0, 0, 255)
        self.GREEN = (0, 255, 0)
        self.YELLOW = (255, 255, 0)
        self.GRAY = (128, 128, 128)
        self.font = pygame.font.SysFont('Arial', 24)
        self.SQUARE_SIZE = self.WIDTH // 8
        self.PIECE_RADIUS = self.SQUARE_SIZE // 2 - 10
        self.KING_RADIUS = self.PIECE_RADIUS - 5
        self.selected_piece = None
        self.valid_moves = []
        
    def draw_board(self):
        self.WIN.fill(self.BROWN)
        #squares
        for row in range(8):
            for col in range(8):
                if (row + col) % 2 == 0:
                    pygame.draw.rect(self.WIN, self.LIGHT_BROWN, (col * self.SQUARE_SIZE, row * self.SQUARE_SIZE, self.SQUARE_SIZE, self.SQUARE_SIZE))
        #pieces
        for row in range(8):
            for col in range(8):
                piece = self.game.board[row][col]
                if piece != ' ':
                    x = col * self.SQUARE_SIZE + self.SQUARE_SIZE // 2
                    y = row * self.SQUARE_SIZE + self.SQUARE_SIZE // 2
                    if piece == self.game.player1['symbol']:
                        color = self.RED
                        pygame.draw.circle(self.WIN, color, (x, y), self.PIECE_RADIUS)
                    elif piece == self.game.player1['king']:
                        color = self.RED
                        pygame.draw.circle(self.WIN, color, (x, y), self.PIECE_RADIUS)
                        pygame.draw.circle(self.WIN, self.YELLOW, (x, y), self.KING_RADIUS)
                    elif piece == self.game.player2['symbol']:
                        color = self.BLUE
                        pygame.draw.circle(self.WIN, color, (x, y), self.PIECE_RADIUS)
                    elif piece == self.game.player2['king']:
                        color = self.BLUE
                        pygame.draw.circle(self.WIN, color, (x, y), self.PIECE_RADIUS)
                        pygame.draw.circle(self.WIN, self.YELLOW, (x, y), self.KING_RADIUS)
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
        turn_text = f"{self.game.current_player['name']}'s turn ({self.game.current_player['symbol']})"
        p1_text = f"{self.game.player1['name']}: {self.game.player1['pieces']} pieces"
        p2_text = f"{self.game.player2['name']}: {self.game.player2['pieces']} pieces"
        turn_surface = self.font.render(turn_text, True, self.BLACK)
        p1_surface = self.font.render(p1_text, True, self.RED)
        p2_surface = self.font.render(p2_text, True, self.BLUE)
        self.WIN.blit(turn_surface, (10, 10))
        self.WIN.blit(p1_surface, (10, 40))
        self.WIN.blit(p2_surface, (10, 70))
        pygame.display.update()
    
    def get_row_col_from_pos(self, pos):
        x, y = pos
        row = y // self.SQUARE_SIZE
        col = x // self.SQUARE_SIZE
        return row, col
    
    def handle_click(self, row, col):
        if self.game.current_player['name'] == "AI":
            return
        piece = self.game.board[row][col]
        
        #capture moves
        capture_moves = []
        for x in range(8):
            for y in range(8):
                if self.game.board[x][y] in [self.game.current_player['symbol'], self.game.current_player['king']]:
                    moves = self.game.palyer_valid_moves(x, y)
                    capture_moves.extend([(x, y, *move) for move in moves if move[2]])  # Only capture moves
        if capture_moves:
            if piece in [self.game.current_player['symbol'], self.game.current_player['king']]:
                piece_capture_moves = [m for m in capture_moves if m[0] == row and m[1] == col]
                if piece_capture_moves:
                    self.selected_piece = (row, col)
                    self.valid_moves = [m[2:] for m in piece_capture_moves]
                elif self.selected_piece:
                    return
            #selected a piece and choosing a capture move
            elif self.selected_piece:
                selected_row, selected_col = self.selected_piece
                for move in self.valid_moves:
                    if move[0] == row and move[1] == col:
                        result = self.game.movement(selected_row, selected_col, row, col, move[2])
                        if result:
                            x, y = result
                            self.selected_piece = (x, y)
                            self.valid_moves = [m for m in self.game.palyer_valid_moves(x, y) if m[2]]
                        else:
                            self.selected_piece = None
                            self.valid_moves = []
                            self.game.switch_player()
                        return
        else:
            #normal move logic when no captures are available
            if self.selected_piece:
                selected_row, selected_col = self.selected_piece
                for move in self.valid_moves:
                    if move[0] == row and move[1] == col:
                        result = self.game.movement(selected_row, selected_col, row, col, move[2])
                        if result:
                            x, y = result
                            self.selected_piece = (x, y)
                            self.valid_moves = [m for m in self.game.palyer_valid_moves(x, y) if m[2]]
                        else:
                            self.selected_piece = None
                            self.valid_moves = []
                            self.game.switch_player()
                        return
                if piece in [self.game.current_player['symbol'], self.game.current_player['king']]:
                    self.selected_piece = (row, col)
                    self.valid_moves = self.game.palyer_valid_moves(row, col)
                else:
                    self.selected_piece = None
                    self.valid_moves = []
            else:
                if piece in [self.game.current_player['symbol'], self.game.current_player['king']]:
                    self.selected_piece = (row, col)
                    self.valid_moves = self.game.palyer_valid_moves(row, col)
    
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
        ai_thinking = False
        ai_move_start_time = 0
        while True:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if not ai_thinking and self.game.current_player['name'] != "AI":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pos = pygame.mouse.get_pos()
                        row, col = self.get_row_col_from_pos(pos)
                        if 0 <= row < 8 and 0 <= col < 8:
                            self.handle_click(row, col)
                            if self.game.current_player['name'] == "AI":
                                ai_thinking = True
                                ai_move_start_time = time.time()
            #ai move
            if ai_thinking and not self.game.check_game_end():
                current_time = time.time()
                # Wait 0.5 seconds before making ai move
                if current_time - ai_move_start_time >= 0.5:
                    move = self.game.get_ai_move()
                    if move:
                        x, y, nx, ny, is_capture = move
                        result = self.game.movement(x, y, nx, ny, is_capture)
                        #handle multiple jumps
                        while result and is_capture:
                            x, y = result
                            moves = self.game.palyer_valid_moves(x, y)
                            capture_moves = [m for m in moves if m[2]]
                            if not capture_moves:
                                break
                            nx, ny, is_capture = capture_moves[0]
                            result = self.game.movement(x, y, nx, ny, True)
                    self.game.switch_player()
                    ai_thinking = False
            self.draw_board()
            #game end
            if self.game.check_game_end():
                if self.game.player1['pieces'] == 0:
                    self.show_message(f"{self.game.player2['name']} wins!")
                elif self.game.player2['pieces'] == 0:
                    self.show_message(f"{self.game.player1['name']} wins!")
                else:
                    self.show_message("Game ended in a draw!")
                pygame.time.delay(3000)
                return
class checkers:
    def __init__(self):
        self.board=[[' ' for _ in range(8)] for _ in range(8)]
        self.player1={'name':"Human",'symbol':'X','king':'k','pieces':12, 'direction':1}
        self.player2={'name': "AI",'symbol':'O','king':'K','pieces': 12,'direction':-1}
        self.current_player=None
        self.opponent=None
        self.difficulty=3
        
    def show_setup_dialog(self):
        pygame.init()
        WIDTH, HEIGHT = 500, 400
        WIN = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Checkers Setup")
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        GRAY = (200, 200, 200)
        BLUE = (70, 130, 180)
        GREEN = (34, 139, 34)
        RED = (255, 0, 0)
        title_font = pygame.font.SysFont('Arial', 32, bold=True)
        font = pygame.font.SysFont('Arial', 24)
        mode = None
        ai_difficulty = 3
        player1_name = ""
        player2_name = ""
        active_input = None
        error_message = ""
        start_active = False
        mode_text = font.render("Select Game Mode:", True, BLACK)
        human_button = pygame.Rect(50, 100, 180, 40)
        ai_button = pygame.Rect(270, 100, 180, 40)
        name1_text = font.render("Player 1 Name:", True, BLACK)
        name2_text = font.render("Player 2 Name:", True, BLACK)
        name1_input = pygame.Rect(200, 160, 200, 32)
        name2_input = pygame.Rect(200, 210, 200, 32)
        difficulty_text = font.render("AI Difficulty (1-5):", True, BLACK)
        difficulty_slider = pygame.Rect(200, 260, 200, 20)
        slider_knob = pygame.Rect(200 + (ai_difficulty-1)*50, 255, 10, 30)
        start_button = pygame.Rect(WIDTH//2 - 75, HEIGHT - 60, 150, 40)
        clock = pygame.time.Clock()
        running = True
        while running:
            if mode == "human":
                start_active = bool(player1_name.strip() and player2_name.strip())
            elif mode == "ai":
                start_active = True
            else:
                start_active = False
            WIN.fill(WHITE)
            title = title_font.render("Checkers Setup", True, BLACK)
            WIN.blit(title, (WIDTH//2 - title.get_width()//2, 20))
            if error_message:
                error_surface = font.render(error_message, True, RED)
                WIN.blit(error_surface, (WIDTH//2 - error_surface.get_width()//2, HEIGHT - 100))
            WIN.blit(mode_text, (50, 70))
            pygame.draw.rect(WIN, GREEN if mode == "human" else GRAY, human_button, border_radius=5)
            human_label = font.render("Human vs Human", True, BLACK)
            WIN.blit(human_label, (human_button.x + 10, human_button.y + 10))
            
            pygame.draw.rect(WIN, BLUE if mode == "ai" else GRAY, ai_button, border_radius=5)
            ai_label = font.render("Human vs AI", True, BLACK)
            WIN.blit(ai_label, (ai_button.x + 40, ai_button.y + 10))
            
            #player names
            if mode == "human":
                WIN.blit(name1_text, (50, 165))
                pygame.draw.rect(WIN, BLACK if active_input == "player1" else GRAY, name1_input, 2, border_radius=3)
                name1_surface = font.render(player1_name, True, BLACK)
                WIN.blit(name1_surface, (name1_input.x + 5, name1_input.y + 5))
                
                WIN.blit(name2_text, (50, 215))
                pygame.draw.rect(WIN, BLACK if active_input == "player2" else GRAY, name2_input, 2, border_radius=3)
                name2_surface = font.render(player2_name, True, BLACK)
                WIN.blit(name2_surface, (name2_input.x + 5, name2_input.y + 5))
            
            #ai difficulty
            elif mode == "ai":
                WIN.blit(difficulty_text, (50, 265))
                pygame.draw.rect(WIN, GRAY, difficulty_slider, border_radius=10)
                pygame.draw.rect(WIN, BLUE, slider_knob, border_radius=5)
                difficulty_value = font.render(str(ai_difficulty), True, BLACK)
                WIN.blit(difficulty_value, (difficulty_slider.x + difficulty_slider.width + 10, difficulty_slider.y))
                
            pygame.draw.rect(WIN, GREEN if start_active else GRAY, start_button, border_radius=5)
            start_label = font.render("Start Game", True, BLACK)
            WIN.blit(start_label, (start_button.x + 30, start_button.y + 10))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    error_message = ""
                    #check mode buttons
                    if human_button.collidepoint(pos):
                        mode = "human"
                        active_input = None
                    elif ai_button.collidepoint(pos):
                        mode = "ai"
                        active_input = None
                    #check name inputs
                    elif mode == "human":
                        if name1_input.collidepoint(pos):
                            active_input = "player1"
                        elif name2_input.collidepoint(pos):
                            active_input = "player2"
                        else:
                            active_input = None
                    #difficulty slider
                    elif mode == "ai" and difficulty_slider.collidepoint(pos):
                        ai_difficulty = min(5, max(1, round((pos[0] - difficulty_slider.x) / 50) + 1))
                        slider_knob.x = difficulty_slider.x + (ai_difficulty-1)*50
                    #start button
                    if start_button.collidepoint(pos):
                        if start_active:
                            if mode == "human":
                                self.player1 = {
                                    'name': player1_name.strip(),
                                    'symbol': 'X',
                                    'king': 'k',
                                    'pieces': 12,
                                    'direction': 1
                                }
                                self.player2 = {
                                    'name': player2_name.strip(),
                                    'symbol': 'O',
                                    'king': 'K',
                                    'pieces': 12,
                                    'direction': -1
                                }
                                self.current_player = self.player1
                                self.opponent = self.player2
                                self.initialize_board()
                                running = False
                            elif mode == "ai":
                                self.player1 = {
                                    'name': "Human",
                                    'symbol': 'X',
                                    'king': 'k',
                                    'pieces': 12,
                                    'direction': 1
                                }
                                self.player2 = {
                                    'name': "AI",
                                    'symbol': 'O',
                                    'king': 'K',
                                    'pieces': 12,
                                    'direction': -1
                                }
                                self.difficulty = ai_difficulty + 2
                                self.current_player = self.player1
                                self.opponent = self.player2
                                self.initialize_board()
                                running = False
                        else:
                            error_message = "Please complete all fields" if mode == "human" else "Please select a mode"
                elif event.type == pygame.KEYDOWN and mode == "human" and active_input:
                    if event.key == pygame.K_RETURN:
                        active_input = None
                    elif event.key == pygame.K_BACKSPACE:
                        if active_input == "player1":
                            player1_name = player1_name[:-1]
                        else:
                            player2_name = player2_name[:-1]
                    else:
                        if len((player1_name if active_input == "player1" else player2_name)) < 10:
                            if active_input == "player1":
                                player1_name += event.unicode
                            else:
                                player2_name += event.unicode
            clock.tick(60)
        pygame.quit()
    
    def setup(self):
        print("\033[0;32m\t\t\t\t\tCHECKERS GAME\033[0m")
        a=input("\033[0;34mPlay against AI or not? (y/n): \033[0m").lower()
        if a=='n':
            self.player1['name']=input("\033[0;34mEnter name of player 1: \033[0m")
            self.player2['name']=input("\033[0;34mEnter name of player 2: \033[0m")
            while True:
                print("\033[0;35m\nCHOOSE SYMBOLS (X/O)\033[0m")
                p1_sym=input(f"{self.player1['name']}: ").upper()
                p2_sym=input(f"{self.player2['name']}: ").upper()
                if p1_sym in ['X', 'O'] and p2_sym in ['X', 'O'] and p1_sym!=p2_sym:
                    self.player1['symbol']=p1_sym
                    self.player2['symbol']=p2_sym
                    self.player1['king']='k'
                    self.player2['king']='K'
                    break
                print("Invalid symbols. Please choose X or O only")
        else:
            self.player1['name']="Human"
            self.player2['name']="AI"
            self.player1['symbol']='X'
            self.player2['symbol']='O'
            self.player1['king']='k'
            self.player2['king']='K'
            while True: #ai Difficluty
                try:
                    level=int(input("Select AI difficulty (1-5, 3 is default): "))
                    if 1<=level<=5:
                        self.difficulty=level+2
                        break
                    print("Please enter a number between 1 and 5")
                except ValueError:
                    print("Invalid input. Please enter a number.")
        self.initialize_board()
        self.current_player=self.player1
        self.opponent=self.player2
        
    def initialize_board(self):
        for row in range(3):
            for col in range(8):
                if (row+col)%2==1:
                    self.board[row][col]=self.player1['symbol']
        for row in range(5,8):
            for col in range(8):
                if (row+col)%2==1:
                    self.board[row][col]=self.player2['symbol']
                    
    def print_board(self):
        print("\033[0;37m  A B C D E F G H")
        print(" +-----------------+")
        for row in range(8):
            print(f"{row+1}|", end="")
            for col in range(8):
                piece=self.board[row][col]
                if piece==self.player1['symbol'] or piece==self.player1['king']:
                    print("\033[0;33m" + piece + "\033[0m", end=" ")
                elif piece==self.player2['symbol'] or piece==self.player2['king']:
                    print("\033[0;31m"+piece+"\033[0m",end=" ")
                else:
                    print(piece,end=" ")
            print(f"|{row+1}")
        print(" +-----------------+")
        print("  A B C D E F G H")
        print(f"\n{self.current_player['name']}'s turn ({self.current_player['symbol']})")
        print(f"Pieces: {self.player1['name']} {self.player1['pieces']} vs {self.player2['name']} {self.player2['pieces']}")
    
    def convert_position(self,pos):
        if len(pos)!=2:
            return None
        col=pos[0].upper()
        row=pos[1]
        if col<'A' or col>'H' or not row.isdigit():
            return None
        x = int(row)-1
        y = ord(col)-ord('A')
        if 0<=x<8 and 0<=y<8:
            return (x,y)
        return None
    
    def palyer_valid_moves(self, x, y, player=None, opponent=None, board=None):
        if player is None:
            player=self.current_player
            opponent=self.opponent
            board=self.board
        moves=[]
        piece=board[x][y]
        is_king=(piece==player['king'])
        directions=[]
        if not is_king:
            directions = [(player['direction'], -1), (player['direction'], 1)]
        else:
            directions = [(1, -1), (1, 1), (-1, -1), (-1, 1)]
        for dx, dy in directions:
            nx,ny=x+dx,y+dy
            if 0<=nx<8 and 0<=ny<8:
                if board[nx][ny] == ' ':
                    moves.append((nx, ny, False))
                elif board[nx][ny] in [opponent['symbol'], opponent['king']]:
                    nx2,ny2=x+2*dx,y+2*dy
                    if 0<=nx2<8 and 0<=ny2<8 and board[nx2][ny2]==' ':
                        moves.append((nx2,ny2,True))
        return moves
    
    def ai_valid_moves(self,player=None,opponent=None,board=None):
        if player is None:
            player=self.current_player
            opponent=self.opponent
            board=self.board
        all_moves=[]
        capture_moves=[]
        for x in range(8):
            for y in range(8):
                piece = board[x][y]
                if piece in [player['symbol'], player['king']]:
                    moves=self.palyer_valid_moves(x,y,player,opponent,board)
                    for move in moves:
                        nx, ny, is_capture = move
                        if is_capture:
                            capture_moves.append((x,y,nx,ny,True))
                        else:
                            all_moves.append((x,y,nx,ny,False))
        if capture_moves:
            return capture_moves
        return all_moves
    
    def movement(self,x,y,nx,ny,is_capture,player=None,opponent=None,board=None):
        if player is None:
            player=self.current_player
            opponent=self.opponent
            board=self.board
        piece=board[x][y]
        board[x][y]=' '
        #king promote
        if (nx==0 and player==self.player2) or (nx==7 and player==self.player1):
            piece=player['king']
        board[nx][ny] = piece
        if is_capture:
            cx,cy=(x+nx)//2, (y+ny)//2
            board[cx][cy]=' '
            opponent['pieces']-=1
        #jump captures
        if is_capture:
            additional_captures=[]
            moves=self.palyer_valid_moves(nx,ny,player,opponent,board)
            for move in moves:
                _, _, additional_capture=move
                if additional_capture:
                    additional_captures.append(move)
            if additional_captures:
                return (nx,ny)
        return None

    def ai_move_simulation(self,move,player,opponent,board):
        x,y,nx,ny,is_capture=move
        new_board=deepcopy(board)
        new_player=deepcopy(player)
        new_opponent=deepcopy(opponent)
        piece=new_board[x][y]
        new_board[x][y]=' '
        #king promotion
        if (nx==0 and player==self.player2) or (nx==7 and player==self.player1):
            piece=new_player['king']
        new_board[nx][ny]=piece
        if is_capture:
            cx,cy=(x+nx)//2, (y+ny)//2
            new_board[cx][cy]=' '
            new_opponent['pieces']-=1
        return new_board, new_player, new_opponent
    
    def count_opponent_captures(self, board, player, opponent):
        capture_count=0
        #opponent moves check for decision making
        for x in range(8):
            for y in range(8):
                piece=board[x][y]
                if piece in [opponent['symbol'], opponent['king']]:
                    moves=self.palyer_valid_moves(x,y,opponent,player,board)
                    for move in moves:
                        if move[2]:  #if capture
                            capture_count+=1
                            nx, ny, _ = move #for jump
                            temp_board=deepcopy(board) #move_simulate
                            temp_board[x][y]=' '
                            temp_board[(x+nx)//2][(y+ny)//2]=' '
                            temp_board[nx][ny]=piece
                            #check of jump capture from new position
                            additional_moves=self.palyer_valid_moves(nx,ny,opponent,player,temp_board)
                            for add_move in additional_moves:
                                if add_move[2]:
                                    capture_count+=1
        return capture_count #returns score for ai
    
    def get_scores(self, player, opponent, board):
        score=0
        piece_value=10
        king_value=30
        capture_penalty=5
        for x in range(8): #evaluating the board
            for y in range(8):
                piece=board[x][y]
                if piece==player['symbol']:
                    score+=piece_value
                    if player==self.player1:
                        score+=(7-x)*0.5  #player 1 moves downward
                    else:
                        score+=x*0.5  #player 2 moves upward
                elif piece==player['king']:
                    score+=king_value
                elif piece==opponent['symbol']:
                    score-=piece_value
                    if opponent==self.player1:
                        score-=(7-x)*0.5
                    else:
                        score-=x*0.5
                elif piece==opponent['king']:
                    score-=king_value
        score+=(player['pieces']-opponent['pieces'])*2
        #center positions score
        center_squares=[(3,3),(3,4),(4,3),(4,4)]
        for x, y in center_squares:
            piece=board[x][y]
            if piece == player['symbol']:
                score+=1
            elif piece == player['king']:
                score+=2
            elif piece == opponent['symbol']:
                score-=1
            elif piece == opponent['king']:
                score-=2
        opponent_captures=self.count_opponent_captures(board,player,opponent) #opponent captures minimizer
        score-=opponent_captures*capture_penalty
        return score
    
    def minmax(self, board, depth, alpha, beta, maximizing_player, player, opponent, forced_capture=True):
        if depth==0 or self.check_game_end(player,opponent,board):
            return self.get_scores(player,opponent,board)
        moves=self.ai_valid_moves(player,opponent,board)
        
        if maximizing_player:
            max_eval=-math.inf
            for move in moves:
                new_board,new_player,new_opponent=self.ai_move_simulation(move, player, opponent, board)
                eval=self.minmax(new_board, depth-1, alpha, beta, False, new_opponent, new_player, forced_capture)
                max_eval=max(max_eval, eval)
                alpha=max(alpha, eval)
                if beta<=alpha:
                    break
            return max_eval
        else:
            min_eval=math.inf
            for move in moves:
                new_board,new_player,new_opponent=self.ai_move_simulation(move,player,opponent,board)
                eval=self.minmax(new_board, depth-1, alpha, beta, True, new_opponent, new_player, forced_capture)
                min_eval=min(min_eval,eval)
                beta=min(beta,eval)
                if beta<=alpha:
                    break
            return min_eval
    #to select best move for ai from all possibilities
    def get_ai_move(self):
        best_move=None
        best_value=-math.inf
        alpha=-math.inf
        beta=math.inf
        moves=self.ai_valid_moves(self.current_player,self.opponent,self.board)
        if not moves:
            return None
        
        for move in moves:
            new_board,new_player,new_opponent=self.ai_move_simulation(move, self.current_player, self.opponent, self.board)
            move_value=self.minmax(new_board, self.difficulty, alpha, beta, False, new_opponent, new_player)
            if move_value>best_value:
                best_value=move_value
                best_move=move
            alpha=max(alpha, best_value)
        return best_move

    def check_game_end(self,player=None,opponent=None,board=None):
        if player is None:
            player=self.current_player
            opponent=self.opponent
            board=self.board
        player_pieces=0
        opponent_pieces=0
        for row in board:
            for piece in row:
                if piece in [player['symbol'], player['king']]:
                    player_pieces+=1
                elif piece in [opponent['symbol'], opponent['king']]:
                    opponent_pieces+=1
        if player_pieces==0 or opponent_pieces==0:
            return True
        if not self.ai_valid_moves(player,opponent,board):
            return True
        return False
    
    def switch_player(self):
        self.current_player,self.opponent=self.opponent,self.current_player
    
    def play(self):
        #self.setup()
        gui = CheckersGUI(self)
        gui.run()
        while True:
            self.print_board()
            if self.check_game_end():
                if self.player1['pieces']==0:
                    print(f"\n\n{self.player2['name']} wins!")
                elif self.player2['pieces']==0:
                    print(f"\n\n{self.player1['name']} wins!")
                else:
                    print("\n\nGame ended in a draw!")
                break
            if self.current_player['name']!="AI": #human
                capture_moves=[]
                all_moves=[]
                for x in range(8):
                    for y in range(8):
                        piece=self.board[x][y]
                        if piece in [self.current_player['symbol'], self.current_player['king']]:
                            moves=self.palyer_valid_moves(x, y)
                            for move in moves:
                                if move[2]:  #if it is a capture move
                                    capture_moves.append((x,y,move[0],move[1],True))
                                else:
                                    all_moves.append((x,y,move[0],move[1],False))
                if capture_moves:
                    print("\nYou must make a capture move!")
                    capture_pieces = set() #sees capture moves availability
                    for move in capture_moves:
                        x, y = move[0], move[1]
                        capture_pieces.add((x, y))
                    print("Pieces that can capture:", end=" ")
                    for x, y in capture_pieces:
                        print(f"{chr(y+ord('A'))}{x+1}", end=" ")
                    print()
                    while True:
                        pos = input("\nSelect piece to move (e.g., A3): ")
                        xy = self.convert_position(pos)
                        if xy:
                            x, y = xy
                            #check if selected piece has capture moves
                            piece_capture_moves = [m for m in capture_moves if m[0]==x and m[1] == y]
                            if piece_capture_moves:
                                moves = piece_capture_moves
                                break
                            print(f"Selected piece doesn't have capture moves. Choose from these pieces: {', '.join([f'{chr(y+ord('A'))}{x+1}' for x, y in capture_pieces])}")
                        else:
                            print("Invalid position")
                    while True:
                        print("\nValid capture moves:", end=" ")
                        for i, (_, _, nx, ny, _) in enumerate(moves):
                            print(f"{i+1}:{chr(ny+ord('A'))}{nx+1}", end=" ")
                        a=input("\nChoose capture move (number): ")
                        if a.isdigit() and 0<int(a)<=len(moves):
                            x,y,nx,ny,is_capture=moves[int(a)-1]
                            #make the capture move
                            result=self.movement(x, y, nx, ny, is_capture)
                            break
                        print("Invalid move")      
                else:
                    while True:
                        pos=input("\nSelect piece to move (e.g., A3): ")
                        xy=self.convert_position(pos)
                        if xy and self.board[xy[0]][xy[1]] in [self.current_player['symbol'], self.current_player['king']]:
                            x,y=xy
                            moves=self.palyer_valid_moves(x, y)
                            if moves:
                                break
                            print("No valid moves for this piece")
                        else:
                            print("Invalid position")
                    
                    while True:
                        print("\nValid moves:", end=" ")
                        for i, (nx, ny, _) in enumerate(moves):
                            print(f"{i+1}:{chr(ny+ord('A'))}{nx+1}", end=" ")
                        a=input("\nChoose move (number): ")
                        if a.isdigit() and 0<int(a)<=len(moves):
                            nx,ny,is_capture=moves[int(a)-1]
                            break
                        print("Invalid move")
                    result = self.movement(x,y,nx,ny,is_capture)
                    #additional jump captures
                    while result and is_capture:
                        x,y=result
                        self.print_board()
                        moves=self.palyer_valid_moves(x, y)
                        capture_moves=[m for m in moves if m[2]]  #only capture moves
                        if not capture_moves:
                            break
                        #get move destination if human wants to do next capture
                        while True:
                            print("\nAdditional capture available:",end=" ")
                            for i, (nx, ny, _) in enumerate(capture_moves):
                                print(f"{i+1}:{chr(ny+ord('A'))}{nx+1}",end=" ")
                            a = input("\nChoose capture (number): ")
                            if a.isdigit() and 0<int(a)<=len(capture_moves):
                                nx, ny,is_capture=capture_moves[int(a)-1]
                                break
                            print("Invalid move")
                        result = self.movement(x, y, nx, ny, is_capture)
            else: #AI
                print("\nAI is thinking...")
                start_time=time.time()
                move=self.get_ai_move()
                end_time = time.time()
                if move is None:
                    print("AI has no valid moves!")
                    self.switch_player()
                    continue
                x, y,nx,ny,is_capture = move
                print(f"AI moves from {chr(y+ord('A'))}{x+1} to {chr(ny+ord('A'))}{nx+1}")
                if is_capture:
                    print(f"Captured piece at {chr((y + ny)//2+ord('A'))}{(x+nx)//2+1}")
                result = self.movement(x, y, nx, ny, is_capture)
                #additional jump captures
                while result and is_capture:
                    x, y = result
                    moves = self.palyer_valid_moves(x, y)
                    capture_moves = [m for m in moves if m[2]]  # Only capture moves
                    if not capture_moves:
                        break
                    move=capture_moves[0]
                    nx,ny,is_capture=move
                    print(f"AI continues capture to {chr(ny+ord('A'))}{nx+1}")
                    result=self.movement(x,y,nx,ny,is_capture)
                print(f"AI thinking time: {end_time-start_time} seconds")
            self.switch_player()
#game=checkers()
#game.play()
