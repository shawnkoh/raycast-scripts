from parsy import regex, string, seq, generate
from datetime import date

# Goal: Parse dates 2017-09-25

year = regex(r'[0-9]{4}').map(int).desc("4 digit year")
month = regex(r'[0-9]{2}').map(int).desc("2 digit month")
day = regex(r'[0-9]{2}').map(int).desc("2 digit day")
dash = string('-')

# parse expects to consume all input (expects EOF)
# parse_partial keeps going?

# same as calling .then
# this discards previous result, so this will only return day
fulldate = year >> dash >> month >> dash >> day
fulldate = seq(year, dash, month, dash, day)
# we dont actually need dash, so we can nuke it with >> aka then
# can also use <<
fulldate = seq(year, dash >> month, dash >> day)
# to combine the list into a date object we can use combine()
fulldate = seq(year, dash >> month, dash >> day).combine(date)
# can also pass lambda to combine or use combine_dict
# can also use map too but tutorial says combine is nicer? not sure why.

# can use + instead of >> to combine result. 
# >> will discard result of previous parser.

# seq combinator takes parsers that are passed in as arguments
# and combines result into a list

# the problem about the previous parser is that it will throw the moment
# it encounters an invalid data
# but we want it to continue, so we need Optionals.
# we can do this using Parser.bind() but
# Python's syntax is not ideal
# Hence, we use generator functions instead.
@generate
def full_date():
    y = yield year
    yield dash #implict skip
    m = yield month
    yield dash
    d = yield day
    return date(y, m, d)