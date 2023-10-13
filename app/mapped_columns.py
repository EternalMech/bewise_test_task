import datetime
from sqlalchemy.orm import (
    as_declarative,
    declared_attr,
    mapped_column,
    Mapped,
    sessionmaker,
)
from sqlalchemy import DateTime
from get_db_conn import get_engine_from_settings


@as_declarative()
class AbstractModel:
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    id: Mapped[int] = mapped_column(primary_key=True)


class QuestionModel(AbstractModel):
    # __tablename__ = 'questionmodel'
    question: Mapped[str] = mapped_column(nullable=False)
    answer: Mapped[str] = mapped_column(nullable=False)
    create_data: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)


def create_tables():
    engine = get_engine_from_settings()
    session = sessionmaker(bind=engine)

    with session() as s:
        with s.begin():
            AbstractModel.metadata.create_all(engine)
