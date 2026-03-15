import time
import requests
from netmiko import ConnectHandler
import datetime

# --- BEÁLLÍTÁSOK ---

# 1. Cisco Sandbox adatok
CISCO_ROUTER = {
    'device_type': 'cisco_ios_telnet',  # <-- EZ A LÉNYEG: SSH helyett Telnet
    'host': '172.16.1.200',
    'username': 'developer', 
    'password': 'C1sco12345',
    'port': 23,                         # <-- Telnet port (23)
}






# 2. A Discord Webhookod URL-je 
# KÉRLEK, EBBEN A SORBAN ÍRD ÁT A WEBHOOKODAT:
WEBHOOK_URL = "https://discord.com/api/webhooks/1475884677998055435/btZhq0onrvV1ilt7QEySidF6V69WGsUuyLuTabnI-PE0c80QzrKallnc8gukJS6uqURI"


def send_discord_alert(interface_name, status, errors):
    """Embed üzenet küldése Discordra a webhookon keresztül"""
    
    color = 15158332 if status == "down" or errors > 0 else 3066993
    
    embed = {
        "title": f"⚠️ Hálózati Interfész Riasztás: {interface_name}",
        "description": "A Borsode CsomagPont központi routere hálózati anomáliát észlelt!",
        "color": color,
        "fields": [
            {"name": "Állapot (Status)", "value": status.upper(), "inline": True},
            {"name": "Hibák (Input Errors)", "value": str(errors), "inline": True},
            {"name": "Időpont", "value": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "inline": False}
        ],
        "footer": {"text": "Powered by Netmiko & Cisco DevNet"}
    }
    
    try:
        requests.post(WEBHOOK_URL, json={"embeds": [embed]})
        print(f"Riasztás kiküldve: {interface_name}")
    except Exception as e:
        print(f"Nem sikerült a Discord üzenet küldése: {e}")

def check_router_interfaces():
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Kapcsolódás a Cisco Sandbox routerhez SSH-n keresztül...")
    
    try:
        net_connect = ConnectHandler(**CISCO_ROUTER)
        
        parancs = 'show ip interface brief'
        print(f"Parancs futtatása: {parancs}")
        kimenet = net_connect.send_command(parancs)
        
        sorok = kimenet.split('\n')
        
        for sor in sorok[1:]:
            if not sor.strip():
                continue
                
            adatok = sor.split()
            if len(adatok) >= 6:
                int_name = adatok[0]
                status = adatok[4]
                
                if "Gigabit" in int_name or "Loopback" in int_name:
                    print(f"Vizsgálat alatt: {int_name} - Állapot: {status}")
                    
                    if status != "up":
                        send_discord_alert(int_name, status, 0)
                        
                    else:
                        detail_cmd = f"show interface {int_name} | include errors"
                        detail_out = net_connect.send_command(detail_cmd)
                        
                        errors = 0
                        if "input errors" in detail_out:
                            try:
                                errors = int(detail_out.split("input errors")[0].split()[-1])
                            except:
                                pass
                                
                        if errors > 0:
                            send_discord_alert(int_name, "up (De hibás!)", errors)

        print("Lekérdezés befejezve, kapcsolat lezárása.")
        net_connect.disconnect()

    except Exception as e:
        print(f"Hiba a kapcsolódás vagy a futtatás során: {e}")

if __name__ == "__main__":
    check_router_interfaces()
