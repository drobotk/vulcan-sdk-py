import asyncio
from datetime import datetime

from vulcan_scraper import VulcanWeb


async def main():
    vulcan = VulcanWeb(host="", email="", password="", symbol="")
    async with vulcan:
        await vulcan.login()

        students = await vulcan.get_students()
        student = students[0]

        # jakikolwiek dzień danego tygodnia; można użyć datetime.now()
        date = datetime(2022, 1, 12)

        timetable = await student.get_timetable(date)
        for day in timetable.days:
            print()
            print("\n".join([repr(l) for l in day.lessons]))


if __name__ == "__main__":
    asyncio.run(main())
