import asyncio
from vulcan_scraper import VulcanWeb


async def main():
    vulcan = VulcanWeb(
        host="fakelog.cf",  # Vulcan e-register host name, eg. "fakelog.cf", "vulcan.net.pl"
        email="jan@fakelog.cf",
        password="jan123",
        symbol="powiatwulkanowy",  # Optional: scraper will attempt to extract symbols from CUFS certificate
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

        print("--- Grades ---")
        for subject in data.subjects:
            grades = "  ".join([g.entry for g in subject.grades])
            if grades:
                print(f"\t{subject.subject_name}: {grades}")

        # fetching notes and achievements of a student
        data = await student.get_notes_and_achievements()

        print("--- Notes ---")
        for note in data.notes:
            entry = (
                "+"
                if note.category_type == 1
                else "-"
                if note.category_type == 3
                else "#"
            )
            print(f"\t{entry} {note.category}: {note.content}")

        print("--- Achievements ---")
        for achievement in data.achievements:
            print(f"\t# {achievement}")


if __name__ == "__main__":
    asyncio.run(main())
