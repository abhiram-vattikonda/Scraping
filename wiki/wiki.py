from bs4 import BeautifulSoup as bs
import requests
import re
import time

def main():
    first = ''
    random = requests.get("https://en.wikipedia.org/wiki/Special:Random")
    # Special:Random
    i = 0
    print(title(random))
    while True:
        first = firstlink(random).strip()
        print(first)
        if first == "Philosophy" or i == 100:
            break
        random = requests.get(f"https://en.wikipedia.org/wiki/{first}")
        i += 1


def title(random):
    html = random.text
    soup = bs(html, 'html.parser')
    headlink = soup.find(id='firstHeading')
    if link := re.search(r"^<h1 class=\"firstHeading mw-first-heading\" id=\"firstHeading\"><span class=\"mw-page-title-main\">(.+)</span></h1>$", str(headlink)):
        return str(link.group(1))

def firstlink(random):
    alllinks = []
    html = random.text
    soup = bs(html, 'html.parser')
    # print(soup.find(id='firstHeading'))
    body = soup.find_all('p')
    for ps in range(len(body) - 1):
        links = body[ps].find_all('a')
        for _ in links:
            if link := re.match(r"^<a (?:class=\"mw-redirect\" )?href=\"/wiki/(.+)\" (?:.+)\">(?:.+)</a>$", str(_)):
                alllinks.append(link.group(1))
    # print(alllinks)

    for i in range(len(alllinks)):
        if validlink(alllinks[i]):
            # print(alllinks[i])
            # print()
            return alllinks[i]


def validlink(word):
    if "_language" in word:
        return False
    elif "Help:IPA" in word:
        return False
    else:
        return True

if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))