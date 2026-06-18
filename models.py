from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String)
    role = Column(String)  # admin / employee

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    text = Column(Text)
    correct_answer = Column(String)
    course_id = Column(Integer, ForeignKey("courses.id"))

class Result(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    course_id = Column(Integer)
    score = Column(Integer)
    total = Column(Integer)