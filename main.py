# Lost Samurai - Beat'em Up
# Desenvolvido por Grupo7 - 2025
# Jogo de ação e aventura 2D em Pygame
# Certifique-se de que o Pygame está instalado e os assets estão no diretório correto.

import pygame
import sys
import random
from player import Player
from obstacle import Enemy

# =====================
# CONFIGURAÇÕES INICIAIS
# =====================
# Resolução base para escala
BASE_LARGURA = 1280
BASE_ALTURA = 720
# Resolução inicial (pode ser alterada no menu de opções)
tela_largura = 800
tela_altura = 600
fps = 60  # Frames por segundo

# Inicialização do Pygame e tela
pygame.init()
pygame.mixer.init()
tela = pygame.display.set_mode((tela_largura, tela_altura))
pygame.display.set_caption("Lost Samurai – Beat'Em Up")
relogio = pygame.time.Clock()

# Cores básicas
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)

# =====================
# SONS E MÚSICAS
# =====================
som_pulo = pygame.mixer.Sound('assets/sfx/Retro Jump 01.wav')
som_colisao = pygame.mixer.Sound('assets/sfx/Retro Impact Punch 07.wav')
som_ataque = pygame.mixer.Sound('assets/sfx/Retro Impact Punch 07.wav')
som_pulo.set_volume(0.4)
som_colisao.set_volume(0.5)
som_ataque.set_volume(0.5)
OST_MENU = 'assets/sound/1 Legend.wav'
OST_NIVEL = 'assets/sound/Dark Dark Woods.wav'
OST_COMBATE = 'assets/sound/6 Combat.wav'
OST_MENU_INGAME = 'assets/sound/27 With Patience Borne.wav'
pygame.mixer.music.load(OST_MENU)
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

# =====================
# BACKGROUND
# =====================
background_layers = [
    pygame.image.load(f'assets/background/{i}.png').convert_alpha() for i in range(1, 9)
]

# =====================
# ESCALA GLOBAL
# =====================
escala_x = tela_largura / BASE_LARGURA
escala_y = tela_altura / BASE_ALTURA

def atualizar_escala():
    global escala_x, escala_y
    escala_x = tela_largura / BASE_LARGURA
    escala_y = tela_altura / BASE_ALTURA

# =====================
# MÚSICA UTILITÁRIA
# =====================
def fadeout_and_play(new_music, fadeout_ms=1200):
    """Transição suave entre músicas (bloqueante)."""
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.fadeout(fadeout_ms)
        pygame.time.delay(fadeout_ms)
    pygame.mixer.music.load(new_music)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

def fadeout_and_play_async(new_music, fadeout_ms=1200):
    """Transição suave entre músicas (não bloqueante)."""
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
    """Verifica se é hora de trocar a música após fadeout."""
    global musica_pendente, musica_fadeout_time, musica_fadeout_ms
    if musica_pendente:
        if pygame.time.get_ticks() - musica_fadeout_time >= musica_fadeout_ms:
            pygame.mixer.music.load(musica_pendente)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
            musica_pendente = None

# =====================
# LOOP PRINCIPAL DO JOGO
# =====================
def main():
    fadeout_and_play_async(OST_NIVEL)
    ronda = 1
    player_stats = {'forca': 1, 'agilidade': 1, 'defesa': 1, 'vida_max': 3}
    fala = ''
    fala_timer = 0
    while True:
        if 'reset_ronda' in locals() and reset_ronda:
            ronda = 1
            reset_ronda = False
        player = Player(80, tela_altura - 50)
        player.vida = player_stats['vida_max']
        inimigos = []
        popups = []  # lista de popups de dano
        # Sistema de spawn dinâmico por ronda
        def gerar_inimigos(ronda):
            lista = []
            posicoes = list(range(200, tela_largura-200, 120))
            random.shuffle(posicoes)
            usados = set()
            for i in range(ronda + 2):
                tipo = Enemy  # Sempre só o esqueleto
                # Garante que não repete posição
                for _ in range(10):
                    x = posicoes[i % len(posicoes)] + random.randint(-30, 30)
                    if x not in usados:
                        usados.add(x)
                        break
                else:
                    x = posicoes[i % len(posicoes)]
                y = tela_altura - 64
                side = None  # Não usar spawn_side para evitar bugs de spawn
                lista.append(tipo(x, y, spawn_side=side))
            return lista
        inimigos = gerar_inimigos(ronda)
        fonte = pygame.font.Font('assets/font/Beholden/Beholden-Medium.ttf', 36)
        rodando = True
        game_over = False
        combate_ativo = False
        ost_atual = OST_NIVEL
        camera_x = 0
        drop_itens = []
        # Aviso de início de ronda
        fala = f'Ronda {ronda} iniciada!'
        fala_timer = 90
        inimigos = []  # Esvazia lista para delay
        delay_spawn = 60  # 1 segundo de delay (60 frames)
        while delay_spawn > 0:
            relogio.tick(fps)
            checar_troca_musica()
            for idx, layer in enumerate(background_layers):
                tela.blit(pygame.transform.scale(layer, (tela_largura, tela_altura)), (0, 0))
            if fala_timer > 0 and fala:
                texto_fala = fonte.render(fala, True, (30,30,30))
                tela.blit(texto_fala, (tela_largura//2 - texto_fala.get_width()//2, 60))
                fala_timer -= 1
            pygame.display.flip()
            delay_spawn -= 1
        inimigos = gerar_inimigos(ronda)
        fala = ''
        fala_timer = 0
        # =====================
        # LOOP DA RONDA
        # =====================
        while rodando:
            relogio.tick(fps)
            checar_troca_musica()
            now = pygame.time.get_ticks()
            # Fundo: desenha todas as camadas do background em ordem (sempre, ANTES de qualquer texto ou UI)
            for idx, layer in enumerate(background_layers):
                tela.blit(pygame.transform.scale(layer, (tela_largura, tela_altura)), (0, 0))
            # Parallax/câmera: centraliza o player na tela (com limites)
            camera_x = player.x - tela_largura // 2 + player.largura // 2
            # Corrigido: o parallax não deixa o fundo "acabar"
            max_camera = (len(background_layers[0].get_width().__str__()) * 800) - tela_largura
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
                    if hasattr(inimigo, 'morrendo') and inimigo.morrendo:
                        continue  # Não interage com inimigos morrendo
                    # Usa hitbox do inimigo e do player para colisão
                    if inimigo.vivo and ataque_rect.colliderect(inimigo.rect):
                        if not hasattr(player, 'ja_acertou') or not player.ja_acertou:
                            dano = player.forca if hasattr(player, 'forca') else 1
                            inimigo.levar_dano(dano)
                            som_colisao.play()
                            popups.append({'dano': dano, 'x': inimigo.x + inimigo.largura//2, 'y': inimigo.y - 20, 'timer': 30})
                            player.ja_acertou = True
                        break
                else:
                    player.ja_acertou = False
            # Ataque do inimigo
            for inimigo in inimigos:
                if hasattr(inimigo, 'morrendo') and inimigo.morrendo:
                    continue
                # Usa hitbox do player para colisão
                if inimigo.vivo and inimigo.ataque_acertou(player):
                    if not hasattr(inimigo, 'ja_acertou') or not inimigo.ja_acertou:
                        player.levar_dano()
                        som_colisao.play()
                        inimigo.ja_acertou = True
                else:
                    inimigo.ja_acertou = False
            # Colisão com inimigo (só se não estiver invencível)
            for inimigo in inimigos:
                if hasattr(inimigo, 'morrendo') and inimigo.morrendo:
                    continue
                if inimigo.vivo and inimigo.rect.colliderect(player.get_hitbox()) and not player.invencivel:
                    player.levar_dano()
                    som_colisao.play()
            # Checa fim da ronda
            if all(not inimigo.vivo for inimigo in inimigos):
                fala = f'Ronda {ronda} completa! Pegue os power-ups!'
                fala_timer = 120
                drop_itens = []
                # Drops mais distantes do player
                drop_offset = 180
                for i in range(2):
                    drop_itens.append({'tipo': 'vida', 'x': player.x + drop_offset + 60*i, 'y': player.y + 40, 'coletado': False})
                for i in range(1):
                    drop_itens.append({'tipo': 'power', 'x': player.x - drop_offset - 60*i, 'y': player.y + 40, 'coletado': False})
                tempo_espera = pygame.time.get_ticks()
                # Espera o player coletar e se preparar
                while any(not item['coletado'] for item in drop_itens) or pygame.time.get_ticks() - tempo_espera < 2000:
                    relogio.tick(fps)
                    checar_troca_musica()
                    for evento in pygame.event.get():
                        if evento.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                        player.mover(-1)
                    elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                        player.mover(1)
                    else:
                        if not player.atacando and not player.pulando:
                            player.acao = 'idle'
                    player.update()
                    tela.fill(BRANCO)
                    for idx, layer in enumerate(background_layers):
                        tela.blit(pygame.transform.scale(layer, (tela_largura, tela_altura)), (0, 0))
                    player.draw(tela)
                    for inimigo in inimigos:
                        inimigo.draw(tela)
                        if inimigo.vivo:
                            barra_w = 40
                            barra_h = 6
                            vida_pct = max(0, inimigo.vida / inimigo.vida_max)
                            barra_x = int(inimigo.x + inimigo.largura//2 - barra_w//2)
                            barra_y = int(inimigo.y - 12)
                            pygame.draw.rect(tela, (60,60,60), (barra_x, barra_y, barra_w, barra_h))
                            pygame.draw.rect(tela, (200,0,0), (barra_x, barra_y, int(barra_w*vida_pct), barra_h))
                    # Removido desenho dos hitboxes
                    for item in drop_itens:
                        if not item['coletado']:
                            cor = (0,200,0) if item['tipo']=='vida' else (0,0,200)
                            pygame.draw.circle(tela, cor, (int(item['x']), int(item['y'])), 16)
                            if player.rect.colliderect(pygame.Rect(item['x'], item['y'], 32, 32)):
                                item['coletado'] = True
                                if item['tipo']=='vida':
                                    player.vida = min(player.vida+1, player_stats['vida_max'])
                                else:
                                    player_stats['forca'] += 1
                                    fala = 'Forca aumentada!'
                                    fala_timer = 60
                    if fala_timer > 0 and fala:
                        texto_fala = fonte.render(fala, True, (30,30,30))
                        tela.blit(texto_fala, (tela_largura//2 - texto_fala.get_width()//2, 60))
                        fala_timer -= 1
                    pygame.display.flip()
                # Só passa de ronda se o player não morreu
                if player.vida > 0:
                    ronda += 1
                    # Aumenta vida máxima do player a cada rodada
                    player_stats['vida_max'] += 1
                    break
                else:
                    rodando = False
                    reset_ronda = True
            if player.vida <= 0:
                rodando = False
                reset_ronda = True
            # Remover parallax: desenha apenas o fundo fixo
            # Removido tela.fill(BRANCO) para evitar fundo branco
            for idx, layer in enumerate(background_layers):
                tela.blit(pygame.transform.scale(layer, (tela_largura, tela_altura)), (0, 0))
            # Desenha player e inimigos SEM offset de câmera
            player.draw(tela)
            for inimigo in inimigos:
                inimigo.draw(tela)
                # Barra de vida acima da cabeça do inimigo
                if inimigo.vivo:
                    barra_w = 40
                    barra_h = 6
                    vida_pct = max(0, inimigo.vida / inimigo.vida_max)
                    barra_x = int(inimigo.x + inimigo.largura//2 - barra_w//2)
                    barra_y = int(inimigo.y - 12)
                    pygame.draw.rect(tela, (60,60,60), (barra_x, barra_y, barra_w, barra_h))
                    pygame.draw.rect(tela, (200,0,0), (barra_x, barra_y, int(barra_w*vida_pct), barra_h))
            for i in range(player.vida):
                pygame.draw.rect(tela, (200,0,0), (20 + i*30, tela_altura-40, 24, 24), border_radius=6)
            # Exibe fala
            if fala_timer > 0 and fala:
                texto_fala = fonte.render(fala, True, (30,30,30))
                tela.blit(texto_fala, (tela_largura//2 - texto_fala.get_width()//2, 60))
                fala_timer -= 1
            # Substitui o texto por ícones de teclado na UI, com melhor espaçamento e alinhamento
            icon_size = 48
            icon_y = 20
            fonte_bold = pygame.font.Font('assets/font/Beholden/Beholden-Bold.ttf', 32)
            try:
                icon_space = pygame.image.load('assets/icons/keyboard/space.png').convert_alpha()
                icon_j = pygame.image.load('assets/icons/keyboard/J.png').convert_alpha()
                icon_a = pygame.image.load('assets/icons/keyboard/A.png').convert_alpha()
                icon_d = pygame.image.load('assets/icons/keyboard/D button.png').convert_alpha()
                icon_wide = int(icon_size * 1.5)
                x_space = 30
                x_j = x_space + icon_size*2 + 60
                x_a = x_j + icon_wide + 60
                x_d = x_a + icon_wide + 30
                tela.blit(pygame.transform.scale(icon_space, (icon_size*2, icon_size)), (x_space, icon_y))
                tela.blit(pygame.transform.scale(icon_j, (icon_wide, icon_size)), (x_j, icon_y))
                tela.blit(pygame.transform.scale(icon_a, (icon_wide, icon_size)), (x_a, icon_y))
                tela.blit(pygame.transform.scale(icon_d, (icon_wide, icon_size)), (x_d, icon_y))
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
            # Exibir FPS atual no canto superior direito
            fonte_fps = pygame.font.Font('assets/font/Beholden/Beholden-Regular.ttf', 24)
            fps_atual = int(relogio.get_fps())
            texto_fps = fonte_fps.render(f"FPS: {fps_atual}", True, (255,255,0))
            tela.blit(texto_fps, (tela_largura - texto_fps.get_width() - 20, 20))
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
    fonte_menu = pygame.font.Font('assets/font/Beholden/Beholden-Bold.ttf', 48)
    fonte_opcao = pygame.font.Font('assets/font/Beholden/Beholden-Regular.ttf', 32)
    opcoes = ['Iniciar', 'Opcoes', 'Sair']
    selecionado = 0
    while menu_ativo:
        checar_troca_musica()
        tela.fill((30, 10, 30))
        titulo = fonte_menu.render('Lost Samurai', True, (255, 255, 255))
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
                    elif opcoes[selecionado] == 'Opcoes':
                        menu_opcoes()
                    elif opcoes[selecionado] == 'Sair':
                        pygame.quit()
                        sys.exit()
            mouse_x, mouse_y = pygame.mouse.get_pos()
            mouse_clicked = False
            op_rects = []
            for i, opcao in enumerate(opcoes):
                cor = (255, 255, 0) if i == selecionado else (255, 255, 255)
                texto = fonte_opcao.render(opcao, True, cor)
                rect = texto.get_rect(center=(tela_largura//2, 180 + i*60))
                tela.blit(texto, rect)
                op_rects.append(rect)
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
                        elif opcoes[selecionado] == 'Opcoes':
                            menu_opcoes()
                        elif opcoes[selecionado] == 'Sair':
                            pygame.quit()
                            sys.exit()
                if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    mouse_clicked = True
            for i, rect in enumerate(op_rects):
                if rect.collidepoint(mouse_x, mouse_y):
                    selecionado = i
                    if mouse_clicked:
                        if opcoes[i] == 'Iniciar':
                            menu_ativo = False
                        elif opcoes[i] == 'Opcoes':
                            menu_opcoes()
                        elif opcoes[i] == 'Sair':
                            pygame.quit()
                            sys.exit()

def menu_ingame():
    fadeout_and_play_async(OST_MENU_INGAME)
    menu_ativo = True
    fonte_menu = pygame.font.Font('assets/font/Beholden/Beholden-Bold.ttf', 48)
    fonte_opcao = pygame.font.Font('assets/font/Beholden/Beholden-Regular.ttf', 32)
    opcoes = ['Voltar ao Jogo', 'Voltar ao Menu Principal', 'Opcoes', 'Sair do Jogo']
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
        op_rects = []  # Garante que op_rects sempre existe
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
                    elif opcoes[selecionado] == 'Opcoes':
                        menu_opcoes()
                    elif opcoes[selecionado] == 'Sair do Jogo':
                        pygame.quit()
                        sys.exit()
            mouse_x, mouse_y = pygame.mouse.get_pos()
            mouse_clicked = False
            op_rects = []
            for i, opcao in enumerate(opcoes):
                cor = (255, 255, 0) if i == selecionado else (255, 255, 255)
                texto = fonte_opcao.render(opcao, True, cor)
                rect = texto.get_rect(center=(tela_largura//2, 180 + i*60))
                tela.blit(texto, rect)
                op_rects.append(rect)
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
                        elif opcoes[selecionado] == 'Opcoes':
                            menu_opcoes()
                        elif opcoes[selecionado] == 'Sair do Jogo':
                            pygame.quit()
                            sys.exit()
                if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    mouse_clicked = True
        for i, rect in enumerate(op_rects):
            if rect.collidepoint(mouse_x, mouse_y):
                selecionado = i
                if mouse_clicked:
                    if opcoes[i] == 'Voltar ao Jogo':
                        return 'voltar'
                    elif opcoes[i] == 'Voltar ao Menu Principal':
                        return 'menu'
                    elif opcoes[i] == 'Opcoes':
                        menu_opcoes()
                    elif opcoes[i] == 'Sair do Jogo':
                        pygame.quit()
                        sys.exit()
                        
def menu_opcoes():
    global tela_largura, tela_altura, tela, fps
    fonte_menu = pygame.font.Font('assets/font/Beholden/Beholden-Bold.ttf', 48)
    fonte_opcao = pygame.font.Font('assets/font/Beholden/Beholden-Regular.ttf', 32)
    resolucoes = [(320, 180), (640, 360), (800, 600)]
    fps_opcoes = [30, 60, 120]
    opcoes = ['Volume Música', 'Volume SFX', 'Resolução', 'FPS', 'Voltar']
    selecionado = 0
    volume_musica = pygame.mixer.music.get_volume()
    volume_sfx = som_pulo.get_volume()
    resolucao_idx = next((i for i, r in enumerate(resolucoes) if r == (tela_largura, tela_altura)), 0)
    fps_idx = fps_opcoes.index(fps) if fps in fps_opcoes else 1
    while True:
        checar_troca_musica()
        tela.fill((30, 10, 30))
        titulo = fonte_menu.render('Opções', True, (255, 255, 255))
        tela.blit(titulo, (tela_largura//2 - titulo.get_width()//2, 60))
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_clicked = False
        op_rects = []
        for i, opcao in enumerate(opcoes):
            cor = (255, 255, 0) if i == selecionado else (255, 255, 255)
            if opcao == 'Volume Música':
                texto = fonte_opcao.render(f'{opcao}: {int(volume_musica*100)}%', True, cor)
            elif opcao == 'Volume SFX':
                texto = fonte_opcao.render(f'{opcao}: {int(volume_sfx*100)}%', True, cor)
            elif opcao == 'Resolução':
                res = f'{resolucoes[resolucao_idx][0]}x{resolucoes[resolucao_idx][1]}'
                texto = fonte_opcao.render(f'{opcao}: {res}', True, cor)
            elif opcao == 'FPS':
                texto = fonte_opcao.render(f'{opcao}: {fps_opcoes[fps_idx]}', True, cor)
            else:
                texto = fonte_opcao.render(opcao, True, cor)
            rect = texto.get_rect(center=(tela_largura//2, 180 + i*60 + 24))
            tela.blit(texto, rect)
            op_rects.append(rect)
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
                if evento.key == pygame.K_LEFT:
                    if selecionado == 0:
                        volume_musica = max(0, volume_musica - 0.1)
                        pygame.mixer.music.set_volume(volume_musica)
                    elif selecionado == 1:
                        volume_sfx = max(0, volume_sfx - 0.1)
                        som_pulo.set_volume(volume_sfx)
                        som_colisao.set_volume(volume_sfx)
                        som_ataque.set_volume(volume_sfx)
                    elif selecionado == 2:
                        resolucao_idx = (resolucao_idx - 1) % len(resolucoes)
                        tela_largura, tela_altura = resolucoes[resolucao_idx]
                        tela = pygame.display.set_mode((tela_largura, tela_altura))
                        atualizar_escala()
                    elif selecionado == 3:
                        fps_idx = (fps_idx - 1) % len(fps_opcoes)
                        fps = fps_opcoes[fps_idx]
                if evento.key == pygame.K_RIGHT:
                    if selecionado == 0:
                        volume_musica = min(1, volume_musica + 0.1)
                        pygame.mixer.music.set_volume(volume_musica)
                    elif selecionado == 1:
                        volume_sfx = min(1, volume_sfx + 0.1)
                        som_pulo.set_volume(volume_sfx)
                        som_colisao.set_volume(volume_sfx)
                        som_ataque.set_volume(volume_sfx)
                    elif selecionado == 2:
                        resolucao_idx = (resolucao_idx + 1) % len(resolucoes)
                        tela_largura, tela_altura = resolucoes[resolucao_idx]
                        tela = pygame.display.set_mode((tela_largura, tela_altura))
                        atualizar_escala()
                    elif selecionado == 3:
                        fps_idx = (fps_idx + 1) % len(fps_opcoes)
                        fps = fps_opcoes[fps_idx]
                if evento.key == pygame.K_ESCAPE or (evento.key == pygame.K_RETURN and selecionado == len(opcoes)-1):
                    return
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                mouse_clicked = True
        # Mouse hover/click
        for i, rect in enumerate(op_rects):
            if rect.collidepoint(mouse_x, mouse_y):
                selecionado = i
                if mouse_clicked:
                    if opcoes[i] == 'Voltar':
                        return
                    elif opcoes[i] == 'Volume Música':
                        volume_musica = min(1, volume_musica + 0.1)
                        pygame.mixer.music.set_volume(volume_musica)
                    elif opcoes[i] == 'Volume SFX':
                        volume_sfx = min(1, volume_sfx + 0.1)
                        som_pulo.set_volume(volume_sfx)
                        som_colisao.set_volume(volume_sfx)
                        som_ataque.set_volume(volume_sfx)
                    elif opcoes[i] == 'Resolução':
                        resolucao_idx = (resolucao_idx + 1) % len(resolucoes)
                        tela_largura, tela_altura = resolucoes[resolucao_idx]
                        tela = pygame.display.set_mode((tela_largura, tela_altura))
                    elif opcoes[i] == 'FPS':
                        fps_idx = (fps_idx + 1) % len(fps_opcoes)
                        fps = fps_opcoes[fps_idx]

# =====================
# EXECUÇÃO PRINCIPAL
# =====================
if __name__ == "__main__":
    menu_inicial()
    main()
