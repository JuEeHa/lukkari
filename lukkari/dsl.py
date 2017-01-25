import enum
from . import daterange

class Filters(enum.Enum):
	in_date_range, is_weekday = range(2)

class Conjunctions(enum.Enum):
	all, any, none, implies = range(4)

def to_ir(parsed):
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
			return (Conjunctions.any,) + tuple(to_ir(('week', week)) for week in parameters)
		else:
			assert(len(parameters) == 1)
			week_data, = parameters
			year, week = week_data

		date_range = daterange.week(year, week)
		return (Filters.in_date_range, date_range)

	elif function == 'weekday':
		if len(parameters) > 1:
			return (Conjunctions.any,) + tuple(to_ir(('weekday', weekday)) for weekday in parameters)
		else:
			assert(len(parameters) == 1)
			weekday, = parameters

		return (Filters.is_weekday, weekday)

	elif function == 'and':
		return (Conjunctions.all,) + tuple(to_ir(parameter) for parameter in parameters)

	elif function == 'or':
		return (Conjunctions.any,) + tuple(to_ir(parameter) for parameter in parameters)

	elif function == 'not':
		return (Conjunctions.none,) + tuple(to_ir(parameter) for parameter in parameters)

	elif function == 'if':
		assert(len(parameters) == 2)
		condition, then = parameters
		return (Conjunctions.implies, to_ir(condition), to_ir(then))

def to_lambda(date_filter):
	assert(len(date_filter) >= 1)
	function, *parameters = date_filter
	assert(function in Filters or function in Conjunctions)

	if function == Conjunctions.all:
		compiled = [to_lambda(parameter) for parameter in parameters]
		return lambda day: all(map(lambda f: f(day), compiled))

	elif function == Conjunctions.any:
		compiled = [to_lambda(parameter) for parameter in parameters]
		return lambda day: any(map(lambda f: f(day), compiled))
	
	elif function == Conjunctions.implies:
		assert(len(parameters) == 2)
		left, right = to_lambda(parameters[0], parameters[1])
		return lambda day: right(day) if left(day) else True
	
	elif function == Conjunctions.none:
		compiled = [to_lambda(parameter) for parameter in parameters]
		return lambda day: not any(map(lambda f: f(day), compiled))
	
	elif function == Filters.in_date_range:
		assert(len(parameters) == 1)
		date_range, = parameters
		return lambda day: day in date_range
	
	elif function == Filters.is_weekday:
		assert(len(parameters) == 1)
		weekday, = parameters
		return lambda day: day.isoweekday() == weekday

def compile(parsed):
	ir = to_ir(parsed)
	return to_lambda(ir)
