import os
import hashlib
import requests
from PIL import Image, ImageTk
from io import BytesIO

CACHE_DIR = "poster_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def fetch_and_resize_image(url, size=(200, 300)):
    try:
        # Use MD5 hash of URL as filename
        filename = hashlib.md5(url.encode()).hexdigest() + ".jpg"
        filepath = os.path.join(CACHE_DIR, filename)

        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                image_data = f.read()
        else:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            image_data = response.content

            with open(filepath, 'wb') as f:
                f.write(image_data)

        image = Image.open(BytesIO(image_data)).resize(size, Image.ANTIALIAS)
        return ImageTk.PhotoImage(image)
    except Exception as e:
        print("Image loading failed:", e)
        return None