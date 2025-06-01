import pygame
from utils import desenhar_texto_sombra

def draw_hud(tela, player, vida_img=None, arma_img=None):
    import random  # Garantir que random está disponível
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
