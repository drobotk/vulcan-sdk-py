from datetime import datetime
from vulcan_scraper.timetable import parse_lesson

PATH = "resources/uczen/timetable"
HEADER = "1<br />08:00<br />08:45"


def test_1div_normal():
    with open(f"{PATH}/1div-normal.html") as f:
        text = f.read()

    lesson = parse_lesson(datetime.now(), HEADER, text)

    assert lesson.number == 1
    assert lesson.subject == "Historia Memów"
    assert lesson.room == "21"
    assert lesson.teacher == "Mike Oxlong"
    assert lesson.group == ""
    assert lesson.comment == ""
    assert lesson.cancelled is False
    assert lesson.changed is False
    assert lesson.new_subject == ""
    assert lesson.new_room == ""
    assert lesson.new_teacher == ""
    assert lesson.new_group == ""
    assert lesson.new_comment == ""


def test_1div_change():
    with open(f"{PATH}/1div-change-group.html") as f:
        text = f.read()

    lesson = parse_lesson(datetime.now(), HEADER, text)

    assert lesson.number == 1
    assert lesson.subject == "Historia Memów"
    assert lesson.room == "21"
    assert lesson.teacher == "Mike Oxlong"
    assert lesson.group == "A"
    assert lesson.comment == ""
    assert lesson.cancelled is False
    assert lesson.changed is True
    assert lesson.new_subject == ""
    assert lesson.new_room == ""
    assert lesson.new_teacher == "Hugh Jass"
    assert lesson.new_group == ""
    assert lesson.new_comment == ""


def test_2div_inv_empty():
    with open(f"{PATH}/2div-inv-empty.html") as f:
        text = f.read()

    lesson = parse_lesson(datetime.now(), HEADER, text)

    assert lesson.number == 1
    assert lesson.subject == "Historia Memów"
    assert lesson.room == "21"
    assert lesson.teacher == "Mike Oxlong"
    assert lesson.group == ""
    assert lesson.comment == "nieobecność nauczyciela: lekcja odwołana"
    assert lesson.cancelled is False
    assert lesson.changed is True
    assert lesson.new_subject == "Netflix and Chill"
    assert lesson.new_room == "37"
    assert lesson.new_teacher == "Hugh Jass"
    assert lesson.new_group == ""
    assert lesson.new_comment == "przeniesiona z lekcji 7, 2.04.2005"


def test_2div_zas_empty():
    with open(f"{PATH}/2div-zas-empty.html") as f:
        text = f.read()

    lesson = parse_lesson(datetime.now(), HEADER, text)

    assert lesson.number == 1
    assert lesson.subject == "Historia Memów"
    assert lesson.room == "21"
    assert lesson.teacher == "Mike Oxlong"
    assert lesson.group == ""
    assert lesson.comment == ""
    assert lesson.cancelled is False
    assert lesson.changed is True
    assert lesson.new_subject == "Netflix and Chill"
    assert lesson.new_room == "37"
    assert lesson.new_teacher == "Hugh Jass"
    assert lesson.new_group == ""
    assert lesson.new_comment == "przeniesiona z lekcji 7, 2.04.2005"


def test_2div_zas_empty_group():
    with open(f"{PATH}/2div-zas-empty-group.html") as f:
        text = f.read()

    lesson = parse_lesson(datetime.now(), HEADER, text)

    assert lesson.number == 1
    assert lesson.subject == "Historia Memów"
    assert lesson.room == "21"
    assert lesson.teacher == "Mike Oxlong"
    assert lesson.group == "A"
    assert lesson.comment == ""
    assert lesson.cancelled is False
    assert lesson.changed is True
    assert lesson.new_subject == "Netflix and Chill"
    assert lesson.new_room == "37"
    assert lesson.new_teacher == "Hugh Jass"
    assert lesson.new_group == "B"
    assert lesson.new_comment == ""


def test_2div_zas_inv():
    with open(f"{PATH}/2div-zas-inv.html") as f:
        text = f.read()

    lesson = parse_lesson(datetime.now(), HEADER, text)

    assert lesson.number == 1
    assert lesson.subject == "Historia Memów"
    assert lesson.room == "21"
    assert lesson.teacher == "Mike Oxlong"
    assert lesson.group == ""
    assert lesson.comment == "nieobecność nauczyciela: lekcja odwołana"
    assert lesson.cancelled is False
    assert lesson.changed is True
    assert lesson.new_subject == "Netflix and Chill"
    assert lesson.new_room == "37"
    assert lesson.new_teacher == "Hugh Jass"
    assert lesson.new_group == "B"
    assert lesson.new_comment == "przeniesiona z lekcji 7, 2.04.2005"


def test_1div_old_6():
    with open(f"{PATH}/1div-old-6.html") as f:
        text = f.read()

    lesson = parse_lesson(datetime.now(), HEADER, text)

    assert lesson.number == 1
    assert lesson.subject == "Historia Memów"
    assert lesson.room == "21"
    assert lesson.teacher == "Mike Oxlong"
    assert lesson.group == ""
    assert lesson.comment == ""
    assert lesson.cancelled is False
    assert lesson.changed is True
    assert lesson.new_subject == "Netflix and Chill"
    assert lesson.new_room == "37"
    assert lesson.new_teacher == "Hugh Jass"
    assert lesson.new_group == ""
    assert lesson.new_comment == ""


def test_1div_old_7():
    with open(f"{PATH}/1div-old-7.html") as f:
        text = f.read()

    lesson = parse_lesson(datetime.now(), HEADER, text)

    assert lesson.number == 1
    assert lesson.subject == "Historia Memów"
    assert lesson.room == "21"
    assert lesson.teacher == "Mike Oxlong"
    assert lesson.group == ""
    assert lesson.comment == ""
    assert lesson.cancelled is False
    assert lesson.changed is True
    assert lesson.new_subject == "Netflix and Chill"
    assert lesson.new_room == "37"
    assert lesson.new_teacher == "Hugh Jass"
    assert lesson.new_group == ""
    assert lesson.new_comment == ""
