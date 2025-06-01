import pygame
import sys
from utils import carregar_icone, fade_in, fade_out, desenhar_texto_sombra
from audio import fadeout_and_play_async, checar_troca_musica

def menu_inicial(tela, tela_largura, tela_altura, OST_MENU, background_layers, menu_opcoes, tela_comandos):
    fade_in(tela, (0,0,0), duracao=24)
    fadeout_and_play_async(OST_MENU)
    menu_ativo = True
    fonte_menu = pygame.font.Font('assets/font/Beholden/Beholden-Bold.ttf', 64)
    fonte_opcao = pygame.font.Font('assets/font/Beholden/Beholden-Regular.ttf', 36)
    opcoes = ['Jogar', 'Opcoes', 'Comandos', 'Sair']
    icones = ['assets/icons/keyboard/space.png', 'assets/icons/keyboard/settings.png', 'assets/icons/keyboard/help.png', 'assets/icons/keyboard/exit.png']
    selecionado = 0
    som_nav = pygame.mixer.Sound('assets/sfx/Movimento.ogg')
    som_nav.set_volume(0.5)
    cursor_img = carregar_icone('HUD/cursor.png')
    parallax_offset = 0
    while menu_ativo:
        checar_troca_musica()
        parallax_offset = (parallax_offset + 0.5) % tela_largura
        for idx, layer in enumerate(background_layers):
            speed = 0.2 + idx*0.05
            x = int(-parallax_offset*speed) % tela_largura
            tela.blit(pygame.transform.scale(layer, (tela_largura, tela_altura)), (x, 0))
            if x > 0:
                tela.blit(pygame.transform.scale(layer, (tela_largura, tela_altura)), (x-tela_largura, 0))
        desenhar_texto_sombra(tela, 'Lost Samurai', fonte_menu, (255,255,255), (0,0,0), (tela_largura//2-220, 60))
        for i, opcao in enumerate(opcoes):
            y = 220 + i*80
            cor = (255,255,0) if i==selecionado else (255,255,255)
            sombra = (60,60,0) if i==selecionado else (0,0,0)
            if i==selecionado:
                pygame.draw.rect(tela, (255,255,180), (tela_largura//2-180, y-10, 360, 60), border_radius=18)
                pygame.draw.rect(tela, (200,200,80), (tela_largura//2-180, y-10, 360, 60), 4, border_radius=18)
            if i < len(icones):
                icone = carregar_icone(icones[i])
                if icone:
                    tela.blit(pygame.transform.scale(icone, (48,48)), (tela_largura//2-160, y))
            desenhar_texto_sombra(tela, opcao, fonte_opcao, cor, sombra, (tela_largura//2-90, y+8))
        if cursor_img:
            tela.blit(cursor_img, (tela_largura//2-200, 220 + selecionado*80 + 8))
        pygame.display.flip()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                fade_out(tela, (0,0,0), duracao=18)
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key in [pygame.K_UP, pygame.K_w]:
                    selecionado = (selecionado - 1) % len(opcoes)
                    som_nav.play()
                if evento.key in [pygame.K_DOWN, pygame.K_s]:
                    selecionado = (selecionado + 1) % len(opcoes)
                    som_nav.play()
                if evento.key == pygame.K_RETURN or evento.key == pygame.K_SPACE:
                    if opcoes[selecionado] == 'Jogar':
                        return
                    elif opcoes[selecionado] == 'Opcoes':
                        menu_opcoes(tela, tela_largura, tela_altura)
                    elif opcoes[selecionado] == 'Comandos':
                        tela_comandos(tela, tela_largura, tela_altura)
                    elif opcoes[selecionado] == 'Sair':
                        pygame.quit()
                        sys.exit()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_clicked = False
        op_rects = []
        for i, opcao in enumerate(opcoes):
            y = 220 + i*80
            rect = pygame.Rect(tela_largura//2-180, y-10, 360, 60)
            op_rects.append(rect)
        for evento in pygame.event.get():
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                mouse_clicked = True
        for i, rect in enumerate(op_rects):
            if rect.collidepoint(mouse_x, mouse_y):
                if i != selecionado:
                    selecionado = i
                    som_nav.play()
                if mouse_clicked:
                    fade_out(tela, (0,0,0), duracao=18)
                    if opcoes[i] == 'Jogar':
                        return
                    elif opcoes[i] == 'Opcoes':
                        menu_opcoes(tela, tela_largura, tela_altura)
                        fade_in(tela, (0,0,0), duracao=18)
                    elif opcoes[i] == 'Comandos':
                        tela_comandos(tela, tela_largura, tela_altura)
                    elif opcoes[i] == 'Sair':
                        pygame.quit()
                        sys.exit()

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
    while rodando:
        tela.fill((30, 10, 30))
        titulo = fonte.render('Comandos', True, (255, 255, 255))
        tela.blit(titulo, (tela_largura//2 - titulo.get_width()//2, 60))
        for i, (acao, tecla) in enumerate(comandos):
            texto = fonte_cmd.render(f'{acao}: {tecla}', True, (255,255,200))
            tela.blit(texto, (tela_largura//2 - texto.get_width()//2, 160 + i*50))
        texto_voltar = fonte_cmd.render('Pressione ESC para voltar', True, (180,180,180))
        tela.blit(texto_voltar, (tela_largura//2 - texto_voltar.get_width()//2, tela_altura-80))
        pygame.display.flip()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                rodando = False

def menu_ingame(tela, tela_largura, tela_altura, OST_MENU_INGAME, menu_opcoes, tela_comandos):
    from audio import fadeout_and_play_async
    fadeout_and_play_async(OST_MENU_INGAME)
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
        for i, opcao in enumerate(opcoes):
            cor = (255, 255, 0) if i == selecionado else (255, 255, 255)
            texto = fonte_opcao.render(opcao, True, cor)
            tela.blit(texto, (tela_largura//2 - texto.get_width()//2, 180 + i*60))
        pygame.display.flip()
        op_rects = []
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
