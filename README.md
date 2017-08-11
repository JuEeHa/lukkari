Installing
----------
Run `make` to generate a zipball runnable by python 3. Copy to bin dir.

Requires `zip` program to be installed

Usage
-----
	lukkari.py file [start [end]]

Displays the timetable between start and end dates (or for current week / next week if weekend). Dates are given in format year-month-day.

File format
-----------
Basic record format is

	name;time range;free-form info;filter

Comments (`#`) are supported and `;` can be excaped with `\` as usual

Time range format
-----------------
Time ranges are `start-end`, where start and end may be either HH:MM or just the hour (then it's assumed the minutes field is 0)

Filter format
-------------
Filters are written in a sexpr based language. A function can be either a filter or a conjunction. Currently three different filters (`date`, `week`, and `weekday`) and four conjunctions (`and`, `or`, `not`, and `if`) are supported.

	(date start-date [end-date])
	(week week1 [week2 week3 …])
	(weekday weekday1 [weekday2 weekday3 …])

Dates are given as year-month-day, weeks as year-week. Weekdays use the three-letter short names: `mon`, `tue`, `wed`, `thu`, `fri`, `sat`, `sun`.

While `date` checks that the date is in a given range (both ends inclusive), `week` and `weekday` check if the date is in a given week or given weekday. Thus, `(weekday mon wed)` only checks if the weekday is monday or wednesday, not if it's tuesday.

	(and [expr1 expr2 expr3 …])
	(or [expr1 expr2 expr3 …])
	(not [expr1 expr2 expr3 …])
	(if condition expr)

`and`, `or`, and `not` all take a variable amount of parameters. `and` checks that all are true, `or` that at least one is true, and `not` that none are true. All of these can be run with zero parameters, in which case `and` and `not` return true and `or` returns false.

`if` is a the implies operator from boolean algebra. If `condition` is true,`expr` needs to be true as well but if `condition` is false the expression is true regardless of the truth value of `expr`.

Whether the conjunctions are short-circuiting or not is not defined, but as the filters are pure functions it should not matter.

Bugs
----
There is no error reporting. All error handling is done by crashing on an assert.
