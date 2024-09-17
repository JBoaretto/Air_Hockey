import pygame
import math
import cv2
import mediapipe as mp

# Inicializa o Pygame
pygame.init()

# Dimensões da tela
WIDTH, HEIGHT = 600, 300
screen = pygame.display.set_mode((WIDTH + 60, HEIGHT + 30))
pygame.display.set_caption("Air Hockey")

# Cores
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)

# Definir os discos
initial_black_disc = {"pos": [WIDTH // 2, HEIGHT // 2], "radius": 15, "velocity": [3, 3]}
initial_red_disc = {"pos": [100, HEIGHT // 2], "radius": 30, "velocity": [0, 2]}  # Disco vermelho
initial_blue_disc = {"pos": [WIDTH - 100, HEIGHT // 2], "radius": 30, "velocity": [0, 2]}  # Disco azul

black_disc = initial_black_disc.copy()
red_disc = initial_red_disc.copy()
blue_disc = initial_blue_disc.copy()

# Inicializa o MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Configurar o detector de mãos
hands = mp_hands.Hands()
cap = cv2.VideoCapture(0)

# Variável para controlar a execução do jogo
running = True

# Função para verificar colisão circular
def check_collision_circle(disc1, disc2):
    dist = math.hypot(disc1["pos"][0] - disc2["pos"][0], disc1["pos"][1] - disc2["pos"][1])
    return dist < disc1["radius"] + disc2["radius"]

# Função para refletir o movimento do disco com base na colisão
def reflect_velocity(moving_disc, stationary_disc):
    dx = moving_disc["pos"][0] - stationary_disc["pos"][0]
    dy = moving_disc["pos"][1] - stationary_disc["pos"][1]
    distance = math.hypot(dx, dy)
    if distance == 0:
        return  # Evitar divisão por zero
    nx, ny = dx / distance, dy / distance  # Vetor normalizado
    dot_product = moving_disc["velocity"][0] * nx + moving_disc["velocity"][1] * ny
    moving_disc["velocity"][0] -= 2 * dot_product * nx
    moving_disc["velocity"][1] -= 2 * dot_product * ny

# Função para verificar colisão com bordas e corrigir sobreposição
def check_boundary_collision(disc, velocity, boundaries):
    if disc["pos"][0] - disc["radius"] < boundaries.left + 30:  # Colisão com a borda esquerda da área de jogo
        disc["pos"][0] = boundaries.left + 30 + disc["radius"]  # Reposicionar para dentro da borda
        velocity[0] = abs(velocity[0])  # Garantir que a velocidade vá para a direita
    if disc["pos"][0] + disc["radius"] > boundaries.right - 30:  # Colisão com a borda direita da área de jogo
        disc["pos"][0] = boundaries.right - 30 - disc["radius"]  # Reposicionar para dentro da borda
        velocity[0] = -abs(velocity[0])  # Garantir que a velocidade vá para a esquerda
    if disc["pos"][1] - disc["radius"] < boundaries.top:  # Colisão com a borda superior
        disc["pos"][1] = boundaries.top + disc["radius"]  # Reposicionar para dentro da borda
        velocity[1] = abs(velocity[1])  # Garantir que a velocidade vá para baixo
    if disc["pos"][1] + disc["radius"] > boundaries.bottom - 30:  # Colisão com a borda inferior
        disc["pos"][1] = boundaries.bottom - 30 - disc["radius"]  # Reposicionar para dentro da borda
        velocity[1] = -abs(velocity[1])  # Garantir que a velocidade vá para cima
    return velocity

# Função para corrigir a sobreposição após a colisão
def correct_overlap(disc1, disc2):
    dx = disc1["pos"][0] - disc2["pos"][0]
    dy = disc1["pos"][1] - disc2["pos"][1]
    distance = math.hypot(dx, dy)
    if distance == 0:
        return  # Evitar divisão por zero
    overlap = disc1["radius"] + disc2["radius"] - distance
    if overlap > 0:
        move_x = (dx / distance) * overlap / 2  # Dividir o movimento entre os dois
        move_y = (dy / distance) * overlap / 2
        disc1["pos"][0] += move_x
        disc1["pos"][1] += move_y
        disc2["pos"][0] -= move_x
        disc2["pos"][1] -= move_y

# Função para movimentar discos vermelhos verticalmente
def move_red_discs(disc):
    disc["pos"][1] += disc["velocity"][1]
    if disc["pos"][1] - disc["radius"] <= 0 or disc["pos"][1] + disc["radius"] >= HEIGHT:
        disc["velocity"][1] = -disc["velocity"][1]

# Função para reiniciar o estado das bolinhas
def reset_game():
    global black_disc, red_disc, blue_disc
    black_disc = initial_black_disc.copy()
    red_disc = initial_red_disc.copy()
    blue_disc = initial_blue_disc.copy()

# Função para verificar se o disco azul tocou as áreas de gol
def check_goal_area_collision(disc):
    left_goal = pygame.Rect(29, HEIGHT // 2 - 50, 5, 100)  # Área de gol esquerda
    right_goal_rect = pygame.Rect(WIDTH + 33, HEIGHT // 2 - 50, 5, 100)  # Área de gol direita
    return left_goal.collidepoint(disc["pos"]) or right_goal_rect.collidepoint(disc["pos"])

# Função principal do jogo
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

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
            # Obter as coordenadas das mãos
            hand_landmarks1 = results.multi_hand_landmarks[0]
            hand_landmarks2 = results.multi_hand_landmarks[1]

            # Calcular a posição média das mãos para os discos
            x_coords1 = [lm.x for lm in hand_landmarks1.landmark]
            y_coords1 = [lm.y for lm in hand_landmarks1.landmark]
            x_center1 = sum(x_coords1) / len(x_coords1)
            y_center1 = sum(y_coords1) / len(y_coords1)
            # Ajuste da posição para o disco vermelho (mão 1)
            red_disc["pos"] = [x_center1 * WIDTH + 30, y_center1 * HEIGHT]

            x_coords2 = [lm.x for lm in hand_landmarks2.landmark]
            y_coords2 = [lm.y for lm in hand_landmarks2.landmark]
            x_center2 = sum(x_coords2) / len(x_coords2)
            y_center2 = sum(y_coords2) / len(y_coords2)
            # Ajuste da posição para o disco azul (mão 2)
            blue_disc["pos"] = [x_center2 * WIDTH + 30, y_center2 * HEIGHT]

    # Movimento do disco preto
    black_disc["pos"][0] += black_disc["velocity"][0]
    black_disc["pos"][1] += black_disc["velocity"][1]

    # Verificar colisão com as áreas de gol
    if check_goal_area_collision(black_disc):
        reset_game()  # Reiniciar o estado das bolinhas
        black_disc["pos"] = [WIDTH // 2, HEIGHT // 2]  # Reposicionar o disco preto no centro
        black_disc["velocity"] = [3, 3]  # Reiniciar a velocidade
        continue  # Ir para o próximo quadro

    # Verificar colisão com bordas para o disco preto
    black_disc["velocity"] = check_boundary_collision(black_disc, black_disc["velocity"], screen.get_rect())

    # Verificar colisão com os discos vermelhos
    if check_collision_circle(black_disc, red_disc):
        reflect_velocity(black_disc, red_disc)
        correct_overlap(black_disc, red_disc)  # Corrigir sobreposição

    if check_collision_circle(black_disc, blue_disc):
        reflect_velocity(black_disc, blue_disc)
        correct_overlap(black_disc, blue_disc)  # Corrigir sobreposição

    # Movimento vertical dos discos vermelhos e azul
    move_red_discs(red_disc)
    move_red_discs(blue_disc)

    # Verificar colisão com bordas para os discos vermelhos e azul
    red_disc["velocity"] = check_boundary_collision(red_disc, red_disc["velocity"], screen.get_rect())
    blue_disc["velocity"] = check_boundary_collision(blue_disc, blue_disc["velocity"], screen.get_rect())

    # Desenhar o cenário
    screen.fill(WHITE)
    pygame.draw.line(screen, BLACK, (30, 0), (WIDTH + 30, 0), 5)  # Borda superior
    pygame.draw.line(screen, BLACK, (30, HEIGHT), (WIDTH + 30, HEIGHT), 5)  # Borda inferior

    pygame.draw.line(screen, BLACK, (30, 0), (30, HEIGHT // 2 - 50), 5)  # Lateral esquerda superior
    pygame.draw.line(screen, BLACK, (30, HEIGHT // 2 + 50), (30, HEIGHT), 5)  # Lateral esquerda inferior

    pygame.draw.line(screen, BLACK, (WIDTH + 30, 0), (WIDTH + 30, HEIGHT // 2 - 50), 5)  # Lateral direita superior
    pygame.draw.line(screen, BLACK, (WIDTH + 30, HEIGHT // 2 + 50), (WIDTH + 30, HEIGHT), 5)  # Lateral direita inferior
    
    # Desenhar as traves
    pygame.draw.line(screen, RED, (27, HEIGHT // 2 - 50), (27, HEIGHT // 2 + 50), 5)  # Trave esquerda
    pygame.draw.line(screen, BLUE, (WIDTH + 33, HEIGHT // 2 - 50), (WIDTH + 33, HEIGHT // 2 + 50), 5)

    # Desenhar os discos
    pygame.draw.circle(screen, BLACK, (int(black_disc["pos"][0]), int(black_disc["pos"][1])), black_disc["radius"])  # Disco preto
    pygame.draw.circle(screen, RED, (int(red_disc["pos"][0]), int(red_disc["pos"][1])), red_disc["radius"])  # Disco vermelho
    pygame.draw.circle(screen, BLUE, (int(blue_disc["pos"][0]), int(blue_disc["pos"][1])), blue_disc["radius"])  # Disco azul

    # Atualizar a tela
    pygame.display.flip()

    # Controlar a taxa de quadros
    pygame.time.Clock().tick(60)

# Finalizar o Pygame e o MediaPipe
cap.release()
pygame.quit()
cv2.destroyAllWindows()
