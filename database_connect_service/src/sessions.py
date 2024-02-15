from sqlalchemy import create_engine, MetaData, Table, Column, JSON, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import dotenv
import os
import sqlalchemy

dotenv.load_dotenv()
Base = declarative_base()


class AmoCRMSession(Base):
    __tablename__ = 'amocrm_sessions'
    id = Column(Integer, primary_key=True, autoincrement=True)

    host = Column(String)
    access_token = Column(String)
    refresh_token = Column(String)
    amojo_id = Column(String)
    chat_token = Column(String)
    headers = Column(JSON)


def get_session(host: str):
    api_engine = sqlalchemy.create_engine(
        f'postgresql://{os.getenv("DB_B_USER")}:{os.getenv("DB_B_PASSWORD")}'
        f'@{os.getenv("DB_B_HOST")}:5432/{os.getenv("DB_B_NAME")}',
        pool_pre_ping=True
    )

    Session = sessionmaker(bind=api_engine)
    session = Session()

    # Assuming 'account' contains an identifier for the session
    db_session = session.query(AmoCRMSession).filter(AmoCRMSession.host == host).first()
    return db_session
