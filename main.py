import pygame
import sys
from player import Player
from obstacle import Enemy, MushroomEnemy, FlyingEnemy

# Lost Samurai - Beat'em Up
# Um jogo de ação e aventura em 2D, onde você controla um samurai pixelado em uma jornada épica por um mundo sombrio e pixelado. Enfrente inimigos variados, colete power-ups e descubra segredos enquanto luta para restaurar a paz.
# Desenvolvido por Grupo7 - 2025
# Importante: Certifique-se de que o Pygame está instalado e que os arquivos de assets estão no diretório correto.

# Configurações iniciais
# Aumenta a resolução da tela para 1280x720 (HD), mantendo proporção 16:9
# Isso não afeta a velocidade dos sprites se fps for mantido
# Ajuste os backgrounds para 1280x720 para melhor visual

tela_largura = 1280
tela_altura = 720
fps = 60 # Quantos frames por segundo o jogo irá rodar

# Inicialização do Pygame
pygame.init() # Inicializando o Pygame
pygame.mixer.init() # Inicializando o mixer para sons
tela = pygame.display.set_mode((tela_largura, tela_altura)) # Criando a tela
pygame.display.set_caption("Lost Samurai – Beat'Em Up") # Definindo o titulo da janela
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
        import random
        # Otimização: impede sobreposição de inimigos ao spawnar
        def gerar_inimigos(ronda):
            lista = []
            posicoes = list(range(200, tela_largura-200, 120))
            random.shuffle(posicoes)
            usados = set()
            for i in range(ronda + 2):
                tipo = Enemy
                if ronda > 2 and i % 3 == 0:
                    tipo = MushroomEnemy
                if ronda > 4 and i % 4 == 0:
                    tipo = FlyingEnemy
                # Garante que não repete posição
                for _ in range(10):
                    x = posicoes[i % len(posicoes)] + random.randint(-30, 30)
                    if x not in usados:
                        usados.add(x)
                        break
                else:
                    x = posicoes[i % len(posicoes)]
                y = tela_altura - 64 if tipo != FlyingEnemy else tela_altura - 180
                side = random.choice(['left', 'right'])
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
                    if inimigo.vivo and ataque_rect.colliderect(inimigo.rect):
                        dano = player.forca if hasattr(player, 'forca') else 1
                        inimigo.levar_dano(dano)
                        som_colisao.play()
                        popups.append({'dano': dano, 'x': inimigo.x + inimigo.largura//2, 'y': inimigo.y - 20, 'timer': 30})
                        player.atacando = False
                        break
            # Ataque do inimigo
            for inimigo in inimigos:
                if hasattr(inimigo, 'morrendo') and inimigo.morrendo:
                    continue
                if inimigo.vivo and inimigo.ataque_acertou(player):
                    player.levar_dano()
                    som_colisao.play()
            # Colisão com inimigo (só se não estiver invencível)
            for inimigo in inimigos:
                if hasattr(inimigo, 'morrendo') and inimigo.morrendo:
                    continue
                if inimigo.vivo and inimigo.colidiu(player) and not player.invencivel:
                    player.levar_dano()
                    som_colisao.play()
            # Checa fim da ronda
            if all(not inimigo.vivo for inimigo in inimigos):
                fala = f'Ronda {ronda} completa! Pegue os power-ups!'
                fala_timer = 120
                drop_itens = []
                for i in range(2):
                    drop_itens.append({'tipo': 'vida', 'x': player.x + 60*i, 'y': player.y + 40, 'coletado': False})
                for i in range(1):
                    drop_itens.append({'tipo': 'power', 'x': player.x - 60*i, 'y': player.y + 40, 'coletado': False})
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
                    # Fundo: desenha todas as camadas do background em ordem (sempre, não só na tela de powerup)
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
                    # Desenha hitbox do player
                    pygame.draw.rect(tela, (0, 0, 255), player.rect, 2)
                    # Desenha hitbox dos inimigos
                    for inimigo in inimigos:
                        pygame.draw.rect(tela, (255, 0, 0), inimigo.rect, 2)
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
                    # Exibe fala do personagem sempre que fala_timer > 0
                    if fala_timer > 0 and fala:
                        texto_fala = fonte.render(fala, True, (30,30,30))
                        tela.blit(texto_fala, (tela_largura//2 - texto_fala.get_width()//2, 60))
                        fala_timer -= 1
                    pygame.display.flip()
                # Só passa de ronda se o player não morreu
                if player.vida > 0:
                    ronda += 1
                    break
                else:
                    rodando = False
                    reset_ronda = True
            if player.vida <= 0:
                rodando = False
                reset_ronda = True
            tela.fill(BRANCO)
            # Remover parallax: desenha apenas o fundo fixo
            tela.blit(pygame.transform.scale(background_layers[0], (tela_largura, tela_altura)), (0, 0))
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
            # Desenha hitbox do player
            pygame.draw.rect(tela, (0, 0, 255), player.rect, 2)
            # Desenha hitbox dos inimigos
            for inimigo in inimigos:
                pygame.draw.rect(tela, (255, 0, 0), inimigo.rect, 2)
            for i in range(player.vida):
                pygame.draw.rect(tela, (200,0,0), (20 + i*30, tela_altura-40, 24, 24), border_radius=6)
            # Exibe fala
            if fala_timer > 0:
                texto_fala = fonte.render(fala, True, (30,30,30))
                tela.blit(texto_fala, (tela_largura//2 - texto_fala.get_width()//2, 60))
                fala_timer -= 1
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
                        # Placeholder para opções futuras
                        pass
                    elif opcoes[selecionado] == 'Sair':
                        pygame.quit()
                        sys.exit()

def menu_ingame():
    fadeout_and_play_async(OST_MENU_INGAME)
    menu_ativo = True
    fonte_menu = pygame.font.Font('assets/font/Beholden/Beholden-Bold.ttf', 48)
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
