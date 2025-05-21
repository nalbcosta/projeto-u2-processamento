import pygame
from utils import carregar_spritesheet

class Enemy:
    def __init__(self, x, y, largura=64, altura=64, spawn_side=None):
        self.sprite_largura = largura
        self.sprite_altura = altura
        # Aparição: inimigo pode surgir da esquerda ou direita fora da tela
        if spawn_side == 'left':
            self.x = -self.sprite_largura
            self.direcao = 1
        elif spawn_side == 'right':
            self.x = pygame.display.get_surface().get_width() + self.sprite_largura
            self.direcao = -1
        else:
            self.x = x
            self.direcao = -1
        self.y = y - self.sprite_altura
        self.largura = self.sprite_largura
        self.altura = self.sprite_altura
        self.rect = pygame.Rect(self.x, self.y, self.largura, self.altura)
        # Carregar todas as animações do inimigo
        self.animations = {}
        sprites_info = {
            'idle':   ('assets/sprite/enemy/Skeleton_01_White_Idle.png', 8),
            'walk':   ('assets/sprite/enemy/Skeleton_01_White_Walk.png', 8),
            'die':    ('assets/sprite/enemy/Skeleton_01_White_Die.png', 6),
            'hurt':   ('assets/sprite/enemy/Skeleton_01_White_Hurt.png', 4),
            'attack': ('assets/sprite/enemy/Skeleton_01_White_Attack1.png', 6),
        }
        for anim, (path, nframes) in sprites_info.items():
            try:
                frames = [pygame.transform.scale(frame, (self.largura, self.altura)) for frame in carregar_spritesheet(path, 64, 64, nframes)]
                self.animations[anim] = frames
            except Exception as e:
                self.animations[anim] = []
        self.current_animation = 'idle'
        self.last_animation = 'idle'
        self.frame = 0
        self.frame_timer = 0
        self.vivo = True
        self.vida = 1
        self.velocidade = 2
        self.patrulha_limite = (x-60, x+60)
        self.anim_speed = 8
        # IA
        self.estado = 'patrulha'  # patrulha, perseguindo, atacando, morto
        self.tempo_ataque = 0
        self.cooldown_ataque = 40  # frames entre ataques
        self.distancia_visao = 180
        self.distancia_ataque = 48
        self.atacando = False
        self.ataque_frame_max = 5  # frame para considerar hit
        self.ataque_frame_atual = 0

    def set_animation(self, anim):
        if anim != self.current_animation and anim in self.animations:
            self.last_animation = self.current_animation
            self.current_animation = anim
            self.frame = 0
            self.frame_timer = 0

    def update(self, player=None):
        if not self.vivo:
            self.set_animation('die')
        else:
            # IA: patrulha, persegue, ataca
            distancia_player = None
            if player:
                distancia_player = abs((self.x + self.largura//2) - (player.x + player.largura//2))
            # Estado
            if player and distancia_player is not None:
                if distancia_player < self.distancia_ataque:
                    if not self.atacando and self.tempo_ataque == 0:
                        self.estado = 'atacando'
                        self.atacando = True
                        self.ataque_frame_atual = 0
                    elif self.atacando:
                        self.estado = 'atacando'
                    else:
                        self.estado = 'idle'
                elif distancia_player < self.distancia_visao:
                    self.estado = 'perseguindo'
                    self.atacando = False
                else:
                    self.estado = 'patrulha'
                    self.atacando = False
            else:
                self.estado = 'patrulha'
                self.atacando = False
            # Lógica de cada estado
            if self.estado == 'patrulha':
                self.set_animation('walk')
                self.x += self.direcao * self.velocidade
                if self.x < self.patrulha_limite[0] or self.x > self.patrulha_limite[1]:
                    self.direcao *= -1
                self.rect.x = self.x
            elif self.estado == 'perseguindo':
                self.set_animation('walk')
                if player.x > self.x:
                    self.direcao = 1
                else:
                    self.direcao = -1
                self.x += self.direcao * (self.velocidade + 1)
                self.rect.x = self.x
            elif self.estado == 'atacando':
                self.set_animation('attack')
                self.rect.x = self.x
            elif self.estado == 'idle':
                self.set_animation('idle')
                self.rect.x = self.x
            # Cooldown de ataque
            if self.tempo_ataque > 0:
                self.tempo_ataque -= 1
        # Animação
        frames = self.animations.get(self.current_animation, [])
        if frames:
            self.frame_timer += 1
            if self.frame_timer >= self.anim_speed:
                self.frame_timer = 0
                self.frame += 1
                if self.frame >= len(frames):
                    if self.current_animation == 'attack':
                        self.frame = 0
                        self.atacando = False
                        self.tempo_ataque = self.cooldown_ataque
                        self.set_animation('idle')
                    elif self.current_animation == 'die':
                        self.frame = len(frames)-1
                        self.vivo = False
                    elif self.current_animation == 'hurt':
                        self.set_animation('idle')
                        self.frame = 0
                    else:
                        self.frame = 0
            # Controle de ataque (frame de hit)
            if self.current_animation == 'attack' and self.atacando:
                self.ataque_frame_atual = self.frame

    def draw(self, tela):
        if not self.vivo and self.current_animation != 'die':
            return
        frames = self.animations.get(self.current_animation, [])
        if frames:
            sprite = frames[self.frame]
            if self.direcao == 1:
                sprite = pygame.transform.flip(sprite, True, False)
            tela.blit(sprite, (self.x, self.y))
        else:
            pygame.draw.rect(tela, (255, 0, 0), self.rect)

    def draw_offset(self, tela, offset_x):
        frames = self.animations.get(self.current_animation, [])
        if frames:
            sprite = frames[self.frame]
            if self.direcao == 1:
                sprite = pygame.transform.flip(sprite, True, False)
            tela.blit(sprite, (self.x + offset_x, self.y))
        else:
            pygame.draw.rect(tela, (255, 0, 0), self.rect.move(offset_x, 0))

    def levar_dano(self):
        self.vida -= 1
        if self.vida <= 0:
            self.set_animation('die')
        else:
            self.set_animation('hurt')

    def colidiu(self, player):
        return self.rect.colliderect(player.rect)

    def pode_atacar(self, player):
        # Só pode atacar se estiver em cooldown 0 e próximo do player
        distancia = abs((self.x + self.largura//2) - (player.x + player.largura//2))
        return self.tempo_ataque == 0 and distancia < self.distancia_ataque

    def ataque_acertou(self, player):
        # Só acerta se estiver no frame certo da animação de ataque
        if self.current_animation == 'attack' and self.atacando and self.ataque_frame_atual == self.ataque_frame_max:
            return self.colidiu(player)
        return False

class MushroomEnemy(Enemy):
    def __init__(self, x, y, largura=64, altura=64, spawn_side=None):
        super().__init__(x, y, largura, altura, spawn_side)
        sprites_info = {
            'idle':   ('assets/sprite/enemy 2/Mushroom-Idle.png', 8),
            'walk':   ('assets/sprite/enemy 2/Mushroom-Run.png', 8),
            'die':    ('assets/sprite/enemy 2/Mushroom-Die.png', 6),
            'hurt':   ('assets/sprite/enemy 2/Mushroom-Hit.png', 4),
            'attack': ('assets/sprite/enemy 2/Mushroom-Attack.png', 6),
        }
        self.animations = {}
        for anim, (path, nframes) in sprites_info.items():
            try:
                frames = [pygame.transform.scale(frame, (self.largura, self.altura)) for frame in carregar_spritesheet(path, 64, 64, nframes)]
                self.animations[anim] = frames
            except Exception as e:
                self.animations[anim] = []
        self.current_animation = 'idle'
        self.last_animation = 'idle'
        self.frame = 0
        self.frame_timer = 0
        self.vida = 2
        self.velocidade = 1.5
        self.distancia_visao = 140
        self.distancia_ataque = 40

class FlyingEnemy(Enemy):
    def __init__(self, x, y, largura=64, altura=64, spawn_side=None):
        super().__init__(x, y, largura, altura, spawn_side)
        sprites_info = {
            'idle':   ('assets/sprite/enemy 3/Enemy3-Idle.png', 8),
            'walk':   ('assets/sprite/enemy 3/Enemy3-Fly.png', 8),
            'die':    ('assets/sprite/enemy 3/Enemy3-Die.png', 6),
            'hurt':   ('assets/sprite/enemy 3/Enemy3-Hit.png', 4),
            'attack': ('assets/sprite/enemy 3/Enemy3-AttackSmashStart.png', 6),
        }
        self.animations = {}
        for anim, (path, nframes) in sprites_info.items():
            try:
                frames = [pygame.transform.scale(frame, (self.largura, self.altura)) for frame in carregar_spritesheet(path, 64, 64, nframes)]
                self.animations[anim] = frames
            except Exception as e:
                self.animations[anim] = []
        self.current_animation = 'idle'
        self.last_animation = 'idle'
        self.frame = 0
        self.frame_timer = 0
        self.vida = 2
        self.velocidade = 2.5
        self.distancia_visao = 200
        self.distancia_ataque = 60
    def update(self, player=None):
        # Voa na vertical para alinhar com o player
        if player:
            if abs(self.y - player.y) > 10:
                self.y += 1.5 if self.y < player.y else -1.5
            self.rect.y = self.y
        super().update(player)