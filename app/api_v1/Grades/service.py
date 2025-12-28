import csv
import re
from datetime import datetime, date
from typing import List, Tuple, Dict
from typing import List, Tuple, Dict
from app.api_v1 import db
from app.api_v1.Grades import crud
from app.api_v1.Students import crud as students_crud
from app.api_v1.settings.config import Config
from app.api_v1.Grades.schemas import ValidationErrorItem



def _parse_date(s: str, row: int) -> datetime.date:
    """
    Парсит строку с датой в формате DD.MM.YYYY и возвращает объект date.

    Валидация:
    - поле не пустое;
    - соответствует формату `Config.DATE_FMT`;
    - дата не в будущем;
    - год в разумном диапазоне (1900..2100).

    При ошибке выбрасывает ValueError с пояснением.
    """
    s = s.strip()
    if not s:
        raise ValueError("Пустая дата")
    try:
        d = datetime.strptime(s, Config.DATE_FMT).date()
    except Exception:
        raise ValueError(f"Неверный формат даты, ожидалось DD.MM.YYYY: '{s}'")
    today = date.today()
    if d > today:
        raise ValueError(f"Дата в будущем: {s}")
    if not (1900 <= d.year <= 2100):
        raise ValueError(f"Неверный год в дате: {d.year}")
    return d

def _validate_group(s: str) -> str:
    """
    Валидирует номер группы.

    Ожидает строку вида три цифры + одна буква (например `101Б`).
    Возвращает нормализованную (верхний регистр) строку или бросает ValueError.
    """
    s = s.strip().upper()
    if not s:
        raise ValueError("Пустой номер группы")
    if not Config.GROUP_RE.match(s):
        raise ValueError(f"Номер группы не соответствует шаблону 'DDDХ' (например 101Б): '{s}'")
    return s

def _validate_fullname(s: str) -> str:
    """
    Валидирует ФИО: нормализует пробелы и проверяет, что указаны как минимум фамилия и имя.

    Возвращает нормализованную строку ФИО или бросает ValueError.
    """
    s = " ".join(s.split())
    if not s:
        raise ValueError("Пустое ФИО")
    parts = s.split(" ")
    if len(parts) < 2:
        raise ValueError("ФИО должно содержать минимум фамилию и имя")
    return s

def _validate_grade(s: str) -> int:
    """
    Валидирует поле оценки: ожидается целое число 1..5.

    Возвращает целое значение оценки или бросает ValueError при неверном формате/диапазоне.
    """
    s = s.strip()
    if not s:
        raise ValueError("Пустая оценка")
    if not re.fullmatch(r'\d+', s):
        raise ValueError("Оценка должна быть целым числом")
    g = int(s)
    if not (1 <= g <= 5):
        raise ValueError("Оценка должна быть в диапазоне 1..5")
    return g

def parse_and_validate_semicolon_csv(content: bytes) -> Tuple[List[Dict], List[ValidationErrorItem]]:
    """
    Разбирает CSV с разделителем `;` и выполняет валидацию каждой строки.

    Логика:
    - пытается декодировать содержимое как UTF-8;
    - определяет, есть ли заголовок (по ключевым словам) — если есть, пропускает первую строку;
    - для каждой строки проверяет количество колонок, дату, номер группы, ФИО и оценку;
    - возвращает кортеж (parsed_rows, errors), где parsed_rows — список корректных записей,
      а errors — список `ValidationErrorItem` с номерами строк и описанием ошибок.
    """
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return [], [ValidationErrorItem(row=0, detail="Файл не в кодировке UTF-8")]

    lines = [ln for ln in text.splitlines() if ln.strip() != ""]
    if not lines:
        return [], [ValidationErrorItem(row=0, detail="Пустой файл")]

    reader = csv.reader(lines, delimiter=';')
    rows = list(reader)
    if not rows:
        return [], [ValidationErrorItem(row=0, detail="Отсутствует заголовок или данные")]

    first = [h.strip().lower() for h in rows[0]]

    has_header = False
    if len(first) >= 4 and (first[0] == "дата" or "фио" in first or "фамилия" in first):
        has_header = True

    parsed = []
    errors: List[ValidationErrorItem] = []

    data_start = 2 if has_header else 1
    data_rows = rows[1:] if has_header else rows

    for idx, row in enumerate(data_rows, start=data_start):
        if len(row) < 4:
            errors.append(ValidationErrorItem(row=idx, detail="Мало колонок в строке"))
            continue
        date_s, group_s, fio_s, grade_s = row[0], row[1], row[2], row[3]
        try:
            d = _parse_date(date_s, idx)
            grp = _validate_group(group_s)
            fio = _validate_fullname(fio_s)
            grade = _validate_grade(grade_s)
        except ValueError as e:
            errors.append(ValidationErrorItem(row=idx, detail=str(e)))
            continue
        parsed.append({"date": d, "group": grp, "full_name": fio, "grade": grade})

    return parsed, errors


async def load_grades(file) -> Tuple[int, int, List[ValidationErrorItem]]:
    """
    Основная функция сервиса: принимает файл (или байты), валидирует строки и
    записывает корректные записи в БД. Возвращает кортеж (records_loaded, students_count, errors).

    Параметры:
    - file: UploadFile или bytes с содержимым CSV;
    """

    if hasattr(file, "read"):
        content = await file.read()
    else:
        content = file

    parsed, errors = parse_and_validate_semicolon_csv(content)

    name_to_group: Dict[str, str] = {}
    for r in parsed:
        if r["full_name"] not in name_to_group:
            name_to_group[r["full_name"]] = r.get("group")
    items = [(n, g) for n, g in name_to_group.items()]

    if parsed:
        pool = db.get_pool()
        async with pool.acquire() as conn:
            async with conn.transaction():
                name_to_id = await students_crud.upsert_students(conn, items)
                grade_rows = [(name_to_id[r["full_name"]], r["date"], r["grade"]) for r in parsed]
                await crud.insert_grades(conn, grade_rows)

    return len(parsed), len(items), errors