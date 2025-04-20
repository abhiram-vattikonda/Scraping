import csv, asyncio, aiohttp,json, time, requests

header = ["Novel Name", "Latest Chapter"]

def main():
    novel_list = {"cerim" : 31891971,            "Zogarth" : 34232701,
                  "DarkTechnomancer" : 48003713, "Shirtaloon" : 22614979,
                  "Ellake" : 110014129,          "Wizardly Dude" : 151887001,
                  "necariin" : 30859026,         "Ryn" : 131199938,
                  "dinniman" : 5429305,          "Honour Rae" : 75697552,
                  "Priam" : 71991276}
    
    current_latest = {}
    try:
        with open("novel_list_with_latest_chapter.csv", "r") as csvfile:
            reader = csv.DictReader(csvfile, header)
            for row in reader:
                current_latest.update({row["Novel Name"] : row["Latest Chapter"]})
    except FileNotFoundError:
        latest_chapters = FindLatest(novel_list)
        WriteToFile(latest_chapters)
        return
    
    latest_chapters = FindLatest(novel_list)
    for auth in novel_list:
        if current_latest[auth] != latest_chapters[auth]:
            
            print(f"New chapter uploded, by {auth}")
            WriteToFile(latest_chapters)
    


def WriteToFile(latest_chapters):

    with open("novel_list_with_latest_chapter.csv", "w") as csvfile:
        writer = csv.DictWriter(csvfile ,header)
        writer.writeheader()
        for auth in latest_chapters:
            writer.writerow({"Novel Name" : auth, "Latest Chapter" : latest_chapters[auth]})




def FindLatest(novel_list :dict):
    latest_chapters = {}

    for auth in novel_list:
        url = f"https://kemono.su/api/v1/patreon/user/{novel_list[auth]}/posts-legacy"
        response = requests.get(url)
        info_json = json.loads(response.text)
        new_chap = info_json["results"][0]["title"]
        latest_chapters.update({auth : new_chap})
    
    return latest_chapters




if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))