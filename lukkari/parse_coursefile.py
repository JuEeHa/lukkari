from . import timerange

def strip_comments(text):
	lines = []
	for line in text.split('\n'):
		comment_start = line.find('#')
		if comment_start != -1:
			lines.append(line[:comment_start])
		else:
			lines.append(line)
	return '\n'.join(lines)

def parse_timerange(text):
	ends = [i.split(':') for i in text.split('-')]
	assert(len(ends) == 2)
	start, end = ((int(i[0]), 0) if len(i) == 1 else tuple(map(int, i)) for i in ends)
	assert(len(start) == 2 and len(end) == 2)
	return timerange.between(start, end)

def parse_filter(text):
	weekdays = {'mon': 1, 'tue': 2, 'wed': 3, 'thu': 4, 'fri': 5, 'sat': 6, 'sun': 7}
	functions = ['date', 'week', 'weekday', 'and', 'or', 'not', 'if']
	def eof():
		nonlocal index, length
		return index >= length

	def skip_whitespace():
		nonlocal index, length
		while not eof() and text[index].isspace():
			index += 1

	def match(matches):
		nonlocal index, length
		assert(not eof())
		assert(text[index] in matches)
		index += 1

	def read_atom():
		nonlocal index, length
		start = index

		while not eof() and not text[index].isspace() and text[index] != ')':
			index += 1

		return text[start:index]

	def subexpression():
		nonlocal index, length
		if not eof() and text[index] == '(':
			match('(')
			skip_whitespace()

			elements = []

			function = read_atom()
			skip_whitespace()
			assert(not eof())

			assert(function in functions)
			elements.append(function)

			while not eof() and text[index] != ')':
				elements.append(subexpression())
				skip_whitespace()

			match(')')

			return elements

		else:
			atom = read_atom()
			assert(len(atom) >= 1)

			if atom in weekdays:
				return weekdays[atom]
			else:
				split = atom.split('-')
				assert(all(map(lambda x: x.isnumeric(), split)))
				assert(len(split) == 2 or len(split) == 3)
				return tuple(map(int, split))

	index = 0
	length = len(text)

	skip_whitespace()
	expression = subexpression()
	skip_whitespace()
	assert(eof())

	return expression

def parse(text):
	def eof():
		nonlocal index, length
		return index >= length

	def skip_whitespace():
		nonlocal index, length
		while not eof() and text[index].isspace():
			index += 1

	def match(matches):
		nonlocal index, length
		assert(not eof())
		assert(text[index] in matches)
		index += 1

	def read_field():
		nonlocal index, length
		skip_whitespace()

		start = index
		while not eof() and text[index] not in [';', '\n']:
			if text[index] == '\\':
				index += 1
			index += 1

		return text[start:index].strip()

	text = strip_comments(text)
	index = 0
	length = len(text)

	courses = []
	while not eof():
		name = read_field()
		match(';')

		time_range = parse_timerange(read_field())
		match(';')

		info = read_field()
		match(';')

		date_filter = parse_filter(read_field())
		if not eof():
			match('\n')

		courses.append((name, time_range, info, date_filter))

	assert(eof())

	return courses
