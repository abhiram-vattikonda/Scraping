import requests
from bs4 import BeautifulSoup as bs
import re, json



    

def get_name_and_links():
    URL='https://www.imdb.com/chart/top/?ref_=nv_mv_250'
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"
    headers = {"user-agent": USER_AGENT} # adding the user agent
    resp = requests.get(URL, headers=headers)
    soup = bs(resp.content, "html.parser")

    data = json.loads(soup.find('script', attrs={'type': "application/ld+json"}).text)

    names = {}

    for _ in data['itemListElement']:
        names.update({_['item']['name'] : _['item']['url']})

    return names


def main():
    name_and_links = get_name_and_links()



# Example usage
if __name__ == "__main__":
    main()