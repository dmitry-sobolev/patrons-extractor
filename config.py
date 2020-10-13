import os


# google sheets vars
GOOGLE_CREDENTIALS_FILE = os.getenv(
    'GOOGLE_CREDENTIALS_FILE', 'credentials.json'
)  # Имя файла с закрытым ключом, вы должны подставить свое
GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
GOOGLE_SHEET_RANGE = os.getenv('GOOGLE_SHEET_RANGE', 'Sheet1!A2:C')
GOOGLE_SHEET_IDX = 0

# patreon
PATREON_CONFIG_FILE = os.getenv('PATREON_CONFIG_FILE', 'patreon.json')