import datetime

class Daterange:
	def __init__(self, start, length):
		self.start = start
		self.length = length

	def range(self):
		end = self.start + self.length - datetime.timedelta(1)
		return (self.start, end)

	def __contains__(self, day):
		delta = day - self.start
		return datetime.timedelta(0) <= delta and delta < self.length

	def overlaps(self, other):
		if other.start < self.start:
			return other.overlaps(self)

		assert(self.start <= other.start)
		return other.start < self.start + self.length

	def __repr__(self):
		return 'Daterange(%s, %s)' % (repr(self.start), repr(self.length))

	def __str__(self):
		start, end = map(str, self.range())
		return '%s - %s' % (start, end)

	def __eq__(self, other):
		return self.start == other.start and self.length == other.length

	def __ne__(self, other):
		return not self == other

def week(year, week):
	# Ensure that week is correct for the given year
	assert(1 <= week and week <= 53)
	if week == 53:
		assert(datetime.date(year, 12, 31).isocalendar()[1] == 53)

	# First attempt, this will most likely be wrong
	# Use 28 instead of probably better 30 so we don't have to special-case february
	days_into_year = 1 + week * 7
	guess = datetime.date(year + days_into_year // 365, days_into_year // 28 % 12 + 1, week * 7 % 28 + 1)
	guess_year, guess_week, guess_weekday = guess.isocalendar()

	while guess_year != year or guess_week != week or guess_weekday != 1:
		year_delta = year - guess_year
		week_delta = week - guess_week
		weekday_delta = 1 - guess_weekday

		# Year is not quite right, but by repeated application year_delta should become 0, after which it's correct
		delta = datetime.timedelta(year_delta * 365 + week_delta * 7 + weekday_delta)

		guess += delta
		guess_year, guess_week, guess_weekday = guess.isocalendar()

	return Daterange(guess, datetime.timedelta(7))

def between(start, end):
	assert(len(start) == 3 and len(end) == 3)
	start_year, start_month, start_day = start
	end_year, end_month, end_day = end
	start_obj = datetime.date(start_year, start_month, start_day)
	end_obj = datetime.date(end_year, end_month, end_day)
	assert(end_obj - start_obj >= datetime.timedelta(0))
	return Daterange(start_obj, end_obj - start_obj + datetime.timedelta(1))
