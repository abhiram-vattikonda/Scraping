import requests
from bs4 import BeautifulSoup as bs
import re, json, time

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"

    

def get_name_and_links():
    URL='https://www.imdb.com/chart/top/?ref_=nv_mv_250'
    headers = {"user-agent": USER_AGENT} # adding the user agent
    resp = requests.get(URL, headers=headers)
    soup = bs(resp.content, "html.parser")

    data = json.loads(soup.find('script', attrs={'type': "application/ld+json"}).text)

    names = {}

    for _ in data['itemListElement']:
        names.update({_['item']['name'] : _['item']['url']})

    with open('names_and_links.txt', 'w') as file:
        for name in names:
            file.write(f"{name} : {names[name]}\n")


def get_directors(name_and_links):
    directors = {}
    for i in name_and_links:
        headers = {"user-agent": USER_AGENT} # adding the user agent
        resp = requests.get(name_and_links[i], headers=headers)
        soup = bs(resp.content, "html.parser")
        data = json.loads(soup.find('script', attrs={'type': "application/ld+json"}).text)
        for j in data['director']:
            if j['@type'] == "Person":
                if j['name'] in directors:
                    directors[j['name']] += 1
                else:
                    directors.update({j['name'] : 1})
        print(i)

    directors = sorted(directors.items(), key=lambda kv: kv[1], reverse=True)
    with open("directors.txt", 'w') as file:
        for i in directors:
            file.write(f"{i[0]} : {i[1]}\n")

def main():
    start_time = time.time()
    try:
        file = open("names_and_links.txt", 'r')
    except FileNotFoundError:
        get_name_and_links()
        file = open("names_and_links.txt", 'r')



    name_and_links = {}
    for line in file:
        name_and_links.update({line.split(' : ')[0] : line.split(' : ')[1][:-2]})
    file.close()

    try:
        file = open("directors.txt", 'r')
    except FileNotFoundError:
        get_directors(name_and_links)
        file = open("directors.txt", 'r')

    directors = {}
    for line in file:
        t = line.split(' : ')
        directors.update({t[0] : t[1]})
    file.close()

    print(*[f"{i} : {directors[i]}\n" for i in directors])

    print("--- %s seconds ---" % (time.time() - start_time))




# Example usage
if __name__ == "__main__":
    main()