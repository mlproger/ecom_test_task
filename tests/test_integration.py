"""
Интеграционный тест: загружает CSV в базу и проверяет аналитические запросы.
"""

import pytest
from app.api_v1 import db
from app.api_v1.Grades import service
from app.api_v1.Students import crud as students_crud


@pytest.mark.asyncio
async def test_load_csv_and_query():
    # Инициализация пула подключений к БД
    await db.init_db_pool()
    try:
        # Тестовый CSV: 4 оценки у Иванова и 2 у Петрова (все двойки)
        csv = (
            "01.09.2023;101Б;Иванов Иван;2\n"
            "02.09.2023;101Б;Иванов Иван;2\n"
            "03.09.2023;101Б;Иванов Иван;2\n"
            "04.09.2023;101Б;Иванов Иван;2\n"
            "05.09.2023;101Б;Петров Пётр;2\n"
            "06.09.2023;101Б;Петров Пётр;2\n"
        ).encode("utf-8")

        # Загружаем данные через сервис загрузки CSV
        records_loaded, students_count, errors = await service.load_grades(csv)

        # Ожидаем отсутствие ошибок и загрузку 6 строк
        assert errors == [] or len(errors) == 0
        assert records_loaded == 6
        assert students_count >= 2

        # Выполняем аналитические запросы
        more = await students_crud.get_students_with_more_than_3_twos()
        less = await students_crud.get_students_with_less_than_5_twos()

        names_more = {r["full_name"] for r in more}
        names_less = {r["full_name"] for r in less}

        # Проверяем, что Иванов попал в список с >3 двоек,
        # а Петров — в список с <5 двоек
        assert "Иванов Иван" in names_more
        assert "Петров Пётр" in names_less

    finally:
        # Очистка данных после теста — аккуратно, если используете общий БД
        pool = db.get_pool()
        async with pool.acquire() as conn:
            await conn.execute("TRUNCATE grades, students RESTART IDENTITY CASCADE")
        await db.close_db_pool()
