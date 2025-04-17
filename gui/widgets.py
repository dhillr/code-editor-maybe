import pygame.draw as draw
import pygame.mouse as mouse
from pygame.font import Font
from helper.gui import Widget, DraggableWidget, Element, Relation, Surface, RightClickMenu

class Explorer(DraggableWidget):
    def __init__(self):
        super().__init__(0, 0, 300, Relation("screen_height"), (10, 5))
        self.menu = None

    def on_option_click(self, option): print(option)

    def draw(self, surface, font):
        super().draw(surface)
        draw.rect(surface, (40, 40, 40), (self.x, self.y, self.w, self.h))
        super().draggable(surface)

        mouse_pos = mouse.get_pos()
        if mouse_pos[0] <= self._w:
            if mouse.get_pressed()[2] and not self.menu:
                self.menu = RightClickMenu([
                    ["New File...", "New Folder..."],
                    ["Copy Path"],
                    ["Other Stuff...", "Other Other Stuff...", "idk man", "code! :D"]
                ], pos=mouse_pos)
        if self.menu: 
            self.menu.draw(surface, font)
            self.menu.on_option_click = self.on_option_click

class ExplorerItem(Element):
    def __init__(self, height, text, parent: Widget=None):
        super().__init__(height, parent)
        self.text = text

    def draw(self, surface: Surface, font: Font):
        super().draw(surface)

        rect = (self.x, self.y, self.parent.w - 2 * self.parent.padding_x, self.height)
        if self.hovering: draw.rect(surface, (31, 31, 31), rect)
        surface.blit(font.render(self.text, True, (255, 255, 255)), (self.x + self.parent.padding_x + 20, self.y + self.height // 2 - 15))

class FileElement(ExplorerItem):
    def __init__(self, height, text, parent: Widget=None):
        super().__init__(height, text, parent)

    def draw(self, surface: Surface, font: Font):
        super().draw(surface, font)
        draw.circle(surface, (255, 255, 255), (self.x + self.parent.padding_x, self.y + self.height // 2), 10)

class FolderElement(ExplorerItem):
    def __init__(self, height, text, parent: Widget=None):
        super().__init__(height, text, parent)

    def draw(self, surface: Surface, font: Font):
        super().draw(surface, font)
        draw.rect(surface, (255, 255, 255), (self.x + self.parent.padding_x - 10, self.y + self.height // 2 - 10, 20, 20))