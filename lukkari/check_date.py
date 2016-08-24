import enum
from . import daterange

class Filters(enum.Enum):
	in_date_range, is_weekday = range(2)

class Conjunctions(enum.Enum):
	all, any, none, implies = range(4)

def compile(parsed):
	assert(len(parsed) >= 1)
	function, *parameters = parsed

	assert(function in ['date', 'week', 'weekday', 'and', 'or', 'not', 'if'])

	if function == 'date':
		if len(parameters) == 1:
			start, = parameters
			end = start
		else:
			assert(len(parameters) == 2)
			start, end = parameters

		date_range = daterange.between(start, end)
		return (Filters.in_date_range, date_range)

	elif function == 'week':
		if len(parameters) > 1:
			return (Conjunctions.any, *[compile(('week', week)) for week in parameters])
		else:
			assert(len(parameters) == 1)
			week_data, = parameters
			year, week = week_data

		date_range = daterange.week(year, week)
		return (Filters.in_date_range, date_range)

	elif function == 'weekday':
		if len(parameters) > 1:
			return (Conjunctions.any, *[compile(('weekday', weekday)) for weekday in parameters])
		else:
			assert(len(parameters) == 1)
			weekday, = parameters

		return (Filters.is_weekday, weekday)

	elif function == 'and':
		return (Conjunctions.all, *[compile(parameter) for parameter in parameters])

	elif function == 'or':
		return (Conjunctions.any, *[compile(parameter) for parameter in parameters])

	elif function == 'not':
		return (Conjunctions.none, *[compile(parameter) for parameter in parameters])

	elif function == 'if':
		assert(len(parameters) == 2)
		condition, then = parameters
		return (Conjunctions.implies, compile(condition), compile(then))

def check_day_match(day, date_filter):
	assert(len(date_filter) >= 1)
	function, *parameters = date_filter

	assert(function in Filters or function in Conjunctions)
	if function == Conjunctions.implies:
		assert(len(parameters) == 2)
	elif function in [Filters.in_date_range, Filters.is_weekday]:
		assert(len(parameters) == 1)
	else:
		assert(function in [Conjunctions.all, Conjunctions.any, Conjunctions.none])

	if function == Conjunctions.all:
		return all(map(lambda parameter: check_day_match(day, parameter), parameters))

	elif function == Conjunctions.any:
		return any(map(lambda parameter: check_day_match(day, parameter), parameters))

	elif function == Conjunctions.implies:
		left, right = parameters
		left_truth = check_day_match(day, left)
		right_truth = check_day_match(day, right)
		return left_truth and right_truth or not left_truth

	elif function == Conjunctions.none:
		return not any(map(lambda parameter: check_day_match(day, parameter), parameters))

	elif function == Filters.in_date_range:
		date_range, = parameters
		return day in date_range

	elif function == Filters.is_weekday:
		weekday, = parameters
		return day.isoweekday() == weekday
