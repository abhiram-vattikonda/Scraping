import csv, requests, re, time
from bs4 import BeautifulSoup as bs


words_missed = []
error_words = []


def main():
    start_time = time.time()

    language = "Spanish"
    
    not_words = ["", "\n"]

    with open('lute3-spanish-to-english-term-bank.csv', mode="a", newline='', encoding="utf-8") as csvfile:
        count = count_csv_rows("lute3-spanish-to-english-term-bank.csv")
        fieldNames = ["language", "term", "translation", "parent", "status", "link_status", "tags", "pronunciation"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldNames)

        if count == -1:
            writer.writeheader()
            count = 0

        with open("Diccionario.Espanol.136k.palabras.txt", mode="r", encoding="utf-16") as txtfile:
            file_as_list = list(txtfile)
            for word in file_as_list[count:]:
                word = word.strip()

                html = requests.get("https://www.spanishdict.com/translate/" + word.strip() + "?langFrom=es").text
                soup = bs(html, 'html.parser')

                if word in not_words:
                    continue

                try:
                    translation, parents = getTranslation(soup, word)
                except:
                    error_words.append(word)
                    print("Error with a translation or parents")
                    break

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
                if count % 500 == 0:
                    print(count)


    print("--- %s seconds ---" % (time.time() - start_time))
    print(words_missed)
    print(error_words)


def getTranslation(soup : bs, word : str):

    yellowBox = soup.find(attrs={"class" : "AF8dOcYf"})

    if yellowBox:
        #print("Went into yellow box for", word)
        meaning_for_nonverbs = soup.find_all(attrs={"class" : "le4jo4Ji"})
        meaning_for_verbs = soup.find_all(attrs={"class" : "iG5azK28"})
        translation = ""
    
        for num, sentance in enumerate(meaning_for_verbs):
            s = sentance.find_all("span")
            sentance = "".join([i.text + " " for i in s[:-1]])
            #print(sentance)
            try:
                if sentance.find("conjugation") != -1:
                    translation += sentance.strip() + ", \n"
                else:
                    translation += (meaning_for_nonverbs[num].text).split('-')[1] + ", \n"
            except IndexError:
                print("Error in translation")
        
        parent = soup.find_all(lambda tag: tag.has_attr("class") and tag["class"] == ["wpZ6GBd8"])
        parents = ""
        for x in parent:
            try:
                parents += (x.text) + ", "
            except IndexError:
                print("Error in finding parents")

        #print(translation[:-2]+ "  |  " + parents[:-2])
        return (translation[:-2], parents[:-2])

    else:
        word_and_meaning = soup.find_all(attrs={"class" : "YZ8gKxpm"})
        return ("".join([(x.text) + ", " for x in word_and_meaning[1:]])[:-2], "")


def count_csv_rows(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return sum(1 for _ in f) - 1
    

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(error_words)
        print(words_missed)