import datetime
from . import check_date

def generate_timetable(day_range, courses):
	start_date, end_date = day_range.range()
	date = start_date
	appointments = []
	while True:
		for name, info, date_filter in courses:
			if check_date.check_day_match(date, date_filter):
				appointments.append((date, name, info))

		if date == end_date:
			break

		date += datetime.timedelta(1)

	return appointments
