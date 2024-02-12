import dataclasses
import datetime
import os
import time

from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Boolean, create_engine
import dotenv
from sqlalchemy.orm import sessionmaker

from database_connect_service.src.api import Messages

dotenv.load_dotenv()
Base = declarative_base()


class Bitrix_Message(Base):
    __tablename__ = 'bitrix_messages'
    id = Column(Integer, primary_key=True)
    text = Column(String)
    date = Column(DateTime, default=datetime.datetime.now())
    pipeline_id = Column(BigInteger)
    status_id = Column(String)
    app_id = Column(Integer)
    rest_hook = Column(String)
    is_started = Column(Boolean, default=False)
    is_finished = Column(Boolean, default=False)
    dialog_id = Column(Integer)
    bot_id = Column(Integer)


@dataclasses.dataclass
class Message:
    id: int
    message_id: int
    lead_id: int
    message: str
    bm: Bitrix_Message

engine = create_engine(
    f'postgresql://{os.getenv("DB_B_USER")}:{os.getenv("DB_B_PASSWORD")}'
    f'@{os.getenv("DB_B_HOST")}:5432/{os.getenv("DB_B_NAME")}',
    pool_pre_ping=True,
)

Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine)



def get_unanswered_messages(rest_hook, pipeline_id, status_ids):
    # Querying Bitrix_Message objects
    message_objects = session.query(Bitrix_Message).filter(
        Bitrix_Message.rest_hook == rest_hook,
        Bitrix_Message.pipeline_id == pipeline_id,
        Bitrix_Message.status_id.in_(status_ids),
        Bitrix_Message.is_finished == False  # Assuming you want only unfinished messages
    ).all()

    # Creating a list of Message dataclass instances
    answer = [Message(
                id=m.id,
                lead_id=m.dialog_id,
                message_id=m.id,
                message=m.text,
                bm=m  # Passing the Bitrix_Message instance
              ) for m in message_objects]
    return answer
