import dataclasses
import os

import dotenv
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker


def as_dict(obj):
    data = obj.__dict__
    data.pop('_sa_instance_state')
    return data


@dataclasses.dataclass
class Settings:
    id: int
    pipeline_id: int
    status_id: int


dotenv.load_dotenv()
engine = sqlalchemy.create_engine(f'postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}'
                                  f'@{os.getenv("DB_HOST")}:5432/{os.getenv("AMO_BOT_DB_NAME")}', pool_pre_ping=True)
Session = sessionmaker(bind=engine)
session = Session()

Base = automap_base()
Base.prepare(engine, reflect=True)

LeadsEntity = Base.classes.leads
MessagesEntity = Base.classes.messages

for c in [LeadsEntity, MessagesEntity]:
    c.as_dict = as_dict
