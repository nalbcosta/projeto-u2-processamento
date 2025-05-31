# player.py - Classe do jogador para Lost Samurai
# Responsável por movimentação, animação, ataque e efeitos do personagem controlado

import pygame
from effects import aplicar_efeito_sombra, aplicar_efeito_blur, aplicar_efeito_tint, aplicar_efeito_shake, aplicar_efeito_fade, aplicar_efeito_sombra_projetada
from utils import carregar_spritesheet

class Player:
    def __init__(self, x, y, largura=96, altura=96):
        """
        Inicializa o player.
        x, y: posição inicial (y é o chão onde o topo do sprite encosta)
        largura, altura: dimensões do sprite
        """
        # --- POSIÇÃO E FÍSICA ---
        self.x = x  # Posição X do player
        self.largura = largura  # Largura do sprite
        self.altura = altura    # Altura do sprite
        self.y = y - self.altura  # Posição Y (topo do sprite encosta no chão)
        self.vel_y = 0  # Velocidade vertical
        self.pulando = False  # Está pulando?
        self.gravidade = 1.5  # Gravidade aplicada
        self.forca_pulo = -20  # Força do pulo
        self.chao = self.y  # Posição do chão
        self.velocidade = 4  # Velocidade de movimento lateral
        self.rect = pygame.Rect(self.x, self.y, self.largura, self.altura)  # Retângulo de colisão

        # --- ANIMAÇÕES ---
        # Carrega animações do personagem (idle, run, attack)
        self.animacoes = {
            'idle': [pygame.transform.scale(frame, (self.largura, self.altura)) for frame in carregar_spritesheet('assets/sprite/samurai/IDLE.png', 96, 96, 10)],
            'run': [pygame.transform.scale(frame, (self.largura, self.altura)) for frame in carregar_spritesheet('assets/sprite/samurai/RUN.png', 96, 96, 16)],
            'attack': [pygame.transform.scale(frame, (self.largura, self.altura)) for frame in carregar_spritesheet('assets/sprite/samurai/ATTACK 1.png', 96, 96, 7)]
        }
        self.acao = 'idle'  # Estado atual da animação
        self.frame = 0  # Frame atual da animação
        self.frame_timer = 0  # Timer para troca de frame
        self.sprite_original = self.animacoes[self.acao][0]  # Sprite atual

        # --- EFEITOS VISUAIS ---
        self.efeito = False  # Efeito visual ativo?
        self.efeito_timer = 0  # Timer do efeito

        # --- ATAQUE ---
        self.atacando = False  # Está atacando?
        self.ataque_timer = 0  # Timer do ataque
        self.ataque_duracao = 42  # Duração do ataque (frames)
        self.direcao = 1  # 1: direita, -1: esquerda

        # --- STATUS ---
        self.vida = 3  # Vida atual
        self.vida_max = 3  # Vida máxima
        self.forca = 3  # Força do ataque
        self.invencivel = False  # Está invencível?
        self.invencivel_timer = 0  # Timer de invencibilidade
        self.invencivel_cooldown = 40  # Duração da invencibilidade (frames)

        # --- STATUS DE EFEITOS ESPECIAIS ---
        self.stunned = False  # Atordoado
        self.stunned_timer = 0
        self.powerup = False  # Powerup ativo
        self.powerup_timer = 0
        self.levou_dano = False  # Levou dano recentemente
        self.levou_dano_timer = 0

        # --- LIMPEZA DE ATRIBUTOS OBSOLETOS ---
        # Nenhum atributo obsoleto detectado para remoção

    def pular(self):
        """Faz o player pular se não estiver no ar."""
        if not self.pulando:
            self.vel_y = self.forca_pulo
            self.pulando = True
            self.acao = 'idle'
            self.frame = 0

    def mover(self, direcao):
        """Move o player para esquerda/direita e atualiza animação."""
        self.x += direcao * self.velocidade
        self.direcao = direcao
        self.acao = 'run'
        self.rect.x = self.x
        self.frame = 0

    def atacar(self):
        """Inicia o ataque se não estiver atacando."""
        if not self.atacando:
            self.atacando = True
            self.ataque_timer = self.ataque_duracao
            self.acao = 'attack'
            self.frame = 0

    def get_ataque_rect(self):
        """Retorna o retângulo de ataque na frente do player."""
        if self.direcao == 1:
            return pygame.Rect(self.x + self.largura - 10, self.y + 10, 60, self.altura - 20)
        else:
            return pygame.Rect(self.x - 50, self.y + 10, 60, self.altura - 20)

    def levar_dano(self, dano=1):
        """Reduz vida e ativa invencibilidade temporária."""
        if not self.invencivel:
            self.vida -= dano
            self.invencivel = True
            self.invencivel_timer = self.invencivel_cooldown
            self.levou_dano = True
            self.levou_dano_timer = 10  # Duração do efeito de levou_dano

    def get_hitbox(self):
        """Retorna o hitbox do player igual ao do inimigo (64x64), centralizado no sprite."""
        hitbox_largura = 64
        hitbox_altura = 64
        hitbox_x = self.x + (self.largura - hitbox_largura) // 2
        hitbox_y = self.y + (self.altura - hitbox_altura)
        return pygame.Rect(hitbox_x, hitbox_y, hitbox_largura, hitbox_altura)

    def update(self):
        """Atualiza física, animação, timers e efeitos do player."""
        self.vel_y += self.gravidade
        self.y += self.vel_y
        if self.y >= self.chao:
            self.y = self.chao
            self.vel_y = 0
            self.pulando = False
            if not self.atacando and self.acao != 'run':
                self.acao = 'idle'
        else:
            if self.vel_y > 0 and not self.atacando:
                self.acao = 'idle'
        self.rect.x = self.x
        self.rect.y = self.y
        # Animação
        self.frame_timer += 1
        # Duração de cada frame depende da animação
        if self.acao == 'run':
            frame_dur = 3  # Corrida: mais rápida
        elif self.acao == 'attack':
            frame_dur = 6  # Ataque: já ajustado
        else:
            frame_dur = 6  # Idle e outras
        if self.frame_timer >= frame_dur:
            self.frame += 1
            if self.frame >= len(self.animacoes[self.acao]):
                self.frame = 0
            self.frame_timer = 0
        frames_anim = self.animacoes[self.acao]
        if self.frame >= len(frames_anim):
            self.frame = 0
        self.sprite_original = frames_anim[self.frame]
        # Timer para efeito visual
        if self.efeito:
            self.efeito_timer -= 1
            if self.efeito_timer <= 0:
                self.efeito = False
        # Timer de ataque
        if self.atacando:
            self.ataque_timer -= 1
            if self.ataque_timer <= 0:
                self.atacando = False
                self.acao = 'idle'
        # Invencibilidade
        if self.invencivel:
            self.invencivel_timer -= 1
            if self.invencivel_timer <= 0:
                self.invencivel = False
        # Timer de atordoamento
        if self.stunned:
            self.stunned_timer -= 1
            if self.stunned_timer <= 0:
                self.stunned = False
        # Timer de powerup
        if self.powerup:
            self.powerup_timer -= 1
            if self.powerup_timer <= 0:
                self.powerup = False
        # Timer de levou_dano
        if self.levou_dano:
            self.levou_dano_timer -= 1
            if self.levou_dano_timer <= 0:
                self.levou_dano = False

        # Detecta início da corrida para tocar som
        if hasattr(self, 'ultimo_estado_corrida'):
            if self.acao == 'run' and not self.ultimo_estado_corrida:
                try:
                    from main import som_corrida
                    som_corrida.play()
                except Exception:
                    pass
            self.ultimo_estado_corrida = (self.acao == 'run')
        else:
            self.ultimo_estado_corrida = (self.acao == 'run')
        # Detecta pouso do pulo para tocar som
        if hasattr(self, 'ultimo_no_ar'):
            if not self.pulando and self.ultimo_no_ar:
                try:
                    from main import som_pouso
                    som_pouso.play()
                except Exception:
                    pass
            self.ultimo_no_ar = self.pulando
        else:
            self.ultimo_no_ar = self.pulando

    def draw(self, tela):
        """Desenha o player na tela, aplicando efeitos visuais e flip se necessário."""
        sprite = self.sprite_original
        pos = (self.x, self.y)

        # Exemplo: aplicar sombra projetada sempre
        sprite = aplicar_efeito_sombra_projetada(sprite, offset=(8,8), shadow_color=(0,0,0), alpha=120)
        pos = (self.x, self.y)  # Ajuste se quiser compensar o offset

        # Exemplo: aplicar blur se estiver atordoado
        if hasattr(self, 'stunned') and self.stunned:
            sprite = aplicar_efeito_blur(sprite, ksize=7)

        # Exemplo: aplicar tint se estiver com powerup
        if hasattr(self, 'powerup') and self.powerup:
            sprite = aplicar_efeito_tint(sprite, color=(0,255,0), alpha=100)

        # Exemplo: aplicar fade se estiver invencível
        if self.invencivel:
            sprite = aplicar_efeito_fade(sprite, alpha=128)

        # Exemplo: shake ao levar dano
        if hasattr(self, 'levou_dano') and self.levou_dano:
            pos = aplicar_efeito_shake(pos, intensidade=6)

        # Flip horizontal se necessário
        if self.direcao == -1:
            sprite = pygame.transform.flip(sprite, True, False)
        tela.blit(sprite, pos)

        # Dica: ajuste as condições conforme o seu sistema de status/efeitos

    def aplicar_efeito(self):
        """Ativa efeito visual temporário."""
        self.efeito = True
        self.efeito_timer = 30

    def draw_offset(self, tela, offset_x):
        """Desenha o player considerando offset de câmera."""
        if hasattr(self, 'animations') and self.acao in self.animations:
            sprite = self.animations[self.acao][self.frame]
            if self.direcao == -1:
                sprite = pygame.transform.flip(sprite, True, False)
            tela.blit(sprite, (self.x + offset_x, self.y))
        else:
            self.draw(tela)

