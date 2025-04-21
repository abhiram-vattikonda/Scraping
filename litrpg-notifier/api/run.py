import asyncio, aiohttp, os, requests, json, gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
from flask import Flask , request, jsonify

load_dotenv()

GOOGLE_SHEET_NAME = "Novel Chapter Tracker"
HEADER = ["Novel Name", "Latest Chapter"]
changed = False
subject = ""
body = ""

app = Flask(__name__)

def get_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.file"]
    service_account_info = json.loads(os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"))
    creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
    client = gspread.authorize(creds)


    try:
        sheet = client.open(GOOGLE_SHEET_NAME).sheet1
        print("Old file opened")
        print(sheet.show())
        
    except gspread.SpreadsheetNotFound:
        spreadsheet = client.create(GOOGLE_SHEET_NAME)
        print("new file created")
        spreadsheet.share(os.getenv("YOUR_EMAIL"), "user", "writer", True, "Your link", True)
        print("shared new file")
        subject = "New file was created"
        global changed 
        changed = True

        sheet = spreadsheet.sheet1
        sheet.append_row(HEADER)
    return sheet

def read_from_sheet():
    sheet = get_sheet()
    data = sheet.get_all_records()
    return {row["Novel Name"]: row["Latest Chapter"] for row in data}

def write_to_sheet(data_dict):
    sheet = get_sheet()
    sheet.clear()
    sheet.append_row(HEADER)
    for name, chapter in data_dict.items():
        sheet.append_row([name, chapter])

def send_email(subject, body):
    api_key = os.getenv('api_key')
    your_email = os.getenv('your_email')
    url = "https://api.resend.com/emails"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {"from": "onboarding@resend.dev", "to": your_email, "subject": subject, "html": "<p>" + body + "</p>"}
    response = requests.post(url, json=data, headers=headers)

async def fetch_latest_chapters(novel_list):
    latest_chapters = {}
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_chapter(session, author, pid, latest_chapters) for author, pid in novel_list.items()]
        await asyncio.gather(*tasks)
    return latest_chapters

async def fetch_chapter(session, author, pid, latest_chapters):
    try:
        async with session.get(f"https://kemono.su/api/v1/patreon/user/{pid}/posts-legacy") as resp:
            if resp.status == 200:
                json_data = await resp.json()
                latest_chapters[author] = json_data["results"][0]["title"]
    except Exception as e:
        print(f"Error for {author}: {e}")

def main():
    print("main is run")
    novel_list = {
        "cerim": 31891971, "Zogarth": 34232701, "DarkTechnomancer": 48003713, 
        "Shirtaloon": 22614979, "Ellake": 110014129, "Wizardly Dude": 151887001,
        "necariin": 30859026, "Ryn": 131199938, "dinniman": 5429305, 
        "Honour Rae": 75697552, "Priam": 71991276, "Miles English": 95765665
    }

    global changed
    
    current_latest = read_from_sheet()

    latest_chapters = asyncio.run(fetch_latest_chapters(novel_list))
    print("latest is run")

    updated_auths = {auth : latest_chapters[auth] for auth in novel_list if current_latest.get(auth) != latest_chapters.get(auth)}
    if updated_auths:
        changed = True
        subject = f"Updated authors: {updated_auths.keys()}"
        body = f"{updated_auths}"

    if changed:
        write_to_sheet(latest_chapters)
        send_email(subject, body)

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"status": "success", "updated": updated_auths})
    }


@app.route('/' , methods=["GET"])
def home():
    result = main()
    return jsonify(json.loads(result["body"])), result["statusCode"]


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)