import requests
from bs4 import BeautifulSoup
import json
import os

URL = "https://www.farming-simulator.com/mods.php?lang=en&country=ro&title=fs2025"
WEBHOOK_URL = os.environ["DISCORD_WEBHOOK"]
DATA_FILE = "seen_mods.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def get_mods():
    resp = requests.get(URL, headers=HEADERS, timeout=30)
    soup = BeautifulSoup(resp.text, "html.parser")
    mods = []
    for card in soup.select("a.mod-card, div.mod-item a, .modItem a"):
        title = card.get("title") or card.get_text(strip=True)
        link = card.get("href")
        if title and link:
            if not link.startswith("http"):
                link = "https://www.farming-simulator.com" + link
            mods.append({"title": title.strip(), "link": link})
    return mods

def load_seen():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_seen(seen):
    with open(DATA_FILE, "w") as f:
        json.dump(list(seen), f)

def send_discord(mod):
    data = {
        "content": f"🆕 **Mod nou pe ModHub FS25!**\n**{mod['title']}**\n{mod['link']}"
    }
    requests.post(WEBHOOK_URL, json=data, timeout=15)

def main():
    mods = get_mods()
    seen = load_seen()

    new_mods = [m for m in mods if m["link"] not in seen]

    if not seen:
        save_seen({m["link"] for m in mods})
        print(f"Prima rulare: salvate {len(mods)} mod-uri existente, fără notificări.")
        return

    for mod in new_mods:
        send_discord(mod)
        seen.add(mod["link"])
        print(f"Notificat: {mod['title']}")

    save_seen(seen)
    print(f"Gata. {len(new_mods)} mod-uri noi găsite.")

if __name__ == "__main__":
    main()
