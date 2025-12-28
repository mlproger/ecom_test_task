from typing import List, Tuple
import asyncpg


async def insert_grades(conn: asyncpg.Connection, rows: List[Tuple[int, 'datetime.date', int]]) -> None:
    """Вставляет список оценок в таблицу `grades`.

    Ожидаемый формат строки: (student_id, grade_date, grade).
    Если список пуст — функция возвращает немедленно.
    """
    if not rows:
        return
    # Используем executemany с параметрами — безопасно и эффективно для пакетной вставки
    await conn.executemany("INSERT INTO grades(student_id, grade_date, grade) VALUES($1,$2,$3)", rows)

