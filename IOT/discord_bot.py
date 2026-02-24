import requests
import json

WEBHOOK_URL = ""

def send_status_update(tracking_number, old_status, new_status):
    embed = {
        "title": f"📦 Csomag státusz frissítés: {tracking_number}",
        "color": 3066993, # Zöldes szín
        "fields": [
            {"name": "Korábbi státusz", "value": old_status, "inline": True},
            {"name": "Új státusz", "value": f"**{new_status}**", "inline": True}
        ]
    }
    requests.post(WEBHOOK_URL, json={"embeds": [embed]})

def send_qos_graph(image_path, average_latency):
    with open(image_path, "rb") as f:
        # Fájl küldése webhookon keresztül
        requests.post(
            WEBHOOK_URL,
            files={"file": (image_path, f, "image/png")},
            data={"payload_json": json.dumps({
                "content": f"📊 **QoS Napi Jelentés**\nÁtlagos válaszidő: {average_latency:.2f} ms"
            })}
        )

