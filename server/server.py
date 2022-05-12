import socket
import sys
from threading import Thread
import tkinter as tk
from icon import *
from configparser import ConfigParser

config = ConfigParser()
config.read("settings.ini")
SERVER_ADDRESS = (socket.gethostbyname(socket.gethostname()), int(config.get("SERVER", "PORT")))
limit = 6
clients = 0
clients_arr = []
frames = {}


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


class Server(tk.Tk):
    def __init__(self, **kwargs):
        """ Формирование основного окна"""
        super().__init__(**kwargs)
        self.resizable(0, 0)
        self.img = tk.PhotoImage(data=icon)
        self.tk.call('wm', 'iconphoto', self._w, self.img)
        self.title("RMS Удаленный доступ - TektoniT - Сервер")
        self.minsize(width='249', height='25')
        self.maxsize(width='249', height='300')
        self.attributes("-topmost", True)
        self.wm_geometry("+%d+%d" % (self.winfo_screenwidth() - 264, self.winfo_screenheight() - 812))

        frame = tk.Frame(self, relief="groove")
        frame.pack(side="top")
        self.b1 = HoverButton(frame, text='Start', activebackground='#FFA500', command=self.start_server)
        self.b1.pack(side="left", fill="x")
        self.b2 = HoverButton(frame, text='Stop', activebackground='#FFA500', command=self.stop_server)
        self.b2.pack(side="left", fill="x")
        self.b3 = HoverButton(frame, text='Exit', activebackground='#FFA500', command=self.exit)
        self.b3.pack(side="left", fill="x")
        self.b2.configure(state=tk.DISABLED)

    def add_buttons_for_client(self, conn):
        """Добавление кнопок при подключении клиента"""
        frame = tk.Frame(self, relief="groove")
        frames[conn] = frame
        frame.pack(side="top", fill="x", padx=2, pady=2)
        for i in range(5):
            if i == 0:
                widget = HoverButton(frame, text="Follow", width=5, height=2, activebackground='#FFA500',
                                     command=lambda j=i + 1: self.send_msg(conn, j))
                widget.pack(side="left", padx=2)
            if i == 1:
                widget = HoverButton(frame, text="Assist", width=5, height=2, activebackground='#FFA500',
                                     command=lambda j=i + 1: self.send_msg(conn, j))
                widget.pack(side="left", padx=2)
            if i == 2:
                widget = HoverButton(frame, text="Buff", width=5, height=2, activebackground='#FFA500',
                                     command=lambda j=i + 1: self.send_msg(conn, j))
                widget.pack(side="left", padx=2)
            if i == 3:
                widget = HoverButton(frame, text="Stop", width=5, height=2, activebackground='#FFA500',
                                     command=lambda j=i + 1: self.send_msg(conn, j))
                widget.pack(side="left", padx=2)
            if i == 4:
                widget = HoverButton(frame, text="Invite", width=5, height=2, activebackground='#FFA500',
                                     command=lambda j=i + 1: self.send_msg(conn, j))
                widget.pack(side="left", padx=2)

    def remove_client_buttons(self, conn):
        """Удаление кнопок при отключении клиента"""
        frames[conn].destroy()

    def exit(self):
        """Выход из программы"""
        self.destroy()
        sys.exit()

    def server_operation(self):
        """Запуск отдельного потока для прослушки подключения клиентов"""
        global clients
        while True:
            try:
                conn, adr = self.socket.accept()
                if clients < limit:
                    clients_arr.append(conn)
                    Thread(target=self.client_thread, args=(conn,)).start()
                    clients += 1
                else:
                    conn.send(bytes("Превышен лимит пользователей", 'utf8'))
                    conn.close()
            except OSError:
                pass

    def start_server(self):
        """Запуск сервера"""
        self.b1.configure(state=tk.DISABLED)
        self.b2.configure(state=tk.NORMAL)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(SERVER_ADDRESS)
        self.socket.listen(5)
        Thread(target=self.server_operation, daemon=True).start()

    def stop_server(self):
        """Остановка сервера"""
        self.b2.configure(state=tk.DISABLED)
        self.b1.configure(state=tk.NORMAL)
        for client in clients_arr:
            client.close()
        if len(clients_arr) > 0:
            for client in clients_arr:
                client.close()
        clients_arr.clear()
        self.socket.close()

    def client_thread(self, conn):
        """Поток клиента"""
        global clients
        conn.send(bytes("Связь с сервером установлена", 'utf8'))
        while True:
            try:
                data = conn.recv(1024)
                conn.send(b"")
            except ConnectionError:
                i = 0
                while i < len(clients_arr):
                    if clients_arr[i] == conn:
                        conn.close()
                        del clients_arr[i]
                    i += 1
                clients -= 1
                print("Отключен " + format(data.decode('utf8')))
                self.remove_client_buttons(conn)
                del frames[conn]
                break
            hid = format(data.decode('utf8'))
            print("Подключен " + hid)
            self.add_buttons_for_client(conn)

    def send_msg(self, conn, msg):
        """Отправка сообщения клиенту"""
        conn.send(bytes(str(msg), 'utf8'))


if __name__ == '__main__':
    Server().mainloop()

# pyinstaller server.py -F -i icon.ico --noconsole --name "rutview_server" --version-file version.txt
