import re
from dataclasses import dataclass
from datetime import datetime, date, time
from bs4 import BeautifulSoup, element

from .model import TimetableResponse
from .utils import tag_own_textcontent, sub_after, sub_before


@dataclass
class TimetableLesson:
    number: int = None
    start: datetime = None
    end: datetime = None
    name: str = None
    room: str = None
    teacher: str = None
    group: str = None
    comment: str = None
    cancelled: bool = False
    changed: bool = False
    new_name: str = None
    new_room: str = None
    new_teacher: str = None
    new_comment: str = None


@dataclass
class TimetableDay:
    date: datetime
    lessons: list[TimetableLesson]


CLASS_CANCELLED: str = "x-treelabel-inv"
CLASS_CHANGED: str = "x-treelabel-zas"

re_substitute_teacher = re.compile(r"\(zastępstwo: (.+?)\)")


def process_lesson_comment(lesson: TimetableLesson, comment: str) -> str:
    teachers = []
    for m in re_substitute_teacher.finditer(comment):
        name = " ".join(m.group(1).split(" ")[::-1])
        teachers.append(name)
        comment = comment.replace(m.group(), "", 1)

    if teachers:
        teacher = ", ".join(teachers)
        lesson.new_teacher = teacher
        lesson.changed = True

    return comment.strip(" ()")


def parse_lesson_simple(
    lesson: TimetableLesson,
    divtext: str,
    namespan: element.Tag,
    roomspan: element.Tag,
    teacherspan: element.Tag,
):
    lesson.name = sub_before(namespan.text, "[").strip()
    lesson.group = sub_after(namespan.text, lesson.name, "").strip(" []")
    lesson.room = roomspan.text.strip()
    lesson.teacher = teacherspan.text.strip()

    if (
        CLASS_CANCELLED in namespan["class"]
        and CLASS_CANCELLED in roomspan["class"]
        and CLASS_CANCELLED in teacherspan["class"]
    ):
        lesson.cancelled = True

    if (
        CLASS_CHANGED in namespan["class"]
        and CLASS_CHANGED in roomspan["class"]
        and CLASS_CHANGED in teacherspan["class"]
    ):
        lesson.changed = True

    lesson.comment = process_lesson_comment(lesson, divtext)


def parse_lesson(date: datetime, header: str, text: str) -> TimetableLesson:
    soup = BeautifulSoup(text, "lxml")
    divs = soup.select("div")
    if not divs:
        return

    lesson = TimetableLesson()

    if len(divs) == 1:
        div = divs[0]
        divtext = tag_own_textcontent(div)
        spans = div.select("span")
        if len(spans) == 3:
            parse_lesson_simple(lesson, divtext, spans[0], spans[1], spans[2])
        elif len(spans) == 4:
            parse_lesson_simple(lesson, divtext, spans[0], spans[2], spans[3])
        else:
            lesson.name = f"TODO: {len(spans)} span timetable entry"

    else:
        lesson.name = f"TODO: {len(divs)} div timetable entry"

    split = header.split("<br />")
    lesson.number = int(split[0])

    start = time.fromisoformat(split[1])
    end = time.fromisoformat(split[2])
    lesson.start = datetime.combine(date.date(), start)
    lesson.end = datetime.combine(date.date(), end)

    return lesson


class Timetable:
    def __init__(self, data: TimetableResponse):
        self.days: list[TimetableDay] = []

        for i, h in enumerate(data.headers[1:]):  # first column is lesson times
            date = h.text.split("<br />")[1]
            date = datetime.strptime(date, "%d.%m.%Y")
            day = TimetableDay(date=date, lessons=[])
            for r in data.rows:
                lesson = parse_lesson(date, r[0], r[i + 1])
                if lesson:
                    day.lessons.append(lesson)

            self.days.append(day)
