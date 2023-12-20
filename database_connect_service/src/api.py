import dataclasses
import datetime
import json
import random
import time

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
import warnings
from sqlalchemy.exc import SADeprecationWarning
import dotenv
import os

import misc

dotenv.load_dotenv()


def as_dict(obj):
    data = obj.__dict__
    if "_sa_instance_state" in data:
        data.pop("_sa_instance_state")
    return data


warnings.filterwarnings("ignore", category=SADeprecationWarning)


@dataclasses.dataclass
class Messages:
    id: int
    message_id: int
    lead_id: int
    text: str
    is_bot: bool


dotenv.load_dotenv()
engine = sqlalchemy.create_engine(
    f'postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}'
    f'@{os.getenv("DB_HOST")}:5432/{os.getenv("AMO_BOT_DB_NAME")}',
    pool_pre_ping=True,
)
Session = sessionmaker(bind=engine)
session = Session()

Base = automap_base()
Base.prepare(engine, reflect=True)
MessagesEntity = Base.classes.messages

for c in [MessagesEntity]:
    c.as_dict = as_dict


def get_messages_history(lead_id: int):
    message_objects = (
        session.query(MessagesEntity).filter(MessagesEntity.lead_id == lead_id).all()
    )
    message_objects = sorted(message_objects, key=lambda x: x.id)
    messages = []
    for message_obj in message_objects:
        if message_obj.is_bot:
            messages.append({"role": "assistant", "content": message_obj.text})
        else:
            messages.append({"role": "user", "content": message_obj.text})
    return messages


def add_message(message_id, lead_id, text, is_bot):
    obj = MessagesEntity(
        message_id=message_id,
        text=text,
        lead_id=lead_id,
        is_bot=is_bot
    )
    session.add(obj)
    session.commit()


def manager_intervened(lead_id, message_history):
    try:
        entity = json.loads(message_history)['message_list'][0]
        for id, message in enumerate(json.loads(message_history)['message_list']):
            if id == 5:
                break

            if not message_exists(lead_id, message['id']) and entity['author']['id'] != message['author']['id']:
                created_at = message['created_at']
                datetime_from_timestamp = datetime.datetime.fromtimestamp(created_at)
                current_datetime = datetime.datetime.now()
                time_difference = current_datetime - datetime_from_timestamp

                if time_difference.total_seconds() < 60 * 60:
                    return True  # Больше часа
        return False
    except:
        return False


def message_exists(lead_id, message_id):
    existing_message = session.query(MessagesEntity).filter(
        MessagesEntity.lead_id == lead_id,
        MessagesEntity.message_id == message_id
    ).first()

    return existing_message is not None
