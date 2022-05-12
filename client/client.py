from socket import *
import platform
import psutil
import autoit
import win32gui
import win32process
import time
import tkinter as tk
from icon import *
from threading import Thread
import sys
from configparser import ConfigParser

config = ConfigParser()
config.read("settings.ini")
SERVER_ADDRESS = (config.get("SERVER", "IP"), int(config.get("SERVER", "PORT")))
process = config.get("PROCESS", "NAME")
follow = config.get("MACROS", "FOLLOW")
assist = config.get("MACROS", "ASSIST")
buff = config.get("MACROS", "BUFF")
stop = config.get("MACROS", "STOP")
invite = config.get("MACROS", "INVITE")

hostname = platform.node()
hwnd = ''

windows = []
stopper = True


class HoverButton(tk.Button):
    def __init__(self, master, **kw):
        tk.Button.__init__(self, master=master, **kw)
        self.defaultBackground = self["background"]
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self['background'] = self['activebackground']

    def on_leave(self, e):
        self['background'] = self.defaultBackground


# получение hwnd всех окон игры
def get_hwnd():
    windows.clear()
    listbox.delete(0, tk.END)
    for proc in psutil.process_iter():
        if proc.name() == process:
            def callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
                    _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                    if found_pid == proc.pid:
                        if hwnd not in windows:
                            windows.append(hwnd)
                        listbox.insert(tk.END, hwnd)
                return True

            win32gui.EnumWindows(callback, windows)
    if listbox.size() > 0:
        listbox.select_set(0)
        b1.configure(state=tk.NORMAL)
        b2.configure(state=tk.DISABLED)
    else:
        b1.configure(state=tk.DISABLED)
        b2.configure(state=tk.DISABLED)


def mainloop():
    global client, hwnd
    while stopper:
        client = socket(AF_INET, SOCK_STREAM)
        try:
            client.connect(SERVER_ADDRESS)
            data = client.recv(1024)
            label_work.configure(text=format(data.decode('utf8')))
            client.send(bytes(str(hwnd), 'utf8'))
        except ConnectionRefusedError:
            label_work.configure(text="Сервер выключен")
            continue
        except TimeoutError:
            label_work.configure(text="Попытка подключения...")
            continue
        except OSError:
            pass
        while stopper:
            try:
                msg = client.recv(1024)
                label_work.configure(text="Получено сообщение: " + format(msg.decode('utf8')))
                if msg == b'1':
                    autoit.win_activate_by_handle(hwnd)
                    time.sleep(1)
                    autoit.send(follow, 0)
                if msg == b'2':
                    autoit.win_activate_by_handle(hwnd)
                    time.sleep(1)
                    autoit.send(assist, 0)
                if msg == b'3':
                    autoit.win_activate_by_handle(hwnd)
                    time.sleep(1)
                    autoit.send(buff, 0)
                if msg == b'4':
                    autoit.win_activate_by_handle(hwnd)
                    time.sleep(1)
                    autoit.send(stop, 0)
                if msg == b'5':
                    autoit.win_activate_by_handle(hwnd)
                    time.sleep(1)
                    autoit.send(invite, 0)

            except ConnectionResetError:
                label_work.configure(text="Потеряна связь с сервером")
                break
            except ConnectionAbortedError:
                b1.configure(state=tk.NORMAL)
                return
    client.close()


def start():
    global stopper, hwnd
    stopper = True
    b1.configure(state=tk.DISABLED)
    b2.configure(state=tk.NORMAL)
    b3.configure(state=tk.DISABLED)
    listbox.configure(state=tk.DISABLED)
    hwnd = listbox.get(listbox.curselection())
    Thread(target=mainloop, daemon=True).start()


def stop_client():
    global stopper, client
    b1.configure(state=tk.NORMAL)
    b2.configure(state=tk.DISABLED)
    b3.configure(state=tk.NORMAL)
    listbox.configure(state=tk.NORMAL)
    stopper = False
    client.close()
    label_work.configure(text="Отключено")


def destroy():
    sys.exit()


if __name__ == '__main__':
    root = tk.Tk()
    img = tk.PhotoImage(data=icon)
    root.tk.call('wm', 'iconphoto', root._w, img)
    root.title("RMS Удаленный доступ - TektoniT - Клиент")
    root.minsize(width='200', height='200')
    root.maxsize(width='200', height='200')
    x = (root.winfo_screenwidth() - root.winfo_reqwidth()) / 2
    y = (root.winfo_screenheight() - root.winfo_reqheight()) / 2
    root.wm_geometry("+%d+%d" % (x, y - 200))

    listbox = tk.Listbox(root, width=10, exportselection=False)
    listbox.place(relx=.5, y=40, anchor="c", height=60, width=180)

    b1 = HoverButton(root, text='Start', activebackground='#FFA500', command=start)
    b1.place(x=10, y=80, height=30, width=85)
    b2 = HoverButton(root, text='Stop', activebackground='#FFA500', command=stop_client)
    b2.place(x=105, y=80, height=30, width=85)
    b3 = HoverButton(root, text='Refresh', activebackground='#FFA500', command=get_hwnd)
    b3.place(x=10, y=120, height=30, width=85)
    b4 = HoverButton(root, text='Exit', activebackground='#FFA500', command=destroy)
    b4.place(x=105, y=120, height=30, width=85)

    label_work = tk.Label(root, text="Отключено")
    label_work.place(relx=.5, y=180, anchor="c")
    get_hwnd()

    root.mainloop()

# pyinstaller client.py -F -i icon.ico --noconsole --name "rutview_client" --version-file version.txt --add-data C:\Users\konkov_va\PycharmProjects\Remote_Game_Control\venv\Lib\site-packages\autoit;.\autoit
