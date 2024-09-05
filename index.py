import pygame
import math

# Necessário arrumar colisão com o gol

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
initial_blue_disc = {"pos": [WIDTH // 2, HEIGHT // 2], "radius": 15, "velocity": [3, 3]}
initial_red_disc1 = {"pos": [100, HEIGHT // 2], "radius": 30, "velocity": [0, 2]}  # Velocidade vertical
initial_red_disc2 = {"pos": [WIDTH - 100, HEIGHT // 2], "radius": 30, "velocity": [0, 2]}  # Velocidade vertical

blue_disc = initial_blue_disc.copy()
red_disc1 = initial_red_disc1.copy()
red_disc2 = initial_red_disc2.copy()

# Variável para controlar a execução do jogo
running = True

# Função para verificar colisão circular
def check_collision_circle(disc1, disc2):
    dist = math.hypot(disc1["pos"][0] - disc2["pos"][0], disc1["pos"][1] - disc2["pos"][1])
    return dist < disc1["radius"] + disc2["radius"]

# Função para refletir o movimento do disco com base na colisão
def reflect_velocity(blue, red):
    dx = blue["pos"][0] - red["pos"][0]
    dy = blue["pos"][1] - red["pos"][1]
    distance = math.hypot(dx, dy)
    if distance == 0:
        return  # Evitar divisão por zero
    nx, ny = dx / distance, dy / distance  # Vetor normalizado
    dot_product = blue["velocity"][0] * nx + blue["velocity"][1] * ny
    blue["velocity"][0] -= 2 * dot_product * nx
    blue["velocity"][1] -= 2 * dot_product * ny

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
def correct_overlap(blue, red):
    dx = blue["pos"][0] - red["pos"][0]
    dy = blue["pos"][1] - red["pos"][1]
    distance = math.hypot(dx, dy)
    if distance == 0:
        return  # Evitar divisão por zero
    overlap = blue["radius"] + red["radius"] - distance
    if overlap > 0:
        move_x = (dx / distance) * overlap / 2  # Dividir o movimento entre os dois
        move_y = (dy / distance) * overlap / 2
        blue["pos"][0] += move_x
        blue["pos"][1] += move_y
        red["pos"][0] -= move_x
        red["pos"][1] -= move_y

# Função para movimentar discos vermelhos verticalmente
def move_red_discs(red_disc):
    red_disc["pos"][1] += red_disc["velocity"][1]
    if red_disc["pos"][1] - red_disc["radius"] <= 0 or red_disc["pos"][1] + red_disc["radius"] >= HEIGHT:
        red_disc["velocity"][1] = -red_disc["velocity"][1]

# Função para reiniciar o estado das bolinhas
def reset_game():
    global blue_disc, red_disc1, red_disc2
    blue_disc = initial_blue_disc.copy()
    red_disc1 = initial_red_disc1.copy()
    red_disc2 = initial_red_disc2.copy()

# Função para verificar se o disco azul tocou as áreas de gol
def check_goal_area_collision(disc):
    left_goal = pygame.Rect(29, HEIGHT // 2 - 50, 5, 100)  # Área de gol esquerda
    right_goal_rect = pygame.Rect(WIDTH + 33, HEIGHT // 2 - 50, WIDTH + 33, HEIGHT // 2 + 50)  # Área de gol direita
    return left_goal.collidepoint(disc["pos"]) or right_goal_rect.collidepoint(disc["pos"])

# Função principal do jogo
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Movimento do disco azul
    blue_disc["pos"][0] += blue_disc["velocity"][0]
    blue_disc["pos"][1] += blue_disc["velocity"][1]

    # Verificar colisão com as áreas de gol
    if check_goal_area_collision(blue_disc):
        reset_game()  # Reiniciar o estado das bolinhas
        blue_disc["pos"] = [WIDTH // 2, HEIGHT // 2]  # Reposicionar o disco preto no centro
        blue_disc["velocity"] = [3, 3]  # Reiniciar a velocidade
        continue  # Ir para o próximo quadro

    # Verificar colisão com bordas para o disco azul
    blue_disc["velocity"] = check_boundary_collision(blue_disc, blue_disc["velocity"], screen.get_rect())

    # Verificar colisão com os discos vermelhos
    if check_collision_circle(blue_disc, red_disc1):
        reflect_velocity(blue_disc, red_disc1)
        correct_overlap(blue_disc, red_disc1)  # Corrigir sobreposição

    if check_collision_circle(blue_disc, red_disc2):
        reflect_velocity(blue_disc, red_disc2)
        correct_overlap(blue_disc, red_disc2)  # Corrigir sobreposição

    # Movimento vertical dos discos vermelhos
    move_red_discs(red_disc1)
    move_red_discs(red_disc2)

    # Verificar colisão com bordas para os discos vermelhos 
    red_disc1["velocity"] = check_boundary_collision(red_disc1, red_disc1["velocity"], screen.get_rect())
    red_disc2["velocity"] = check_boundary_collision(red_disc2, red_disc2["velocity"], screen.get_rect())

    # Desenhar o cenário
    screen.fill(WHITE)
    pygame.draw.line(screen, BLACK, (30, 0), (WIDTH + 30, 0), 5) # Borda superior
    pygame.draw.line(screen, BLACK, (30, HEIGHT), (WIDTH + 30, HEIGHT), 5) # Borda inferior

    pygame.draw.line(screen, BLACK, (30, 0), (30, HEIGHT // 2 - 50), 5) # Lateral esquerda superior
    pygame.draw.line(screen, BLACK, (30, HEIGHT // 2 + 50), (30, HEIGHT), 5) # Lateral esquerda inferior

    pygame.draw.line(screen, BLACK, (WIDTH + 30, 0), (WIDTH + 30, HEIGHT // 2 - 50), 5) # Lateral direita superior
    pygame.draw.line(screen, BLACK, (WIDTH + 30, HEIGHT // 2 + 50), (WIDTH + 30, HEIGHT), 5) # Lateral direita inferior
    
    # Desenhar as traves
    pygame.draw.line(screen, RED, (27, HEIGHT // 2 - 50), (27, HEIGHT // 2 + 50), 5) # Trave esquerda
    pygame.draw.line(screen, BLUE, (WIDTH + 33, HEIGHT // 2 - 50),(WIDTH + 33, HEIGHT // 2 + 50),5)

    # Desenhar os discos
    pygame.draw.circle(screen, BLACK, blue_disc["pos"], blue_disc["radius"])  # Disco azul
    pygame.draw.circle(screen, RED, red_disc1["pos"], red_disc1["radius"])  # Disco vermelho 1
    pygame.draw.circle(screen, BLUE, red_disc2["pos"], red_disc2["radius"])  # Disco vermelho 2

    # Atualizar a tela
    pygame.display.flip()

    # Controlar a taxa de quadros
    pygame.time.Clock().tick(60)

# Finalizar o Pygame
pygame.quit()
