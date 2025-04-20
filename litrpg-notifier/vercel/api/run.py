import asyncio, aiohttp, os, requests, json, gspread, time
from google.oauth2.service_account import Credentials

def handler(request):
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"status": "ok"})
    }
