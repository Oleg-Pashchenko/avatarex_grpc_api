import json

import aiohttp
import requests
from proto import amocrm_site_pb2


class AmoCRM:
    def __init__(self, host, email, password):
        self.host = host
        self.login = email
        self.password = password

    def _create_session(self):
        self.session = requests.Session()
        if "/" not in self.host[-1]:
            self.host += "/"
        if "https://" not in self.host:
            self.host = "https://" + self.host

        response = self.session.get(self.host)
        session_id = response.cookies.get("session_id")
        self.csrf_token = response.cookies.get("csrf_token")
        self.headers = {
            "Accept": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "Cookie": f"session_id={session_id}; " f"csrf_token={self.csrf_token};",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/111.0.0.0 Safari/537.36",
        }

    async def _create_session_async(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.host) as response:
                self.cookies = response.cookies
                self.csrf_token = self.cookies.get("csrf_token").value
                self.headers = {
                    "Accept": "application/json",
                    "X-Requested-With": "XMLHttpRequest",
                    "Cookie": f'session_id={self.cookies.get("session_id").value}; csrf_token={self.csrf_token};',
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
                }

    def is_host_supported(self):
        url = "https://www.amocrm.ru/v3/accounts"
        response = self.session.get(url)
        if response.status_code != 200:
            return False
        for account in response.json()["_embedded"]["items"]:
            if account["name"] in self.host:
                return True
        return False

    def connect(self) -> bool:
        self._create_session()
        response = self.session.post(
            f"https://www.amocrm.ru/oauth2/authorize",
            data={
                "csrf_token": self.csrf_token,
                "username": self.login,
                "password": self.password,
            },
            headers=self.headers,
        )

        if response.status_code != 200:
            return False

        self.headers["access_token"] = response.cookies.get("access_token")
        self.headers["refresh_token"] = response.cookies.get("refresh_token")
        return True

    async def connect_async(self) -> bool:
        await self._create_session_async()
        url = f"{self.host}oauth2/authorize"
        payload = {
            "csrf_token": self.csrf_token,
            "username": self.login,
            "password": self.password,
        }
        async with aiohttp.ClientSession(cookies=self.cookies) as session:
            async with session.post(
                    url=url, data=payload, headers=self.headers
            ) as response:
                if response.status != 200:
                    return False  # TODO: оповестить об ошибке
                self.cookies = response.cookies
                self.access_token = self.cookies.get("access_token").value
                self.refresh_token = self.cookies.get("refresh_token").value

                self.headers["access_token"], self.headers["refresh_token"] = (
                    self.access_token,
                    self.refresh_token,
                )
                self.headers["Host"] = self.host.replace("https://", "").replace(
                    "/", ""
                )
                return True


    async def _create_chat_token(self):
        url = f"{self.host}ajax/v1/chats/session"
        payload = {"request[chats][session][action]": "create"}

        async with aiohttp.ClientSession() as session:
            response = await session.post(url=url, headers=self.headers, data=payload)
            data = await response.json()
            self.chat_token = data["response"]["chats"]["session"]["access_token"]

    async def _create_amo_hash(self):
        url = f"{self.host}api/v4/account?with=amojo_id"
        async with aiohttp.ClientSession() as session:
            response = await session.get(url, headers=self.headers)
            data = await response.json()
            self.amo_hash = data["amojo_id"]

    async def send_message(self, message: str, chat_id: str):
        await self._create_chat_token()
        await self._create_amo_hash()
        headers = {"X-Auth-Token": self.chat_token}
        url = f"https://amojo.amocrm.ru/v1/chats/{self.amo_hash}/{chat_id}/messages?with_video=true&stand=v16"
        async with aiohttp.ClientSession() as session:
            response = await session.post(
                url=url, data=json.dumps({"text": message}), headers=headers
            )
            answer = await response.json()

            return answer['id']


    def get_custom_fields(self):
        try:
            url = f"{self.host}api/v4/leads/custom_fields"
            response = self.session.get(url, headers=self.headers).json()["_embedded"][
                "custom_fields"
            ]
            result = []
            for f in response:
                possible_values = []
                if f["enums"] is not None:
                    for v in f["enums"]:
                        possible_values.append(
                            amocrm_site_pb2.Select(
                                id=v["id"], value=v["value"], sort=v["sort"]
                            )
                        )
                if f["type"] != "tracking_data":
                    result.append(
                        amocrm_site_pb2.Field(
                            id=f["id"],
                            name=f["name"],
                            type=f["type"],
                            active_value=None,
                            possible_values=possible_values,
                        )
                    )
        except:
            return []
        return result

    def get_pipelines_info(self):
        response = self.session.get(
            f"{self.host}ajax/v1/pipelines/list", headers=self.headers
        ).json()["response"]["pipelines"]
        pipelines = []
        for p in response.values():
            p_id = p["id"]
            p_name = p["name"]
            p_sort = p["sort"]
            statuses = []
            for s in p["statuses"].values():
                s_id = s["id"]
                s_sort = s["sort"]
                s_name = s["name"]
                statuses.append(
                    amocrm_site_pb2.Status(id=s_id, sort=s_sort, name=s_name)
                )
            pipelines.append(
                amocrm_site_pb2.Pipeline(
                    id=p_id,
                    name=p_name,
                    sort=p_sort,
                    statuses=statuses,
                    # custom_fields=self.get_custom_fields()
                )
            )
        return pipelines

    def get_last_message_by_deal_id(self, chat_id):
        try:
            url = f"{self.host}ajax/v2/talks"
            data = {"chats_ids[]": chat_id}
            response = self.session.post(
                url=url, data=data, headers=self.headers
            ).json()
            for k, v in response.items():
                v = v[0]
                return v["last_message"], v["last_message_author"]["type"]
        except:
            return "", "contact"

    def set_field_by_id(self, field_id: int, value, pipeline_id, deal_id):
        url = f"{self.host}ajax/leads/detail/"
        if value.is_digit():
            value = int(value)

        data = {
            f"CFV[{field_id}]": value,
            "lead[STATUS]": "",
            "lead[PIPELINE_ID]": pipeline_id,
            "ID": deal_id,
        }
        self.session.post(url=url, data=data, headers=self.headers)

# amo = AmoCRM(email="havaisaeva19999@gmail.com", password="A12345mo", host="https://olegtest12.amocrm.ru/")
# amo.connect()
# amo.get_fields_by_deal_id(361335)

# amo.set_field_by_id(449327, "19", 7519106, 361335)
# amo.set_field_by_id(449329, 254631, 7519106, 361335)

# amo.get_custom_fields()
# print(amo.get_pipelines_info())
# response = amo.get_unanswered_messages([[7519106, [62333722]], [7556182, [62592642]]])
# print(response)
# for r in response:
#     amo.send_message("Лол", r['chat_id'])
