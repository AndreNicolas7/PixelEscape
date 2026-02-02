import pygame
import math
import arma
import constantes

class Personagem():
  def __init__(self, x, y, health, mob_animations, char_type, boss, size):
    self.char_type = char_type
    self.boss = boss
    self.score = 0
    self.flip = False
    self.animation_list = mob_animations[char_type]
    self.frame_index = 0
    self.action = 0#0:idle, 1:run
    self.update_time = pygame.time.get_ticks()
    self.running = False
    self.health = health
    self.alive = True
    self.hit = False
    self.last_hit = pygame.time.get_ticks()
    self.last_attack = pygame.time.get_ticks()
    self.stunned = False

    self.image = self.animation_list[self.action][self.frame_index]
    self.rect = pygame.Rect(0, 0, constantes.TAMANHO_TILE * size, constantes.TAMANHO_TILE * size)
    self.rect.center = (x, y)

  def move(self, dx, dy, obstacle_tiles, exit_tile = None):
    screen_scroll = [0, 0]
    level_complete = False
    self.running = False

    if dx != 0 or dy != 0:
      self.running = True
    if dx < 0:
      self.flip = True
    if dx > 0:
      self.flip = False
    #controla velocidade diagonal
    if dx != 0 and dy != 0:
      dx = dx * (math.sqrt(2)/2)
      dy = dy * (math.sqrt(2)/2)

    #checa colisão com o mapa na direção x
    self.rect.x += dx
    for obstacle in obstacle_tiles:
      #checa a colisão
      if obstacle[1].colliderect(self.rect):
        #checa de qual lado a colisão ocorreu
        if dx > 0:
          self.rect.right = obstacle[1].left
        if dx < 0:
          self.rect.left = obstacle[1].right

    #checa colisão com o mapa na direção y
    self.rect.y += dy
    for obstacle in obstacle_tiles:
      #checa a colisão
      if obstacle[1].colliderect(self.rect):
        #checa de qual lado a colisão ocorreu
        if dy > 0:
          self.rect.bottom = obstacle[1].top
        if dy < 0:
          self.rect.top = obstacle[1].bottom


    #lógica aplicável apenas ao jogador
    if self.char_type == 0:
      #verifica colisão com a escada de saída
      if exit_tile[1].colliderect(self.rect):
        #garante que o jogador esteja próximo ao centro da escada
        exit_dist = math.sqrt(((self.rect.centerx - exit_tile[1].centerx) ** 2) + ((self.rect.centery - exit_tile[1].centery) ** 2))
        if exit_dist < 20:
          level_complete = True

      #atualiza a rolagem da tela com base na posição do jogador
      #move a câmera para os lados
      if self.rect.right > (constantes.LARGURA_TELA - constantes.LIMITE_ROLAGEM):
        screen_scroll[0] = (constantes.LARGURA_TELA - constantes.LIMITE_ROLAGEM) - self.rect.right
        self.rect.right = constantes.LARGURA_TELA - constantes.LIMITE_ROLAGEM
      if self.rect.left < constantes.LIMITE_ROLAGEM:
        screen_scroll[0] = constantes.LIMITE_ROLAGEM - self.rect.left
        self.rect.left = constantes.LIMITE_ROLAGEM

      #move a câmera para cima e para baixo
      if self.rect.bottom > (constantes.ALTURA_TELA - constantes.LIMITE_ROLAGEM):
        screen_scroll[1] = (constantes.ALTURA_TELA - constantes.LIMITE_ROLAGEM) - self.rect.bottom
        self.rect.bottom = constantes.ALTURA_TELA - constantes.LIMITE_ROLAGEM
      if self.rect.top < constantes.LIMITE_ROLAGEM:
        screen_scroll[1] = constantes.LIMITE_ROLAGEM - self.rect.top
        self.rect.top = constantes.LIMITE_ROLAGEM

    return screen_scroll, level_complete


  def ai(self, player, obstacle_tiles, screen_scroll, fireball_image):
    clipped_line = ()
    stun_cooldown = 100
    ai_dx = 0
    ai_dy = 0
    fireball = None

    self.rect.x += screen_scroll[0]
    self.rect.y += screen_scroll[1]

    line_of_sight = ((self.rect.centerx, self.rect.centery), (player.rect.centerx, player.rect.centery))
    for obstacle in obstacle_tiles:
      if obstacle[1].clipline(line_of_sight):
        clipped_line = obstacle[1].clipline(line_of_sight)

    dist = math.sqrt(((self.rect.centerx - player.rect.centerx) ** 2) + ((self.rect.centery - player.rect.centery) ** 2))
    if not clipped_line and dist > constantes.ALCANCE:
      if self.rect.centerx > player.rect.centerx:
        ai_dx = -constantes.VELOCIDADE_INIMIGO
      if self.rect.centerx < player.rect.centerx:
        ai_dx = constantes.VELOCIDADE_INIMIGO
      if self.rect.centery > player.rect.centery:
        ai_dy = -constantes.VELOCIDADE_INIMIGO
      if self.rect.centery < player.rect.centery:
        ai_dy = constantes.VELOCIDADE_INIMIGO

    if self.alive:
      if not self.stunned:
        self.move(ai_dx, ai_dy, obstacle_tiles)
        if dist < constantes.ALCANCE_ATAQUE and player.hit == False:
          player.health -= 10
          player.hit = True
          player.last_hit = pygame.time.get_ticks()
        fireball_cooldown = 700
        if self.boss:
          if dist < 500:
            if pygame.time.get_ticks() - self.last_attack >= fireball_cooldown:
              fireball = arma.BolaFogo(fireball_image, self.rect.centerx, self.rect.centery, player.rect.centerx, player.rect.centery)
              self.last_attack = pygame.time.get_ticks()


      if self.hit == True:
        self.hit = False
        self.last_hit = pygame.time.get_ticks()
        self.stunned = True
        self.running = False
        self.update_action(0)

      if (pygame.time.get_ticks() - self.last_hit > stun_cooldown):
        self.stunned = False

    return fireball

  def update(self):
    if self.health <= 0:
      self.health = 0
      self.alive = False

    hit_cooldown = 1000
    if self.char_type == 0:
      if self.hit == True and (pygame.time.get_ticks() - self.last_hit) > hit_cooldown:
        self.hit = False

    if self.running == True:
      self.update_action(1)
    else:
      self.update_action(0)

    animation_cooldown = 70
    self.image = self.animation_list[self.action][self.frame_index]
    if pygame.time.get_ticks() - self.update_time > animation_cooldown:
      self.frame_index += 1
      self.update_time = pygame.time.get_ticks()
    if self.frame_index >= len(self.animation_list[self.action]):
      self.frame_index = 0


  def update_action(self, new_action):
    if new_action != self.action:
      self.action = new_action
      self.frame_index = 0
      self.update_time = pygame.time.get_ticks()


  def draw(self, surface):
    flipped_image = pygame.transform.flip(self.image, self.flip, False)
    if self.char_type == 0:
      surface.blit(flipped_image, (self.rect.x, self.rect.y - constantes.ESCALA * constantes.MARGEM))
    else:
      surface.blit(flipped_image, self.rect)