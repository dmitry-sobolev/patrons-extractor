Patrons extractor
=================

Syncs patrons list with table in Google Spreadsheets

Config
------

Env vars:
* `GOOGLE_CREDENTIALS_FILE` - path to file which contains Google API credentials
* `GOOGLE_SHEET_ID` - identifier in sheet's URL 
* `GOOGLE_SHEET_RANGE` (optional)
* `PATREON_CONFIG_FILE` - path to file which contains Patreon credentials

### Patreon config

This file contains credentials which are needed to authorize app on Patreon's API as well as cached `access_token` and `refresh_token`. To be able to dump new token's values script must have rights to rewrite this config file.

```json
{
  "client_id": "",
  "client_secret": "",
  "access_token": "",
  "refresh_token": "",
  "expires_at": 0
}
```

Values for all fields except of `expires_at` will fields available [here](https://www.patreon.com/portal/registration/register-clients) after you create client.

`expires_at` contains timestamp until when `access_token` is valid.

Run with docker
---------------

Build image:
```
docker build -t patreon .
```

Run in container:
```shell script
docker container run --rm -v "$(pwd)/credentials.json:/opt/app/credentials.json:ro" -v "$(pwd)/patreon.json:/opt/app/patreon.json" -e "GOOGLE_SHEET_ID=<some kind of ID>" patreon
```
