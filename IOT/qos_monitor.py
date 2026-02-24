import time
from ping3 import ping
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from database import SessionLocal
import models
import discord_bot

TARGET_IP = "8.8.8.8" # Lehet a saját gateway-ed, vagy a Google DNS

def measure_qos():
    db = SessionLocal()
    latency = ping(TARGET_IP, unit='ms')
    
    if latency is None:
        latency = 0.0 # Timeout esetén

    log = models.QoSLog(target_ip=TARGET_IP, latency_ms=latency)
    db.add(log)
    db.commit()
    db.close()
    return latency

def generate_and_send_graph():
    db = SessionLocal()
    # Lekérjük az utolsó 50 mérést
    logs = db.query(models.QoSLog).order_by(models.QoSLog.timestamp.desc()).limit(50).all()
    db.close()

    logs.reverse() # Időrendi sorrendbe rakjuk
    
    times = [log.timestamp for log in logs]
    latencies = [log.latency_ms for log in logs]
    avg_lat = sum(latencies) / len(latencies) if latencies else 0

    # Grafikon rajzolása Matplotlib-bel
    plt.figure(figsize=(10, 5))
    plt.plot(times, latencies, marker='o', linestyle='-', color='b', label='Késleltetés (ms)')
    
    plt.title('Hálózati Minőség (QoS) Monitor')
    plt.xlabel('Idő')
    plt.ylabel('Késleltetés (ms)')
    plt.grid(True)
    plt.legend()
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    plt.gcf().autofmt_xdate() # Dátumok elforgatása, hogy olvashatók legyenek

    # Kép mentése fájlba (ez a plt.savefig funkció, amit Discordra küldünk)
    image_path = "qos_graph.png"
    plt.savefig(image_path)
    plt.close()

    # Beküldés Discordra
    discord_bot.send_qos_graph(image_path, avg_lat)

if __name__ == "__main__":
    # Csinálunk 5 gyors mérést a teszt kedvéért, majd generálunk egy gráfot
    for _ in range(5):
        measure_qos()
        time.sleep(1)
    
    generate_and_send_graph()
    print("Mérés és grafikon elküldve!")
