import datetime
import sqlalchemy
from sqlalchemy import orm
from data.db_session import SqlAlchemyBase


# модель пользователя
class User(SqlAlchemyBase):
    __tablename__ = 'users'

    chat_id = sqlalchemy.Column(sqlalchemy.Integer,
                                primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    number = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
