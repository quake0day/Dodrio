import urllib2
import BeautifulSoup as bs
import re


def init():
    URL = "http://signature.statseb.fr/index.py?cpid=c60f07487dde49e4caa5a251579ef544"
    r = urllib2.urlopen(URL)
    soup = bs.BeautifulSoup(r)
    return soup


def getBadges(soup):
    IMG_URL_BASE = "https://signature.statseb.fr/"
    imgs = soup.findAll("img")
    res = []
    for img in imgs:
        # print img
        title = img.get('title', '')
        src = img.get('src', '')
        full_url = IMG_URL_BASE + src
        if title:
            res.append([title, full_url])
    return res


def getRanks(soup):
    # print soup
    world = soup.find(text=re.compile("World"))
    worldPos = world.next.string

    county = soup.find(text=re.compile("Country position"))
    countyPos = county.next.string
    return worldPos, countyPos


# print getBadges(soup)
# print getRanks(soup)
