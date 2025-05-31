# obstacle.py - Inimigos do Lost Samurai
# Define as classes Enemy, MushroomEnemy e FlyingEnemy, responsáveis pela IA, animação e colisão dos inimigos

import pygame
from utils import carregar_spritesheet

class Enemy:
    def __init__(self, x, y, largura=64, altura=64, spawn_side=None):
        """
        Inicializa um inimigo padrão (esqueleto).
        x, y: posição inicial (y é o chão onde o topo do sprite encosta)
        largura, altura: dimensões do sprite
        spawn_side: não utilizado, compatível com outros inimigos
        """
        self.sprite_largura = largura
        self.sprite_altura = altura
        self.x = x
        self.direcao = -1  # -1: esquerda, 1: direita
        self.y = y - self.sprite_altura
        self.largura = self.sprite_largura
        self.altura = self.sprite_altura
        self.rect = pygame.Rect(self.x, self.y, self.largura, self.altura)  # Hitbox do inimigo
        # Carrega animações do inimigo
        self.animations = {}
        sprites_info = {
            'idle':   ('assets/sprite/enemy/Skeleton_01_White_Idle.png', 8),
            'walk':   ('assets/sprite/enemy/Skeleton_01_White_Walk.png', 10),
            'die':    ('assets/sprite/enemy/Skeleton_01_White_Die.png', 13),
            'hurt':   ('assets/sprite/enemy/Skeleton_01_White_Hurt.png', 5),
            'attack': ('assets/sprite/enemy/Skeleton_01_White_Attack1.png', 10),
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
        self.vida = 3
        self.vida_max = 3
        self.velocidade = 1  # Velocidade de patrulha
        self.forca = 1       # Dano do inimigo
        self.patrulha_limite = (x-60, x+60)  # Limites de patrulha
        self.anim_speed = 8  # Velocidade da animação
        # --- IA e ataque ---
        self.estado = 'patrulha'  # patrulha, perseguindo, atacando, morto
        self.tempo_ataque = 0  # Cooldown do ataque
        self.cooldown_ataque = 40  # Frames entre ataques
        self.distancia_visao = 180  # Distância para perseguir o player
        self.distancia_ataque = 48  # Distância para atacar
        self.atacando = False  # Está atacando?
        self.ataque_frame_max = 5  # Frame do hit
        self.ataque_frame_atual = 0  # Frame atual do ataque

    def set_animation(self, anim):
        """Troca a animação atual do inimigo."""
        if anim != self.current_animation and anim in self.animations:
            self.last_animation = self.current_animation
            self.current_animation = anim
            self.frame = 0
            self.frame_timer = 0

    def update(self, player=None):
        """Atualiza IA, física e animação do inimigo."""
        # Morte
        if hasattr(self, 'morrendo') and self.morrendo:
            if self.morte_timer > 0:
                self.morte_timer -= 1
            else:
                self.morrendo = False
                self.x = -9999
                self.rect.x = self.x
            self.set_animation('die')
            self._anim_update()
            return
        if not self.vivo:
            self.set_animation('die')
            self._anim_update()
            return
        # IA: persegue ou patrulha
        if player:
            if player.x > self.x:
                self.direcao = 1
            else:
                self.direcao = -1
            distancia_player = abs((self.x + self.largura//2) - (player.x + player.largura//2))
            if distancia_player < self.distancia_ataque:
                if not self.atacando and self.tempo_ataque == 0:
                    self.estado = 'atacando'
                    self.atacando = True
                    self.ataque_frame_atual = 0
                elif self.atacando:
                    self.estado = 'atacando'
                else:
                    self.estado = 'idle'
            else:
                self.estado = 'perseguindo'
                self.atacando = False
        else:
            self.estado = 'patrulha'
            self.atacando = False
        # Lógica de movimento e animação
        if self.estado == 'patrulha':
            self.set_animation('walk')
            if not self.atacando:
                self.x += self.direcao * self.velocidade
                if self.x < self.patrulha_limite[0] or self.x > self.patrulha_limite[1]:
                    self.direcao *= -1
            self.rect.x = self.x
        elif self.estado == 'perseguindo':
            self.set_animation('walk')
            if not self.atacando:
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
        # Atualiza hitbox
        self.rect.x = self.x
        self.rect.y = self.y
        self._anim_update()

    def _anim_update(self):
        """Atualiza o frame da animação do inimigo."""
        frames = self.animations.get(self.current_animation, [])
        if frames:
            self.frame_timer += 1
            if self.frame_timer >= self.anim_speed:
                self.frame_timer = 0
                if self.current_animation == 'die':
                    if self.frame < len(frames) - 1:
                        self.frame += 1
                else:
                    self.frame += 1
                    if self.frame >= len(frames):
                        if self.current_animation == 'attack':
                            self.frame = 0
                            self.atacando = False
                            self.tempo_ataque = self.cooldown_ataque
                            self.set_animation('idle')
                        elif self.current_animation == 'hurt':
                            self.set_animation('idle')
                            self.frame = 0
                        else:
                            self.frame = 0
            # Atualiza frame de hit do ataque
            if self.current_animation == 'attack' and self.atacando:
                self.ataque_frame_atual = self.frame

    def draw(self, tela):
        """Desenha o inimigo na tela."""
        if not self.vivo and (not hasattr(self, 'morrendo') or not self.morrendo):
            return
        frames = self.animations.get(self.current_animation, [])
        if frames:
            sprite = frames[self.frame]
            # Corrige flip: só inverte para a esquerda, nunca para a direita
            if self.direcao == -1:
                sprite = pygame.transform.flip(sprite, True, False)
            # Desenha o sprite na posição da hitbox para evitar "tremedeira"
            tela.blit(sprite, (self.rect.x, self.rect.y))
        else:
            pygame.draw.rect(tela, (255, 0, 0), self.rect)

    def draw_offset(self, tela, offset_x):
        """Desenha o inimigo considerando offset de câmera (não usado atualmente)."""
        frames = self.animations.get(self.current_animation, [])
        if frames:
            sprite = frames[self.frame]
            if self.direcao == 1:
                sprite = pygame.transform.flip(sprite, True, False)
            tela.blit(sprite, (self.x + offset_x, self.y))
        else:
            pygame.draw.rect(tela, (255, 0, 0), self.rect.move(offset_x, 0))

    def levar_dano(self, dano=1):
        """Aplica dano ao inimigo e troca animação para hurt ou die."""
        self.vida -= dano
        if self.vida <= 0:
            self.vida = 0
            self.set_animation('die')
            self.vivo = False
            self.morrendo = True
            self.morte_timer = len(self.animations['die']) * self.anim_speed
        else:
            self.set_animation('hurt')

    def causar_dano(self, player):
        """Aplica dano ao player usando a força do inimigo."""
        player.levar_dano(self.forca)

    def colidiu(self, player):
        """Retorna True se o inimigo colidiu com o player."""
        return self.rect.colliderect(player.rect)

    def pode_atacar(self, player):
        """Retorna True se pode atacar o player (distância e cooldown)."""
        distancia = abs((self.x + self.largura//2) - (player.x + player.largura//2))
        return self.tempo_ataque == 0 and distancia < self.distancia_ataque

    def ataque_acertou(self, player):
        """Retorna True se o ataque do inimigo acertou o player (no frame certo)."""
        if self.current_animation == 'attack' and self.atacando and self.ataque_frame_atual == self.ataque_frame_max:
            return self.colidiu(player)
        return False

class MushroomEnemy(Enemy):
    def __init__(self, x, y, largura=64, altura=64, spawn_side=None):
        """
        Inicializa um inimigo tipo cogumelo.
        """
        super().__init__(x, y, largura, altura, spawn_side)
        sprites_info = {
            'idle':   ('assets/sprite/enemy 2/Mushroom-Idle.png', 7),
            'walk':   ('assets/sprite/enemy 2/Mushroom-Run.png', 8),
            'die':    ('assets/sprite/enemy 2/Mushroom-Die.png', 15),
            'hurt':   ('assets/sprite/enemy 2/Mushroom-Hit.png', 5),
            'attack': ('assets/sprite/enemy 2/Mushroom-Attack.png', 10),
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
        """
        Inicializa um inimigo voador.
        """
        super().__init__(x, y, largura, altura, spawn_side)
        sprites_info = {
            'idle':   ('assets/sprite/enemy 3/Enemy3-Idle.png', 8),
            'walk':   ('assets/sprite/enemy 3/Enemy3-Fly.png', 8),
            'die':    ('assets/sprite/enemy 3/Enemy3-Die.png', 16),
            'hurt':   ('assets/sprite/enemy 3/Enemy3-Hit.png', 4),
            'attack_start': ('assets/sprite/enemy 3/Enemy3-AttackSmashStart.png', 12),
            'attack_end':   ('assets/sprite/enemy 3/Enemy3-SmashEnd.png', 8),
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
        self.attack_phase = 'start'  # 'start' ou 'end'
        self.attack_anim_playing = False

    def update(self, player=None):
        """Atualiza IA, física e animação do inimigo voador."""
        if hasattr(self, 'morrendo') and self.morrendo:
            if self.morte_timer > 0:
                self.morte_timer -= 1
            else:
                self.morrendo = False
                self.x = -9999
                self.rect.x = self.x
            self.set_animation('die')
            self._anim_update()
            return
        if not self.vivo:
            self.set_animation('die')
            self._anim_update()
            return
        if player:
            if player.x > self.x:
                self.direcao = 1
            else:
                self.direcao = -1
            distancia_player = abs((self.x + self.largura//2) - (player.x + player.largura//2))
            if distancia_player < self.distancia_ataque:
                if not self.atacando and self.tempo_ataque == 0:
                    self.estado = 'atacando'
                    self.atacando = True
                    self.ataque_frame_atual = 0
                    self.attack_phase = 'start'
                    self.attack_anim_playing = True
                elif self.atacando:
                    self.estado = 'atacando'
                else:
                    self.estado = 'idle'
            else:
                self.estado = 'perseguindo'
                self.atacando = False
        else:
            self.estado = 'patrulha'
            self.atacando = False
        # Lógica de movimento e animação
        if self.estado == 'patrulha':
            self.set_animation('walk')
            if not self.atacando:
                self.x += self.direcao * self.velocidade
                if self.x < self.patrulha_limite[0] or self.x > self.patrulha_limite[1]:
                    self.direcao *= -1
            self.rect.x = self.x
        elif self.estado == 'perseguindo':
            self.set_animation('walk')
            if not self.atacando:
                self.x += self.direcao * (self.velocidade + 1)
            self.rect.x = self.x
        elif self.estado == 'atacando':
            # Fase de ataque: start -> end
            if self.attack_phase == 'start':
                self.set_animation('attack_start')
                frames = self.animations.get('attack_start', [])
                if self.frame >= len(frames)-1:
                    self.attack_phase = 'end'
                    self.frame = 0
            elif self.attack_phase == 'end':
                self.set_animation('attack_end')
                frames = self.animations.get('attack_end', [])
                if self.frame >= len(frames)-1:
                    self.atacando = False
                    self.tempo_ataque = self.cooldown_ataque
                    self.attack_phase = 'start'
                    self.set_animation('idle')
                    self.frame = 0
            self.rect.x = self.x
        elif self.estado == 'idle':
            self.set_animation('idle')
            self.rect.x = self.x
        # Cooldown de ataque
        if self.tempo_ataque > 0:
            self.tempo_ataque -= 1
        # Animação
        anim_key = self.current_animation
        frames = self.animations.get(anim_key, [])
        if frames:
            self.frame_timer += 1
            if self.frame_timer >= self.anim_speed:
                self.frame_timer = 0
                self.frame += 1
                if self.frame >= len(frames):
                    if anim_key == 'attack_start':
                        self.attack_phase = 'end'
                        self.frame = 0
                    elif anim_key == 'attack_end':
                        self.atacando = False
                        self.tempo_ataque = self.cooldown_ataque
                        self.attack_phase = 'start'
                        self.set_animation('idle')
                        self.frame = 0
                    elif anim_key == 'attack':
                        self.frame = 0
                        self.atacando = False
                        self.tempo_ataque = self.cooldown_ataque
                        self.set_animation('idle')
                    elif anim_key == 'die':
                        self.frame = len(frames)-1
                        self.vivo = False
                    elif anim_key == 'hurt':
                        self.set_animation('idle')
                        self.frame = 0
                    else:
                        self.frame = 0
            # Atualiza frame de hit do ataque
            if (anim_key == 'attack_start' or anim_key == 'attack_end') and self.atacando:
                self.ataque_frame_atual = self.frame