import pygame
import sys
from human_vs_AI_checkers import CheckersGUI, checkers
from four_player_checkers import FourPlayerCheckersGUI, FourPlayerCheckers

def show_menu():
    pygame.init()
    WIDTH, HEIGHT = 600, 400
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Checkers Game Selection")
    #colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    BLUE = (70, 130, 180)      #steel blue
    GREEN = (34, 139, 34)      #forest green
    BACKGROUND = (240, 240, 240)  #light gray
    #fonts
    title_font = pygame.font.SysFont('Arial', 48, bold=True)
    button_font = pygame.font.SysFont('Arial', 28)
    subtitle_font = pygame.font.SysFont('Arial', 24)
    #buttons
    button1 = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 50, 300, 50)
    button2 = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 50, 300, 50)
    clock = pygame.time.Clock()
    while True:
        WIN.fill(BACKGROUND)
        #title
        title = title_font.render("CHECKERS GAME", True, BLACK)
        title_rect = title.get_rect(center=(WIDTH//2, HEIGHT//4))
        WIN.blit(title, title_rect)
        #subtitle
        subtitle = subtitle_font.render("Select Game Mode:", True, BLACK)
        subtitle_rect = subtitle.get_rect(center=(WIDTH//2, HEIGHT//3))
        WIN.blit(subtitle, subtitle_rect)
        #button for mode options
        pygame.draw.rect(WIN,BLUE,button1)
        pygame.draw.rect(WIN,GREEN,button2)
        #text for buttons
        text1 = button_font.render("2-Player Checkers", True, WHITE)
        text1_rect = text1.get_rect(center=button1.center)
        WIN.blit(text1, text1_rect)
        text2 = button_font.render("4-Player Checkers", True, WHITE)
        text2_rect = text2.get_rect(center=button2.center)
        WIN.blit(text2, text2_rect)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if button1.collidepoint(mouse_pos):
                    pygame.quit()
                    return "2player"
                if button2.collidepoint(mouse_pos):
                    pygame.quit()
                    return "4player"
        clock.tick(60)
def main():
    while True:
        game_type=show_menu()
        if game_type=="2player":
            game=checkers()
            game.show_setup_dialog()
            gui=CheckersGUI(game)
            gui.run()
            
        elif game_type=="4player":
            game=FourPlayerCheckers()
            game.show_setup_dialog()
            gui=FourPlayerCheckersGUI(game)
            gui.run()
if __name__ == "__main__":
    main()