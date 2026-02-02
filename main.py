import pygame
from pygame import mixer
import csv
import constantes
from personagem import Personagem
from arma import Arma
from itens import Item
from mundo import Mundo
from botao import Botao

mixer.init()
pygame.init()

screen = pygame.display.set_mode((constantes.LARGURA_TELA, constantes.ALTURA_TELA))
pygame.display.set_caption("Dungeon Crawler")

clock = pygame.time.Clock()

level = 1
start_game = False
pause_game = False
start_intro = False
screen_scroll = [0, 0]

vitoria = False
vitoria_inicio = 0
VITORIA_DURACAO = 3000

moving_left = False
moving_right = False
moving_up = False
moving_down = False

font = pygame.font.Font("assets/fonts/AtariClassic.ttf", 20)
font_title = pygame.font.Font("assets/fonts/AtariClassic.ttf", 40)

def scale_img(image, scale):
  w = image.get_width()
  h = image.get_height()
  return pygame.transform.scale(image, (w * scale, h * scale))

pygame.mixer.music.load("assets/audio/music.wav")
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 5000)
shot_fx = pygame.mixer.Sound("assets/audio/arrow_shot.mp3")
shot_fx.set_volume(0.5)
hit_fx = pygame.mixer.Sound("assets/audio/arrow_hit.wav")
hit_fx.set_volume(0.5)
coin_fx = pygame.mixer.Sound("assets/audio/coin.wav")
coin_fx.set_volume(0.5)
heal_fx = pygame.mixer.Sound("assets/audio/heal.wav")
heal_fx.set_volume(0.5)

start_img = scale_img(pygame.image.load("assets/images/buttons/button_start.png").convert_alpha(), constantes.ESCALA_BOTAO)
exit_img = scale_img(pygame.image.load("assets/images/buttons/button_exit.png").convert_alpha(), constantes.ESCALA_BOTAO)
restart_img = scale_img(pygame.image.load("assets/images/buttons/button_restart.png").convert_alpha(), constantes.ESCALA_BOTAO)
resume_img = scale_img(pygame.image.load("assets/images/buttons/button_resume.png").convert_alpha(), constantes.ESCALA_BOTAO)

heart_empty = scale_img(pygame.image.load("assets/images/items/heart_empty.png").convert_alpha(), constantes.ESCALA_ITEM)
heart_half = scale_img(pygame.image.load("assets/images/items/heart_half.png").convert_alpha(), constantes.ESCALA_ITEM)
heart_full = scale_img(pygame.image.load("assets/images/items/heart_full.png").convert_alpha(), constantes.ESCALA_ITEM)

coin_images = []
for x in range(4):
  img = scale_img(pygame.image.load(f"assets/images/items/coin_f{x}.png").convert_alpha(), constantes.ESCALA_ITEM)
  coin_images.append(img)

red_potion = scale_img(pygame.image.load("assets/images/items/potion_red.png").convert_alpha(), constantes.ESCALA_POCAO)

item_images = []
item_images.append(coin_images)
item_images.append(red_potion)

bow_image = scale_img(pygame.image.load("assets/images/weapons/bow.png").convert_alpha(), constantes.ESCALA_ARMA)
arrow_image = scale_img(pygame.image.load("assets/images/weapons/arrow.png").convert_alpha(), constantes.ESCALA_ARMA)
fireball_image = scale_img(pygame.image.load("assets/images/weapons/fireball.png").convert_alpha(), constantes.ESCALA_BOLA_FOGO)

tile_list = []
for x in range(constantes.TIPOS_TILE):
  tile_image = pygame.image.load(f"assets/images/tiles/{x}.png").convert_alpha()
  tile_image = pygame.transform.scale(tile_image, (constantes.TAMANHO_TILE, constantes.TAMANHO_TILE))
  tile_list.append(tile_image)

mob_animations = []
mob_types = ["elf", "imp", "skeleton", "goblin", "muddy", "tiny_zombie", "big_demon"]

animation_types = ["idle", "run"]
for mob in mob_types:
  animation_list = []
  for animation in animation_types:
    temp_list = []
    for i in range(4):
      img = pygame.image.load(f"assets/images/characters/{mob}/{animation}/{i}.png").convert_alpha()
      img = scale_img(img, constantes.ESCALA)
      temp_list.append(img)
    animation_list.append(temp_list)
  mob_animations.append(animation_list)


def draw_text(text, font, text_col, x, y):
  img = font.render(text, True, text_col)
  screen.blit(img, (x, y))

def draw_info():
  pygame.draw.rect(screen, constantes.PAINEL, (0, 0, constantes.LARGURA_TELA, 50))
  pygame.draw.line(screen, constantes.BRANCO, (0, 50), (constantes.LARGURA_TELA, 50))
  half_heart_drawn = False
  for i in range(5):
    if jogador.health >= ((i + 1) * 20):
      screen.blit(heart_full, (10 + i * 50, 0))
    elif (jogador.health % 20 > 0) and half_heart_drawn == False:
      screen.blit(heart_half, (10 + i * 50, 0))
      half_heart_drawn = True
    else:
      screen.blit(heart_empty, (10 + i * 50, 0))

  draw_text("FASE: " + str(level), font, constantes.BRANCO, constantes.LARGURA_TELA / 2, 15)
  draw_text(f"MOEDAS: {jogador.score}", font, constantes.BRANCO, constantes.LARGURA_TELA - 200, 15)

def draw_menu_background():
  for y in range(0, constantes.ALTURA_TELA, constantes.TAMANHO_TILE):
    for x in range(0, constantes.LARGURA_TELA, constantes.TAMANHO_TILE):
      screen.blit(tile_list[0], (x, y))

def reset_level():
  grupo_texto_dano.empty()
  grupo_flechas.empty()
  grupo_itens.empty()
  grupo_bolas.empty()

  data = []
  for row in range(constantes.LINHAS):
    r = [-1] * constantes.COLUNAS
    data.append(r)

  return data



class DamageText(pygame.sprite.Sprite):
  def __init__(self, x, y, damage, color):
    pygame.sprite.Sprite.__init__(self)
    self.image = font.render(damage, True, color)
    self.rect = self.image.get_rect()
    self.rect.center = (x, y)
    self.counter = 0

  def update(self):
    self.rect.x += screen_scroll[0]
    self.rect.y += screen_scroll[1]

    self.rect.y -= 1
    self.counter += 1
    if self.counter > 30:
      self.kill()

class ScreenFade():
  def __init__(self, direction, colour, speed):
    self.direction = direction
    self.colour = colour
    self.speed = speed
    self.fade_counter = 0

  def fade(self):
    fade_complete = False
    self.fade_counter += self.speed
    if self.direction == 1:
      pygame.draw.rect(screen, self.colour, (0 - self.fade_counter, 0, constantes.LARGURA_TELA // 2, constantes.ALTURA_TELA))
      pygame.draw.rect(screen, self.colour, (constantes.LARGURA_TELA // 2 + self.fade_counter, 0, constantes.LARGURA_TELA, constantes.ALTURA_TELA))
      pygame.draw.rect(screen, self.colour, (0, 0 - self.fade_counter, constantes.LARGURA_TELA, constantes.ALTURA_TELA // 2))
      pygame.draw.rect(screen, self.colour, (0, constantes.ALTURA_TELA // 2 + self.fade_counter, constantes.LARGURA_TELA, constantes.ALTURA_TELA))
    elif self.direction == 2:
      pygame.draw.rect(screen, self.colour, (0, 0, constantes.LARGURA_TELA, 0 + self.fade_counter))

    if self.fade_counter >= constantes.LARGURA_TELA:
      fade_complete = True
world_data = []
for row in range(constantes.LINHAS):
  r = [-1] * constantes.COLUNAS
  world_data.append(r)
with open(f"levels/level{level}_data.csv", newline="") as csvfile:
  reader = csv.reader(csvfile, delimiter = ",")
  for x, row in enumerate(reader):
    for y, tile in enumerate(row):
      world_data[x][y] = int(tile)


world = Mundo()
world.process_data(world_data, tile_list, item_images, mob_animations)

jogador = world.player
arco = Arma(bow_image, arrow_image)

lista_inimigos = world.character_list

grupo_texto_dano = pygame.sprite.Group()
grupo_flechas = pygame.sprite.Group()
grupo_itens = pygame.sprite.Group()
grupo_bolas = pygame.sprite.Group()

score_coin = Item(constantes.LARGURA_TELA - 115, 23, 0, coin_images, True)
grupo_itens.add(score_coin)
for item in world.item_list:
  grupo_itens.add(item)

intro_fade = ScreenFade(1, constantes.PRETO, 4)
death_fade = ScreenFade(2, constantes.ROSA, 4)

start_button = Botao(constantes.LARGURA_TELA // 2 - 100, constantes.ALTURA_TELA // 2 - 50, start_img)
exit_button = Botao(constantes.LARGURA_TELA // 2 - 100, constantes.ALTURA_TELA // 2 + 50, exit_img)
restart_button = Botao(constantes.LARGURA_TELA // 2 - 100, constantes.ALTURA_TELA // 2 - 50, restart_img)
resume_button = Botao(constantes.LARGURA_TELA // 2 - 100, constantes.ALTURA_TELA // 2 - 150, resume_img)

run = True
while run:

  clock.tick(constantes.FPS)

  if start_game == False:
    draw_menu_background()
    title_text = font_title.render("Pixel Escape", True, constantes.BRANCO)
    screen.blit(title_text, (constantes.LARGURA_TELA // 2 - title_text.get_width() // 2, 100))
    if start_button.desenhar(screen):
      start_game = True
      start_intro = True
    if exit_button.desenhar(screen):
      run = False
  else:
    if pause_game == True:
      draw_menu_background()
      if resume_button.desenhar(screen):
        pause_game = False
      if exit_button.desenhar(screen):
        run = False
    else:
      screen.fill(constantes.FUNDO)

      if jogador.alive:
        dx = 0
        dy = 0
        if moving_right == True:
          dx = constantes.VELOCIDADE
        if moving_left == True:
          dx = -constantes.VELOCIDADE
        if moving_up == True:
          dy = -constantes.VELOCIDADE
        if moving_down == True:
          dy = constantes.VELOCIDADE

        screen_scroll, level_complete = jogador.move(dx, dy, world.obstacle_tiles, world.exit_tile)

        world.update(screen_scroll)
        for enemy in lista_inimigos:
          fireball = enemy.ai(jogador, world.obstacle_tiles, screen_scroll, fireball_image)
          if fireball:
            grupo_bolas.add(fireball)
          if enemy.alive:
            enemy.update()
        jogador.update()
        arrow = arco.update(jogador)
        if arrow:
          grupo_flechas.add(arrow)
          shot_fx.play()
        for flecha in grupo_flechas:
          damage, damage_pos = flecha.update(screen_scroll, world.obstacle_tiles, lista_inimigos)
          if damage:
            damage_text = DamageText(damage_pos.centerx, damage_pos.y, str(damage), constantes.VERMELHO)
            grupo_texto_dano.add(damage_text)
            hit_fx.play()
        grupo_texto_dano.update()
        grupo_bolas.update(screen_scroll, jogador)
        grupo_itens.update(screen_scroll, jogador, coin_fx, heal_fx)

        if not vitoria:
          for enemy in lista_inimigos:
            if getattr(enemy, 'boss', False) and not enemy.alive:
              vitoria = True
              vitoria_inicio = pygame.time.get_ticks()
              break

      world.draw(screen)
      for enemy in lista_inimigos:
        enemy.draw(screen)
      jogador.draw(screen)
      arco.draw(screen)
      for flecha in grupo_flechas:
        flecha.draw(screen)
      for bola in grupo_bolas:
        bola.draw(screen)
      grupo_texto_dano.draw(screen)
      grupo_itens.draw(screen)
      draw_info()
      score_coin.desenhar(screen)

      if vitoria:
        v_img = font.render("VOCÊ VENCEU!", True, constantes.BRANCO)
        screen.blit(v_img, (constantes.LARGURA_TELA//2 - v_img.get_width()//2, constantes.ALTURA_TELA//2 - 100))

        if pygame.time.get_ticks() - vitoria_inicio > VITORIA_DURACAO:
          vitoria = False
          start_game = False
          level = 1
          world_data = reset_level()
          with open(f"levels/level{level}_data.csv", newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter = ",")
            for x, row in enumerate(reader):
              for y, tile in enumerate(row):
                world_data[x][y] = int(tile)
          world = Mundo()
          world.process_data(world_data, tile_list, item_images, mob_animations)
          jogador = world.player
          lista_inimigos = world.character_list
          score_coin = Item(constantes.LARGURA_TELA - 115, 23, 0, coin_images, True)
          grupo_itens.add(score_coin)
          for item in world.item_list:
            grupo_itens.add(item)

      if level_complete == True:
        start_intro = True
        level += 1
        world_data = reset_level()
        with open(f"levels/level{level}_data.csv", newline="") as csvfile:
          reader = csv.reader(csvfile, delimiter = ",")
          for x, row in enumerate(reader):
            for y, tile in enumerate(row):
              world_data[x][y] = int(tile)
        world = Mundo()
        world.process_data(world_data, tile_list, item_images, mob_animations)
        temp_hp = jogador.health
        temp_score = jogador.score
        jogador = world.player
        jogador.health = temp_hp
        jogador.score = temp_score
        lista_inimigos = world.character_list
        score_coin = Item(constantes.LARGURA_TELA - 115, 23, 0, coin_images, True)
        grupo_itens.add(score_coin)
        for item in world.item_list:
          grupo_itens.add(item)


      if start_intro == True:
        if intro_fade.fade():
          start_intro = False
          intro_fade.fade_counter = 0

      if jogador.alive == False:
        death_fade.fade()

        go_img = font.render("FIM DE JOGO", True, constantes.BRANCO)
        screen.blit(go_img, (constantes.LARGURA_TELA//2 - go_img.get_width()//2, constantes.ALTURA_TELA//2 - 100))

        if restart_button.desenhar(screen):
          death_fade.fade_counter = 0
          start_intro = True
          world_data = reset_level()
          with open(f"levels/level{level}_data.csv", newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter = ",")
            for x, row in enumerate(reader):
              for y, tile in enumerate(row):
                world_data[x][y] = int(tile)
          world = Mundo()
          world.process_data(world_data, tile_list, item_images, mob_animations)
          temp_score = jogador.score
          jogador = world.player
          jogador.score = temp_score
          lista_inimigos = world.character_list
          score_coin = Item(constantes.LARGURA_TELA - 115, 23, 0, coin_images, True)
          grupo_itens.add(score_coin)
          for item in world.item_list:
            grupo_itens.add(item)

        if exit_button.desenhar(screen):
          run = False

  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      run = False
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_a:
        moving_left = True
      if event.key == pygame.K_d:
        moving_right = True
      if event.key == pygame.K_w:
        moving_up = True
      if event.key == pygame.K_s:
        moving_down = True
      if event.key == pygame.K_ESCAPE:
        pause_game = True

    if event.type == pygame.KEYUP:
      if event.key == pygame.K_a:
        moving_left = False
      if event.key == pygame.K_d:
        moving_right = False
      if event.key == pygame.K_w:
        moving_up = False
      if event.key == pygame.K_s:
        moving_down = False

  pygame.display.update()
  
pygame.quit()