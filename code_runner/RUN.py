import pygame
import math

pygame.init()

screen = pygame.display.set_mode((1280, 720))
x = 0
dir = 1
frames = 0

while True:
	screen.fill((0, 0, 0))
	
	pygame.draw.rect(screen, (
		round(255*(math.sin(0.004*frames)**2)),
		round(255*(math.sin(0.004*frames+(math.pi/4))**2)),
		round(255*(math.sin(0.002*frames+(math.pi/4))**2))
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
	frames += 1
	pygame.display.flip()