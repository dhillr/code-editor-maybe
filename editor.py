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
import gui.widgets as widgets
import gui.explorer as gui_explorer
from tkinter import messagebox
from helper import filehelper
from sys import platform
from math import log10, floor

def get_cursor_line(p, t):
    if p == -1: return len(t.split("\n"))-1
    return p

def get_cursor_char(p, t):
    if p == -1: return len(t)-1
    return p

def restore():
    messagebox.showerror("Error", "An error occured while trying to load your last file.\nTo prevent more errors, we reset:\n- Your active folder cache\n- Your active file cache\n- Your recent folder cache")
    open("local/files.json", "w").write('{\n\t"active_folder": "",\n\t"active": "",\n\t"recent": []\n}')

def save():
    open(files["active"], "w").write(code)

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
        "active": files["active"],
        "recent": files["recent"]
    }))
    files = json.loads(open("local/files.json").read())

active = "" if not files["active"] else open(files["active"]).read()
code: str = active

clock = pygame.time.Clock()
elapsed_ms = 0
start_time = time.time()
typing = False
since_key_press = 0
keycombo = []

cursor_pos = [-1, -1] # [row, column] (-1 = last letter/line)

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
                    subprocess.Popen(['python', files["active"]])
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
                        if (lines[cursor_pos[1]] == ""): new_line = cursor_pos[1]
                        code = ""
                        for i, line in enumerate(lines):
                            code += line + ("\n" if i < len(lines)-1 or i == new_line else "")
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

    events = open("./local/event.dat").read()
    if events[0] == "1":
        open("local/files.json", "w").write(json.dumps({
            "active_folder": files["active_folder"],
            "active": gui_explorer.clicked_item,
            "recent": files["recent"]
        }, indent=4))
        files = json.loads(open("local/files.json").read())
        code = open(gui_explorer.clicked_item).read()
        open("./local/event.dat", "w").write("0")

    code = code.replace("\r", "\n")
    l = get_cursor_line(cursor_pos[1], code)
    tab_level = code.split("\n")[l].count("\t")

    line_num = len(code.split("\n"))
    offset = 20 * (floor(log10(line_num)-2) if floor(log10(line_num)-2) > -1 else 0)
    for i, line in enumerate(code.split("\n")):
        line_num = i+1
        txt = font.render(str(line_num), True, (255, 255, 255) if get_cursor_line(cursor_pos[1], code)==i else (100, 100, 100))
        rect = txt.get_rect(topright=(explorer._w + 40 + offset, 20+20*i))
        screen.blit(txt, rect)
        screen.blit(font.render(line.replace("\t", "    "), True, (255, 255, 255)), (explorer._w + 70, 20+20*i))

    cursor_line = get_cursor_line(cursor_pos[1], code)
    line = code.split("\n")[cursor_line]
    tab_offset = 3 * line.count("\t") if cursor_pos[0] > -1 else 0
    screen.blit(
        font.render(" "*(get_cursor_char(cursor_pos[0], line.replace("\t", "    ")) + 1 + tab_offset)+"|", 
                    True, (127, 127, 127)
    ), (explorer._w + 65, 20+20*cursor_line))

    explorer.draw(screen, alt_font)
    for item in items: item.draw(screen, alt_font)

    elapsed_ms = 1000 * (time.time() - start_time)

    clock.tick(100000)
    # print(clock.get_fps())
    pygame.display.flip()