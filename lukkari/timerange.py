import datetime

class Timerange:
	def __init__(self, start, length):
		self.start = start
		self.length = length

	def range(self):
		end = self.start + self.length
		return (self.start, end)

	def __contains__(self, day):
		delta = day - self.start
		return datetime.timedelta(seconds = 0) <= delta and delta < self.length

	def overlaps(self, other):
		if other.start < self.start:
			return other.overlaps(self)

		assert(self.start <= other.start)
		return other.start < self.start + self.length

	def __repr__(self):
		return 'Timerange(%s, %s)' % (repr(self.start), repr(self.length))

	def __str__(self):
		start, end = (i.strftime('%H:%M') for i in self.range())
		return '%s - %s' % (start, end)

	def __eq__(self, other):
		return self.start == other.start and self.length == other.length

	def __ne__(self, other):
		return not self == other

def between(start, end):
	assert(len(start) == 2 and len(end) == 2)
	start_hour, start_minute = start
	end_hour, end_minute = end
	start_obj = datetime.datetime(1970, 1, 1, start_hour, start_minute)
	end_obj = datetime.datetime(1970, 1, 1, end_hour, end_minute)
	assert(end_obj - start_obj > datetime.timedelta(seconds = 0))
	return Timerange(start_obj, end_obj - start_obj)
