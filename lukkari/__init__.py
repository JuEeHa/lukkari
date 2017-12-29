import datetime
import sys
import os.path
from . import dsl
from . import daterange
from . import generate_timetable
from . import parse_coursefile

def parse_date(text):
	split = text.split('-')
	assert(len(split) == 3)
	return tuple(map(int, split))

def main():
	args = sys.argv[1:]

	if len(args) > 2 and args[1] == '--overlaps':
		only_overlaps = True
		args = args[:1] + args[2:]
	else:
		only_overlaps = False

	if len(args) == 1:
		year, week, day = datetime.date.today().isocalendar()
		if day >= 6: # on weekend, show next week
			year, week, day = (datetime.date.today() + datetime.timedelta(2)).isocalendar()
		dates = daterange.week(year, week)
		filename = args[0]
	elif len(args) == 2:
		filename = args[0]
		date = parse_date(args[1])
		dates = daterange.between(date, date)
	elif len(args) == 3:
		filename = args[0]
		start = parse_date(args[1])
		end = parse_date(args[2])
		dates = daterange.between(start, end)
	else:
		print('%s [--overlaps] file [start [end]]' % (os.path.basename(sys.argv[0])), file = sys.stderr)
		print('start and end are in yyyy-mm-dd format', file = sys.stderr)
		sys.exit(1)

	with open(filename, 'r') as f:
		courses_parsed = parse_coursefile.parse(f.read())

	courses = []
	for name, time_range, info, parsed_filter in courses_parsed:
		date_filter = dsl.compile(parsed_filter)
		courses.append((name, time_range, info, date_filter))
	
	timetable = generate_timetable.generate_timetable(dates, courses)

	timetable_by_date = []
	current_date = None
	current_date_entries = []
	for date, time_range, name, info in timetable:
		if current_date is None:
			current_date = date

		if date == current_date:
			current_date_entries.append((time_range, name, info))
		else:
			timetable_by_date.append((current_date, current_date_entries))
			current_date = date
			current_date_entries = []
			current_date_entries.append((time_range, name, info))
	
	if current_date is not None and current_date_entries != []:
		timetable_by_date.append((current_date, current_date_entries))
	
	print(dates)
	print()

	for date, entries in timetable_by_date:
		entries.sort(key = lambda x: x[0].range()[0])
		previous_time_range = None
		previous_name = None
		if not only_overlaps:
			print(date)
		for time_range, name, info in entries:
			if not only_overlaps:
				print('\t%s %s: %s' % (time_range, name, info))
			if previous_time_range is not None:
				if time_range.overlaps(previous_time_range):
					if only_overlaps:
						print('%s: %s %s | %s %s' % (date, previous_time_range, previous_name, time_range, name))
					else:
						print('\t\tOverlap')
					# If the current's ending time is before the previous's, don't change previous_time_range in case it overlaps with several
					# If current's ending time after, it's safe to change
					if time_range.range()[1] >= previous_time_range.range()[1]:
						previous_time_range = time_range
						previous_name = name
				else:
					previous_time_range = time_range
					previous_name = name
			else:
				previous_time_range = time_range
				previous_name = name
