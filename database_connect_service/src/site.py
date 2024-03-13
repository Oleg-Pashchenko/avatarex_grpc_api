import dataclasses
import datetime
import json
import time
from sqlalchemy import and_

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
import warnings
from sqlalchemy.exc import SADeprecationWarning

import dotenv
import os


def as_dict(obj):
    data = obj.__dict__
    if "_sa_instance_state" in data:
        data.pop("_sa_instance_state")
    return data


warnings.filterwarnings("ignore", category=SADeprecationWarning)


@dataclasses.dataclass
class AuthUser:
    id: int
    password: str
    last_login: datetime.datetime
    is_superuser: bool
    first_name: str
    last_name: str
    email: str
    is_staff: bool
    is_active: bool
    data_joined: datetime.datetime
    openai_api_key: str


@dataclasses.dataclass
class ApiSettings:
    id: int
    pipeline_id_id: int
    mode_id: int
    voice_detection: bool
    model_title: str
    model_limit: int

    pipeline_id: int
    statuses_ids: list

    use_amocrm_fields: bool
    amocrm_fields: list

    qualification_fields: list
    qualification_finished: str

    hi_message: str
    openai_error_message: str
    avatarex_error_message: str

    prompt_context: str
    max_tokens: int
    temperature: float
    fine_tuned_model: str
    use_fine_tuned: bool
    manager_intervented_active: bool

    amo_email: str
    amo_password: str
    amo_host: str
    api_token: str
    knowledge_data: list

    assistant_id: str

    database_data: list
    search_rules: dict
    message_format: str
    repeat: int
    trigger_phrases: list
    qualification_finished_stage: str
    is_date_work_active: bool
    datetimeValueStart: str
    datetimeValueFinish: str


@dataclasses.dataclass
class Statuses:
    id: int
    status_id: int
    name: str
    order: int
    is_active: bool
    pipeline_id_id: int
    user_id_id: int
    bitrix_status_id: str

@dataclasses.dataclass
class Settings:
    id: int
    name: str
    mode_id: int
    is_enabled: bool
    voice_detection: bool
    model_id: int
    pipeline_id_id: int
    qualification_id_id: int
    request_settings_id_id: int
    work_mode_id: int
    user_id_id: int
    amocrm_fields_enabled: bool
    statuses: list
    prompt_settings_id: int
    fields: list
    is_manager_intervented_active: bool

    database_data: list
    database_link: str
    database_name: str

    knowledge_data: list
    knowledge_link: str
    knowledge_name: str
    assistant_id: str
    trigger_phrases: str
    database_repeat: int
    message_format: str
    is_date_work_active: bool
    datetimeValueStart: str
    datetimeValueFinish: str


@dataclasses.dataclass
class Pipeline:
    id: int
    pipeline_id: int
    name: str
    order: int
    user_id_id: int


@dataclasses.dataclass
class Qualification:
    id: int
    questions: list
    finish_message: str
    stage: str


@dataclasses.dataclass
class RequestSettings:
    id: int
    hi_message: str
    openai_error_message: str
    avatarex_error_message: str


@dataclasses.dataclass
class PromptSettings:
    id: int
    context: str
    max_tokens: int
    temperature: float
    fine_tuned_model_id: str
    use_fine_tuned: bool


@dataclasses.dataclass
class OpenAIModels:
    id: int
    title: str
    tokens_limit: int
    source_id_id: int


@dataclasses.dataclass
class AmoCRM:
    id: int
    email: str
    password: str
    host: str
    user_id_id: int


dotenv.load_dotenv()
engine = sqlalchemy.create_engine(
    f'postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}'
    f'@{os.getenv("DB_HOST")}:5432/{os.getenv("SITE_DB_NAME")}',
    pool_pre_ping=True,
)
Session = sessionmaker(bind=engine)
session = Session()

Base = automap_base()
Base.prepare(engine, reflect=True)

Settings = Base.classes.settings
Statuses = Base.classes.statuses
Pipeline = Base.classes.pipelines
Qualification = Base.classes.qualification
RequestSettings = Base.classes.request_settings
PromptSettings = Base.classes.prompt_settings
OpenAIModels = Base.classes.openai_models
AmoCRM = Base.classes.amocrm
AuthUser = Base.classes.avatarex_users

for c in [
    AuthUser,
    Settings,
    Pipeline,
    Qualification,
    RequestSettings,
    PromptSettings,
    ApiSettings,
    OpenAIModels,
    AmoCRM,
]:
    c.as_dict = as_dict



def get_btx_statuses_by_id(id):
    response = []
    q = session.query(Statuses).filter(Statuses.pipeline_id_id == id)

    for status in q:
        response.append(status.bitrix_status_id)
       #  r = session.query(Statuses).filter(Statuses.id == status)[0].bitrix_status_id
       #  response.append(r)
    return response


def get_enabled_api_settings() -> list[ApiSettings]:
    start_time = time.time()
    q = session.query(Settings).filter(Settings.is_enabled == True)
    result = []
    for obj in q.all():
        try:
            s = Settings(**obj.as_dict())
            try:
                s.database_data = json.loads(s.database_data)
            except Exception as e:
                s.database_data = []

            try:
                q2 = session.query(Pipeline).filter(
                    and_(Pipeline.id == s.pipeline_id_id, Pipeline.user_id_id == s.user_id_id)
                )
            except Exception as e:
                print(s.pipeline_id_id, s.user_id_id)
                print(2, e)
            try:
                q3 = session.query(Qualification).filter(
                    Qualification.id == s.qualification_id_id
                )
            except Exception as e:
                print(3, e)
            try:
                q4 = session.query(RequestSettings).filter(
                    RequestSettings.id == s.request_settings_id_id
                )
            except Exception as e:
                print(4, e)
            try:
                q5 = session.query(PromptSettings).filter(
                    PromptSettings.id == s.prompt_settings_id
                )
            except Exception as e:
                print(5, e)
            try:
                q6 = session.query(OpenAIModels).filter(OpenAIModels.id == s.model_id)
            except Exception as e:
                print(6, e)
            try:
                q7 = session.query(AmoCRM).filter(AmoCRM.user_id_id == s.user_id_id)
            except Exception as e:
                print(7, e)
            try:
                q8 = session.query(AuthUser).filter(AuthUser.id == s.user_id_id)
            except Exception as e:
                print(8, e)
            try:
                p = Pipeline(**q2.first().as_dict())
            except:
                print(s.pipeline_id_id, s.user_id_id)
                print('pipeline error')
            try:
                qual = Qualification(**q3.first().as_dict())
            except:
                print('qual error')
            try:
                rs = RequestSettings(**q4.first().as_dict())
            except:
                print('rs error')
            try:
                ps = PromptSettings(**q5.first().as_dict())
            except:
                print('ps error')
            try:
                model = OpenAIModels(**q6.first().as_dict())
            except:
                print('model error')
            try:
                amo = AmoCRM(**q7.first().as_dict())
            except:
                print('amo error')
            try:
                user = AuthUser(**q8.first().as_dict())
            except:
                print('user error')
            try:
                triggers = s.trigger_phrases.split(';')
            except:
                triggers = []
            result.append(
                ApiSettings(
                    id=s.id,
                    pipeline_id_id=s.pipeline_id_id,
                    mode_id=s.mode_id,
                    voice_detection=s.voice_detection,
                    model_title=model.title,
                    model_limit=model.tokens_limit,
                    pipeline_id=p.pipeline_id,
                    statuses_ids=s.statuses,
                    use_amocrm_fields=s.amocrm_fields_enabled,
                    amocrm_fields=s.fields,
                    qualification_fields=qual.questions,
                    qualification_finished=qual.finish_message,
                    hi_message=rs.hi_message,
                    openai_error_message=rs.openai_error_message,
                    avatarex_error_message=rs.avatarex_error_message,
                    prompt_context=ps.context,
                    max_tokens=ps.max_tokens,
                    temperature=ps.temperature,
                    fine_tuned_model=ps.fine_tuned_model_id,
                    use_fine_tuned=ps.use_fine_tuned,
                    amo_email=amo.email,
                    amo_password=amo.password,
                    amo_host=amo.host,
                    api_token=user.openai_api_key,
                    knowledge_data=s.knowledge_data,
                    manager_intervented_active=s.is_manager_intervented_active,
                    assistant_id=s.assistant_id,
                    database_data=s.database_data,
                    search_rules={},
                    repeat=s.database_repeat,
                    message_format=s.database_message_format,
                    trigger_phrases=triggers,
                    qualification_finished_stage=qual.stage,
                    is_date_work_active=s.is_date_work_active,
                    datetimeValueStart=s.datetimeValueStart,
                    datetimeValueFinish=s.datetimeValueFinish
                )
            )
        except Exception as e:
            print(e)

            # print('error', s.name, e)
    return result
