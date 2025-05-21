import pygame
from PIL import Image, ImageEnhance
import numpy as np
import cv2

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

# Você pode criar outros efeitos, como brilho, distorção, etc.
