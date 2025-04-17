"""
GUI Elements.
"""

from pygame.draw import rect
from pygame import Surface, SRCALPHA, Cursor
import pygame.cursors as cursors
import pygame.mouse
import pygame.font

def zero(x): return x if x > 0 else 0

class Relation:
    """
    "Pointer" to a surface variable.

    ### Parameters
    - `r` - The variable.
    - `f` - A function of `x` to pass in to the value of `r`

    ### Working Variables
    - `screen_height`
    """
    def __init__(self, r, f=None):
        self.string = r
        self.function = f

class Widget:
    def __init__(self, x, y, w, h, padding: tuple[int, int]):
        self._x = x
        self._y = y
        self._w = w
        self._h = h
        self.padding_x = padding[0]
        self.padding_y = padding[1]
        self.children = []
    
    @staticmethod
    def convert(r, surface: Surface):
        if isinstance(r, Relation):
            if r.string == "screen_height":
                if r.function:
                    return r.function(surface.get_height())
                return surface.get_height()
        return r

    def draw(self, surface: Surface):
        self.x = Widget.convert(self._x, surface)
        self.y = Widget.convert(self._y, surface)
        self.w = Widget.convert(self._w, surface)
        self.h = Widget.convert(self._h, surface)

    def add_child(self, elem): self.children.append(elem)

    def set_padding(self, x, y):
        self.padding_x = x
        self.padding_y = y
        return self
    
class DraggableWidget(Widget):
    def __init__(self, x, y, w, h, padding: tuple[int, int]):
        self.original_w = w
        super().__init__(x, y, w, h, padding)

    def draggable(self, surface: Surface):
        mouse_pos = pygame.mouse.get_pos()
        surf = Surface((6, 300), SRCALPHA)
        if self.x + self.w - 20 < mouse_pos[0] < self.x + self.w + 20:
            pygame.mouse.set_cursor(7)
            rect(surf, (100, 100, 100), (0, 0, 6, surf.get_height()))
            surf.set_alpha(100)
            surface.blit(surf, (self.x + self.w - 3, mouse_pos[1] - 150))
            if pygame.mouse.get_pressed()[0]:
                if self._w >= 150:
                    self._w = mouse_pos[0]
                else:
                    self._w = 150
            if pygame.mouse.get_pressed()[1]: self._w = self.original_w
        else:
            pygame.mouse.set_cursor(0)

class Element:
    def __init__(self, height, parent: Widget=None):
        self.height = height
        self.parent = parent
        self.index = len(self.parent.children)
        if self.parent: parent.add_child(self)
        self.hovering = False

    def draw(self, surface: Surface):
        self.x = self.parent.x + self.parent.padding_x
        self.y = self.parent.y + self.parent.padding_x + (self.height + self.parent.padding_y) * self.index

        mouse_pos = pygame.mouse.get_pos()
        if self.x < mouse_pos[0] < self.x + self.parent.w - 2 * self.parent.padding_x and self.y < mouse_pos[1] < self.y + self.height:
            self.hovering = True
            if pygame.mouse.get_pressed()[0]: self.on_click(self)
        else:
            self.hovering = False

    def on_click(self): ...

class RightClickMenu:
    def __init__(self, options, pos=(0, 0), w=200):
        self.options = options
        self.option_list = []

        for g in options: self.option_list.extend(g)
        self.max_len = max([len(option) for option in self.option_list])

        self.x = pos[0]
        self.y = pos[1]
        self.w = w

    def draw(self, surface: Surface, font: pygame.font.Font):
        r = (self.x, self.y, self.w + 8 * zero(self.max_len - 15), 20 + 25 * len(self.option_list) + 5 * len(self.options))
        rect(surface, (35, 35, 35), r, border_radius=5)
        rect(surface, (63, 63, 63), r, width=1, border_radius=5)

        offset = 0
        padding = 0

        mouse_pos = pygame.mouse.get_pos()
        for i, option in enumerate(self.option_list):
            option_rect = pygame.Rect(self.x, self.y + 7 + 25 * i + padding, self.w, 25)
            if option_rect.collidepoint(mouse_pos):
                rect(surface, (255, 63, 127), (option_rect[0] + 5, option_rect[1], option_rect[2] - 10, option_rect[3]), border_radius=5)
                if pygame.mouse.get_pressed()[0]:
                    self.on_option_click(option)
        
        for group in self.options:
            for i, option in enumerate(group):
                surface.blit(font.render(option, True, (255, 255, 255)), (self.x + 15, self.y + 5 + padding + 25 * (i + offset)))
            offset += len(group)
            padding += 10
            if group != self.options[len(self.options)-1]: rect(surface, (63, 63, 63), (self.x, self.y + 10 + 25 * offset + (padding - 10), self.w + 8 * zero(self.max_len - 15), 2))