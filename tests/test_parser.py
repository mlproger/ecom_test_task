"""
Unit-тесты для CSV-парсера `parse_and_validate_semicolon_csv`.

Покрывают основные сценарии парсинга и валидации входного CSV:
- корректный вход без заголовка;
- вход с заголовком и пустыми строками;
- сбор и возвращение ошибок для некорректных строк;
- обработка данных не в кодировке UTF-8.
"""

import pytest
from app.api_v1.Grades import service
from app.api_v1.Grades.schemas import ValidationErrorItem


def test_parse_valid_rows_without_header():
    # Проверяет корректный разбор строк без заголовка
    csv_bytes = (
        "01.09.2023;101Б;Иванов Иван;3\n"
        "02.09.2023;102А;Петров Пётр;2\n"
    ).encode("utf-8")
    parsed, errors = service.parse_and_validate_semicolon_csv(csv_bytes)
    assert errors == []
    assert len(parsed) == 2
    assert parsed[0]["full_name"] == "Иванов Иван"
    assert parsed[1]["grade"] == 2


def test_parse_with_header_and_blank_lines():
    # Заголовок и пустые строки должны игнорироваться
    csv_bytes = (
        "Дата;Номер группы;ФИО;Оценка\n\n"
        "01.09.2023;101Б;Сидоров С.;5\n"
    ).encode("utf-8")
    parsed, errors = service.parse_and_validate_semicolon_csv(csv_bytes)
    assert errors == []
    assert len(parsed) == 1
    assert parsed[0]["full_name"].startswith("Сидоров")


def test_parse_invalid_rows_collects_errors():
    # Некорректные строки должны попадать в список ошибок, корректных parsed быть не должно
    csv_bytes = (
        "01.09.2023;BAD;NoName;6\n"
        "bad-date;101Б;Иван;4\n"
    ).encode("utf-8")
    parsed, errors = service.parse_and_validate_semicolon_csv(csv_bytes)
    assert len(parsed) == 0
    assert len(errors) == 2
    assert isinstance(errors[0], ValidationErrorItem)


def test_parse_non_utf8_returns_error():
    # Некорректная кодировка должна приводить к одной ошибке с row=0
    content = b"\x80\x81\x82"
    parsed, errors = service.parse_and_validate_semicolon_csv(content)
    assert parsed == []
    assert len(errors) == 1
    assert errors[0].row == 0
    assert "UTF-8" in errors[0].detail
