import pygame
from effects import aplicar_efeito_sombra
from utils import carregar_spritesheet

class Player:
    def __init__(self, x, y, largura=96, altura=96):
        self.x = x
        self.largura = largura
        self.altura = altura
        # Ajusta o y para que o personagem fique "em pé" no chão
        self.y = y - self.altura  # posiciona o topo do sprite no chão
        self.vel_y = 0
        self.pulando = False
        self.gravidade = 1.5
        self.forca_pulo = -20
        self.chao = self.y  # topo do sprite encosta no chão
        self.velocidade = 3  # velocidade lateral reduzida
        self.rect = pygame.Rect(self.x, self.y, self.largura, self.altura)
        # Carrega animações do Samurai (Idle e Run apenas)
        self.animacoes = {
            'idle': [pygame.transform.scale(frame, (self.largura, self.altura)) for frame in carregar_spritesheet('assets/sprite/samurai/IDLE.png', 96, 96, 10)],
            'run': [pygame.transform.scale(frame, (self.largura, self.altura)) for frame in carregar_spritesheet('assets/sprite/samurai/RUN.png', 96, 96, 16)],
            'attack': [pygame.transform.scale(frame, (self.largura, self.altura)) for frame in carregar_spritesheet('assets/sprite/samurai/ATTACK 1.png', 96, 96, 10)]
        }
        self.acao = 'idle'
        self.frame = 0
        self.frame_timer = 0
        self.sprite_original = self.animacoes[self.acao][0]
        self.efeito = False
        self.efeito_timer = 0
        self.atacando = False
        self.ataque_timer = 0
        self.ataque_duracao = 12  # frames
        self.direcao = 1  # 1: direita, -1: esquerda
        self.vida = 3
        self.vida_max = 3
        self.velocidade = 3
        self.forca = 3  # Aumenta o dano do ataque do player
        self.invencivel = False
        self.invencivel_timer = 0
        self.invencivel_cooldown = 40

    def pular(self):
        if not self.pulando:
            self.vel_y = self.forca_pulo
            self.pulando = True
            self.acao = 'idle'  # Mantém idle durante o pulo
            self.frame = 0

    def mover(self, direcao):
        self.x += direcao * self.velocidade
        self.direcao = direcao
        self.acao = 'run'
        self.rect.x = self.x

    def atacar(self):
        if not self.atacando:
            self.atacando = True
            self.ataque_timer = self.ataque_duracao
            self.acao = 'attack'
            self.frame = 0

    def get_ataque_rect(self):
        # Retângulo de ataque na frente do player (maior hitbox)
        if self.direcao == 1:
            return pygame.Rect(self.x + self.largura - 10, self.y + 10, 60, self.altura - 20)
        else:
            return pygame.Rect(self.x - 50, self.y + 10, 60, self.altura - 20)

    def levar_dano(self):
        if not self.invencivel:
            self.vida -= 1
            self.invencivel = True
            self.invencivel_timer = self.invencivel_cooldown

    def update(self):
        self.vel_y += self.gravidade
        self.y += self.vel_y
        if self.y >= self.chao:
            self.y = self.chao
            self.vel_y = 0
            self.pulando = False
            # Só fica idle se não estiver andando nem atacando
            if not self.atacando and self.acao != 'run':
                self.acao = 'idle'
        else:
            if self.vel_y > 0 and not self.atacando:
                self.acao = 'idle'
        self.rect.x = self.x
        self.rect.y = self.y
        # Animação
        self.frame_timer += 1
        if self.frame_timer >= 6:
            self.frame = (self.frame + 1) % len(self.animacoes[self.acao])
            self.frame_timer = 0
        # Corrige frame inválido para animação
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
        # Atualiza invencibilidade
        if self.invencivel:
            self.invencivel_timer -= 1
            if self.invencivel_timer <= 0:
                self.invencivel = False

    def draw(self, tela):
        sprite = self.sprite_original
        if self.efeito:
            sprite = aplicar_efeito_sombra(sprite)
        if self.direcao == -1:
            sprite = pygame.transform.flip(sprite, True, False)
        tela.blit(sprite, (self.x, self.y))
        # Debug: desenhar hitbox de ataque
        #if self.atacando:
        #    pygame.draw.rect(tela, (255,0,0), self.get_ataque_rect(), 2)

    def aplicar_efeito(self):
        self.efeito = True
        self.efeito_timer = 30  # frames

    def draw_offset(self, tela, offset_x):
        # Desenha o player considerando o offset da câmera
        if hasattr(self, 'animations') and self.acao in self.animations:
            sprite = self.animations[self.acao][self.frame]
            if self.direcao == -1:
                sprite = pygame.transform.flip(sprite, True, False)
            tela.blit(sprite, (self.x + offset_x, self.y))
        else:
            self.draw(tela)

