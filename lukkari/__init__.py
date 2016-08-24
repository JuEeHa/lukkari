import datetime
import sys
import os.path
from . import check_date
from . import daterange
from . import generate_timetable
from . import parse_coursefile

def parse_date(text):
	split = text.split('-')
	assert(len(split) == 3)
	return tuple(map(int, split))

def main():
	if len(sys.argv) == 2:
		year, week, day = datetime.date.today().isocalendar()
		if day >= 6: # on weekend, show next week
			year, week, day = (datetime.date.today() + datetime.timedelta(2)).isocalendar()
		dates = daterange.week(year, week)
		filename = sys.argv[1]
	elif len(sys.argv) == 3:
		date = parse_date(sys.argv[1])
		dates = daterange.between(date, date)
		filename = sys.argv[2]
	elif len(sys.argv) == 4:
		start = parse_date(sys.argv[1])
		end = parse_date(sys.argv[2])
		dates = daterange.between(start, end)
		filename = sys.argv[3]
	else:
		print('%s [start [end]] file' % (os.path.basename(sys.argv[0])))
		print('start and end are in yyyy-mm-dd format')
		sys.exit(1)

	with open(filename, 'r') as f:
		courses_parsed = parse_coursefile.parse(f.read())

	courses = []
	for name, info, parsed_filter in courses_parsed:
		date_filter = check_date.compile(parsed_filter)
		courses.append((name, info, date_filter))
	
	timetable = generate_timetable.generate_timetable(dates, courses)

	timetable_by_date = []
	current_date = None
	current_date_entries = []
	for date, name, info in timetable:
		if current_date is None:
			current_date = date

		if date == current_date:
			current_date_entries.append((name, info))
		else:
			timetable_by_date.append((current_date, current_date_entries))
			current_date = date
			current_date_entries = []
			current_date_entries.append((name, info))
	
	if current_date is not None and current_date_entries != []:
		timetable_by_date.append((current_date, current_date_entries))
	
	print(dates)
	print()

	for date, entries in timetable_by_date:
		print(date)
		for name, info in entries:
			print('\t%s: %s' % (name, info))
