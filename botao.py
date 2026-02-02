import pygame

class Botao():
  def __init__(self, x, y, image):
    self.image = image
    self.rect = self.image.get_rect()
    self.rect.topleft = (x, y)

  def desenhar(self, surface):
    acao = False

    pos = pygame.mouse.get_pos()

    if self.rect.collidepoint(pos):
      if pygame.mouse.get_pressed()[0]:
        acao = True

    surface.blit(self.image, self.rect)

    return acao