import dataclasses
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
class Sessions:
    id: int
    host: str
    headers: dict
    amo_hash: str
    chat_token: str


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
SessionsEntity = Base.classes.sessions

for c in [SessionsEntity]:
    c.as_dict = as_dict


def get_session(host: str):
    try:
        s = session.query(SessionsEntity).filter(
            SessionsEntity.host == host
        ).first()
    except Exception as e:
        pass

    return s


def update_session(host: str, headers: dict, amo_hash: str, chat_token: str):
    existing_session = get_session(host)

    if existing_session:
        # Update the existing session
        existing_session.headers = headers
        existing_session.amo_hash = amo_hash
        existing_session.chat_token = chat_token
        session.commit()
    else:
        # Create a new session if it doesn't exist
        create_session(host, headers, amo_hash, chat_token)


def create_session(host: str, headers: dict, amo_hash: str, chat_token: str):
    try:
        new_session = SessionsEntity(
            host=host,
            headers=headers,
            amo_hash=amo_hash,
            chat_token=chat_token
        )
        session.add(new_session)
        session.commit()
    except Exception as e:
        print(e)