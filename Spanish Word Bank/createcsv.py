import csv, time, requests
import asyncio, aiohttp
from bs4 import BeautifulSoup as bs


words_missed = []
error_words = []
headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537."}
url = "https://www.spanishdict.com/translate/{}?langFrom=es"
limit = 3000
start_at = 5000

async def main():
    start_time = time.time()
    language = "Spanish"
    not_words = ["", "\n"]

    try: 
        #with open('lute3-spanish-to-english-term-bank.csv', mode="a", newline='', encoding="utf-8") as csvfile:
        with open("Diccionario.Espanol.136k.palabras.txt", mode="r", encoding="utf-16") as txtfile:
            file_as_list = list(txtfile)
            response_queue = asyncio.Queue()
            fetch_task = asyncio.create_task(get_html(file_as_list[start_at:], response_queue))
            count = 0
            while count < limit:
                word, html = await response_queue.get()

                word = word.strip()
                soup = bs(html, 'html.parser')

                if word in not_words:
                    continue

                try:
                    translation, parents = getTranslation(soup)
                except:
                    if html is None:
                        error_words.append(word)
                        continue

                if translation == "":
                    words_missed.append(word)
                    continue

                row = {
                    "language" : language,
                    "term" : word,
                    "translation" : translation,
                    "parent" : parents,
                    "status" : 1,
                    "link_status" : "Y" if parents != "" else "",
                    "tags" : "",
                    "pronunciation" : ""
                    }
                
                writer.writerow(row)

                count += 1
                if count % 50 == 0:
                    print(count)
    except TypeError as e:
        print(e)


    print("--- %s seconds ---" % (time.time() - start_time))
    print(words_missed)
    print(error_words)






async def get_html(words, response_queue):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for word in words[:limit]:  # Limit to 100 words
            task = asyncio.create_task(fetch_translation(session, word, response_queue))
            tasks.append(task)
        
        # Instead of waiting for all tasks, we process as they finish
        for task in asyncio.as_completed(tasks):
            await task  # Process the task as soon as it's done

async def fetch_translation(session, word, response_queue):
    try:
        async with session.get(url.format(word), ssl=False) as response:
            html = await response.text()
            await response_queue.put((word, html))  # Store result in queue
    except Exception as e:
        print(f"Failed to fetch {word}: {e}")
        await response_queue.put((word, None))  # Store None for failed requests



def getTranslation(soup : bs):

    yellowBox = soup.find(attrs={"class" : "AF8dOcYf"})

    if yellowBox:
        return getStuffFromYellowBox(soup)

    else:
        return getStuffFromDefault(soup)
    

def getStuffFromDefault(soup: bs):
    word_and_meaning = soup.find_all(attrs={"class" : "YZ8gKxpm"})
    return ("".join([(x.text) + ", " for x in word_and_meaning[1:]])[:-2], "")


def getStuffFromYellowBox(soup: bs):
    translation = getTranslationInYelloBox(soup)
    parents = getParentsInYellowBox(soup)

    #print(translation+ "  |  " + parents)
    return (translation, parents)


def getTranslationInYelloBox(soup : bs):
    #print("Went into yellow box for", word)
    meaning_for_nonverbs = soup.find_all(attrs={"class" : "le4jo4Ji"})
    meaning_for_verbs = soup.find_all(attrs={"class" : "iG5azK28"})
    translation = ""

    for num, sentance in enumerate(meaning_for_verbs):
        # to get the conjugation part
        s = sentance.find_all("span")
        sentance = "".join([i.text + " " for i in s[:-1]])
        #print(sentance)
        try:
            if sentance.find("conjugation") != -1:
                translation += sentance.strip() + ", \n"
            else:
                translation += (meaning_for_nonverbs[num].text).split('-')[1] + ", \n"
        except IndexError:
            #print("Error in translation")
            pass

    return translation[:-3]


def getParentsInYellowBox(soup : bs):
    parent = soup.find_all(lambda tag: tag.has_attr("class") and tag["class"] == ["wpZ6GBd8"])
    parents = ""
    for x in parent:
        try:
            parents += (x.text) + ", "
        except IndexError:
            print("Error in finding parents")

    return parents[:-2]


def count_csv_rows(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return sum(1 for _ in f) - 1
    

if __name__ == "__main__":
    start_time = time.time()
    with open('lute3-spanish-to-english-term-bank.csv', mode="a", newline='', encoding="utf-8") as csvfile:
        fieldNames = ["language", "term", "translation", "parent", "status", "link_status", "tags", "pronunciation"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldNames)
        if count_csv_rows('lute3-spanish-to-english-term-bank.csv') == -1:
            writer.writeheader()

        try:
            asyncio.run(main())
            print(error_words)
            print(words_missed)
        except KeyboardInterrupt:
            print("--- %s seconds ---" % (time.time() - start_time))
            print(error_words)
            print(words_missed)