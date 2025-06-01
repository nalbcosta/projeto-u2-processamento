import pygame

musica_pendente = None
musica_fadeout_time = 0
musica_fadeout_ms = 0

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

def checar_troca_musica():
    global musica_pendente, musica_fadeout_time, musica_fadeout_ms
    if musica_pendente:
        if pygame.time.get_ticks() - musica_fadeout_time >= musica_fadeout_ms:
            pygame.mixer.music.load(musica_pendente)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
            musica_pendente = None
