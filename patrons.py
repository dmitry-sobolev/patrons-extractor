import json
import operator
import dataclasses
from datetime import datetime

import patreon
import patreon.schemas.member

from typing import NamedTuple

from patreon.jsonapi.parser import JSONAPIParser

from config import PATREON_CONFIG_FILE


class PatronInfo(NamedTuple):
    name: str
    email: str
    pledge_cents: int

    @property
    def pledge_usd(self):
        return f'${(self.pledge_cents / 100):.2f}'

    def as_row(self):
        return self.name, self.email, self.pledge_usd

    @classmethod
    def fields_num(cls):
        return len(cls._fields)

    @classmethod
    def field_idx(cls, name):
        if name == 'name':
            return 0
        if name == 'email':
            return 1,
        if name == 'pledge_usd':
            return 2

        return -1


@dataclasses.dataclass
class PatreonConfig:
    client_id: str
    client_secret: str
    access_token: str
    refresh_token: str
    expires_at: int


class PatreonAuth:
    def __init__(self, config_path: str):
        self.config_path = config_path
        with open(config_path, mode='r') as fp:
            data = json.load(fp)
            self.config = PatreonConfig(**data)

        self._client = patreon.OAuth(
            client_id=self.config.client_id,
            client_secret=self.config.client_secret
        )

    def auth(self):
        if datetime.utcnow().timestamp() >= self.config.expires_at:
            self._refresh()

        if not self.config.access_token:
            self._refresh()

        return self.config.access_token

    def _refresh(self):
        data = self._client.refresh_token(self.config.refresh_token)
        self.config.access_token = data['access_token']
        self.config.refresh_token = data['refresh_token']
        self.config.expires_at = (
                datetime.utcnow().timestamp() + data['expires_in']
        )

        self._dump_config()

    def _dump_config(self):
        with open(self.config_path, mode='w') as fp:
            json.dump(dataclasses.asdict(self.config), fp=fp)


def get_patrons():
    p_auth = PatreonAuth(PATREON_CONFIG_FILE)
    access_token = p_auth.auth()

    client = patreon.API(access_token=access_token)

    campaigns = client.get_campaigns(page_size=10)

    if not isinstance(campaigns, JSONAPIParser):
        raise Exception('Could not get campaigns')

    campaign_id = campaigns.data()[0].id()

    members = []
    cursor = None
    while True:
        members_response = client.get_campaigns_by_id_members(
            campaign_id, page_size=10, cursor=cursor,
            fields={
                'member': [
                    patreon.schemas.member.Attributes.full_name,
                    patreon.schemas.member.Attributes.currently_entitled_amount_cents,
                    patreon.schemas.member.Attributes.email,
                    patreon.schemas.member.Attributes.patron_status
                ]
            }
        )
        members += members_response.data()
        try:
            cursor = client.extract_cursor(members_response)
        except Exception as e:
            if type(e) == Exception:
                break  # хак, чтобы либа завершила пагинацию

            raise

    res = [
        PatronInfo(
            name=member.attribute('full_name'),
            email=member.attribute('email'),
            pledge_cents=member.attribute('currently_entitled_amount_cents'),
        ) for member in members
        if member.attribute('patron_status') == 'active_patron'
    ]

    return res
