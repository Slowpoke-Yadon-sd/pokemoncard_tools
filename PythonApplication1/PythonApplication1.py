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
import csv

PDF_NAME = "デッキプロキシ.pdf"
BASE_URL = "https://www.pokemon-card.com/"
DECK_URL = BASE_URL + "deck/result.html/deckID/"
image_width = 6.2*cm
image_height = 8.7*cm
#28.3cm 28.6でぴった
# 画像の配置位置を計算
IMAGE_POSITIONS = [
    # 1行目
    (1*cm, 28*cm - image_height),(1.2*cm+image_width-0.1*cm, 28*cm - image_height),(1.4*cm+2*image_width-0.2*cm, 28*cm - image_height),
    # 2行目
    (1*cm, 28*cm - 2*image_height),(1.2*cm+image_width-0.1*cm, 28*cm - 2*image_height),(1.4*cm+2*image_width-0.2*cm, 28*cm - 2*image_height),
    # 3行目
    (1*cm, 28*cm - 3*image_height),(1.2*cm+image_width-0.1*cm, 28*cm - 3*image_height),(1.4*cm+2*image_width-0.2*cm, 28*cm - 3*image_height),
]

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
    driver = webdriver.Chrome()
    driver.get(DECK_URL + deck_id)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    quantities = [int(span.text.strip('枚')) for span in soup.find(id="cardImagesView").find_all("span")]
    image_urls = [BASE_URL + img.get("src") for img in soup.find(id="cardImagesView").find_all('img')]
    return quantities, image_urls

def generate_pdf(deck_id, deck_name):
    quantities, image_urls = get_deck_data(deck_id)
    file_path = os.path.expanduser("~") +"\\"+ deck_name+".pdf"
    pdf = canvas.Canvas(file_path, pagesize=portrait(A4))

    card_index = 0
    for i in range(min(7, len(quantities))):
        for pos in IMAGE_POSITIONS:
            if quantities[card_index] == 0:
                card_index += 1
            if card_index >= len(quantities):
                break
            img = fetch_image_url(image_urls[card_index])
            pdf.drawInlineImage(img, pos[0], pos[1], width=6.2*cm, height=8.7*cm)
            quantities[card_index] -= 1
        if i < 6:
            pdf.showPage()

    pdf.save()
    print("プロキシが生成されました")
    
def read_decks_from_csv(csv_file):
        with open(csv_file, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                deck_name, deck_id = row
                print(f"Generating PDF for {deck_name}...{deck_id}")
                generate_pdf(deck_id, deck_name)

if __name__ == "__main__":
   csv_file_path =os.path.expanduser("~")+"\\"+'decks.csv'  # CSVファイルのパス
   read_decks_from_csv(csv_file_path)
