import sqlalchemy
import sqlalchemy.ext.declarative as dec

SqlAlchemyBase = dec.declarative_base()


class Role(SqlAlchemyBase):
    __tablename__ = 'roles'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    nick_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    nick_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    role = sqlalchemy.Column(sqlalchemy.String, nullable=False)
