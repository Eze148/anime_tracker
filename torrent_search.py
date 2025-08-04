import requests
from bs4 import BeautifulSoup
import datetime
import pytz

def search_nyaa(anime_title, max_results=50):
    url = f"https://nyaa.si/?f=0&c=0_0&q={anime_title.replace(' ', '+')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    results = []

    for row in soup.select("table.torrent-list tbody tr")[:max_results]:
        try:
            cols = row.find_all("td")
            # if len(cols) < 9:
            #     continue

            # Title
            title_tag = cols[1].find("a", href=True)
            title = title_tag.text.strip() if title_tag else "?"

            # Magnet link
            magnet_tag = cols[2].find_all("a", href=True)[1]
            magnet = magnet_tag['href'] if magnet_tag else None

            # Uploaded timestamp
            timestamp_attr = cols[4].get("data-timestamp")
            uploaded = "?"
            if timestamp_attr:
                uploaded = datetime.datetime.fromtimestamp(int(timestamp_attr)).strftime("%Y-%m-%d %H:%M")

            # Seeders and Leechers
            seeders = cols[5].text.strip()
            leechers = cols[6].text.strip()

            if title and magnet:
                results.append({
                    "title": title,
                    "magnet": magnet,
                    "uploaded": uploaded,
                    "seeders": seeders,
                    "leechers": leechers
                })

        except Exception as e:
            print("Error parsing row:", e)

    return results

def search_nyaa_multi(titles, max_results=50):
    seen = set()
    all_results = []

    for title in titles:
        if not title:
            continue
        results = search_nyaa(title, max_results=max_results)
        for r in results:
            key = r['magnet']  # Use magnet link as unique ID
            if key not in seen:
                seen.add(key)
                all_results.append(r)

    return all_results