import time
import psutil
import subprocess
from threading import Thread
from plyer import notification
from PIL import Image, ImageDraw
import pystray

# Lista de processos a monitorar
PROCESSOS_ALVO = ["veyon-service.exe", "veyon-server.exe", "veyon-worker.exe"]
LIMITE_MBPS = 0.4  # limite em MB/s

def criar_icone(cor):
        img = Image.new('RGB', (64, 64), color=cor)
        d = ImageDraw.Draw(img)
        d.rectangle([16, 16, 48, 48], fill=cor)
        return img
    
def monitor_rede(icon):
    last_total = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
    while True:
        time.sleep(1)
        current_total = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
        usage_bytes = current_total - last_total
        last_total = current_total
        usage_mbps = usage_bytes / 1024 / 1024  # MB/s

        processos_ativos = [p.info['name'].lower() for p in psutil.process_iter(['name'])]
        if any(proc.lower() in processos_ativos for proc in PROCESSOS_ALVO):
            if usage_mbps > LIMITE_MBPS:
                # notification.notify(
                    # title="Alerta de Charles",
                    # message=f"Rede alta: {usage_mbps:.2f} MB/s",
                    # timeout=5
                # )
                # abre explorer e fecha depois de 60s em thread separada
                Thread(target=abrir_explorer_60s, daemon=True).start()
                icon.icon = criar_icone('red')
            else:
                icon.icon = criar_icone('blue')

def abrir_explorer_60s():
    # abre explorer.exe
    proc = subprocess.Popen("explorer.exe")
    # espera 60 segundos
    time.sleep(60)

def iniciar_tray():
    icon = pystray.Icon("MonitorRede", criar_icone('blue'), "Monitor de Charles")
    Thread(target=monitor_rede, args=(icon,), daemon=True).start()
    icon.run()

iniciar_tray()
