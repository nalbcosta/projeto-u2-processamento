import pygame

def carregar_spritesheet(caminho, largura, altura, n_frames=None):
    '''
    Carrega um spritesheet e retorna uma lista de frames (pygame.Surface).
    caminho: caminho do arquivo PNG
    largura, altura: tamanho de cada frame
    n_frames: número de frames a extrair (opcional)
    '''
    spritesheet = pygame.image.load(caminho).convert_alpha()
    sheet_width, sheet_height = spritesheet.get_size()
    frames = []
    max_possible_frames = sheet_width // largura
    max_frames = n_frames if n_frames else max_possible_frames
    for i in range(max_frames):
        x = i * largura
        if x + largura > sheet_width or altura > sheet_height:
            print(f"[ERRO] Frame {i} fora do limite do spritesheet: {caminho} (x={x}, largura={largura}, sheet_width={sheet_width})")
            break
        frame = spritesheet.subsurface((x, 0, largura, altura))
        frames.append(frame)
    if len(frames) == 0:
        print(f"[ERRO] Nenhum frame extraído do spritesheet: {caminho} (largura={largura}, altura={altura}, n_frames={n_frames})")
    else:
        print(f"[INFO] {len(frames)} frames extraídos de {caminho} ({sheet_width}x{sheet_height}, frame={largura}x{altura})")
    return frames
