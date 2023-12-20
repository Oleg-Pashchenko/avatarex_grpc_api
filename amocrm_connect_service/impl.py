import asyncio
import json

import aiohttp
import requests

import db
from proto import amocrm_connect_pb2


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

    async def update_session(self, host):
        db.update_session(host, self.headers, self.amo_hash, '')
        await self.connect_async()

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
        session_info = db.get_session(self.host)
        if session_info is None or session_info.chat_token == '':
            await self._create_session_async()
            self.host = self.host.strip()
            url = f"{self.host}oauth2/authorize"
            payload = {
                "csrf_token": self.csrf_token,
                "username": self.login.strip(),
                "password": self.password.strip(),
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
                    await self._create_amo_hash()
                    await self._create_chat_token()
                    db.update_session(self.host, self.headers, self.amo_hash, self.chat_token)
                    return True
        else:
            self.host = session_info.host
            self.headers = session_info.headers
            self.chat_token = session_info.chat_token
            self.amo_hash = session_info.amo_hash

    async def get_unanswered_messages(self, search_info: list[list]):

        """Gets pipeline ids and stage ids and returned all talks"""
        try:
            search_info = search_info[0]
            self.headers["Host"] = self.host.replace("https://", "").replace("/", "")

            url = f"{self.host}ajax/v4/inbox/list"
            params = {
                "limit": 10,
                "order[sort_by]": "first_unanswered_message_at",
                "order[sort_type]": "desc",
                "filter[is_read][]": "false",
            }
            index = 0
            for param in search_info[1]:
                params[f"filter[pipe][{search_info[0]}][{index}]"] = param
                index += 1
            async with aiohttp.ClientSession() as session:
                talks = await session.get(url=url, headers=self.headers, params=params)

                talks = await talks.json()
                """https://drive-b.amocrm.ru/download/7b294ea0-53f2-5ea1-bfa0-464c3c297b79/0e49c658-b1d0-498a-986f-b50bb509c896/0098a61d-c343-4df3-8135-b61a2f3cb593/file-11.m4a"""
                response = []
                for t in talks["_embedded"]["talks"]:
                    chat_id = t["chat_id"]
                    message = t["last_message"]["text"]
                    pipeline_id = int(t["entity"]["pipeline_id"])
                    lead_id = int(t["entity"]["id"])
                    status_id = int(t["entity"]["status_id"])
                    headers = {"X-Auth-Token": self.chat_token}
                    url = f"https://amojo.amocrm.ru/messages/{self.amo_hash}/merge?stand=v16&offset=0&limit=20&chat_id%5B%5D={chat_id}&get_tags=true&lang=ru"
                    r = await session.get(url, headers=headers)
                    try:
                        messages_history = await r.json()
                        if message == "🔊":
                            message = messages_history["message_list"][0]["message"][
                                "attachment"
                            ]["media"]
                        response.append(
                            amocrm_connect_pb2.Chat(
                                id=messages_history["message_list"][0]['id'],
                                chat_id=chat_id,
                                message=message,
                                pipeline_id=pipeline_id,
                                lead_id=lead_id,
                                status_id=status_id,
                                messages_history=json.dumps(messages_history),
                            )
                        )
                    except Exception as e:
                        pass  # Пользователь удалил сообщение
                await session.close()
            return response
        except Exception as e:
            print("HAHHAHA", e)
            await self.update_session(self.host)
            return []

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
        headers = {"X-Auth-Token": self.chat_token}
        url = f"https://amojo.amocrm.ru/v1/chats/{self.amo_hash}/{chat_id}/messages?with_video=true&stand=v16"
        async with aiohttp.ClientSession() as session:
            response = await session.post(
                url=url, data=json.dumps({"text": message}), headers=headers
            )
            if response.status != 200:
                await self.update_session(self.host)
                response = await session.post(
                    url=url, data=json.dumps({"text": message}), headers=headers
                )
            answer = await response.json()

            return answer['id']

    async def get_fields_by_deal_id(self, deal_id):
        url = f"{self.host}api/v4/leads/{deal_id}"
        async with aiohttp.ClientSession() as session:
            response = await session.get(url, headers=self.headers)
            response = await response.json()
            print(response.status)
            fields = []
            for f in response["custom_fields_values"]:
                fields.append(
                    amocrm_connect_pb2.Field(
                        id=f["field_id"],
                        name=f["field_name"],
                        type=f["field_type"],
                        active_value=f["values"][0]["value"],
                        possible_values=None,
                    )
                )
        return fields

    def get_custom_fields(self):
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
                        amocrm_connect_pb2.Select(
                            id=v["id"], value=v["value"], sort=v["sort"]
                        )
                    )
            if f["type"] != "tracking_data":
                result.append(
                    amocrm_connect_pb2.Field(
                        id=f["id"],
                        name=f["name"],
                        type=f["type"],
                        active_value=None,
                        possible_values=possible_values,
                    )
                )

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
                    amocrm_connect_pb2.Status(id=s_id, sort=s_sort, name=s_name)
                )
            pipelines.append(
                amocrm_connect_pb2.Pipeline(
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

# async def main():
#     stages = [21679132, 60147942, 42011356, 42011413, 39441121, 42927400, 26079310, 21966199, 21593752, 21677467,
#               21677470, 39837472, 40032241, 28575823, 142, 143, 25450495, 51076282, 57470634, 57471506]
#     pipeline = 1342063
#     amo = AmoCRM(email='general@mosdommebel.ru', host='https://mdmbase.amocrm.ru/', password='31081220Vl')
#     await amo.connect_async()
#     ans = await amo.get_unanswered_messages([[pipeline, stages]])
#     print(ans)
#
#
# asyncio.run(main())
