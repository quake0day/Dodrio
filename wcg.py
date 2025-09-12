import urllib.request
from bs4 import BeautifulSoup
import re


def init():
    URL = "http://signature.statseb.fr/index.py?cpid=c60f07487dde49e4caa5a251579ef544"
    try:
        with urllib.request.urlopen(URL) as response:
            html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        return soup
    except Exception as e:
        print(f"Error fetching WCG data: {e}")
        return None


def getBadges(soup):
    if not soup:
        return []
    
    IMG_URL_BASE = "https://signature.statseb.fr/"
    imgs = soup.find_all("img")
    res = []
    for img in imgs:
        title = img.get('title', '')
        src = img.get('src', '')
        full_url = IMG_URL_BASE + src
        if title:
            res.append([title, full_url])
    return res


def getRanks(soup):
    if not soup:
        return None, None
    
    world = soup.find(text=re.compile("World"))
    worldPos = world.next.string if world else None
    
    county = soup.find(text=re.compile("Country position"))
    countyPos = county.next.string if county else None
    return worldPos, countyPos