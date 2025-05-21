import pygame
import sys
from player import Player
from obstacle import Enemy, MushroomEnemy, FlyingEnemy

# ShadowRun – A Jornada Pixelada
# Um jogo de plataforma 2D onde o jogador controla um personagem pixelado que deve correr e pular para evitar obstáculos.
# O jogo é inspirado em clássicos como Super Mario e Sonic, mas com uma estética única e jogabilidade fluida.

# Configurações iniciais
tela_largura = 800 # Instanciando a largura da tela
tela_altura = 400 # Instanciando a altura da tela
fps = 60 # Quantos frames por segundo o jogo irá rodar

# Inicialização do Pygame
pygame.init() # Inicializando o Pygame
pygame.mixer.init() # Inicializando o mixer para sons
tela = pygame.display.set_mode((tela_largura, tela_altura)) # Criando a tela
pygame.display.set_caption('ShadowRun – A Jornada Pixelada') # Definindo o titulo da janela
relogio = pygame.time.Clock() # Criando o relógio para controlar os frames por segundo

# Cores básicas
BRANCO = (255, 255, 255) # Cor branca
PRETO = (0, 0, 0) # Cor preta

# Carregar sons
som_pulo = pygame.mixer.Sound('assets/sfx/Retro Jump 01.wav')
som_colisao = pygame.mixer.Sound('assets/sfx/Retro Impact Punch 07.wav')
som_ataque = pygame.mixer.Sound('assets/sfx/Retro Impact Punch 07.wav')
# Ajuste de volume dos SFX
som_pulo.set_volume(0.4)
som_colisao.set_volume(0.5)
som_ataque.set_volume(0.5)
# OSTs
OST_MENU = 'assets/sound/1 Legend.wav'
OST_NIVEL = 'assets/sound/Dark Dark Woods.wav'
OST_COMBATE = 'assets/sound/6 Combat.wav'
OST_MENU_INGAME = 'assets/sound/27 With Patience Borne.wav'
pygame.mixer.music.load(OST_MENU)
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

# Carregar camadas do background
background_layers = [
    pygame.image.load(f'assets/background/{i}.png').convert_alpha() for i in range(1, 9)
]

# Função utilitária para transição suave entre músicas usando fadeout
def fadeout_and_play(new_music, fadeout_ms=1200):
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.fadeout(fadeout_ms)
        pygame.time.delay(fadeout_ms)
    pygame.mixer.music.load(new_music)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

# Controle de transição de música sem travar o loop
def fadeout_and_play_async(new_music, fadeout_ms=1200):
    global musica_pendente, musica_fadeout_time, musica_fadeout_ms
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.fadeout(fadeout_ms)
        musica_pendente = new_music
        musica_fadeout_time = pygame.time.get_ticks()
        musica_fadeout_ms = fadeout_ms
    else:
        pygame.mixer.music.load(new_music)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

musica_pendente = None
musica_fadeout_time = 0
musica_fadeout_ms = 0

def checar_troca_musica():
    global musica_pendente, musica_fadeout_time, musica_fadeout_ms
    if musica_pendente:
        if pygame.time.get_ticks() - musica_fadeout_time >= musica_fadeout_ms:
            pygame.mixer.music.load(musica_pendente)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
            musica_pendente = None

# Loop principal do jogo
def main():
    fadeout_and_play_async(OST_NIVEL)
    while True:
        player = Player(80, tela_altura - 50)
        inimigos = []
        spawn_queue = [
            (Enemy, 400, tela_altura - 64, 'left', 1200),
            (MushroomEnemy, 600, tela_altura - 64, 'right', 2200),
            (FlyingEnemy, 700, tela_altura - 180, 'right', 3200),
        ]
        spawn_timers = [pygame.time.get_ticks() + delay for _,_,_,_,delay in spawn_queue]
        spawned = [False]*len(spawn_queue)
        fonte = pygame.font.Font('assets/font/Beholden/Beholden-Regular.ttf', 36)
        rodando = True
        game_over = False
        combate_ativo = False
        ost_atual = OST_NIVEL
        camera_x = 0
        while rodando:
            relogio.tick(fps)
            checar_troca_musica()
            now = pygame.time.get_ticks()
            # Spawn temporizado dos inimigos
            for i, (cls, x, y, side, delay) in enumerate(spawn_queue):
                if not spawned[i] and now >= spawn_timers[i]:
                    inimigos.append(cls(x, y, spawn_side=side))
                    spawned[i] = True
            # Parallax/câmera: centraliza o player na tela (com limites)
            camera_x = player.x - tela_largura // 2 + player.largura // 2
            camera_x = max(0, min(camera_x, 1000))  # 1000: limite do mapa, ajuste conforme necessário
            # Combate e música
            combate_ativo = any(inimigo.vivo and abs((inimigo.x + inimigo.largura//2) - (player.x + player.largura//2)) < 180 for inimigo in inimigos)
            if combate_ativo and ost_atual != OST_COMBATE:
                fadeout_and_play_async(OST_COMBATE)
                ost_atual = OST_COMBATE
            elif not combate_ativo and ost_atual != OST_NIVEL:
                fadeout_and_play_async(OST_NIVEL)
                ost_atual = OST_NIVEL
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        acao = menu_ingame()
                        if acao == 'menu':
                            return 'menu'
                    if evento.key == pygame.K_SPACE:
                        player.pular()
                        som_pulo.play()
                    if evento.key == pygame.K_j or evento.key == pygame.K_z:
                        player.atacar()
                        som_ataque.play()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                player.mover(-1)
            elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                player.mover(1)
            else:
                if not player.atacando and not player.pulando:
                    player.acao = 'idle'
            player.update()
            for inimigo in inimigos:
                inimigo.update(player)
            # Ataque do player
            if player.atacando:
                ataque_rect = player.get_ataque_rect()
                for inimigo in inimigos:
                    if inimigo.vivo and ataque_rect.colliderect(inimigo.rect):
                        inimigo.levar_dano()
                        som_colisao.play()
            # Ataque do inimigo
            for inimigo in inimigos:
                if inimigo.vivo and inimigo.ataque_acertou(player):
                    player.levar_dano()
                    som_colisao.play()
            # Colisão com inimigo (só se não estiver invencível)
            for inimigo in inimigos:
                if inimigo.vivo and inimigo.colidiu(player) and not player.invencivel:
                    player.levar_dano()
                    som_colisao.play()
            if player.vida <= 0:
                rodando = False
            tela.fill(BRANCO)
            # Parallax: camadas do fundo se movem em velocidades diferentes
            for idx, layer in enumerate(background_layers):
                parallax = 0.2 + 0.1 * idx  # camadas mais distantes movem menos
                offset = int(-camera_x * parallax)
                tela.blit(pygame.transform.scale(layer, (tela_largura, tela_altura)), (offset, 0))
            # Desenha player e inimigos com offset da câmera
            player.draw_offset(tela, -camera_x)
            for inimigo in inimigos:
                inimigo.draw_offset(tela, -camera_x)
            # UI de vida do player
            for i in range(player.vida):
                pygame.draw.rect(tela, (200,0,0), (20 + i*30, tela_altura-40, 24, 24), border_radius=6)
            # Substitui o texto por ícones de teclado na UI, com melhor espaçamento e alinhamento
            # UI/UX aprimorada: ícones maiores, espaçamento, e uso de fonte Bold para legendas
            icon_size = 48
            icon_y = 20
            fonte_bold = pygame.font.Font('assets/font/Beholden/Beholden-Bold.ttf', 32)
            try:
                icon_space = pygame.image.load('assets/icons/keyboard/space.png').convert_alpha()
                icon_j = pygame.image.load('assets/icons/keyboard/J.png').convert_alpha()
                icon_a = pygame.image.load('assets/icons/keyboard/A.png').convert_alpha()
                icon_d = pygame.image.load('assets/icons/keyboard/D button.png').convert_alpha()
                # Define proporção desejada (ex: 1.5x mais largo)
                icon_wide = int(icon_size * 1.5)
                # Espaçamento horizontal aprimorado
                x_space = 30
                x_j = x_space + icon_size*2 + 60
                x_a = x_j + icon_wide + 60
                x_d = x_a + icon_wide + 30
                # Ícones (maiores, mais largos e centralizados verticalmente)
                tela.blit(pygame.transform.scale(icon_space, (icon_size*2, icon_size)), (x_space, icon_y))
                tela.blit(pygame.transform.scale(icon_j, (icon_wide, icon_size)), (x_j, icon_y))
                tela.blit(pygame.transform.scale(icon_a, (icon_wide, icon_size)), (x_a, icon_y))
                tela.blit(pygame.transform.scale(icon_d, (icon_wide, icon_size)), (x_d, icon_y))
                # Legendas com fonte Bold e espaçamento, centralizadas abaixo dos botões
                texto_ui = fonte_bold.render("Pular", True, (30,30,30))
                texto_rect = texto_ui.get_rect(center=(x_space + icon_size, icon_y + icon_size + 18))
                tela.blit(texto_ui, texto_rect)
                texto_ui = fonte_bold.render("Atacar", True, (30,30,30))
                texto_rect = texto_ui.get_rect(center=(x_j + icon_wide//2, icon_y + icon_size + 18))
                tela.blit(texto_ui, texto_rect)
                texto_ui = fonte_bold.render("Andar", True, (30,30,30))
                texto_rect = texto_ui.get_rect(center=(x_a + icon_wide//2, icon_y + icon_size + 18))
                tela.blit(texto_ui, texto_rect)
            except Exception as e:
                print(f"[UI] Erro ao carregar ícones dos botões: {e}")
            pygame.display.flip()
        # Tela de Game Over
        while not game_over:
            tela.fill(BRANCO)
            texto_gameover = fonte.render("Game Over!", True, (200, 0, 0))
            texto_restart = fonte.render("Press SPACE to try again", True, (0, 0, 0))
            tela.blit(texto_gameover, (tela_largura//2 - texto_gameover.get_width()//2, tela_altura//2 - 60))
            tela.blit(texto_restart, (tela_largura//2 - texto_restart.get_width()//2, tela_altura//2 + 40))
            pygame.display.flip()
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_SPACE:
                        game_over = True

def menu_inicial():
    fadeout_and_play_async(OST_MENU)
    menu_ativo = True
    fonte_menu = pygame.font.Font('assets/font/Beholden/Beholden-Regular.ttf', 48)
    fonte_opcao = pygame.font.Font('assets/font/Beholden/Beholden-Regular.ttf', 32)
    opcoes = ['Iniciar', 'Opções', 'Sair']
    selecionado = 0
    while menu_ativo:
        checar_troca_musica()
        tela.fill((30, 10, 30))
        titulo = fonte_menu.render('ShadowRun', True, (255, 255, 255))
        tela.blit(titulo, (tela_largura//2 - titulo.get_width()//2, 60))
        for i, opcao in enumerate(opcoes):
            cor = (255, 255, 0) if i == selecionado else (255, 255, 255)
            texto = fonte_opcao.render(opcao, True, cor)
            tela.blit(texto, (tela_largura//2 - texto.get_width()//2, 180 + i*60))
        pygame.display.flip()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key in [pygame.K_UP, pygame.K_w]:
                    selecionado = (selecionado - 1) % len(opcoes)
                if evento.key in [pygame.K_DOWN, pygame.K_s]:
                    selecionado = (selecionado + 1) % len(opcoes)
                if evento.key == pygame.K_RETURN or evento.key == pygame.K_SPACE:
                    if opcoes[selecionado] == 'Iniciar':
                        menu_ativo = False
                    elif opcoes[selecionado] == 'Opções':
                        # Placeholder para opções futuras
                        pass
                    elif opcoes[selecionado] == 'Sair':
                        pygame.quit()
                        sys.exit()

def menu_ingame():
    fadeout_and_play_async(OST_MENU_INGAME)
    menu_ativo = True
    fonte_menu = pygame.font.Font('assets/font/Beholden/Beholden-Regular.ttf', 48)
    fonte_opcao = pygame.font.Font('assets/font/Beholden/Beholden-Regular.ttf', 32)
    opcoes = ['Voltar ao Jogo', 'Voltar ao Menu Principal', 'Sair do Jogo']
    selecionado = 0
    while menu_ativo:
        checar_troca_musica()
        tela.fill((30, 10, 30))
        titulo = fonte_menu.render('Menu', True, (255, 255, 255))
        tela.blit(titulo, (tela_largura//2 - titulo.get_width()//2, 60))
        for i, opcao in enumerate(opcoes):
            cor = (255, 255, 0) if i == selecionado else (255, 255, 255)
            texto = fonte_opcao.render(opcao, True, cor)
            tela.blit(texto, (tela_largura//2 - texto.get_width()//2, 180 + i*60))
        pygame.display.flip()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key in [pygame.K_UP, pygame.K_w]:
                    selecionado = (selecionado - 1) % len(opcoes)
                if evento.key in [pygame.K_DOWN, pygame.K_s]:
                    selecionado = (selecionado + 1) % len(opcoes)
                if evento.key == pygame.K_ESCAPE:
                    return 'voltar'
                if evento.key == pygame.K_RETURN or evento.key == pygame.K_SPACE:
                    if opcoes[selecionado] == 'Voltar ao Jogo':
                        return 'voltar'
                    elif opcoes[selecionado] == 'Voltar ao Menu Principal':
                        return 'menu'
                    elif opcoes[selecionado] == 'Sair do Jogo':
                        pygame.quit()
                        sys.exit()

if __name__ == '__main__':
    while True:
        menu_inicial()
        resultado = main()
        if resultado != 'menu':
            break
