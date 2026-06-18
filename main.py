from fastapi import FastAPI, Depends, HTTPException, Form, Response, Cookie
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jose import jwt
from sqlalchemy.orm import Session

import random
import models
import schemas
from urllib.parse import quote
from auth import hash_password, verify_password
from database import SessionLocal, engine
from certificate import generate_certificate

# uvicorn main:app --reload для запуска сайта

app = FastAPI(title="CyberSecurity Corporate LMS")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ГЛАВНАЯ
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "active": "home"})

# СТРАНИЦА КУРСОВ
@app.get("/courses_page", response_class=HTMLResponse)
def courses_page(request: Request, db: Session = Depends(get_db)):
    courses = db.query(models.Course).all()
    return templates.TemplateResponse("courses.html", {
        "request": request,
        "courses": courses,
        "active": "courses"
    })
# разлогин
@app.get("/logout")
def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("user_id")
    return response

# вход в акк
@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.username == username
    ).first()

    if not user or not verify_password(password, user.password):
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Неверный логин или пароль"
            }
        )

    response = RedirectResponse(
        url="/profile",
        status_code=303
    )

    response.set_cookie(
        key="user_id",
        value=str(user.id)
    )

    return response

# ТЕОРИЯ КУРСА
@app.get("/course/{course_id}", response_class=HTMLResponse)
def course_theory(request: Request, course_id: int, db: Session = Depends(get_db)):
    course = db.query(models.Course).filter(models.Course.id == course_id).first()

    if not course:
        return {"error": "Курс не найден"}

    if "Основы" in course.title:
        theory = """
Введение в основы кибербезопасности
Современный мир невозможно представить без интернета: мы общаемся, работаем, учимся и совершаем покупки онлайн. Но вместе с удобством появляются и риски — злоумышленники могут украсть данные, заразить устройства или получить доступ к личной информации. Чтобы защитить себя, важно понимать базовые принципы кибербезопасности.

🔒 Защита соединения: VPN
Одним из инструментов является VPN (Virtual Private Network). Он создаёт защищённый канал между вашим устройством и интернетом, шифруя данные и скрывая реальный IP-адрес. Это особенно полезно при подключении к общественным Wi-Fi сетям, где риск перехвата информации выше.

🦠 Опасности: вредоносное ПО
Главная угроза в цифровой среде — вредоносное программное обеспечение (malware). Это программы, созданные для нанесения ущерба: вирусы, трояны, шпионские утилиты или программы-вымогатели. Они могут украсть пароли, заблокировать доступ к файлам или вывести из строя систему. Поэтому важно быть внимательным при скачивании файлов и открытии ссылок.

🔑 Ключ к безопасности: пароли
Основным способом защиты учётных записей остаётся пароль. Надёжный пароль должен быть длинным, содержать буквы разных регистров, цифры и специальные символы. Использование простых комбинаций вроде «123456» или даты рождения делает систему уязвимой. Хорошая практика — применять разные пароли для разных сервисов.

🛡️ Защитник системы: антивирус
Чтобы противостоять вредоносному ПО, используют антивирусные программы. Они сканируют файлы и процессы, выявляют подозрительное поведение и блокируют угрозы. Современные антивирусы работают в реальном времени, предотвращая заражение ещё до того, как оно нанесёт ущерб.

📲 Дополнительный барьер: двухфакторная аутентификация
Даже самый сложный пароль может быть украден. Поэтому всё чаще применяют двухфакторную аутентификацию (2FA). Она требует второй шаг подтверждения — код из SMS, push-уведомление, биометрические данные или специальное приложение. Это значительно усложняет задачу злоумышленникам, ведь одного пароля уже недостаточно.
"""

    elif "Социальная" in course.title:
        theory = """
Основы социальной инженерии
В кибербезопасности существует особая угроза, связанная не столько с технологиями, сколько с человеческим фактором. Она называется социальная инженерия. Это совокупность методов, при которых злоумышленники используют психологические приёмы, чтобы обмануть человека и заставить его добровольно раскрыть конфиденциальную информацию или выполнить действия, выгодные атакующему. Главная цель социальной инженерии — не взломать систему напрямую, а обойти её через доверчивость или невнимательность пользователя.

👨‍💻 Роль хакера
Хакер — это человек, обладающий глубокими знаниями в области информационных технологий. В контексте социальной инженерии хакер может использовать свои навыки для получения несанкционированного доступа к данным или системам. Важно понимать, что не каждый хакер — злоумышленник: существуют «этичные хакеры», которые помогают компаниям находить уязвимости. Но в случае атак социальной инженерии речь идёт именно о тех, кто стремится использовать слабости людей и систем в корыстных целях.

📧 Фишинг как инструмент обмана
Одним из самых распространённых методов социальной инженерии является фишинг. Это рассылка поддельных сообщений (обычно по электронной почте), которые выглядят как официальные письма от банков, сервисов или коллег. В таких письмах пользователя просят перейти по ссылке или ввести свои данные. На самом деле ссылка ведёт на поддельный сайт, созданный для кражи паролей, номеров карт и другой личной информации.

🗑️ Спам как массовая угроза
Спам — это массовая рассылка нежелательных сообщений. Чаще всего он используется для рекламы, но может быть и частью атак социальной инженерии. Среди сотен писем могут скрываться фишинговые сообщения или ссылки на вредоносные сайты. Спам отвлекает внимание и повышает вероятность того, что человек случайно откроет опасное письмо.
"""

    else:
        theory = "Описание курса отсутствует"

    return templates.TemplateResponse("course_theory.html", {
        "request": request,
        "course": course,
        "theory": theory
    })

#  ТЕСТ КУРСА
@app.get("/course/{course_id}/test", response_class=HTMLResponse)
def course_test(request: Request, course_id: int, db: Session = Depends(get_db)):
    course = db.query(models.Course).filter(models.Course.id == course_id).first()

    if not course:
        return {"error": "Курс не найден"}

    if course.title and "Основы" in course.title:

        content = "Проверьте свои знания по основам кибербезопасности"

        all_questions = [
            {"q": "Что такое фишинг?", "options": ["Тип атаки", "Антивирус", "VPN", "Фаервол"], "correct": 0},
            {"q": "Что такое вредоносное ПО?", "options": ["Защита", "Атака", "Программа", "Тип угрозы"], "correct": 3},
            {"q": "Что делает антивирус?", "options": ["Удаляет вирусы", "Создаёт", "Ломает", "Шифрует"], "correct": 0},
            {"q": "Что такое VPN?", "options": ["Защита", "Игра", "Вирус", "Файл"], "correct": 0},
            {"q": "Что такое пароль?", "options": ["Ключ", "Вирус", "Файл", "Игра"], "correct": 0},
            {"q": "Что такое 2FA?", "options": ["Доп защита", "Файл", "Вирус", "Пароль"], "correct": 0},
        ]

        questions = random.sample(all_questions, 5)

    elif course.title and "Социальная" in course.title:

        content = "Проверьте знания по социальной инженерии"

        all_questions = [
            {"q": "Что такое социальная инженерия?", "options": ["Метод защиты", "Метод обмана", "Шифрование", "Протокол"], "correct": 1},
            {"q": "Что делает хакер?", "options": ["Защищает", "Обманывает", "Обновляет", "Шифрует"], "correct": 1},
            {"q": "Что такое фишинг?", "options": ["Атака", "Игра", "Файл", "VPN"], "correct": 0},
            {"q": "Что такое спам?", "options": ["Письма", "Защита", "Файл", "Игра"], "correct": 0},
        ]

        questions = random.sample(all_questions, 4)

    else:
        questions = []
        content = "Тест отсутствует"

    return templates.TemplateResponse("course_detail.html", {
        "request": request,
        "course": course,
        "questions": questions,
        "content": content
    })

# проверка теста
@app.post("/submit_test", response_class=HTMLResponse)
async def submit_test(request: Request, db: Session = Depends(get_db)):
    form = dict(await request.form())

    print("FORM:", form)
    user_id = request.cookies.get("user_id")

    user = db.query(models.User).filter(
        models.User.id == int(user_id)
    ).first()

    if not user:
        return RedirectResponse(url="/login")

    username = user.username

    print("USERNAME:", username)  
    course_id = int(form.get("course_id"))

    score = 0
    total = 0

    i = 0
    while True:
        user_answer = form.get(f"q{i}")
        correct_answer = form.get(f"correct{i}")

        if correct_answer is None:
            break

        total += 1

        if user_answer is not None and int(user_answer) == int(correct_answer):
            score += 1

        i += 1

    result = models.Result(
        username=username,
        course_id=course_id,
        score=score,
        total=total
    )

    db.add(result)
    db.commit()
    db.refresh(result)

    course = db.query(models.Course).filter(models.Course.id == course_id).first()

    return templates.TemplateResponse("result.html", {
        "request": request,
        "score": score,
        "total": total,
        "result_id": result.id,
        "course": course
    })

# скачать сертификат о прохождении курса
@app.get("/certificate/{result_id}")
def download_certificate(request: Request, result_id: int, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")

    if not user_id:
        return RedirectResponse(url="/login")

    user = db.query(models.User).filter(
        models.User.id == int(user_id)
    ).first()

    if not user:
        return RedirectResponse(url="/login")

    username = user.username

    if not username:
        return RedirectResponse(url="/login")

    result = db.query(models.Result).filter(models.Result.id == result_id).first()

    if not result or result.username != username:
        raise HTTPException(status_code=404, detail="Сертификат не найден")

    if not result.total or result.score < result.total * 0.7:
        raise HTTPException(status_code=403, detail="Курс не пройден — сертификат недоступен")

    course = db.query(models.Course).filter(models.Course.id == result.course_id).first()
    course_title = course.title if course else "Курс"

    pdf_bytes = generate_certificate(
        username=username,
        course_title=course_title,
        score=result.score,
        total=result.total,
        result_id=result.id
    )

    safe_filename = f"certificate_{result.id}.pdf"
    encoded_filename = quote(f"Сертификат_{course_title}_{username}.pdf")

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f'attachment; filename="{safe_filename}"; '
                f"filename*=UTF-8''{encoded_filename}"
            )
        }
    )
# регистрация
@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
def register_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    db: Session = Depends(get_db)
):
    existing_user = db.query(models.User).filter(models.User.username == username).first()

    if existing_user:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Пользователь уже существует"
        })
    hashed = hash_password(password)

    user = models.User(
        username=username,
        password=hashed,
        role=role
    )

    db.add(user)
    db.commit()

    return templates.TemplateResponse("success.html", {"request": request})

# личный кабинет
@app.get("/profile", response_class=HTMLResponse)
def profile(
    request: Request,
    db: Session = Depends(get_db)
):
    user_id = request.cookies.get("user_id")

    if not user_id:
        return RedirectResponse(url="/login")

    user = db.query(models.User).filter(
        models.User.id == int(user_id)
    ).first()

    if not user:
        return RedirectResponse(url="/login")

    results = db.query(models.Result).filter(
        models.Result.username == user.username
    ).all()

    courses_by_id = {
        c.id: c.title
        for c in db.query(models.Course).all()
    }

    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "user": user,
            "results": results,
            "courses_by_id": courses_by_id,
            "active": "profile"
        }
    )

def seed_courses():
    db = SessionLocal()

    if not db.query(models.Course).filter(models.Course.title == "Основы кибербезопасности").first():
        courses = [
            models.Course(
                title="Основы кибербезопасности",
                description="Базовые понятия, угрозы и защита"
            ),
            models.Course(
                title="Социальная инженерия",
                description="Как хакеры обманывают людей"
            )
        ]

        db.add_all(courses)
        db.commit()

    db.close()


seed_courses()