import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime


def trim_text(text, remove_multiple_lines=False):
    """
    Trims the input text by removing leading/trailing whitespace, extra spaces,
    and unnecessary line breaks, and condensing the content for cleaner storage.
    """
    # Remove leading and trailing whitespace
    trimmed_text = text.strip()

    # Replace multiple spaces with a single space
    trimmed_text = " ".join(trimmed_text.split())

    if remove_multiple_lines:
        # Optionally, remove excessive line breaks (you can customize this)
        trimmed_text = trimmed_text.replace("\n", " ").replace("\r", "")

    return trimmed_text


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


def save_to_google_sheet(sheet, gpt_dict):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    row = [
        gpt_dict["id"],
        timestamp,
        gpt_dict["assistant_id"],
        trim_text(gpt_dict["instructions"]),
        trim_text(gpt_dict["input_message"]),
        trim_text(gpt_dict["gpt_message"]),
        gpt_dict["completion_tokens"],
        gpt_dict["prompt_tokens"],
        gpt_dict["total_tokens"],
        gpt_dict["total_cost"],
        gpt_dict["temperature"],
        gpt_dict["top_p"],
    ]

    sheet.append_row(row)
