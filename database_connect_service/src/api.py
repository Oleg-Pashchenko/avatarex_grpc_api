import dataclasses
import datetime
import json

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
import warnings
from sqlalchemy.exc import SADeprecationWarning
import dotenv
import os

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
    is_q: bool


@dataclasses.dataclass
class Threads:
    id: int
    lead_id: int
    thread_id: str


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
ThreadsEntity = Base.classes.threads

for c in [MessagesEntity, ThreadsEntity]:
    c.as_dict = as_dict


def get_messages_history(lead_id: int):
    message_objects = (
        session.query(MessagesEntity).filter(MessagesEntity.lead_id == lead_id).all()
    )
    message_objects = sorted(message_objects, key=lambda x: x.id)
    messages = []
    for message_obj in message_objects:
        if message_obj.is_q:
            continue
        if message_obj.is_bot:
            messages.append({"role": "assistant", "content": message_obj.text})
        else:
            messages.append({"role": "user", "content": message_obj.text})
    return messages


def get_last_question_id(lead_id: int):
    message_objects = (
        session.query(MessagesEntity).filter(MessagesEntity.lead_id == lead_id).all()
    )
    message_objects = sorted(message_objects, key=lambda x: x.id, reverse=True)
    return message_objects[-1].id


def get_last_question(lead_id: int):
    message_objects = (
        session.query(MessagesEntity).filter(MessagesEntity.lead_id == lead_id).all()
    )
    message_objects = sorted(message_objects, key=lambda x: x.id, reverse=True)
    for m in message_objects:
        if m.is_bot:
            return {"role": "assistant", "content": m.text}
        else:
            return None


def add_message(message_id, lead_id, text, is_bot, is_q=False):
    obj = MessagesEntity(
        message_id=message_id,
        text=text,
        lead_id=lead_id,
        is_bot=is_bot,
        is_q=is_q
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


def get_thread_by_lead_id(lead_id: int):
    existing_lead = session.query(ThreadsEntity).filter(
        ThreadsEntity.lead_id == lead_id
    ).first()
    if existing_lead:
        return existing_lead.thread_id


def save_thread(lead_id: int, thread_id: int):
    obj = ThreadsEntity(lead_id=lead_id,
                        thread_id=thread_id)
    session.add(obj)
    session.commit()


def message_from_wazzap(lead_id):
    messages = get_messages_history(lead_id)
    for m in messages:
        if '=== Исходящее сообщение, ' in m['content']:
            return True
    return False


def add_stats(t, name, message_id):
    return
    t = round(int(t), 2)
    if name == 'CRM Fields':
        pass
    elif name == 'Prompt mode':
        pass
    elif name == 'Finish time':
        pass
    elif name == 'CRM Read':
        pass
    elif name == 'Start Time':
        pass
