from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str
    role: str

class CourseCreate(BaseModel):
    title: str
    description: str

class QuestionCreate(BaseModel):
    text: str
    correct_answer: str
    course_id: int

class AnswerSubmit(BaseModel):
    question_id: int
    answer: str
