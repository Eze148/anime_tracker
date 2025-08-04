import requests
from PIL import Image, ImageTk
from io import BytesIO

def fetch_and_resize_image(url, size=(200, 300)):
    try:
        response = requests.get(url)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        return ImageTk.PhotoImage(img.resize(size, Image.ANTIALIAS))
    except Exception as e:
        print("Image loading failed:", e)
        return None
