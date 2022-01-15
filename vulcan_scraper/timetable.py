import re
from dataclasses import dataclass, field
from datetime import datetime, time
from bs4 import BeautifulSoup, element

from .model import TimetableResponse
from .utils import tag_own_textcontent, sub_after, sub_before


@dataclass
class TimetableLesson:
    number: int
    start: datetime = field(repr=False)
    end: datetime = field(repr=False)
    subject: str = ""
    room: str = ""
    teacher: str = ""
    group: str = ""
    comment: str = ""
    cancelled: bool = False
    changed: bool = False
    new_subject: str = ""
    new_room: str = ""
    new_teacher: str = ""
    new_group: str = ""
    new_comment: str = ""


@dataclass
class TimetableDay:
    date: datetime
    lessons: list[TimetableLesson]

    def __str__(self) -> str:
        return self.date.strftime("%A, %d %B %Y")


CLASS_CANCELLED: str = "x-treelabel-inv"
CLASS_CHANGED: str = "x-treelabel-zas"
OLDFORMAT_CLASS_CHANGES: str = "x-treelabel-rlz"

re_substitute_teacher = re.compile(r"\(zastępstwo: ([^,]+?)\)")
re_moved_to = re.compile(r"\(przeniesiona na lekcję (\d+), ([0-9\.]+?)\)")
re_oldformat_changes = re.compile(r"\(zastępstwo: (.+?), sala (.+?)\)")


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

        # vulcan bug: replaced teachers change to the substitute teachers after the lesson happens
        if lesson.teacher == teacher:  
            lesson.teacher = ""

    teachers = []
    rooms = []
    for m in re_oldformat_changes.finditer(comment):
        teachers.append(m.group(1))
        rooms.append(m.group(2))
        comment = comment.replace(m.group(), "", 1)

    if teachers and rooms:
        teacher = ", ".join(teachers)
        room = ", ".join(rooms)
        if teacher != lesson.teacher:
            lesson.new_teacher = teacher
            lesson.changed = True

        if room != lesson.room:
            lesson.new_room = room
            lesson.changed = True

    return comment.strip(" ()")


def parse_lesson_simple(
    lesson: TimetableLesson,
    divtext: str,
    namespan: element.Tag,
    roomspan: element.Tag,
    teacherspan: element.Tag,
):
    lesson.subject = sub_before(namespan.text, "[").strip()
    lesson.group = sub_after(namespan.text, lesson.subject, "").strip(" []")
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

    split = header.split("<br />")
    number = int(split[0])
    start = datetime.combine(date.date(), time.fromisoformat(split[1]))
    end = datetime.combine(date.date(), time.fromisoformat(split[2]))

    lesson = TimetableLesson(number=number, start=start, end=end)

    if len(divs) == 1:
        div = divs[0]
        divtext = tag_own_textcontent(div)
        spans = div.select("span")
        if len(spans) == 3:
            parse_lesson_simple(lesson, divtext, spans[0], spans[1], spans[2])
        elif len(spans) == 4:
            if OLDFORMAT_CLASS_CHANGES in spans[3]["class"]:
                parse_lesson_simple(
                    lesson, spans[3].text.strip(), spans[0], spans[1], spans[2]
                )
            else:
                parse_lesson_simple(lesson, divtext, spans[0], spans[2], spans[3])
        else:
            lesson.subject = f"TODO: {len(spans)} span timetable entry"

    elif len(divs) == 2:
        old = divs[0]
        divtext = tag_own_textcontent(old)
        spans = old.select("span")
        if len(spans) == 3:
            parse_lesson_simple(lesson, divtext, spans[0], spans[1], spans[2])
        elif len(spans) == 4:
            parse_lesson_simple(lesson, divtext, spans[0], spans[2], spans[3])
        else:
            lesson.subject = f"TODO: 2 div {len(spans)} span timetable entry"

        new_lesson = TimetableLesson(number=0, start=None, end=None)
        new = divs[1]
        divtext = tag_own_textcontent(new)
        spans = new.select("span")
        if len(spans) == 3:
            parse_lesson_simple(new_lesson, divtext, spans[0], spans[1], spans[2])
        elif len(spans) == 4:
            parse_lesson_simple(new_lesson, divtext, spans[0], spans[2], spans[3])
        else:
            new_lesson.subject = f"TODO: 2 div {len(spans)} span timetable entry"

        if new_lesson.subject and new_lesson.subject != lesson.subject:
            lesson.new_subject = new_lesson.subject
        if new_lesson.room and new_lesson.room != lesson.room:
            lesson.new_room = new_lesson.room
        if new_lesson.teacher and new_lesson.teacher != lesson.teacher:
            lesson.new_teacher = new_lesson.teacher
        if new_lesson.group and new_lesson.group != lesson.group:
            lesson.new_group = new_lesson.group
        if new_lesson.comment and new_lesson.comment != lesson.comment:
            lesson.new_comment = new_lesson.comment

        lesson.cancelled = False
        lesson.changed = True
    else:
        lesson.subject = f"TODO: {len(divs)} div timetable entry"

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
