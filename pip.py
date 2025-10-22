import time
import psutil
import subprocess
from threading import Thread, Lock
from PIL import Image, ImageDraw
import pystray

PROCESSOS_ALVO = ["veyon-service.exe", "veyon-server.exe", "veyon-worker.exe"]
LIMITE_MBPS = 0.5
#abaixo de 0.5mb ele vai disparar toda hora pois ele fica em uma mini janela
#>= 0.4 ele vai disparar quando clicar na janela

# Controle pra evitar múltiplos explorers
explorer_aberto = False
lock = Lock()

def criar_icone():
    img = Image.new('RGB', (64, 64), color='blue')
    d = ImageDraw.Draw(img)
    d.rectangle([16, 16, 48, 48], fill='white')
    return img

def abrir_explorer_60s():
    global explorer_aberto
    with lock:
        if explorer_aberto:
            return
        explorer_aberto = True

    subprocess.Popen("explorer.exe")
    time.sleep(60)
    with lock:
        explorer_aberto = False

def monitor_rede():
    last_total = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
    while True:
        time.sleep(1)
        current_total = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
        usage_bytes = current_total - last_total
        last_total = current_total
        usage_mbps = usage_bytes / 1024 / 1024  # MB/s

        processos_ativos = [p.info['name'].lower() for p in psutil.process_iter(['name'])]
        if any(proc in processos_ativos for proc in PROCESSOS_ALVO):
            if usage_mbps > LIMITE_MBPS:
                Thread(target=abrir_explorer_60s, daemon=True).start()

def iniciar_tray():
    icon = pystray.Icon("MonitorCharles", criar_icone(), "Monitor de Charles")
    icon.run()

# Inicia o monitor em thread separada
Thread(target=monitor_rede, daemon=True).start()
iniciar_tray()