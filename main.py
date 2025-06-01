# Lost Samurai - Beat'em Up
# Desenvolvido por Grupo7 - 2025
# Jogo de ação e aventura 2D em Pygame
# Certifique-se de que o Pygame está instalado e os assets estão no diretório correto.

import pygame
import sys
import random
from player import Player
from obstacle import Enemy
from utils import carregar_icone, fade_in, fade_out, desenhar_texto_sombra
from hud import draw_hud
from audio import fadeout_and_play, fadeout_and_play_async, checar_troca_musica
from menus import menu_inicial, menu_ingame, tela_comandos

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
som_pulo = pygame.mixer.Sound('assets/sfx/Dirt Jump.ogg')
som_pouso = pygame.mixer.Sound('assets/sfx/Dirt Land.ogg')
som_colisao = pygame.mixer.Sound('assets/sfx/Sword Impact Hit 1.wav')
som_ataque = pygame.mixer.Sound('assets/sfx/Sword Attack 1.wav')
som_corrida = pygame.mixer.Sound('assets/sfx/Dirt Run 1.ogg')
som_defesa = pygame.mixer.Sound('assets/sfx/Sword Blocked 2.ogg')
som_pulo.set_volume(0.4)
som_colisao.set_volume(0.5)
som_ataque.set_volume(0.5)
som_corrida.set_volume(0.5)
som_defesa.set_volume(0.5)
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

# ===== HUD E MENU VISUAIS =====
# Remover as definições de desenhar_texto_sombra, fade_in, fade_out, carregar_icone daqui
def draw_hud(tela, player, vida_img=None, arma_img=None):
    # Vida com sombra e efeito de piscar/tremer
    for i in range(player.vida_max):
        x = 20 + i*40
        y = tela.get_height()-60
        if vida_img:
            img = vida_img.copy()
            if i < player.vida:
                if hasattr(player, 'levou_dano') and player.levou_dano and i == player.vida-1:
                    # Piscar/tremer
                    if pygame.time.get_ticks()//100 % 2 == 0:
                        img.set_alpha(120)
                        x += random.randint(-2,2)
                        y += random.randint(-2,2)
                else:
                    img.set_alpha(255)
            else:
                img.set_alpha(60)
            tela.blit(img, (x, y))
        else:
            cor = (200,0,0) if i < player.vida else (80,30,30)
            pygame.draw.rect(tela, cor, (x, y, 32, 32), border_radius=8)
    # Arma equipada
    if arma_img:
        tela.blit(arma_img, (20, tela.get_height()-110))
    # Sombra/brilho nos textos HUD
    fonte = pygame.font.Font('assets/font/Beholden/Beholden-Bold.ttf', 28)
    desenhar_texto_sombra(tela, f'Rodada: {getattr(player, "ronda", "-")}', fonte, (255,255,255), (0,0,0), (tela.get_width()-180, tela.get_height()-50))

# =====================
# CUTSCENE INICIAL
# =====================
def cutscene_inicial(tela, tela_largura, tela_altura):
    """Exibe a cutscene inicial com a história e objetivo do jogador, com visual aprimorado."""
    fonte_titulo = pygame.font.Font('assets/font/Beholden/Beholden-Bold.ttf', 60)
    fonte_texto = pygame.font.Font('assets/font/Beholden/Beholden-Regular.ttf', 32)
    fonte_objetivo = pygame.font.Font('assets/font/Beholden/Beholden-Bold.ttf', 36)
    historia = [
        "Em um Japão feudal devastado pela guerra,",
        "um samurai sem mestre busca redenção.",
        "",
        "Seu objetivo:",
        f"Sobreviver às ondas de inimigos e restaurar sua honra!",
        f"Derrote todos os inimigos em cada rodada.",
        f"Sobreviva até a rodada {MAX_RONDAS} para vencer!"
    ]
    rodando = True
    timer = 0
    alpha = 0
    fadein_speed = 6
    while rodando:
        # Fundo gradiente escuro
        for y in range(tela_altura):
            cor = (10 + y//16, 10 + y//24, 30 + y//12)
            pygame.draw.line(tela, cor, (0, y), (tela_largura, y))
        # Caixa translúcida para o texto
        caixa = pygame.Surface((tela_largura-120, 380), pygame.SRCALPHA)
        caixa.fill((20, 20, 40, 180))
        tela.blit(caixa, (60, 120))
        # Título com sombra e brilho
        titulo = fonte_titulo.render('Lost Samurai', True, (255, 255, 255))
        sombra = fonte_titulo.render('Lost Samurai', True, (40, 40, 80))
        tela.blit(sombra, (tela_largura//2 - titulo.get_width()//2 + 4, 74))
        tela.blit(titulo, (tela_largura//2 - titulo.get_width()//2, 70))
        # Fade-in do texto
        if alpha < 255:
            alpha = min(255, alpha + fadein_speed)
        y = 150
        for i, linha in enumerate(historia):
            if i == 3:
                # "Seu objetivo:" destacado
                texto = fonte_objetivo.render(linha, True, (255, 255, 80))
                texto.set_alpha(alpha)
                tela.blit(texto, (tela_largura//2 - texto.get_width()//2, y))
                y += 44
            elif i > 3:
                # Objetivo com brilho amarelo
                texto = fonte_texto.render(linha, True, (255, 230, 120))
                texto.set_alpha(alpha)
                tela.blit(texto, (tela_largura//2 - texto.get_width()//2, y))
                y += 38
            else:
                # História normal
                texto = fonte_texto.render(linha, True, (220, 220, 220))
                texto.set_alpha(alpha)
                tela.blit(texto, (tela_largura//2 - texto.get_width()//2, y))
                y += 38
        # Caixa e instrução para continuar
        instrucao_caixa = pygame.Surface((tela_largura, 50), pygame.SRCALPHA)
        instrucao_caixa.fill((0,0,0,120))
        tela.blit(instrucao_caixa, (0, tela_altura - 90))
        instrucao = fonte_texto.render('Pressione ESPACO para continuar', True, (255, 255, 0))
        instrucao.set_alpha(alpha)
        tela.blit(instrucao, (tela_largura//2 - instrucao.get_width()//2, tela_altura - 80))
        pygame.display.flip()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN and alpha >= 200:
                if evento.key == pygame.K_SPACE:
                    rodando = False
        timer += 1
        pygame.time.delay(12)

# =====================
# LOOP PRINCIPAL DO JOGO
# =====================

MAX_RONDAS = 10  # Número máximo de rodadas

def cutscene_inicial(tela, tela_largura, tela_altura):
    """Exibe a cutscene inicial com a história e objetivo do jogador."""
    fonte_titulo = pygame.font.Font('assets/font/Beholden/Beholden-Bold.ttf', 48)
    fonte_texto = pygame.font.Font('assets/font/Beholden/Beholden-Regular.ttf', 32)
    historia = [
        "Em um Japão feudal devastado pela guerra,",
        "um samurai sem mestre busca redenção.",
        "\nSeu objetivo: sobreviver às ondas de inimigos",
        "e restaurar sua honra perdida!",
        "\nDerrote todos os inimigos em cada rodada.",
        f"Sobreviva até a rodada {MAX_RONDAS} para vencer!"
    ]
    rodando = True
    timer = 0
    while rodando:
        tela.fill((20, 10, 30))
        titulo = fonte_titulo.render('Lost Samurai', True, (255, 255, 255))
        tela.blit(titulo, (tela_largura//2 - titulo.get_width()//2, 60))
        y = 180
        for linha in historia:
            texto = fonte_texto.render(linha, True, (220, 220, 220))
            tela.blit(texto, (tela_largura//2 - texto.get_width()//2, y))
            y += 50
        instrucao = fonte_texto.render('Pressione ESPAÇO para continuar', True, (255, 255, 0))
        tela.blit(instrucao, (tela_largura//2 - instrucao.get_width()//2, tela_altura - 80))
        pygame.display.flip()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    rodando = False
        timer += 1

# =====================
# LOOP PRINCIPAL DO JOGO
# =====================
def main():
    while True:
        # Exibe o menu inicial e aguarda ação do jogador
        acao = menu_inicial(tela, tela_largura, tela_altura, OST_MENU, background_layers, menu_opcoes, tela_comandos)
        if acao == 'iniciar' or acao is None:
            # Exibe a cutscene apenas ao iniciar o jogo
            cutscene_inicial(tela, tela_largura, tela_altura)
            break
        elif acao == 'sair':
            pygame.quit()
            sys.exit()
    fadeout_and_play(OST_COMBATE)  # Troca imediatamente para música de combate ao entrar no jogo
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
        player.ronda = ronda  # Atualiza o atributo ronda do player para o HUD
        inimigos = []
        popups = []  # lista de popups de dano
        # Sistema de spawn dinâmico por ronda
        def gerar_inimigos(ronda):
            lista = []
            # Sempre só um inimigo por rodada
            tipo = Enemy
            x = tela_largura // 2 + random.randint(-100, 100)
            y = tela_altura - 64
            side = None
            inimigo = tipo(x, y, spawn_side=side)
            # Escala atributos conforme a rodada
            inimigo.vida = inimigo.vida_max = 3 + ronda  # Vida aumenta a cada rodada
            inimigo.velocidade = 1 + 0.3 * ronda         # Velocidade aumenta
            inimigo.forca = 1 + ronda // 2 if hasattr(inimigo, 'forca') else None  # Dano aumenta
            inimigo.distancia_visao = 180 + 10 * ronda   # Visão aumenta
            inimigo.distancia_ataque = 48 + 2 * ronda    # Alcance aumenta
            lista.append(inimigo)
            return lista
        inimigos = gerar_inimigos(ronda)
        fonte = pygame.font.Font('assets/font/Beholden/Beholden-Medium.ttf', 36)
        rodando = True
        game_over = False
        combate_ativo = False
        ost_atual = OST_COMBATE  # Música padrão é sempre a de combate
        camera_x = 0
        drop_itens = []
        ultimo_estado_corrida = False
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
        # Carregar imagens do HUD (vida, arma) uma vez
        vida_img = carregar_icone('HUD/heart.png')
        arma_img = carregar_icone('HUD/sword.png')
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
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        acao = menu_ingame(tela, tela_largura, tela_altura, OST_MENU_INGAME, menu_opcoes, tela_comandos)
                        if acao == 'menu':
                            menu_inicial(tela, tela_largura, tela_altura, OST_MENU, background_layers, menu_opcoes, tela_comandos)
                            return  # Sai do main atual, voltando para o menu inicial
                    if evento.key == pygame.K_SPACE:
                        player.pular()
                        som_pulo.play()
                    if evento.key == pygame.K_j or evento.key == pygame.K_z:
                        player.atacar()
                        som_ataque.play()
                    if evento.key == pygame.K_k or evento.key == pygame.K_DOWN:
                        player.defender(True)
                if evento.type == pygame.KEYUP:
                    if evento.key == pygame.K_k or evento.key == pygame.K_DOWN:
                        player.defender(False)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                player.mover(-1)
            elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                player.mover(1)
            else:
                if not player.atacando and not player.pulando and not player.defendendo:
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
                        if not hasattr(inimigo, 'ja_acertou_player') or not inimigo.ja_acertou_player:
                            dano = player.forca if hasattr(player, 'forca') else 1
                            inimigo.levar_dano(dano)
                            som_colisao.play()
                            popups.append({'dano': dano, 'x': inimigo.x + inimigo.largura//2, 'y': inimigo.y - 20, 'timer': 30})
                            inimigo.ja_acertou_player = True
                # Reset flag quando ataque termina
                if not player.atacando:
                    for inimigo in inimigos:
                        inimigo.ja_acertou_player = False
            else:
                for inimigo in inimigos:
                    inimigo.ja_acertou_player = False
            # Ataque do inimigo
            for inimigo in inimigos:
                if hasattr(inimigo, 'morrendo') and inimigo.morrendo:
                    continue
                # Usa hitbox do player para colisão
                if inimigo.vivo and inimigo.ataque_acertou(player):
                    if not hasattr(inimigo, 'ja_acertou') or not inimigo.ja_acertou:
                        inimigo.causar_dano(player)
                        som_colisao.play()
                        inimigo.ja_acertou = True
                else:
                    inimigo.ja_acertou = False
            # Colisão com inimigo (só se não estiver invencível)
            for inimigo in inimigos:
                if hasattr(inimigo, 'morrendo') and inimigo.morrendo:
                    continue
                if inimigo.vivo and inimigo.rect.colliderect(player.get_hitbox()) and not player.invencivel:
                    inimigo.causar_dano(player)
                    som_colisao.play()
            # Checa fim da ronda
            if all(not inimigo.vivo for inimigo in inimigos):
                fala = f'Ronda {ronda} completa! Pegue os power-ups!'
                fala_timer = 120
                drop_itens = []
                # Drops mais distantes do player
                drop_offset = 180
                for i in range(2):
                    x_spawn = max(0, min(tela_largura - 32, player.x + drop_offset + 60*i))
                    drop_itens.append({'tipo': 'vida', 'x': x_spawn, 'y': min(player.y + 40, tela_altura - 32), 'coletado': False})
                for i in range(1):
                    x_spawn = max(0, min(tela_largura - 32, player.x - drop_offset - 60*i))
                    drop_itens.append({'tipo': 'power', 'x': x_spawn, 'y': min(player.y + 40, tela_altura - 32), 'coletado': False})
                tempo_espera = pygame.time.get_ticks()
                # Espera o player coletar e se preparar
                while any(not item['coletado'] for item in drop_itens) or pygame.time.get_ticks() - tempo_espera < 2000:
                    relogio.tick(fps)
                    checar_troca_musica()
                    for evento in pygame.event.get():
                        if evento.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        if evento.type == pygame.KEYDOWN:
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
                    if ronda >= MAX_RONDAS:
                        # Vitória!
                        fala = f'Parabéns! Você sobreviveu até a rodada {MAX_RONDAS}!'
                        fala_timer = 180
                        while fala_timer > 0:
                            relogio.tick(fps)
                            for evento in pygame.event.get():
                                if evento.type == pygame.QUIT:
                                    pygame.quit()
                                    sys.exit()
                            for idx, layer in enumerate(background_layers):
                                tela.blit(pygame.transform.scale(layer, (tela_largura, tela_altura)), (0, 0))
                            texto_fala = fonte.render(fala, True, (30,200,30))
                            tela.blit(texto_fala, (tela_largura//2 - texto_fala.get_width()//2, 60))
                            pygame.display.flip()
                            fala_timer -= 1
                        rodando = False
                        game_over = True  # Exibe tela de Game Over (pode customizar para tela de vitória)
                        break
                    ronda += 1
                    player_stats['vida_max'] += 1
                    break
                else:
                    rodando = False
                    game_over = True  # Marca para exibir Game Over
            if player.vida <= 0:
                rodando = False
                game_over = True  # Marca para exibir Game Over
            # Remover parallax: desenha apenas o fundo fixo
            # Removido tela.fill(BRANCO) para evitar fundo branco
            for idx, layer in enumerate(background_layers):
                tela.blit(pygame.transform.scale(layer, (tela_largura, tela_altura)), (0, 0))
            # Desenha player e inimigos SEM offset de câmera
            for inimigo in inimigos:
                inimigo.draw(tela)
                # Barra de vida estilizada do inimigo
                if inimigo.vivo:
                    barra_w = 56
                    barra_h = 12
                    vida_pct = max(0, inimigo.vida / inimigo.vida_max)
                    barra_x = int(inimigo.x + inimigo.largura//2 - barra_w//2)
                    barra_y = int(inimigo.y - 24)
                    pygame.draw.rect(tela, (40,40,40), (barra_x, barra_y, barra_w, barra_h), border_radius=8)
                    pygame.draw.rect(tela, (220,40,40), (barra_x+2, barra_y+2, int((barra_w-4)*vida_pct), barra_h-4), border_radius=6)
                    if vida_pct > 0:
                        pygame.draw.rect(tela, (255,180,180), (barra_x+2, barra_y+2, int((barra_w-4)*vida_pct), 4), border_radius=3)
            # EFEITO VISUAL DE DEFESA
            if hasattr(player, 'defendendo') and player.defendendo:
                player.draw(tela)
                s = pygame.Surface((player.largura, player.altura), pygame.SRCALPHA)
                s.fill((60, 180, 255, 90))
                tela.blit(s, (player.x, player.y))
                if hasattr(player, 'defesa_cooldown') and player.defesa_cooldown > 0:
                    cooldown_pct = player.defesa_cooldown / getattr(player, 'defesa_cooldown_max', 60)
                    pygame.draw.arc(tela, (60,180,255), (player.x+player.largura//2-18, player.y-28, 36, 36), 0, 2*3.14*cooldown_pct, 6)
            else:
                player.draw(tela)
                if hasattr(player, 'defesa_cooldown') and player.defesa_cooldown > 0:
                    cooldown_pct = player.defesa_cooldown / getattr(player, 'defesa_cooldown_max', 60)
                    pygame.draw.rect(tela, (60,180,255), (player.x+player.largura//2-20, player.y-18, int(40*cooldown_pct), 6), border_radius=3)
            # Indicativo de dano: popups animados
            for popup in popups[:]:
                alpha = int(255 * (popup['timer']/30))
                fonte_popup = pygame.font.Font('assets/font/Beholden/Beholden-Bold.ttf', 28)
                texto = fonte_popup.render(f"-{popup['dano']}", True, (255,80,80))
                texto.set_alpha(alpha)
                x = popup['x']
                y = popup['y'] - (30 - popup['timer'])
                tela.blit(texto, (x - texto.get_width()//2, y))
                popup['timer'] -= 1
                if popup['timer'] <= 0:
                    popups.remove(popup)
            # HUD estilizado
            draw_hud(tela, player, vida_img, arma_img)
            # Exibe fala
            if fala_timer > 0 and fala:
                texto_fala = fonte.render(fala, True, (30,30,30))
                tela.blit(texto_fala, (tela_largura//2 - texto_fala.get_width()//2, 60))
                fala_timer -= 1
            # Remove exibição dos comandos/ícones de teclado da tela principal
            # Exibir FPS atual no canto superior direito
            fonte_fps = pygame.font.Font('assets/font/Beholden/Beholden-Regular.ttf', 24)
            fps_atual = int(relogio.get_fps())
            texto_fps = fonte_fps.render(f"FPS: {fps_atual}", True, (255,255,0))
            tela.blit(texto_fps, (tela_largura - texto_fps.get_width() - 20, 20))
            pygame.display.flip()
        # Exibe tela de Game Over apenas se o player perdeu
        if game_over:
            if ronda > MAX_RONDAS:
                # Tela de vitória
                while True:
                    tela.fill(BRANCO)
                    texto_vitoria = fonte.render("VOCÊ VENCEU!", True, (0, 180, 0))
                    texto_restart = fonte.render("Pressione ESPAÇO para jogar novamente", True, (0, 0, 0))
                    tela.blit(texto_vitoria, (tela_largura//2 - texto_vitoria.get_width()//2, tela_altura//2 - 60))
                    tela.blit(texto_restart, (tela_largura//2 - texto_restart.get_width()//2, tela_altura//2 + 40))
                    pygame.display.flip()
                    for evento in pygame.event.get():
                        if evento.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        if evento.type == pygame.KEYDOWN:
                            if evento.key == pygame.K_SPACE:
                                game_over = False
                                reset_ronda = True
                                break
                if not game_over:
                    break
            else:
                while True:
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
                                game_over = False
                                reset_ronda = True
                                break
                if not game_over:
                    break

def menu_ingame(tela, tela_largura, tela_altura, musica_fadeout, menu_opcoes, tela_comandos):
    from audio import fadeout_and_play_async
    fadeout_and_play_async(musica_fadeout)
    menu_ativo = True
    fonte_menu = pygame.font.Font('assets/font/Beholden/Beholden-Bold.ttf', 48)
    fonte_opcao = pygame.font.Font('assets/font/Beholden/Beholden-Regular.ttf', 32)
    opcoes = ['Voltar ao Jogo', 'Voltar ao Menu Principal', 'Opcoes', 'Comandos', 'Sair do Jogo']
    selecionado = 0
    while menu_ativo:
        checar_troca_musica()
        tela.fill((30, 10, 30))
        titulo = fonte_menu.render('Menu', True, (255, 255, 255))
        tela.blit(titulo, (tela_largura//2 - titulo.get_width()//2, 60))
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_clicked = False
        op_rects = []
        for i, opcao in enumerate(opcoes):
            cor = (255, 255, 0) if i == selecionado else (255, 255, 255)
            sombra = (60, 60, 0) if i == selecionado else (0, 0, 0)
            y = 180 + i*60
            if i == selecionado:
                pygame.draw.rect(tela, (255,255,180), (tela_largura//2-180, y-10, 360, 54), border_radius=16)
                pygame.draw.rect(tela, (200,200,80), (tela_largura//2-180, y-10, 360, 54), 4, border_radius=16)
            sombra_surf = fonte_opcao.render(opcao, True, sombra)
            tela.blit(sombra_surf, (tela_largura//2 - fonte_opcao.size(opcao)[0]//2 + 2, y + 2))
            texto = fonte_opcao.render(opcao, True, cor)
            tela.blit(texto, (tela_largura//2 - texto.get_width()//2, y))
            rect = pygame.Rect(tela_largura//2-180, y-10, 360, 54)
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
                        menu_opcoes(tela, tela_largura, tela_altura)
                    elif opcoes[selecionado] == 'Comandos':
                        tela_comandos(tela, tela_largura, tela_altura)
                    elif opcoes[selecionado] == 'Sair do Jogo':
                        pygame.quit()
                        sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                mouse_clicked = True
        for i, rect in enumerate(op_rects):
            if rect.collidepoint(mouse_x, mouse_y):
                if i != selecionado:
                    selecionado = i
                if mouse_clicked:
                    if opcoes[i] == 'Voltar ao Jogo':
                        return 'voltar'
                    elif opcoes[i] == 'Voltar ao Menu Principal':
                        return 'menu'
                    elif opcoes[i] == 'Opcoes':
                        menu_opcoes(tela, tela_largura, tela_altura)
                    elif opcoes[i] == 'Comandos':
                        tela_comandos(tela, tela_largura, tela_altura)
                    elif opcoes[i] == 'Sair do Jogo':
                        pygame.quit()
                        sys.exit()

def menu_opcoes(tela_arg, tela_largura_arg, tela_altura_arg):
    global tela_largura, tela_altura, tela, fps
    tela_largura = tela_largura_arg
    tela_altura = tela_altura_arg
    tela = tela_arg
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
            sombra = (60, 60, 0) if i == selecionado else (0, 0, 0)
            y = 180 + i*60
            if opcao == 'Volume Música':
                texto_str = f'{opcao}: {int(volume_musica*100)}%'
            elif opcao == 'Volume SFX':
                texto_str = f'{opcao}: {int(volume_sfx*100)}%'
            elif opcao == 'Resolução':
                res = f'{resolucoes[resolucao_idx][0]}x{resolucoes[resolucao_idx][1]}'
                texto_str = f'{opcao}: {res}'
            elif opcao == 'FPS':
                texto_str = f'{opcao}: {fps_opcoes[fps_idx]}'
            else:
                texto_str = opcao
            texto = fonte_opcao.render(texto_str, True, cor)
            sombra_surf = fonte_opcao.render(texto_str, True, sombra)
            if i == selecionado:
                pygame.draw.rect(tela, (255,255,180), (tela_largura//2-180, y-10, 360, 54), border_radius=16)
                pygame.draw.rect(tela, (200,200,80), (tela_largura//2-180, y-10, 360, 54), 4, border_radius=16)
            tela.blit(sombra_surf, (tela_largura//2 - texto.get_width()//2 + 2, y + 2))
            tela.blit(texto, (tela_largura//2 - texto.get_width()//2, y))
            rect = pygame.Rect(tela_largura//2-180, y-10, 360, 54)
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
        for i, rect in enumerate(op_rects):
            if rect.collidepoint(mouse_x, mouse_y):
                if i != selecionado:
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

def tela_comandos(tela, tela_largura, tela_altura):
    fonte = pygame.font.Font('assets/font/Beholden/Beholden-Bold.ttf', 40)
    fonte_cmd = pygame.font.Font('assets/font/Beholden/Beholden-Regular.ttf', 28)
    comandos = [
        ("Pular", "Espaco"),
        ("Atacar", "J ou Z"),
        ("Defender", "K ou Seta Baixo"),
        ("Mover", "A/D ou Setas"),
        ("Menu/Pause", "ESC")
    ]
    rodando = True
    selecionado = 0
    while rodando:
        tela.fill((30, 10, 30))
        titulo = fonte.render('Comandos', True, (255, 255, 255))
        tela.blit(titulo, (tela_largura//2 - titulo.get_width()//2, 60))
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_clicked = False
        op_rects = []
        for i, (acao, tecla) in enumerate(comandos):
            cor = (255,255,0) if i==selecionado else (255,255,200)
            sombra = (60,60,0) if i==selecionado else (0,0,0)
            y = 160 + i*50
            if i==selecionado:
                pygame.draw.rect(tela, (255,255,180), (tela_largura//2-180, y-10, 360, 44), border_radius=14)
                pygame.draw.rect(tela, (200,200,80), (tela_largura//2-180, y-10, 360, 44), 3, border_radius=14)
            sombra_surf = fonte_cmd.render(f'{acao}: {tecla}', True, sombra)
            tela.blit(sombra_surf, (tela_largura//2 - fonte_cmd.size(f'{acao}: {tecla}')[0]//2 + 2, y + 2))
            texto = fonte_cmd.render(f'{acao}: {tecla}', True, cor)
            tela.blit(texto, (tela_largura//2 - texto.get_width()//2, y))
            rect = pygame.Rect(tela_largura//2-180, y-10, 360, 44)
            op_rects.append(rect)
        texto_voltar = fonte_cmd.render('Pressione ESC para voltar', True, (180,180,180))
        tela.blit(texto_voltar, (tela_largura//2 - texto_voltar.get_width()//2, tela_altura-80))
        pygame.display.flip()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key in [pygame.K_UP, pygame.K_w]:
                    selecionado = (selecionado - 1) % len(comandos)
                if evento.key in [pygame.K_DOWN, pygame.K_s]:
                    selecionado = (selecionado + 1) % len(comandos)
                if evento.key == pygame.K_ESCAPE:
                    rodando = False
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                mouse_clicked = True
        for i, rect in enumerate(op_rects):
            if rect.collidepoint(mouse_x, mouse_y):
                if i != selecionado:
                    selecionado = i

if __name__ == "__main__":
    main()
