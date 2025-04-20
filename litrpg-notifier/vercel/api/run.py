import asyncio, aiohttp, os, requests, json, gspread, time
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

GOOGLE_SHEET_NAME = "Novel Chapter Tracker"  # name of your sheet
HEADER = ["Novel Name", "Latest Chapter"]

def main():
    novel_list = {
        "cerim": 31891971, "Zogarth": 34232701, "DarkTechnomancer": 48003713, 
        "Shirtaloon": 22614979, "Ellake": 110014129, "Wizardly Dude": 151887001,
        "necariin": 30859026, "Ryn": 131199938, "dinniman": 5429305, 
        "Honour Rae": 75697552, "Priam": 71991276, "Miles English": 95765665
    }

    changed = False
    subject = ""
    body = ""

    try:
        current_latest = read_from_sheet()
    except gspread.SpreadsheetNotFound:
        subject = "New file was created"
        changed = True


    latest_chapters =  asyncio.run(CreateAsyncTask(novel_list))

    updated_auths = []
    for auth in novel_list:
        if current_latest.get(auth) != latest_chapters.get(auth):
            changed = True
            updated_auths.append(auth)

    if updated_auths:
        subject = f"The authors that updated are {updated_auths}"
        body = f"{updated_auths}"

    if changed:
        write_to_sheet(latest_chapters)
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

def get_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.file"]
    creds = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    service_account_info = json.loads(os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"))
    creds = Credentials.from_service_account_info(service_account_info, scopes=scope)

    client = gspread.authorize(creds)
    
    try:
        # Try to open the existing sheet
        sheet = client.open(GOOGLE_SHEET_NAME).sheet1
    except gspread.SpreadsheetNotFound:

        spreadsheet = client.create(GOOGLE_SHEET_NAME)  # Create a new sheet
        sheet = spreadsheet.sheet1  # Get the first sheet
        print("new spread sheet was created")
        sheet.append_row(HEADER)  # You can pre-set the header row

    return sheet


def read_from_sheet():
    sheet = get_sheet()
    data = sheet.get_all_records()
    result = {}
    for row in data:
        result[row["Novel Name"]] = row["Latest Chapter"]
    return result

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
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "from": "onboarding@resend.dev",
        "to": f"{your_email}",
        "subject": subject,
        "html": "<p>" + body + "</p>"
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        print("Email sent successfully!")
    else:
        print(f"Failed to send email: {response.status_code}, {response.text}")

def handler(request):
    start_time = time.time()
    result = main()
    print("--- %s seconds ---" % (time.time() - start_time))

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": result
    }

