# import pygame
# import math
# import cv2
# import mediapipe as mp

# # Definir os discos
# initial_black_disc = {
#     "pos": [WIDTH // 2, HEIGHT // 2],
#     "radius": 30,
#     "velocity": [3, 3],
# }
# initial_red_disc = {
#     "pos": [100, HEIGHT // 2],
#     "radius": 45,
#     "velocity": [0, 2],
# }  # Disco vermelho
# initial_blue_disc = {
#     "pos": [WIDTH - 100, HEIGHT // 2],
#     "radius": 45,
#     "velocity": [0, 2],
# }  # Disco azul

# black_disc = initial_black_disc.copy()
# red_disc = initial_red_disc.copy()
# blue_disc = initial_blue_disc.copy()

# # Inicializa o MediaPipe
# mp_hands = mp.solutions.hands
# mp_drawing = mp.solutions.drawing_utils

# # Configurar o detector de mãos
# hands = mp_hands.Hands()
# cap = cv2.VideoCapture(0)

# # Variável para controlar a execução do jogo
# running = True


# # Função para verificar colisão circular
# def check_collision_circle(disc1, disc2):
#     dist = math.hypot(
#         disc1["pos"][0] - disc2["pos"][0], disc1["pos"][1] - disc2["pos"][1]
#     )
#     return dist < disc1["radius"] + disc2["radius"]


# # Função para refletir o movimento do disco com base na colisão
# def reflect_velocity(moving_disc, stationary_disc):
#     dx = moving_disc["pos"][0] - stationary_disc["pos"][0]
#     dy = moving_disc["pos"][1] - stationary_disc["pos"][1]
#     distance = math.hypot(dx, dy)
#     if distance == 0:
#         return  # Evitar divisão por zero
#     nx, ny = dx / distance, dy / distance  # Vetor normalizado
#     dot_product = moving_disc["velocity"][0] * nx + moving_disc["velocity"][1] * ny
#     moving_disc["velocity"][0] -= 2 * dot_product * nx
#     moving_disc["velocity"][1] -= 2 * dot_product * ny


# # Função para verificar colisão com bordas e corrigir sobreposição
# def check_boundary_collision(disc, velocity, boundaries):
#     if (
#         disc["pos"][0] - disc["radius"] < 0
#     ):  # Colisão com a borda esquerda da área de jogo
#         disc["pos"][0] = 0 + disc["radius"]  # Reposicionar para dentro da borda
#         velocity[0] = abs(velocity[0])  # Garantir que a velocidade vá para a direita
#     if (
#         disc["pos"][0] + disc["radius"] > boundaries.right
#     ):  # Colisão com a borda direita da área de jogo
#         disc["pos"][0] = (
#             boundaries.right - disc["radius"]
#         )  # Reposicionar para dentro da borda
#         velocity[0] = -abs(velocity[0])  # Garantir que a velocidade vá para a esquerda
#     if disc["pos"][1] - disc["radius"] < 0:  # Colisão com a borda superior
#         disc["pos"][1] = 0 + disc["radius"]  # Reposicionar para dentro da borda
#         velocity[1] = abs(velocity[1])  # Garantir que a velocidade vá para baixo
#     if (
#         disc["pos"][1] + disc["radius"] > boundaries.bottom
#     ):  # Colisão com a borda inferior
#         disc["pos"][1] = (
#             boundaries.bottom - disc["radius"]
#         )  # Reposicionar para dentro da borda
#         velocity[1] = -abs(velocity[1])  # Garantir que a velocidade vá para cima
#     return velocity


# # Função para corrigir a sobreposição após a colisão
# def correct_overlap(disc1, disc2):
#     dx = disc1["pos"][0] - disc2["pos"][0]
#     dy = disc1["pos"][1] - disc2["pos"][1]
#     distance = math.hypot(dx, dy)
#     if distance == 0:
#         return  # Evitar divisão por zero
#     overlap = disc1["radius"] + disc2["radius"] - distance
#     if overlap > 0:
#         move_x = (dx / distance) * overlap / 2  # Dividir o movimento entre os dois
#         move_y = (dy / distance) * overlap / 2
#         disc1["pos"][0] += move_x
#         disc1["pos"][1] += move_y
#         disc2["pos"][0] -= move_x
#         disc2["pos"][1] -= move_y


# # Função para movimentar discos vermelhos verticalmente
# def move_red_discs(disc):
#     disc["pos"][1] += disc["velocity"][1]
#     if (
#         disc["pos"][1] - disc["radius"] <= 0
#         or disc["pos"][1] + disc["radius"] >= HEIGHT
#     ):
#         disc["velocity"][1] = -disc["velocity"][1]


# # Função para reiniciar o estado das bolinhas
# def reset_game():
#     global black_disc, red_disc, blue_disc
#     black_disc = initial_black_disc.copy()
#     red_disc = initial_red_disc.copy()
#     blue_disc = initial_blue_disc.copy()


# # Função para verificar se o disco azul tocou as áreas de gol
# def check_goal_area_collision(disc):
#     left_goal = pygame.Rect(0, HEIGHT // 2 - 50, 5, 100)  # Área de gol esquerda
#     right_goal_rect = pygame.Rect(
#         WIDTH - 5, HEIGHT // 2 - 50, 5, 100
#     )  # Área de gol direita
#     return left_goal.collidepoint(disc["pos"]) or right_goal_rect.collidepoint(
#         disc["pos"]
#     )


# # Função principal do jogo
# while running:

#     # Captura frame a frame
#     ret, frame = cap.read()
#     if not ret:
#         break

#     # Converter a imagem para RGB
#     rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

#     # Processar a imagem para detectar mãos
#     results = hands.process(rgb_frame)

#     # Se forem detectadas mãos
#     if results.multi_hand_landmarks:
#         if len(results.multi_hand_landmarks) >= 2:
#             # Obter as coordenadas das mãos diretamente da landmark 9 (centro da palma)
#             hand_landmarks1 = results.multi_hand_landmarks[0]
#             hand_landmarks2 = results.multi_hand_landmarks[1]

#             # Ponto central da mão 1 (landmark 9) para o disco vermelho
#             x_center1 = hand_landmarks1.landmark[9].x
#             y_center1 = hand_landmarks1.landmark[9].y
#             red_disc["pos"] = [x_center1 * WIDTH, y_center1 * HEIGHT]

#             # Ponto central da mão 2 (landmark 9) para o disco azul
#             x_center2 = hand_landmarks2.landmark[9].x
#             y_center2 = hand_landmarks2.landmark[9].y
#             blue_disc["pos"] = [x_center2 * WIDTH, y_center2 * HEIGHT]

#     # Movimento do disco preto
#     black_disc["pos"][0] += black_disc["velocity"][0]
#     black_disc["pos"][1] += black_disc["velocity"][1]

#     # Verificar colisão com as áreas de gol
#     if check_goal_area_collision(black_disc):
#         reset_game()  # Reiniciar o estado das bolinhas
#         black_disc["pos"] = [
#             WIDTH // 2,
#             HEIGHT // 2,
#         ]  # Reposicionar o disco preto no centro
#         black_disc["velocity"] = [3, 3]

#     # Verificar colisões com os limites da tela
#     black_disc["velocity"] = check_boundary_collision(
#         black_disc, black_disc["velocity"], pygame.Rect(0, 0, WIDTH, HEIGHT)
#     )
#     move_red_discs(red_disc)
#     move_red_discs(blue_disc)

#     # Verificar colisão entre o disco preto e os discos vermelho e azul
#     if check_collision_circle(black_disc, red_disc):
#         reflect_velocity(black_disc, red_disc)
#         correct_overlap(black_disc, red_disc)

#     if check_collision_circle(black_disc, blue_disc):
#         reflect_velocity(black_disc, blue_disc)
#         correct_overlap(black_disc, blue_disc)

#     # Limpar a tela
#     screen.fill(WHITE)

#     # Desenhar a linha verde das áreas de gol
#     pygame.draw.rect(screen, GREEN, pygame.Rect(187, HEIGHT // 2 - 50, 5, 100))
#     pygame.draw.rect(screen, GREEN, pygame.Rect(WIDTH - 197, HEIGHT // 2 - 50, 5, 100))

#     pygame.draw.rect(screen, BLACK, pygame.Rect(192, 216, 5, HEIGHT - 432))

#     # Desenhar os discos
#     pygame.draw.circle(screen, BLACK, black_disc["pos"], black_disc["radius"])
#     pygame.draw.circle(screen, RED, red_disc["pos"], red_disc["radius"])
#     pygame.draw.circle(screen, BLUE, blue_disc["pos"], blue_disc["radius"])

#     # Atualizar a tela
#     pygame.display.flip()

# # Encerrar o Pygame
# pygame.quit()
# cap.release()
# cv2.destroyAllWindows()
import sys
import math
import pygame
import cv2
import mediapipe as mp

# Inicializa o MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Configurar o detector de mãos
hands = mp_hands.Hands()
cap = cv2.VideoCapture(0)

# Initialize Pygame
pygame.init()

# Set up the full screen display
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
width, height = screen.get_size()
pygame.display.set_caption("Air Hockey")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Calculate dimensions
border_thickness = 5
green_line_inset = 20
main_rect_width = width - 200  # 1720
main_rect_height = height - 250
main_rect_x = (width - main_rect_width) // 2  # 100
main_rect_y = (height - main_rect_height) // 2
mid_x = width // 2

# Discs positions [x, y]
blue_disc = [main_rect_x + main_rect_width // 4, height // 2]
red_disc = [main_rect_x + 3 * main_rect_width // 4, height // 2]
black_disc = [mid_x - main_rect_width // 8, height // 2]


def draw_main_rectangle():
    # Top line
    pygame.draw.line(
        screen,
        BLACK,
        (main_rect_x, main_rect_y),  # X: 100
        (main_rect_x + main_rect_width, main_rect_y),  # X: 1820
        border_thickness,
    )
    # Bottom line
    pygame.draw.line(
        screen,
        BLACK,
        (main_rect_x, main_rect_y + main_rect_height),
        (main_rect_x + main_rect_width, main_rect_y + main_rect_height),
        border_thickness,
    )
    # Left line (with gap)
    pygame.draw.line(
        screen,
        BLACK,
        (main_rect_x, main_rect_y),
        (main_rect_x, height // 2 - 100),
        border_thickness,
    )
    pygame.draw.line(
        screen,
        BLACK,
        (main_rect_x, height // 2 + 100),
        (main_rect_x, main_rect_y + main_rect_height),
        border_thickness,
    )
    # Right line (with gap)
    pygame.draw.line(
        screen,
        BLACK,
        (main_rect_x + main_rect_width, main_rect_y),
        (main_rect_x + main_rect_width, height // 2 - 100),
        border_thickness,
    )
    pygame.draw.line(
        screen,
        BLACK,
        (main_rect_x + main_rect_width, height // 2 + 100),
        (main_rect_x + main_rect_width, main_rect_y + main_rect_height),
        border_thickness,
    )

    # Draw the dividing line
    pygame.draw.line(
        screen,
        BLACK,
        (mid_x, main_rect_y),
        (mid_x, main_rect_y + main_rect_height),
        border_thickness,
    )


def draw_green_lines():
    green_line_top = height // 2 - 100
    green_line_bottom = height // 2 + 100
    pygame.draw.line(
        screen,
        GREEN,
        (main_rect_x - 5, green_line_top),
        (main_rect_x - 5, green_line_bottom),
        border_thickness,
    )
    pygame.draw.line(
        screen,
        GREEN,
        (main_rect_x + main_rect_width + 5, green_line_top),
        (main_rect_x + main_rect_width + 5, green_line_bottom),
        border_thickness,
    )


def draw_disc():
    pygame.draw.circle(screen, BLUE, (blue_disc[0], blue_disc[1]), 45)
    pygame.draw.circle(screen, BLACK, (black_disc[0], black_disc[1]), 20)
    pygame.draw.circle(screen, RED, (red_disc[0], red_disc[1]), 45)


def draw_text():
    font = pygame.font.Font(None, 48)
    text_p1 = font.render("P1", True, BLUE)
    text_p2 = font.render("P2", True, RED)
    screen.blit(text_p1, (main_rect_x + 10, main_rect_y - 40))
    screen.blit(text_p2, (main_rect_x + main_rect_width - 50, main_rect_y - 40))


def draw_scoreboard():
    bottom_circle_y = main_rect_y + main_rect_height + 55
    circle_colors = [
        WHITE,
        WHITE,
        WHITE,
        WHITE,
        WHITE,
    ]
    for i in range(5):
        x = mid_x + (i - 2) * 85
        pygame.draw.circle(screen, circle_colors[i], (x, bottom_circle_y), 30)
        pygame.draw.circle(screen, BLACK, (x, bottom_circle_y), 30, 3)


# Main game loop
def main():
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                pygame.quit()
                sys.exit()

        # Fill the background
        screen.fill(WHITE)

        # Draw the main rectangle with gaps
        draw_main_rectangle()

        # Draw the green lines
        draw_green_lines()

        # Draw the scoreboard
        draw_scoreboard()

        # Draw the text
        draw_text()

        # Captura frame a frame
        ret, frame = cap.read()
        if not ret:
            break

        # Converter a imagem para RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Processar a imagem para detectar mãos
        results = hands.process(rgb_frame)

        # Se forem detectadas mãos
        if results.multi_hand_landmarks:
            if len(results.multi_hand_landmarks) >= 2:
                # Getting both hand_landmarks
                hand_landmarks1 = results.multi_hand_landmarks[0]
                hand_landmarks2 = results.multi_hand_landmarks[1]

                # (landmark 9) Hand 1
                red_disc[0] = hand_landmarks1.landmark[9].x * width
                red_disc[1] = hand_landmarks1.landmark[9].y * height

                # (landmark 9) Hand 2
                blue_disc[0] = hand_landmarks2.landmark[9].x * width
                blue_disc[1] = hand_landmarks2.landmark[9].y * height

        # Draw the discs
        draw_disc()

        # Update the display
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
