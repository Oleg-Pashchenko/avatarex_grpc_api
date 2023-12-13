import dataclasses
import datetime
import random
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
import warnings
from sqlalchemy.exc import SADeprecationWarning
import dotenv
import os
from database_connect_service.src import misc
warnings.filterwarnings('ignore', category=SADeprecationWarning)


@dataclasses.dataclass
class Leads:
    id: int
    pipeline_id: int
    status_id: int
    deal_id: int


@dataclasses.dataclass
class Messages:
    id: int
    message_id: int
    lead_id: int
    text: str
    is_bot: bool
    date: datetime.datetime


dotenv.load_dotenv()
engine = sqlalchemy.create_engine(f'postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}'
                                  f'@{os.getenv("DB_HOST")}:5432/{os.getenv("API_DB_NAME")}', pool_pre_ping=True)
Session = sessionmaker(bind=engine)
session = Session()

Base = automap_base()
Base.prepare(engine, reflect=True)


LeadsEntity = Base.classes.leads
MessagesEntity = Base.classes.messages

for c in [LeadsEntity, MessagesEntity]:
    c.as_dict = misc.as_dict


def get_messages_history(lead_id: int):
    message_objects = session.query(MessagesEntity).filter(MessagesEntity.lead_id == lead_id).all()
    message_objects = sorted(message_objects, key=lambda x: x.date)
    messages = []
    for message_obj in message_objects:
        if message_obj.is_bot:
            messages.append({'role': 'assistant', 'content': message_obj.message})
        else:
            messages.append({'role': 'user', 'content': message_obj.message})
    return messages


def add_message(message, lead_id, is_bot):
    if is_bot:
        message_id = f'assistant-{random.randint(1000000, 10000000)}'
    else:
        message_id = f'assistant-{random.randint(1000000, 10000000)}'
    obj = MessagesEntity(id=message_id, message=message, lead_id=lead_id, is_bot=is_bot, date=datetime.datetime.now())
    session.add(obj)
    session.commit()


def get_lead(lead_id):
    return session.query(LeadsEntity).filter(LeadsEntity.id == lead_id).first()
