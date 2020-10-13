from datetime import datetime
from typing import List

import httplib2
import googleapiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials

from config import GOOGLE_CREDENTIALS_FILE, GOOGLE_SHEET_ID, \
    GOOGLE_SHEET_RANGE, GOOGLE_SHEET_IDX
from patrons import PatronInfo


def write_patrons(data: List[PatronInfo]):
    # Читаем ключи из файла
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        GOOGLE_CREDENTIALS_FILE,
        ['https://www.googleapis.com/auth/spreadsheets']
    )

    http_auth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
    service = googleapiclient.discovery.build('sheets', 'v4', http=http_auth)  # Выбираем работу с таблицами и 4 версию API

    spreadsheets = service.spreadsheets()

    spreadsheets.values().clear(
        spreadsheetId=GOOGLE_SHEET_ID,
        range=GOOGLE_SHEET_RANGE
    ).execute()

    spreadsheets.values().batchUpdate(
        spreadsheetId=GOOGLE_SHEET_ID,
        body={
            "value_input_option": "USER_ENTERED",
            "data": [
                {
                    "range": GOOGLE_SHEET_RANGE,
                    "majorDimension": "ROWS",
                    'values': [r.as_row() for r in data]
                },
                {
                    "range": 'Sheet1!E2:F2',
                    "majorDimension": "ROWS",
                    'values': [
                        ('Last Update', datetime.now().isoformat()),
                    ]
                }
            ]
        }
    ).execute()

    sort_range = {
        'sheetId': GOOGLE_SHEET_IDX,
        'startRowIndex': 1,
        'endColumnIndex': PatronInfo.fields_num()
    }

    spreadsheets.batchUpdate(
        spreadsheetId=GOOGLE_SHEET_ID,
        body={
            'requests': [{
                'sortRange': {
                    'range': sort_range,
                    'sortSpecs': [{
                        'sortOrder': 'DESCENDING',
                        'dimensionIndex': PatronInfo.field_idx('pledge_usd'),
                    }, {
                        'sortOrder': 'ASCENDING',
                        'dimensionIndex': PatronInfo.field_idx('name'),
                    }]
                }
            }],
            'includeSpreadsheetInResponse': False
        }
    ).execute()

