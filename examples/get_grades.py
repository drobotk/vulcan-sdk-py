import asyncio
from vulcan_scraper import VulcanWeb

async def main():
    vulcan = VulcanWeb(
        host        = "fakelog.cf",
        email       = "jan@fakelog.cf",
        password    = "jan123",
        symbol      = "powiatwulkanowy" # Optional: scraper will attempt to extract symbols from CUFS certificate
    )
    async with vulcan:
        await vulcan.login()

        # get all students from all schools available on this account
        students = await vulcan.get_students()
        
        for student in students:
            print(repr(student))

        # fetching grades of a student
        data = await student.get_grades()
        for subject in data.subjects:
            grades = '  '.join([g.entry for g in subject.grades])
            print(f"{subject.subject_name}: {grades}")
    
if __name__ == "__main__":
    asyncio.run( main() )