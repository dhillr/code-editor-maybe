import pygame
import math

pygame.init()

screen = pygame.display.set_mode((1280, 720))
x = 0
dir = 1

while True:
	screen.fill((0, 0, 0))
	
	pygame.draw.rect(screen, (
		round(255*(math.sin(0.004*x)**2)),
		round(255*(math.sin(0.004*x+(math.pi/4))**2)),
		round(255*(math.sin(0.002*x+(math.pi/4))**2))
	), (x, 0, 100, 100))
	
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			exit()
	
	x += dir
	if x > screen.get_width() - 100:
		x = screen.get_width() - 100
		dir = -dir
	if x < 0:
		x = 0
		dir = -dir
	pygame.display.flip()