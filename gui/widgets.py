import pygame.draw as draw
import pygame.mouse as mouse
from json import loads
from pygame import quit
from pygame.font import Font
from helper.gui import Widget, DraggableWidget, Element, Relation, Surface, RightClickMenu

class Explorer(DraggableWidget):
    def __init__(self):
        super().__init__(0, 0, 300, Relation("screen_height"), (10, 5))
        self.menu = None

    def on_option_click(self, option, option_id): 
        if (option_id == 0):
            files = loads(open("./local/files.json", "r").read())
            open(files["active_folder"]+"/"+"Untitled-1", "w")

    def destroy_menu(self): self.menu = None

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
                ], pos=mouse_pos, destroyer=self.destroy_menu)
        if self.menu: 
            self.menu.on_option_click = self.on_option_click
            self.menu.draw(surface, font)         

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