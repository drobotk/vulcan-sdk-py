import asyncio
from vulcan_scraper import VulcanWeb


async def main():
    vulcan = VulcanWeb(
        host="fakelog.cf",  # Vulcan e-register host name, eg. "fakelog.cf", "vulcan.net.pl"
        email="jan@fakelog.cf",
        password="jan123",
        # Optional - scraper will attempt to extract symbols from CUFS certificate
        # The symbol might be required if your account is ADFS
        symbol="powiatwulkanowy",
    )
    async with vulcan:
        await vulcan.login()

        # get all students from all schools available on this account
        students = await vulcan.get_students()

        for student in students:
            print(student)

        # use the first student; this will usually be the current year student
        student = students[0]

        # fetching grades of a student for a given period index
        data = await student.get_grades(period=0)

        print("\t--- Grades ---")
        for subject in data.subjects:
            grades = "  ".join([g.entry for g in subject.grades])
            if grades:
                print(f"{subject.subject_name}: {grades}")

        # fetching notes and achievements of a student
        data = await student.get_notes_and_achievements()

        print("\t--- Notes ---")
        for note in data.notes:
            entry = (
                "+"
                if note.category_type == 1
                else "-"
                if note.category_type == 3
                else "#"
            )
            print(f"{entry} {note.category}: {note.content}")

        print("\t--- Achievements ---")
        for achievement in data.achievements:
            print(f"# {achievement}")

        print("\t--- Meetings ---")
        meetings = await student.get_meetings()
        for m in meetings:
            print(f"# {m.date} | {m.title} | {m.topic}")


if __name__ == "__main__":
    asyncio.run(main())
