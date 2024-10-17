import sys
import time
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
circle_colors = [
    WHITE,
    WHITE,
    WHITE,
    WHITE,
    WHITE,
]

# Constantes de física
FRICTION = 1  # Se quiser fricção, só alterar para um valor entre 0 e 1
FORCE_MULTIPLIER = 1.2
MAX_SPEED = 20

# Variáveis de estado para detectar colisões anteriores
collision_with_red = False
collision_with_blue = False

# Calculate dimensions
border_thickness = 5
green_line_inset = 20
main_rect_width = width - 200  # 1720
main_rect_height = height - 250
main_rect_x = (width - main_rect_width) // 2  # 100
main_rect_y = (height - main_rect_height) // 2
mid_x = width // 2
mid_y = height // 2

# Discs positions [x, y]
blue_disc = [main_rect_x + main_rect_width // 4, mid_y]
red_disc = [main_rect_x + 3 * main_rect_width // 4, mid_y]
black_disc = [mid_x - main_rect_width // 8, mid_y]  # P1
initial_black_disc_pos = [width // 2, mid_y]
restart_black_disc_pos_p1 = [mid_x - main_rect_width // 8, mid_y]
restart_black_disc_pos_p2 = [mid_x + main_rect_width // 8, mid_y]

# Velocidade inicial do disco preto
black_disc_vel = [0, 0]

# Variáveis de pontuação
blue_score = 0
red_score = 0


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
        (main_rect_x, mid_y - 100),
        border_thickness,
    )
    pygame.draw.line(
        screen,
        BLACK,
        (main_rect_x, mid_y + 100),
        (main_rect_x, main_rect_y + main_rect_height),
        border_thickness,
    )
    # Right line (with gap)
    pygame.draw.line(
        screen,
        BLACK,
        (main_rect_x + main_rect_width, main_rect_y),
        (main_rect_x + main_rect_width, mid_y - 100),
        border_thickness,
    )
    pygame.draw.line(
        screen,
        BLACK,
        (main_rect_x + main_rect_width, mid_y + 100),
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
    green_line_top = mid_y - 100
    green_line_bottom = mid_y + 100
    pygame.draw.line(
        screen,
        GREEN,
        (main_rect_x + 1, green_line_top),
        (main_rect_x + 1, green_line_bottom),
        border_thickness + 2,
    )
    pygame.draw.line(
        screen,
        GREEN,
        (main_rect_x + main_rect_width - 1, green_line_top),
        (main_rect_x + main_rect_width - 1, green_line_bottom),
        border_thickness + 2,
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

    for i in range(5):
        x = mid_x + (i - 2) * 85
        pygame.draw.circle(screen, circle_colors[i], (x, bottom_circle_y), 30)
        pygame.draw.circle(screen, BLACK, (x, bottom_circle_y), 30, 3)


# Função para calcular a força e aumentar a velocidade do disco preto, apenas no momento da colisão
def adjust_black_disc_speed(disc_pos, disc_vel, previous_collision):
    distance = math.dist(disc_pos, black_disc)

    if distance < 45 + 20:  # Se houver colisão
        if (
            not previous_collision
        ):  # Ajusta a velocidade apenas se não houve colisão no quadro anterior
            force_x = disc_vel[0] - black_disc_vel[0]
            force_y = disc_vel[1] - black_disc_vel[1]

            # Aumenta a velocidade do disco preto proporcionalmente à força da batida
            black_disc_vel[0] += force_x * FORCE_MULTIPLIER
            black_disc_vel[1] += force_y * FORCE_MULTIPLIER

        return True  # Há colisão

    return False  # Sem colisão


# Função para checar colisão e aplicar força apenas no momento certo
def check_collision_with_players(blue_vel, red_vel):
    global collision_with_red, collision_with_blue

    # Colisão com o disco vermelho
    collision_with_red = adjust_black_disc_speed(red_disc, red_vel, collision_with_red)

    # Colisão com o disco azul
    collision_with_blue = adjust_black_disc_speed(
        blue_disc, blue_vel, collision_with_blue
    )


# Movimento do disco preto
def move_black_disc():
    black_disc[0] += black_disc_vel[0]
    black_disc[1] += black_disc_vel[1]

    # Aplica atrito
    black_disc_vel[0] *= FRICTION
    black_disc_vel[1] *= FRICTION

    # Limita a velocidade máxima
    speed = math.sqrt(black_disc_vel[0] ** 2 + black_disc_vel[1] ** 2)

    if speed > MAX_SPEED:
        scaling_factor = MAX_SPEED / speed
        black_disc_vel[0] *= scaling_factor
        black_disc_vel[1] *= scaling_factor

    # Verifica colisões com as bordas e aplica reversão de direção
    if (
        black_disc[0] <= main_rect_x + 20
        or black_disc[0] >= main_rect_x + main_rect_width - 20
    ):
        black_disc_vel[0] = -black_disc_vel[0]
    if (
        black_disc[1] <= main_rect_y + 20
        or black_disc[1] >= main_rect_y + main_rect_height - 20
    ):
        black_disc_vel[1] = -black_disc_vel[1]

    # Verifica se o disco preto saiu do campo
    if (
        black_disc[0] < main_rect_x
        or black_disc[0] > main_rect_x + main_rect_width
        or black_disc[1] < main_rect_y
        or black_disc[1] > main_rect_y + main_rect_height
    ):
        # Reinicia a posição do disco preto
        black_disc[0], black_disc[1] = initial_black_disc_pos
        # Redefine a velocidade para zero
        black_disc_vel[0], black_disc_vel[1] = 0, 0


# Verifica colisão com as linhas verdes (gols)
def check_goal():
    global blue_score, red_score

    green_line_top = mid_y - 100
    green_line_bottom = mid_y + 100

    # Ajustando a posição das linhas verdes para um ponto mais acessível dentro dos limites do campo
    # Verifica a colisão com a linha verde esquerda (Ponto para o jogador vermelho)
    if (
        main_rect_x <= black_disc[0] <= main_rect_x + 15
        and green_line_top - 10 <= black_disc[1] <= green_line_bottom + 10
    ):
        red_score += 1
        update_scoreboard("red")
        reset_black_disc("red")

    # Verifica a colisão com a linha verde direita (Ponto para o jogador azul)
    if (
        main_rect_x + main_rect_width - 15
        <= black_disc[0]
        <= main_rect_x + main_rect_width
        and green_line_top - 10 <= black_disc[1] <= green_line_bottom + 10
    ):
        blue_score += 1
        update_scoreboard("blue")
        reset_black_disc("blue")


# Atualiza o placar visual e muda a cor dos círculos
def update_scoreboard(player):
    if player == "blue":
        for i in range(blue_score):
            circle_colors[i] = BLUE
    elif player == "red":
        for i in range(red_score):
            circle_colors[-(i + 1)] = RED


def reset_black_disc(player):
    # Reinicia a posição do disco preto e a velocidade
    if player == "blue":
        black_disc[0], black_disc[1] = restart_black_disc_pos_p2
    elif player == "red":
        black_disc[0], black_disc[1] = restart_black_disc_pos_p1
    black_disc_vel[0], black_disc_vel[1] = 0, 0  # Reinicia a velocidade


def check_match():
    if blue_score == 3:
        print("Jogador Azul venceu!")
        # Limpa a tela
        screen.fill(WHITE)
        # Define a fonte e o texto para o jogador azul
        font = pygame.font.Font(None, 256)
        text_blue_win = font.render("P1 Ganhou!", True, BLUE)
        text_rect = text_blue_win.get_rect(center=(width // 2, mid_y))
        # Desenha o texto
        screen.blit(text_blue_win, text_rect)
        # Atualiza a tela
        pygame.display.flip()
        # Mantém a tela até o usuário fechar ou pressionar uma tecla
        wait_for_exit()

    elif red_score == 3:
        print("Jogador Vermelho venceu!")
        # Limpa a tela
        screen.fill(WHITE)
        # Define a fonte e o texto para o jogador vermelho
        font = pygame.font.Font(None, 256)
        text_red_win = font.render("P2 Ganhou!", True, RED)
        text_rect = text_red_win.get_rect(center=(width // 2, mid_y))
        # Desenha o texto
        screen.blit(text_red_win, text_rect)
        # Atualiza a tela
        pygame.display.flip()
        # Mantém a tela até o usuário fechar ou pressionar uma tecla
        wait_for_exit()


# Função para esperar o usuário pressionar uma tecla ou fechar a janela
def wait_for_exit():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN):
                pygame.quit()
                sys.exit()


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
                # Obter landmarks das mãos
                hand_landmarks1 = results.multi_hand_landmarks[0]
                hand_landmarks2 = results.multi_hand_landmarks[1]

                # (landmark 9)
                new_red_pos = [
                    hand_landmarks1.landmark[9].x * width,
                    hand_landmarks1.landmark[9].y * height,
                ]
                new_blue_pos = [
                    hand_landmarks2.landmark[9].x * width,
                    hand_landmarks2.landmark[9].y * height,
                ]

                # Calcula a velocidade de movimento das mãos
                red_vel = [new_red_pos[0] - red_disc[0], new_red_pos[1] - red_disc[1]]
                blue_vel = [
                    new_blue_pos[0] - blue_disc[0],
                    new_blue_pos[1] - blue_disc[1],
                ]

                # Atualiza as posições dos discos
                red_disc[0], red_disc[1] = new_red_pos
                blue_disc[0], blue_disc[1] = new_blue_pos

                # Verifica se os discos estão dentro dos limites do campo e nos lados corretos
                # Disco azul (lado esquerdo)
                blue_disc[0] = max(main_rect_x + 45, min(blue_disc[0], mid_x - 45))
                blue_disc[1] = max(
                    main_rect_y + 45,
                    min(blue_disc[1], main_rect_y + main_rect_height - 45),
                )

                # Disco vermelho (lado direito)
                red_disc[0] = max(
                    mid_x + 45, min(red_disc[0], main_rect_x + main_rect_width - 45)
                )
                red_disc[1] = max(
                    main_rect_y + 45,
                    min(red_disc[1], main_rect_y + main_rect_height - 45),
                )

                # Verifica colisão com os discos dos jogadores
                check_collision_with_players(blue_vel, red_vel)

        # Movimento do disco preto
        move_black_disc()

        # Verifica se o disco preto atingiu as linhas verdes (gols)
        check_goal()

        # Verifica se a partida finalizou
        check_match()

        # Draw the discs
        draw_disc()

        # Update the display
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
