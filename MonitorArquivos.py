import tkinter as tk
#Permite abrir uma janela para o usuário escolher uma pasta
#Cria uma área de texto com barra de rolagem, usada para mostrar os eventos monitorados
from tkinter import filedialog, scrolledtext
# fica de olho nas alterações feitas na pasta monitorada
from watchdog.observers import Observer
#permite reagir a eventos como criação, modificação ou exclusão de arquivos
from watchdog.events import FileSystemEventHandler
# rodar o monitoramento em paralelo com a interface gráfica, sem travar a janela
import threading
#mostrar o horário em que cada evento aconteceu
import time
#verificar se o caminho escolhido é uma pasta válida
import os

# Classe que lida com os eventos de arquivos
class ManipuladorEventos(FileSystemEventHandler):
    def __init__(self, registrar_evento):
        self.registrar_evento = registrar_evento

    def on_modified(self, evento):
        self.registrar_evento(f"Arquivo modificado: {evento.src_path}")

    def on_created(self, evento):
        self.registrar_evento(f"Arquivo criado: {evento.src_path}")

    def on_deleted(self, evento):
        self.registrar_evento(f"Arquivo deletado: {evento.src_path}")

# Classe principal da aplicação
class MonitorArquivosApp:
    def __init__(self, janela):
        self.janela = janela
        self.janela.title("Monitor de Arquivos")
        self.janela.geometry("600x400")

        self.caminho_pasta = tk.StringVar()

        # Elementos da interface
        tk.Label(janela, text="Pasta para Monitorar:").pack()
        tk.Entry(janela, textvariable=self.caminho_pasta, width=60).pack()
        tk.Button(janela, text="Selecionar Pasta", command=self.selecionar_pasta).pack(pady=5)
        tk.Button(janela, text="Iniciar Monitoramento", command=self.iniciar_monitoramento).pack(pady=5)
        tk.Button(janela, text="Parar Monitoramento", command=self.parar_monitoramento).pack(pady=5)

        self.area_log = scrolledtext.ScrolledText(janela, width=70, height=15)
        self.area_log.pack(pady=10)

        self.observador = None
        self.thread_monitoramento = None

    def registrar_evento(self, mensagem):
        horario = time.strftime("%H:%M:%S")
        self.area_log.insert(tk.END, f"[{horario}] {mensagem}\n")
        self.area_log.see(tk.END)

    def selecionar_pasta(self):
        pasta = filedialog.askdirectory()
        if pasta:
            self.caminho_pasta.set(pasta)

    def iniciar_monitoramento(self):
        caminho = self.caminho_pasta.get()
        if not os.path.isdir(caminho):
            self.registrar_evento("Caminho inválido. Selecione uma pasta válida.")
            return

        if self.observador:
            self.registrar_evento("Monitoramento já está em execução.")
            return

        manipulador = ManipuladorEventos(self.registrar_evento)
        self.observador = Observer()
        self.observador.schedule(manipulador, caminho, recursive=True)

        # Executa o monitoramento em uma thread separada
        self.thread_monitoramento = threading.Thread(target=self.observador.start)
        self.thread_monitoramento.daemon = True
        self.thread_monitoramento.start()

        self.registrar_evento(f"Monitoramento iniciado na pasta: {caminho}")

    def parar_monitoramento(self):
        if self.observador:
            self.observador.stop()
            self.observador.join()
            self.registrar_evento("Monitoramento encerrado.")
            self.observador = None


if __name__ == "__main__":
    janela = tk.Tk()
    app = MonitorArquivosApp(janela)
    janela.mainloop()