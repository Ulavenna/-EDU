"""
Генерация PDF-сертификата о прохождении курса.
Дизайн выдержан в стиле сайта: тёмный фон, мятный акцент, рамка, печать.
"""

import io
from datetime import date

from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# === Цвета (соответствуют CSS-переменным сайта) ===
BG = HexColor("#1c2526")
SURFACE = HexColor("#243032")
BORDER = HexColor("#3c4d50")
TEXT = HexColor("#e8ece9")
TEXT_MUTED = HexColor("#9fb0ac")
ACCENT = HexColor("#5fd0a8")
ACCENT_DARK = HexColor("#3aa782")

# === Шрифты с поддержкой кириллицы (лежат внутри проекта) ===
FONT_DIR = "static/fonts"
pdfmetrics.registerFont(TTFont("DejaVuSans", f"{FONT_DIR}/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", f"{FONT_DIR}/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DejaVuSerif", f"{FONT_DIR}/DejaVuSerif.ttf"))
pdfmetrics.registerFont(TTFont("DejaVuSerif-Bold", f"{FONT_DIR}/DejaVuSerif-Bold.ttf"))

MONTHS_RU = [
    "", "января", "февраля", "марта", "апреля", "мая", "июня",
    "июля", "августа", "сентября", "октября", "ноября", "декабря"
]


def _format_date_ru(d: date) -> str:
    return f"{d.day} {MONTHS_RU[d.month]} {d.year} г."


def generate_certificate(
    username: str,
    course_title: str,
    score: int,
    total: int,
    result_id: int,
    issue_date: date | None = None,
) -> bytes:
    """Создаёт PDF-сертификат и возвращает его как bytes."""

    issue_date = issue_date or date.today()
    percent = round((score / total * 100), 1) if total else 0

    buffer = io.BytesIO()
    page_size = landscape(A4)
    c = canvas.Canvas(buffer, pagesize=page_size)
    width, height = page_size

    # --- Фон ---
    c.setFillColor(BG)
    c.rect(0, 0, width, height, fill=1, stroke=0)

    # --- Внешняя рамка (акцент) ---
    margin = 14 * mm
    c.setStrokeColor(ACCENT)
    c.setLineWidth(2.2)
    c.rect(margin, margin, width - 2 * margin, height - 2 * margin, fill=0, stroke=1)

    # --- Внутренняя тонкая рамка ---
    inner_margin = margin + 6 * mm
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.8)
    c.rect(inner_margin, inner_margin, width - 2 * inner_margin, height - 2 * inner_margin, fill=0, stroke=1)

    # --- Декоративные уголки ---
    corner = 9 * mm
    c.setStrokeColor(ACCENT)
    c.setLineWidth(1.4)
    for x_base, y_base, dx, dy in [
        (margin, height - margin, 1, -1),
        (width - margin, height - margin, -1, -1),
        (margin, margin, 1, 1),
        (width - margin, margin, -1, 1),
    ]:
        c.line(x_base, y_base, x_base + dx * corner, y_base)
        c.line(x_base, y_base, x_base, y_base + dy * corner)

    center_x = width / 2

    # --- Логотип / щит (рисуем векторно, без эмодзи-шрифтов) ---
    shield_y = height - margin - 20 * mm
    shield_w = 9 * mm
    shield_h = 11 * mm
    sx, sy = center_x, shield_y

    c.saveState()
    p = c.beginPath()
    p.moveTo(sx, sy + shield_h * 0.55)
    p.lineTo(sx - shield_w / 2, sy + shield_h * 0.30)
    p.lineTo(sx - shield_w / 2, sy - shield_h * 0.45)
    p.curveTo(sx - shield_w / 2, sy - shield_h * 0.75,
              sx - shield_w / 4, sy - shield_h * 0.95,
              sx, sy - shield_h * 1.0)
    p.curveTo(sx + shield_w / 4, sy - shield_h * 0.95,
              sx + shield_w / 2, sy - shield_h * 0.75,
              sx + shield_w / 2, sy - shield_h * 0.45)
    p.lineTo(sx + shield_w / 2, sy + shield_h * 0.30)
    p.close()
    c.setFillColor(ACCENT)
    c.setStrokeColor(ACCENT)
    c.setLineWidth(0.6)
    c.drawPath(p, fill=1, stroke=1)

    # галочка внутри щита
    c.setStrokeColor(BG)
    c.setLineWidth(1.4)
    c.setLineCap(1)
    c.setLineJoin(1)
    check = c.beginPath()
    check.moveTo(sx - shield_w * 0.22, sy - shield_h * 0.08)
    check.lineTo(sx - shield_w * 0.04, sy - shield_h * 0.28)
    check.lineTo(sx + shield_w * 0.28, sy + shield_h * 0.12)
    c.drawPath(check, fill=0, stroke=1)
    c.restoreState()

    # --- Бренд ---
    c.setFont("DejaVuSans-Bold", 13)
    c.setFillColor(TEXT_MUTED)
    c.drawCentredString(center_x, shield_y - shield_h - 4 * mm, "CYBEREDU  •  CYBERSECURITY LMS")

    # --- Заголовок ---
    title_y = shield_y - shield_h - 17 * mm
    c.setFont("DejaVuSerif-Bold", 30)
    c.setFillColor(TEXT)
    c.drawCentredString(center_x, title_y, "СЕРТИФИКАТ")

    c.setFont("DejaVuSans", 11)
    c.setFillColor(TEXT_MUTED)
    c.drawCentredString(center_x, title_y - 7 * mm, "О ЗАВЕРШЕНИИ КУРСА")

    # --- Разделительная линия с акцентом ---
    line_y = title_y - 13 * mm
    line_half = 28 * mm
    c.setStrokeColor(ACCENT)
    c.setLineWidth(1.2)
    c.line(center_x - line_half, line_y, center_x + line_half, line_y)

    # --- "Настоящим подтверждается, что" ---
    sub_y = line_y - 11 * mm
    c.setFont("DejaVuSans", 11.5)
    c.setFillColor(TEXT_MUTED)
    c.drawCentredString(center_x, sub_y, "Настоящим подтверждается, что")

    # --- Имя пользователя ---
    name_y = sub_y - 13 * mm
    c.setFont("DejaVuSerif-Bold", 26)
    c.setFillColor(ACCENT)
    c.drawCentredString(center_x, name_y, username)

    # --- подложка под именем ---
    name_width = c.stringWidth(username, "DejaVuSerif-Bold", 26)
    c.setStrokeColor(ACCENT_DARK)
    c.setLineWidth(0.8)
    c.line(center_x - name_width / 2 - 4 * mm, name_y - 4 * mm,
           center_x + name_width / 2 + 4 * mm, name_y - 4 * mm)

    # --- "успешно завершил(а) курс" ---
    desc_y = name_y - 13 * mm
    c.setFont("DejaVuSans", 11.5)
    c.setFillColor(TEXT_MUTED)
    c.drawCentredString(center_x, desc_y, "успешно завершил(а) учебный курс")

    # --- Название курса ---
    course_y = desc_y - 10 * mm
    c.setFont("DejaVuSerif-Bold", 18)
    c.setFillColor(TEXT)
    c.drawCentredString(center_x, course_y, f"«{course_title}»")

    # --- Результат теста ---
    result_y = course_y - 11 * mm
    c.setFont("DejaVuSans-Bold", 12)
    c.setFillColor(ACCENT)
    c.drawCentredString(center_x, result_y, f"Результат теста: {score} / {total}  ({percent}%)")

    # --- Нижняя часть: дата слева, подпись/печать справа ---
    bottom_y = inner_margin + 14 * mm

    # Дата
    date_x = inner_margin + 26 * mm
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.8)
    c.line(date_x - 22 * mm, bottom_y, date_x + 22 * mm, bottom_y)
    c.setFont("DejaVuSans", 9.5)
    c.setFillColor(TEXT_MUTED)
    c.drawCentredString(date_x, bottom_y - 5 * mm, "Дата выдачи")
    c.setFont("DejaVuSans-Bold", 10.5)
    c.setFillColor(TEXT)
    c.drawCentredString(date_x, bottom_y + 2.5 * mm, _format_date_ru(issue_date))

    # Номер сертификата
    cert_x = center_x
    c.setFont("DejaVuSans", 9.5)
    c.setFillColor(TEXT_MUTED)
    c.drawCentredString(cert_x, bottom_y - 5 * mm, "Номер сертификата")
    c.setFont("DejaVuSans-Bold", 10.5)
    c.setFillColor(TEXT)
    c.drawCentredString(cert_x, bottom_y + 2.5 * mm, f"CE-{result_id:06d}")

    # Печать / подпись платформы
    seal_x = width - inner_margin - 26 * mm
    c.setStrokeColor(ACCENT)
    c.setLineWidth(1.6)
    c.circle(seal_x, bottom_y + 1 * mm, 11 * mm, fill=0, stroke=1)
    c.setFont("DejaVuSans-Bold", 8.5)
    c.setFillColor(ACCENT)
    c.drawCentredString(seal_x, bottom_y + 3 * mm, "CYBEREDU")
    c.setFont("DejaVuSans", 7)
    c.drawCentredString(seal_x, bottom_y - 1.5 * mm, "VERIFIED")

    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer.read()
