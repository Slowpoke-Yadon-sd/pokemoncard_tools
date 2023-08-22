from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4, portrait
from PIL import Image
import os
import sys
from bs4 import BeautifulSoup
from selenium import webdriver
import urllib.request
from io import BytesIO 

PDF_NAME = "デッキプロキシ.pdf"
BASE_URL = "https://www.pokemon-card.com/"
DECK_URL = BASE_URL + "deck/result.html/deckID/"
IMAGE_POSITIONS = [(30, 600), (203, 600), (376, 600), (30, 370), (203, 370), (376, 370), (30, 140), (203, 140), (376, 140)]

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)

def fetch_image_url(url):
    buffer = urllib.request.urlopen(url).read()
    return Image.open(BytesIO(buffer))

def get_deck_data(deck_id):
    driver = webdriver.Chrome(resource_path("C:\chromedriver"))
    driver.get(DECK_URL + deck_id)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    quantities = [int(span.text.strip('枚')) for span in soup.find(id="cardImagesView").find_all("span")]
    image_urls = [BASE_URL + img.get("src") for img in soup.find(id="cardImagesView").find_all('img')]
    return quantities, image_urls

def generate_pdf(deck_id):
    quantities, image_urls = get_deck_data(deck_id)
    file_path = os.path.expanduser("~") + "/Desktop/" + PDF_NAME
    pdf = canvas.Canvas(file_path, pagesize=portrait(A4))

    card_index = 0
    for i in range(min(7, len(quantities))):
        for pos in IMAGE_POSITIONS:
            if quantities[card_index] == 0:
                card_index += 1
            if card_index >= len(quantities):
                break
            img = fetch_image_url(image_urls[card_index])
            pdf.drawInlineImage(img, pos[0], pos[1], width=6*cm, height=8*cm)
            quantities[card_index] -= 1
        if i < 6:
            pdf.showPage()

    pdf.save()
    print("プロキシが生成されました")

if __name__ == "__main__":
    print("デッキコードを入力してください")
    deck_id = input()
    generate_pdf(deck_id)
