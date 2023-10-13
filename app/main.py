from typing import Annotated, Union
from fastapi import FastAPI, Body
from pydantic import BaseModel, Field
import aiohttp
from get_db_conn import get_engine_from_settings
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from mapped_columns import QuestionModel, create_tables
from datetime import datetime

engine = get_engine_from_settings()
session = sessionmaker(bind=engine)
create_tables()
app = FastAPI()


# Request "question" until get unique one
async def get_unique():
    json_response = await get_response(1)
    with session() as s:
        with s.begin():
            res = s.execute(
                select(QuestionModel).where(QuestionModel.id == json_response[0]["id"])
            ).scalar()

    if res is None:
        return json_response[0]
    else:
        json = await get_unique()
        return json


# get questions from API
async def get_response(count: int = 1):
    params = {"count": count}
    async with aiohttp.ClientSession() as session:
        async with session.get("https://jservice.io/api/random", params=params) as resp:
            json = await resp.json()
    return json


class Question_response_model(BaseModel):
    id: int
    question: str
    answer: str
    create_data: datetime


class Questions_count(BaseModel):
    questions_num: int = Field(title="Set count of requestable questions")


@app.post("/get_question")
async def get_question(questions_count: Annotated[Questions_count, Body()]) -> Union[Question_response_model, None]:
    if questions_count.questions_num <= 0:
        json_response = []
    else:
        json_response = await get_response(questions_count.questions_num)

    for question in json_response:
        with session() as s:
            with s.begin():
                res = s.execute(select(QuestionModel).where(QuestionModel.id == question["id"])).scalar()

        if res is None:
            question_obj = QuestionModel(
                id=question["id"],
                question=question["question"],
                answer=question["answer"],
                create_data=question["created_at"],
            )
            with session() as s:
                with s.begin():
                    s.add(question_obj)
        else:
            question = await get_unique()
            question_obj = QuestionModel(
                id=question["id"],
                question=question["question"],
                answer=question["answer"],
                create_data=question["created_at"],
            )
            with session() as s:
                with s.begin():
                    s.add(question_obj)

    with session() as s:
        with s.begin():
            res = s.query(QuestionModel).all()
            if len(res) == 0:
                return None
            else:
                res = res[-1]
            question_response = Question_response_model(
                id=res.id,
                question=res.question,
                answer=res.answer,
                create_data=res.create_data,
            )
    return question_response
