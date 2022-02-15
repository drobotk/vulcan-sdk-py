from asyncio import get_event_loop
from vulcan_scraper import VulcanWeb
from vulcan_scraper.error import BadCredentialsException
from pytest import raises
from pytest_asyncio import fixture


FAKELOG_HOST: str = "fakelog.cf"
FAKELOG_EMAIL: str = "jan@fakelog.cf"
FAKELOG_PASSWD: str = "jan123"


@fixture(scope="module")
def event_loop():
    return get_event_loop()


@fixture(scope="module")
async def client():
    v = VulcanWeb(host=FAKELOG_HOST, email=" ", password=" ")
    async with v:
        yield v


async def test_login_logout(client: VulcanWeb):
    client.email = "example@example.com"
    client.password = "example"

    with raises(BadCredentialsException):
        await client.login()

    assert not client.logged_in

    client.email = FAKELOG_EMAIL
    client.password = FAKELOG_PASSWD

    await client.login()
    assert client.logged_in

    await client.logout()
    assert not client.logged_in


async def test_students(client: VulcanWeb):
    client.email = FAKELOG_EMAIL
    client.password = FAKELOG_PASSWD

    await client.login()
    assert client.logged_in

    students = await client.get_students()
    assert client.students is students
    assert len(students) == 24

    student = students[0]
    assert student.id == 1
    assert student.register_id == 15
    assert student.first_name == "Jan"
    assert student.middle_name == "Marek"
    assert student.last_name == "Kowalski"
    assert student.school_id in ("123456", "123457", "123458")
    assert student.school_name == "Publiczna szkoła Wulkanowego nr 1 w fakelog.cf"
    assert student.school_abbreviation == "Fake123456"
    assert student.year == 2018
    assert student.level == 4
    assert student.class_symbol == "4A"
    assert student.full_name_with_year == "4A 2018 - Jan Kowalski"
    assert str(student) == "4A 2018 - Jan Kowalski"
