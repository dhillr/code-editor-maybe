from gui.widgets import FileElement, FolderElement
from os import listdir, path
from json import loads, dumps

def first_file(folder):
    l = listdir(folder)
    for f in l:
        if path.isfile(path.join(folder, f)): return f

clicked_item: str = ""
open("./local/event.dat", "w").write("\0")

def set_active(val):
    global clicked_item
    clicked_item = val

def explorer_tab(parent):
    parent.children = []
    json = loads(open("./local/files.json").read())

    dirlist = listdir(json["active_folder"])
    res = [FileElement(30, i, parent) if path.isfile(path.join(json["active_folder"], i)) else FolderElement(30, i, parent) for i in dirlist]

    for i, item in enumerate(res):
        def file_event(self):
            open("./local/files.json", "w").write(dumps({
                "active_folder": json["active_folder"],
                "active": json["active_folder"] + "/" + self.text,
                "recent": json["recent"]
            }, indent=4))
            set_active(json["active_folder"] + "/" + self.text)
            # active = open(json["active_folder"] + "/" + self.text).read()
            open("./local/event.dat", "w").write("\u0001")

        def folder_event(self):
            open("./local/event.dat", "w").write(f"\u0002{self.index}")
            open("./local/files.json", "w").write(dumps({
                "active_folder": json["active_folder"]+"/"+self.text,
                "active": json["active_folder"]+"/"+self.text+"/"+first_file(json["active_folder"]+"/"+self.text),
                "recent": json["recent"]
            }, indent=4))

        if isinstance(item, FileElement):
            item.on_click = file_event
        else:
            item.index = i
            item.on_click = folder_event

    return res