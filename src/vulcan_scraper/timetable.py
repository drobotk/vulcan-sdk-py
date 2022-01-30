import re
from dataclasses import dataclass, field
from datetime import datetime, time
from bs4 import BeautifulSoup, element

from .model import TimetableResponse
from .utils import (
    tag_own_textcontent,
    sub_after,
    sub_before,
    get_first,
    reverse_teacher_name,
)


@dataclass
class TimetableLesson:
    _html: str = field(repr=False)

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
class TimetableAdditionalLesson:
    start: datetime
    end: datetime
    subject: str


@dataclass
class TimetableDay:
    date: datetime
    lessons: list[TimetableLesson]
    additionals: list[TimetableAdditionalLesson]
    description: str = ""

    def __str__(self) -> str:
        return self.date.strftime("%A, %d %B %Y")


CLASS_CANCELLED: str = "x-treelabel-inv"
CLASS_CHANGED: str = "x-treelabel-zas"
OLDFORMAT_CLASS_COMMENT: str = "x-treelabel-rlz"

re_substitute_teacher = re.compile(r"\(zastępstwo: (.+?)\)")
re_moved_to = re.compile(r"\(przeniesiona na lekcję (\d+), ([0-9\.]+?)\)")
re_oldformat_changes = re.compile(r"\(zastępstwo: ([^)]+?), sala (.+?)\)")


def parse_lesson_comment(lesson: TimetableLesson, comment: str) -> str:
    teachers = set()
    rooms = set()
    # old format
    for m in re_oldformat_changes.finditer(comment):
        teachers.add(m.group(1))
        rooms.add(m.group(2))
        comment = comment.replace(m.group(), "", 1)

    # current format
    for m in re_substitute_teacher.finditer(comment):
        name = reverse_teacher_name(m.group(1))
        teachers.add(name)
        comment = comment.replace(m.group(), "", 1)

    if teachers:
        teacher = ", ".join(teachers)
        if lesson.teacher != teacher:
            lesson.new_teacher = teacher
            lesson.changed = True

    if rooms:
        room = ", ".join(rooms)
        if lesson.room != room:
            lesson.new_room = room
            lesson.changed = True

    return "; ".join(comment.removeprefix("(").removesuffix(")").split(")("))


def parse_lesson_info(
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

    if re.search(
        r"\d", lesson.teacher
    ):  # HACK: if teacher contains a number, assume its actually the room and flip
        lesson.room, lesson.teacher = lesson.teacher, lesson.room

    if CLASS_CANCELLED in namespan["class"]:
        lesson.cancelled = True
    # if CLASS_CHANGED in namespan["class"]:
    #     lesson.changed = True

    lesson.comment = parse_lesson_comment(lesson, divtext)


def parse_div(lesson: TimetableLesson, divtext: str, spans: list[element.Tag]):
    comment = divtext
    for s in spans.copy():
        if OLDFORMAT_CLASS_COMMENT in s["class"]:
            comment += s.text.strip()
            spans.remove(s)

    if len(spans) == 2:
        parse_lesson_info(lesson, comment, spans[0], spans[1], element.Tag(name="span"))
    elif len(spans) == 3:
        parse_lesson_info(lesson, comment, spans[0], spans[1], spans[2])
    elif len(spans) == 4:
        parse_lesson_info(lesson, comment, spans[0], spans[2], spans[3])
    elif len(spans) == 6 or len(spans) == 8:  # old format changes
        old = (
            (spans[0], spans[1], spans[2])
            if len(spans) == 6
            else (spans[0], spans[2], spans[3])
        )
        new = (
            (spans[3], spans[4], spans[5])
            if len(spans) == 6
            else (spans[4], spans[6], spans[7])
        )
        if CLASS_CANCELLED in new[0]["class"]:  # invert
            old, new = new, old

        parse_lesson_info(lesson, comment, *old)

        new_lesson = TimetableLesson(_html="", number=0, start=None, end=None)
        parse_lesson_info(new_lesson, "", *new)

        if new_lesson.subject and new_lesson.subject != lesson.subject:
            lesson.new_subject = new_lesson.subject
        if new_lesson.room and new_lesson.room != lesson.room:
            lesson.new_room = new_lesson.room
        if new_lesson.teacher and new_lesson.teacher != lesson.teacher:
            lesson.new_teacher = new_lesson.teacher
        if new_lesson.group and new_lesson.group != lesson.group:
            lesson.new_group = new_lesson.group

        lesson.cancelled = False
        lesson.changed = True
    else:
        lesson.subject = f"TODO: {len(spans)} span timetable entry"


def parse_lesson(date: datetime, header: str, text: str) -> TimetableLesson:
    soup = BeautifulSoup(text, "lxml")
    divs = soup.select("div:not([class])")
    if not divs:
        return

    split = header.split("<br />")
    number = int(split[0])
    start = datetime.combine(date.date(), time.fromisoformat(split[1]))
    end = datetime.combine(date.date(), time.fromisoformat(split[2]))

    lesson = TimetableLesson(_html=text, number=number, start=start, end=end)

    if len(divs) == 1:
        div = divs[0]
        divtext = tag_own_textcontent(div)
        spans = div.select("span")
        parse_div(lesson, divtext, spans)

    elif len(divs) == 2:
        old = divs[0]
        new = divs[1]
        old_s = old.select("span")
        new_s = new.select("span")
        if len(old_s) < 2 or len(new_s) < 2:
            lesson.subject = f"TODO: {len(old_s) = }, {len(new_s) = }"
            return lesson

        if (
            CLASS_CANCELLED in new_s[0]["class"] or "(przeniesiona z lekcji" in old.text
        ):  # invert
            old, new = new, old
            old_s, new_s = new_s, old_s

        divtext = tag_own_textcontent(old)

        parse_div(lesson, divtext, old_s)

        new_lesson = TimetableLesson(_html="", number=0, start=None, end=None)
        divtext = tag_own_textcontent(new)

        parse_div(new_lesson, divtext, new_s)

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


def parse_additional_lesson(
    date: datetime, description: str
) -> TimetableAdditionalLesson:
    soup = BeautifulSoup(description, "lxml")
    text = soup.text.strip()
    split = text.split(" ")
    start = datetime.combine(date.date(), time.fromisoformat(split[0]))
    end = datetime.combine(date.date(), time.fromisoformat(split[2]))
    subject = " ".join(split[3:])

    return TimetableAdditionalLesson(start=start, end=end, subject=subject)


class Timetable:
    def __init__(self, data: TimetableResponse):
        self.days: list[TimetableDay] = []

        for i, h in enumerate(data.headers[1:]):  # first column is lesson times
            split = h.text.split("<br />")
            date = datetime.strptime(split[1], "%d.%m.%Y")
            desc = "; ".join(split[2:])
            day = TimetableDay(date=date, lessons=[], additionals=[], description=desc)
            for r in data.rows:
                lesson = parse_lesson(date, r[0], r[i + 1])
                if lesson:
                    day.lessons.append(lesson)

            self.days.append(day)

        for a in data.additionals:
            date = a.header.split(", ")[1]
            date = datetime.strptime(date, "%d.%m.%Y")
            day = get_first(self.days, date=date)
            if not day:
                day = TimetableDay(date=date, lessons=[], additionals=[])
                self.days.append(day)

            for d in a.descriptions:
                lesson = parse_additional_lesson(date, d)
                if lesson:
                    day.additionals.append(lesson)

            day.additionals.sort(key=lambda a: a.start)
