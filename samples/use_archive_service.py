from pprint import pprint
from edgar.client import EdgarClient

# Initialize the Edgar Client
edgar_client = EdgarClient()

# Initialize the Archives Services.
archive_services = edgar_client.archives()

# Grab the Company Directories for CIK `1326801` also known as Facebook.
pprint(archive_services.get_company_directories(cik='1326801')[:2])

# Grab a specific Company Directory for CIK `1326801` also known as Facebook.
pprint(
    archive_services.get_company_directory(
        cik='1326801',
        filing_id='000095010321003805'
    )
)

# Grab a specific Company Directory for CIK `1326801` also known as Facebook.
pprint(archive_services.get_feed(year=1996, quarter='qtr4'))

# Grab the old loads for the year 1996 of Qtr 4.
pprint(archive_services.get_old_loads(year=1996, quarter='qtr4'))

# Grab all the Virtual Private Reference Rooms.
pprint(archive_services.get_virtual_private_reference_rooms())

# Grab a specific Virtual Private Reference Room.
pprint(archive_services.get_virtual_private_reference_room(film_number='1403'))

# Grab all the Daily Indexes.
pprint(archive_services.get_daily_indexes())

# Grab the Daily Indexes for QTR4 of 2002.
pprint(archive_services.get_daily_index(year=2002, quarter='qtr4'))

# Grab all the Full Indexes.
pprint(archive_services.get_full_indexes())

# Grab the Full Indexes for QTR4 of 2002.
pprint(archive_services.get_full_index(year=2002))