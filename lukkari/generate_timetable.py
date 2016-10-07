import datetime

def generate_timetable(day_range, courses):
	start_date, end_date = day_range.range()
	date = start_date
	appointments = []
	while True:
		for name, time_range, info, date_filter in courses:
			if date_filter(date):
				appointments.append((date, time_range, name, info))

		if date == end_date:
			break

		date += datetime.timedelta(1)

	return appointments
