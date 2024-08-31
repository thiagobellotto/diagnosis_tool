import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime


def authenticate_google_sheets(gcp_service_account, sheet_name):
    creds_json = gcp_service_account
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        creds_json,
        [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ],
    )
    client = gspread.authorize(creds)
    spreadsheet = client.open(sheet_name)
    last_sheet = spreadsheet.worksheets()[-1]
    return last_sheet


def save_to_google_sheet(sheet, input_data, api_response):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    row = [timestamp, input_data, api_response]

    sheet.append_row(row)
