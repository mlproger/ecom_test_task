from typing import Iterable, Dict, Tuple
from typing import List

from app.api_v1 import db


async def upsert_students(conn, items: Iterable[Tuple[str, str]]) -> Dict[str, int]:
    """
    Вставляет студентов по списку кортежей (full_name, group_name), 

    Возвращает словарь {full_name: id} для всех переданных имён.
    """
    items_list = list(dict.fromkeys(items))  # убрать дубликаты, сохранить порядок
    if not items_list:
        return {}

    insert_sql = "INSERT INTO students (full_name, group_name) VALUES($1, $2) ON CONFLICT (full_name) DO NOTHING"
    await conn.executemany(insert_sql, items_list)

    # Получаем id для всех запрошенных имён
    names = [name for name, _ in items_list]
    select_sql = "SELECT id, full_name FROM students WHERE full_name = ANY($1::text[])"
    rows = await conn.fetch(select_sql, names)

    result: Dict[str, int] = {r['full_name']: r['id'] for r in rows}
    return result


async def get_students_with_more_than_n_twos(n: int) -> List[Dict]:
    """
    Возвращает список словарей {full_name, count_twos} для студентов,
    у которых количество оценок 2 больше чем n.
    """
    query = """
        SELECT s.full_name, t.count_twos
        FROM (
            SELECT g.student_id, COUNT(*)::int AS count_twos
            FROM grades g
            WHERE g.grade = 2
            GROUP BY g.student_id
            HAVING COUNT(*) > $1
        ) t
        JOIN students s ON s.id = t.student_id
        ORDER BY t.count_twos DESC, s.full_name
    """
    rows = await db.fetch(query, n)
    return [{"full_name": r["full_name"], "count_twos": r["count_twos"]} for r in rows]
async def get_students_with_less_than_n_twos(n: int) -> List[Dict]:
    # временная заглушка — не используется
    raise RuntimeError("unused")


async def get_students_with_more_than_3_twos() -> List[Dict]:
    """
    Возвращает студентов, у которых количество оценок 2 больше 3.
    """
    query = """
    SELECT s.full_name, t.count_twos
    FROM (
      SELECT g.student_id, COUNT(*)::int AS count_twos
      FROM grades g
      WHERE g.grade = 2
      GROUP BY g.student_id
      HAVING COUNT(*) > 3
    ) t
    JOIN students s ON s.id = t.student_id
    ORDER BY t.count_twos DESC, s.full_name
    """
    rows = await db.fetch(query)
    return [{"full_name": r["full_name"], "count_twos": r["count_twos"]} for r in rows]


async def get_students_with_less_than_5_twos() -> List[Dict]:
    """
    Возвращает студентов, у которых количество оценок 2 меньше 5 
    """
    query = """
    SELECT s.full_name, t.count_twos
    FROM (
      SELECT g.student_id, COUNT(*)::int AS count_twos
      FROM grades g
      WHERE g.grade = 2
      GROUP BY g.student_id
      HAVING COUNT(*) < 5 AND COUNT(*) > 0
    ) t
    JOIN students s ON s.id = t.student_id
    ORDER BY t.count_twos DESC, s.full_name
    """
    rows = await db.fetch(query)
    return [{"full_name": r["full_name"], "count_twos": r["count_twos"]} for r in rows]
