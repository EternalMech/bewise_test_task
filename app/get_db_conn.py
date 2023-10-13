from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from db_config import postgresql as settings


def get_engine(user, passwd, host, port, db):
    url = f"postgresql://{user}:{passwd}@{host}:{port}/{db}"
    if not database_exists(url):
        print("db_not_exist")
        create_database(url)
        print("CreatedDB")
    engine = create_engine(url, pool_size=10, echo=False)
    print("engine get")
    return engine


def get_engine_from_settings():
    keys = ["pguser", "pgpassword", "pghost", "pgport", "pgdb"]
    if not all(key in keys for key in settings.keys()):
        raise Exception("Bad config file")

    return get_engine(
        settings["pguser"],
        settings["pgpassword"],
        settings["pghost"],
        settings["pgport"],
        settings["pgdb"],
    )


# def get_session():
#     engine = get_engine_from_settings()
#     session = sessionmaker(bind=engine)()
#     return session
