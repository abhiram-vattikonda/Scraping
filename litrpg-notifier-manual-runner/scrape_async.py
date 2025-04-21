import csv, asyncio, aiohttp, os, requests, time
from dotenv import load_dotenv
import json

load_dotenv()

header = ["Novel Name", "Latest Chapter"]

def main():
    print("main is run")
    novel_list = {
        "cerim": 31891971, "Zogarth": 34232701, "DarkTechnomancer": 48003713, 
        "Shirtaloon": 22614979, "Ellake": 110014129, "Wizardly Dude": 151887001,
        "necariin": 30859026, "Ryn": 131199938, "dinniman": 5429305, 
        "Honour Rae": 75697552, "Priam": 71991276, "Miles English": 95765665
    }
    
    changed = False
    subject = ""
    body = ""
    current_latest = {}

    # Check if CSV file exists and read existing chapter data
    try:
        with open("novel_list_with_latest_chapter.csv", "r") as csvfile:
            reader = csv.DictReader(csvfile, fieldnames=header)
            for row in reader:
                current_latest[row["Novel Name"]] = row["Latest Chapter"]
    except FileNotFoundError:
        changed = True
        subject = "New list file is Created"

    latest_chapters = asyncio.run(CreateAsyncTask(novel_list))
    print("Got latest chapter")
    updated_auths = []
    try:
        for auth in novel_list:
            if current_latest.get(auth) != latest_chapters.get(auth):
                changed = True
                updated_auths.append(auth)
        
        if updated_auths:
            subject = f"The authors that updated are {updated_auths}"
            body = f"{updated_auths}"

    except KeyError:
        changed = True
    
    if changed:
        WriteToFile(latest_chapters)
        send_email(subject, body)
    
    return json.dumps({"status": "success", "message": "Checked for updates."})

async def CreateAsyncTask(novel_list):
    latest_chapters = {}
    async with aiohttp.ClientSession() as async_session:
        tasks = [FindLatest(async_session, auth, novel_list, latest_chapters) for auth in novel_list]
        await asyncio.gather(*tasks)
    
    return latest_chapters

async def FindLatest(async_session, auth, novel_list, latest_chapters):
    try:
        async with async_session.get(f"https://kemono.su/api/v1/patreon/user/{novel_list[auth]}/posts-legacy") as response:
            if response.status == 200:
                info_json = await response.json()
                new_chap = info_json["results"][0]["title"]
                latest_chapters[auth] = new_chap
            else:
                print(f"Failed to fetch data for {auth}: HTTP {response.status}")
    except Exception as e:
        print(f"Error fetching data for {auth}: {e}")

def send_email(subject, body):
    api_key = os.getenv('api_key')
    your_email = os.getenv('your_email')
    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "from": "onboarding@resend.dev",  # Replace with your email
        "to": f"{your_email}",
        "subject": subject,
        "html": "<p>" + body + "</p>"
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        print("Email sent successfully!")
    else:
        print(f"Failed to send email: {response.status_code}, {response.text}")

def WriteToFile(latest_chapters):
    with open("novel_list_with_latest_chapter.csv", "w") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)
        writer.writeheader()
        for auth in latest_chapters:
            writer.writerow({"Novel Name": auth, "Latest Chapter": latest_chapters[auth]})

if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))