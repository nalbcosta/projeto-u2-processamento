import pygame

def carregar_spritesheet(caminho, largura, altura, n_frames=None):
    '''
    Carrega um spritesheet e retorna uma lista de frames (pygame.Surface).
    Remove frames totalmente transparentes (vazios).
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
        frame = spritesheet.subsurface((x, 0, largura, altura)).copy()
        # Remove frames totalmente transparentes (vazios)
        if pygame.surfarray.pixels_alpha(frame).max() == 0:
            continue
        frames.append(frame)
    if len(frames) == 0:
        print(f"[ERRO] Nenhum frame extraído do spritesheet: {caminho} (largura={largura}, altura={altura}, n_frames={n_frames})")
    else:
        print(f"[INFO] {len(frames)} frames extraídos de {caminho} ({sheet_width}x{sheet_height}, frame={largura}x{altura})")
    return frames

def carregar_icone(nome):
    try:
        return pygame.image.load(f'assets/icons/{nome}').convert_alpha()
    except:
        return None

def fade_in(tela, cor=(0,0,0), duracao=30):
    fade = pygame.Surface((tela.get_width(), tela.get_height()))
    fade.fill(cor)
    for alpha in range(255, -1, -int(255/duracao)):
        fade.set_alpha(alpha)
        tela.blit(fade, (0,0))
        pygame.display.flip()
        pygame.time.delay(8)

def fade_out(tela, cor=(0,0,0), duracao=30):
    fade = pygame.Surface((tela.get_width(), tela.get_height()))
    fade.fill(cor)
    for alpha in range(0, 256, int(255/duracao)):
        fade.set_alpha(alpha)
        tela.blit(fade, (0,0))
        pygame.display.flip()
        pygame.time.delay(8)

def desenhar_texto_sombra(tela, texto, fonte, cor, sombra_cor, pos, deslocamento=(2,2)):
    sombra = fonte.render(texto, True, sombra_cor)
    tela.blit(sombra, (pos[0]+deslocamento[0], pos[1]+deslocamento[1]))
    texto_img = fonte.render(texto, True, cor)
    tela.blit(texto_img, pos)
