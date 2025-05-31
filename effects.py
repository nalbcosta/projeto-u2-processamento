import pygame
from PIL import Image, ImageEnhance
import numpy as np
import cv2
import random

def aplicar_efeito_sombra(surface):
    # Converte Surface para array
    arr = pygame.surfarray.array3d(surface)
    arr = np.transpose(arr, (1, 0, 2))
    # Converte para escala de cinza (efeito sombra)
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    sombra = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
    # Converte de volta para Surface
    sombra = np.transpose(sombra, (1, 0, 2))
    surf_sombra = pygame.surfarray.make_surface(sombra)
    return surf_sombra

def aplicar_efeito_blur(surface, ksize=5):
    """Aplica desfoque (blur) na surface."""
    arr = pygame.surfarray.array3d(surface)
    arr = np.transpose(arr, (1, 0, 2))
    blurred = cv2.GaussianBlur(arr, (ksize, ksize), 0)
    blurred = np.transpose(blurred, (1, 0, 2))
    return pygame.surfarray.make_surface(blurred)

def aplicar_efeito_tint(surface, color=(255,0,0), alpha=128):
    """Aplica uma cor (tint) sobre a surface."""
    tint = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    tint.fill((*color, alpha))
    surf = surface.copy()
    surf.blit(tint, (0,0), special_flags=pygame.BLEND_RGBA_ADD)
    return surf

def aplicar_efeito_shake(pos, intensidade=5):
    """Retorna uma posição tremida para efeito shake."""
    dx = random.randint(-intensidade, intensidade)
    dy = random.randint(-intensidade, intensidade)
    return (pos[0]+dx, pos[1]+dy)

def aplicar_efeito_fade(surface, alpha):
    """Aplica fade (transparência) na surface."""
    surf = surface.copy().convert_alpha()
    surf.fill((255,255,255,alpha), special_flags=pygame.BLEND_RGBA_MULT)
    return surf

def aplicar_efeito_sombra_projetada(surface, offset=(8,8), shadow_color=(0,0,0), alpha=120):
    """Cria uma sombra projetada com deslocamento e transparência."""
    shadow = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    shadow.blit(surface, (0,0))
    arr = pygame.surfarray.pixels_alpha(shadow)
    arr[:] = (arr * (alpha/255)).astype(np.uint8)
    del arr
    shadow.fill((*shadow_color, 0), special_flags=pygame.BLEND_RGBA_MIN)
    shadow.blit(surface, (0,0), special_flags=pygame.BLEND_RGBA_MULT)
    result = pygame.Surface((surface.get_width()+offset[0], surface.get_height()+offset[1]), pygame.SRCALPHA)
    result.blit(shadow, offset)
    result.blit(surface, (0,0))
    return result