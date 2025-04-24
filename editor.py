"""
### Code Editor
My goal is to make an IDE that can run on a Chromebook.

(Yes, you can run Python files on a chromebook)
"""
import pygame
import os
import subprocess
import json
import time
import re
import gui.widgets as widgets
import gui.explorer as gui_explorer
from tkinter import messagebox
from helper import filehelper
from helper.tokenizer import *
from gui import widgets
from sys import platform
from math import log10, floor

def get_cursor_line(p, t) -> int:
    if p == -1: return len(t.split("\n"))-1
    return p

def get_cursor_char(p, t) -> int:
    if p == -1: return len(t)-1
    return p

def restore(additional_data="") -> None:
    messagebox.showerror("Error", "An error occured while trying to load your last file.\nTo prevent more errors, we reset:\n- Your active folder cache\n- Your active file cache\n- Your recent folder cache\n\nError: " + additional_data)
    open("local/files.json", "w").write('{\n\t"active_folder": "",\n\t"active": "",\n\t"recent": []\n}')

def save() -> None:
    open(files["active"], "w").write(code)

def set_index_in_str(str, index, val) -> str:
    return str[0:index]+val+str[index+1:len(str)]

def render_text_colormap(txt: str, colormap: str, font: pygame.font.Font) -> pygame.Surface:
    colored_text = ""
    text_blocks = []

    colors = {
        " ": (255, 255, 255),
        "a": (195, 135, 190),
        "b": (220, 220, 175),
        "c": (216, 141, 109),
        "d": (184, 204, 169),
        "e": (80, 200, 175),
        "f": (159, 219, 253)
    }

    for color_index, char in enumerate(txt):
        colored_text += char
        color = colormap[color_index]
        next_color = colormap[color_index+1] if color_index < len(txt)-1 and color_index < len(txt)-1 else ""

        if color != next_color:
            text_blocks.append({
                "text": colored_text,
                "color": color
            })
            colored_text = ""
    text_surface = pygame.Surface(font.size(txt))
    text_surface.set_colorkey((0, 0, 0))
    offset = 0

    for block in text_blocks:
        text = font.render(block["text"], True, colors.get(block["color"]))
        text_surface.blit(text, (offset, 0))
        offset += font.size(block["text"])[0]

    return text_surface

pygame.init()
screen: pygame.Surface = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
pygame.display.set_caption("Code Editor")
font = pygame.font.Font("fonts/CONSOLA.TTF", 20)
alt_font = pygame.font.Font("fonts/SEGOEUI.TTF", 20)

if open("local/files.json").read() == "": restore()

files = json.loads(open("local/files.json").read())

if not os.path.isfile(files["active"]): restore()

if files["active_folder"] == "":
    f = filehelper.folder_chooser()
    open("local/files.json", "w").write(json.dumps({
        "active_folder": f,
        "active": f+"/"+filehelper.first_file(f),
        "recent": files["recent"]
    }))
    files = json.loads(open("local/files.json").read())

active = ""
try:
    active = "" if not files["active"] else open(files["active"]).read()
except Exception as e:
    restore(str(e))
    f = filehelper.folder_chooser()
    open("local/files.json", "w").write(json.dumps({
        "active_folder": f,
        "active": f+"/"+filehelper.first_file(f),
        "recent": files["recent"]
    }))
    files = json.loads(open("local/files.json").read())

code: str = active
prev_code: str = ""
tokenizer = PythonTokenizer(code)
c = []

clock = pygame.time.Clock()
elapsed_ms = 0
start_time = time.time()
typing = False
since_key_press = 0
keycombo = []
output = None

cursor_pos = [-1, -1] # [row, column] (-1 = last letter/line)
scroll = 0

explorer = widgets.Explorer().set_padding(10, 0)
items = gui_explorer.explorer_tab(explorer)

pygame.key.set_repeat(500, 30)
while True:
    screen.fill((31, 31, 31))

    if time.time() - since_key_press > 0.5: typing = False
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if open(files["active"]).read() != code:
                if messagebox.askyesno("Your changes are unsaved", "You have some unsaved changes.\nWould you like to save them?", icon="warning"): save()
            pygame.quit()
            exit()
        
        if event.type == pygame.KEYDOWN:
            if not event.key in keycombo: keycombo.append(event.key)
            since_key_press = time.time()
            typing = True

            if event.key == pygame.K_UP:
                code = code.replace("\r", "\n")
                if cursor_pos[1] == -1: cursor_pos[1] = len(code.split("\n"))-1
                if cursor_pos[1] > 0: cursor_pos[1] -= 1
                cursor_pos[0] = -1
            if event.key == pygame.K_DOWN:
                code = code.replace("\r", "\n")
                if cursor_pos[1] != -1: cursor_pos[1] += 1
                if cursor_pos[1] == len(code.split("\n"))-1: cursor_pos[1] = -1
                cursor_pos[0] = -1
            line_len = len(code.split("\n")[get_cursor_line(cursor_pos[1], code)])
            if event.key == pygame.K_LEFT:
                code = code.replace("\r", "\n")
                if cursor_pos[0] == -1: cursor_pos[0] = line_len-1
                if cursor_pos[0] > 0: cursor_pos[0] -= 1
            if event.key == pygame.K_RIGHT:
                code = code.replace("\r", "\n")
                if cursor_pos[0] != -1: cursor_pos[0] += 1
                if cursor_pos[0] == line_len-1: cursor_pos[0] = -1

            if keycombo == [pygame.K_LCTRL, pygame.K_s]:
                save()
            elif keycombo == [pygame.K_LCTRL, pygame.K_m]:
                if platform == "win32":
                    output = subprocess.Popen(['python', files["active"]])
                    # output = subprocess.Popen(['python', files["active"]], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                else:
                    os.system(f'python3 "{files["active"]}"')
            elif keycombo == [pygame.K_LCTRL, pygame.K_LSHIFT, pygame.K_p]:
                f = filehelper.folder_chooser()
                if f == "": break
                dirlist = os.listdir(f)

                open("local/files.json", "w").write(json.dumps({
                    "active_folder": f,
                    "active": f+"/"+filehelper.first_file(f),
                    "recent": [f, *files["recent"][0:9]]
                }, indent=4))
                items = gui_explorer.explorer_tab(explorer)
                files = json.loads(open("local/files.json").read())
                code = open(f+"/"+filehelper.first_file(f)).read()
            elif event.key == pygame.K_BACKSPACE:
                if cursor_pos[1] == -1:
                    if cursor_pos[0] == -1:
                        code = code[0:len(code)-1]
                    else:
                        lines = code.split("\n")
                        lines[len(lines)-1] = lines[len(lines)-1][0:cursor_pos[0]] + lines[len(lines)-1][cursor_pos[0]+1:len(lines[len(lines)-1])]
                        new_line = -1
                        code = ""
                        for i, line in enumerate(lines):
                            code += line + ("\n" if i < len(lines)-1 or i == new_line else "")
                        if cursor_pos[0] == -1: cursor_pos[0] = line_len-1
                        if cursor_pos[0] > 0: cursor_pos[0] -= 1
                else:
                    if cursor_pos[0] == -1:
                        lines = code.split("\n")
                        lines[cursor_pos[1]] = lines[cursor_pos[1]][0:len(lines[cursor_pos[1]])-1]
                        new_line = -1
                        
                        code = ""
                        for i, line in enumerate(lines):
                            code += line + ("\n" if i < len(lines)-1 or i == new_line else "")

                        if (lines[cursor_pos[1]] == ""):
                            newline_index = list(re.finditer(re.escape("\n"), code))[cursor_pos[1]].start()
                            code = set_index_in_str(code, newline_index, "")
                            new_line = cursor_pos[1]
                            cursor_pos[1] -= 1
                    else:
                        lines = code.split("\n")
                        lines[cursor_pos[1]] = lines[cursor_pos[1]][0:cursor_pos[0]] + lines[cursor_pos[1]][cursor_pos[0]+1:len(lines[cursor_pos[1]])]
                        new_line = -1
                        if (lines[cursor_pos[1]] == ""): new_line = cursor_pos[1]
                        code = ""
                        for i, line in enumerate(lines):
                            code += line + ("\n" if i < len(lines)-1 or i == new_line else "")
                        if cursor_pos[0] == -1: cursor_pos[0] = line_len-1
                        if cursor_pos[0] > 0: cursor_pos[0] -= 1
            else:
                if str(event.unicode).isascii():
                    if cursor_pos[1] == -1:
                        if cursor_pos[0] == -1:
                            code += event.unicode
                            if event.unicode == "\r": code += "\t" * tab_level
                        else:
                            lines = code.split("\n")
                            lines[len(lines)-1] = lines[len(lines)-1][0:cursor_pos[0]+1] + str(event.unicode).replace("\r", "\n") + lines[len(lines)-1][cursor_pos[0]+1:len(lines[len(lines)-1])]
                            if event.key != pygame.K_LEFT and event.key != pygame.K_RIGHT and event.key != pygame.K_LSHIFT and event.key != pygame.K_LCTRL and event.key != pygame.K_LALT:
                                if cursor_pos[0] == -1: cursor_pos[0] = line_len-1
                                if cursor_pos[0] > 0: cursor_pos[0] += 1
                            code = ""
                            for i, line in enumerate(lines):
                                code += line + ("\n" if i < len(lines)-1 else "")

                    else:
                        if cursor_pos[0] == -1:
                            lines = code.split("\n")
                            if str(event.unicode).replace("\r", "\n") == "\n":
                                cursor_pos[1] += 1
                                if cursor_pos[1] == len(code.split("\n"))-1: cursor_pos[1] = -1
                                lines = code.split("\n")
                            lines[cursor_pos[1]] += str(event.unicode).replace("\r", "\n")
                            code = ""
                            for i, line in enumerate(lines):
                                code += line + ("\n" if i < len(lines)-1 else "")
                        else:
                            lines = code.split("\n")
                            lines[cursor_pos[1]] = lines[cursor_pos[1]][0:cursor_pos[0]+1] + str(event.unicode).replace("\r", "\n") + lines[cursor_pos[1]][cursor_pos[0]+1:len(lines[cursor_pos[1]])]
                            if event.key != pygame.K_LEFT and event.key != pygame.K_RIGHT:
                                if cursor_pos[0] == -1: cursor_pos[0] = line_len-1
                                if cursor_pos[0] > 0: cursor_pos[0] += 1
                            code = ""
                            for i, line in enumerate(lines):
                                code += line + ("\n" if i < len(lines)-1 else "")
                        
        if event.type == pygame.KEYUP:
            keycombo.remove(event.key)

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if event.button < 4 and mouse_pos[0] > explorer._w:
                cursor_pos[1] = (mouse_pos[1] - 20) // 20 + scroll // 20
                if cursor_pos[1] >= len(code.split("\n"))-1: cursor_pos[1] = -1
                cursor_pos[0] = -1
            if event.button == 4 and scroll > 0 and pygame.mouse.get_pos()[0] > explorer._w: scroll -= 30
            if event.button == 5 and pygame.mouse.get_pos()[0] > explorer._w: scroll += 30

    events = open("./local/event.dat").read()
    if str(events[0]) == "\u0001":
        open("local/files.json", "w").write(json.dumps({
            "active_folder": files["active_folder"],
            "active": gui_explorer.clicked_item,
            "recent": files["recent"]
        }, indent=4))
        files = json.loads(open("local/files.json").read())
        code = open(gui_explorer.clicked_item).read()
        open("./local/event.dat", "w").write("\0")
    if str(events[0]) == "\u0002":
        # folder opened
        print(events[1])
        items.insert(int(events[1]), widgets.FileElement(30, "test", explorer))
        open("./local/event.dat", "w").write("\0")

    code = code.replace("\r", "\n")
    tokenizer.code = code
    l = get_cursor_line(cursor_pos[1], code)
    tab_level = code.split("\n")[l].count("\t")

    if code != prev_code:
        c = []
        tokenizer.clear_scan()
        for line in code.split("\n"):
            tokenizer.scan(line.replace("\0", "\t"))
            c.append(tokenizer.get_colormap(line.replace("\0", "\t")))
    

    line_num = len(code.split("\n"))
    offset = 20 * (floor(log10(line_num)-2) if floor(log10(line_num)-2) > -1 else 0)
    for i, line in enumerate(code.split("\n")):
        if i > (scroll - 10) // 20:
            if i > screen.get_height() // 20 + scroll // 20: break
            processed = line.replace("\t", "    ").replace("\0", "\t")

            line_num = i+1
            txt = font.render(str(line_num), True, (255, 255, 255) if get_cursor_line(cursor_pos[1], code)==i else (100, 100, 100))
            rect = txt.get_rect(topright=(explorer._w + 40 + offset, 20+20*i-scroll))
            screen.blit(txt, rect)
            # print(len(tokenizer.get_colormap(processed)), len(processed))
            # print(i, line, tokenizer.tokenize(line))
            if str(files["active"]).endswith(".py"):
                screen.blit(render_text_colormap(processed, c[i], font), (explorer._w + 70, 20+20*i-scroll))
            else:
                screen.blit(font.render(processed, True, (255, 255, 255)), (explorer._w + 70, 20+20*i-scroll))

    cursor_line = get_cursor_line(cursor_pos[1], code)
    
    line = code.split("\n")[cursor_line]
    cursor_char = cursor_pos[0]
    if cursor_char == -1: cursor_char = len(line)
    screen.blit(
        font.render("|", 
                    True, (127, 127, 127)
    ), (explorer._w + 65 + font.size((" " if cursor_pos[0] != -1 else "")+line[:cursor_char].replace("\t", "    "))[0], 20+20*cursor_line-scroll))

    explorer.draw(screen, alt_font)
    for item in items: item.draw(screen, alt_font)

    elapsed_ms = 1000 * (time.time() - start_time)
    prev_code = code
    
    # if output:
    #     stdout, stderr = output.communicate()
    #     print(stdout)
    clock.tick(1000000)
    pygame.display.set_caption(f"Code Editor - FPS: {clock.get_fps():.2f} ({'Great' if clock.get_fps() >= 1000 else ('Good' if clock.get_fps() >= 800 else ('Okay' if clock.get_fps() >= 500 else 'Slow'))})")
    pygame.display.flip()