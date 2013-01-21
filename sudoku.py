# Sudoku Solver for Google App Engine
# Last updated: January 18, 2013
# Author: Po Shan Cheah

import cgi
import re
import time
from google.appengine.ext import webapp
import os
import jinja2

jinja_environment = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__)))


# Replace newlines with <br> tags. Consecutive <br> tags need to be
# separated by non-breaking spaces so that the browser won't collapse the
# blank lines.
def nl2br(str):
    return re.sub('\n+', lambda mobj: '<br>' + '&nbsp;<br>' * (len(mobj.group(0)) - 1), str)

class MainPage(webapp.RequestHandler):

    default_puz = """xxx 6xx 9x2
xx6 1xx x87
2x7 5xx xx1

xxx xx8 7xx
4x2 xxx 1x6
xx9 2xx xxx

6xx xx3 5x8
59x xx1 2xx
8x4 xx7 xxx"""

    output = ''

    def write(self, msg):
	self.output += msg

    def write_error(self, msg):
	self.output += '<span class="error">Error: %s</span>\n' % msg

    def write_bold(self, msg):
	self.output += '<strong>%s</strong>\n' % msg

    def render_template(self, puz, output):
	t = jinja_environment.get_template('sudtempl.htm')
	html = t.render({ 'puz' : puz, 'output' : output })
	self.response.out.write(html)

    # This is the initial page. Just display the form and put a default
    # puzzle into the textbox.
    def get(self):
	self.render_template(self.default_puz, '')

    # Solve the puzzle in input and output the solution.
    def solve_puzzle(self, input):
	if self.process_input(input):
	    self.write_bold("Puzzle:")
	    self.print_board()
	    self.write("\n")

	    if self.check_board():
		self.nodecount = 0
		starttime = time.clock()
		if not self.try_board(0, 0):
		    self.write("No solution found\n")
		elapsedtime = time.clock() - starttime

		self.write("""
%d nodes examined.
Elapsed time: %.3f seconds.
""" % (self.nodecount, elapsedtime))

    # Non-AJAX handler so we build up the whole page with the solution inside.
    def post(self):
	input = self.request.get('input')

	self.solve_puzzle(input)

	# Leave the user's input in the textbox when displaying the form.
	self.render_template(cgi.escape(input), nl2br(self.output))

    # Parse the board info from the text area.
    def process_input(self, input):
	lineno = 0
	self.board = []

	for line in input.split('\n'):
	    line = re.sub(r'\s+', '', line)
	    if len(line) == 0:
		continue

	    lineno += 1
	    if len(line) < 9:
		self.write_error('Line %d is too short.' % lineno)
		return False

	    # Take the first 9 chars of the line and convert them to int or 0.
	    self.board.append([c.isdigit() and int(c) or 0 for c in line[:9]])

	if lineno < 9:
	    self.write_error('Not enough rows. Only %d rows found.' % lineno)
	    return False

	return True

    # Display the board.
    def print_board(self):
	for i in range(0, 9):
	    self.write('%d: %s\n' % (i + 1,
		' '.join([cell == 0 and 'x' or str(cell)
		    for cell in self.board[i]])))

    # Check board for simple inconsistencies.
    def check_board(self):

	# Check rows
	for i in range(0, 9):
	    used = [ False ] * 10
	    for j in range(0, 9):
		cell = self.board[i][j]
		if cell and used[cell]:
		    self.write_error('Digit %d occurs more than once in row %d' % (cell, i + 1))
		    return False
		else:
		    used[cell] = True

	# Check columns
	for j in range(0, 9):
	    used = [ False ] * 10
	    for i in range(0, 9):
		cell = self.board[i][j]
		if cell and used[cell]:
		    self.write_error('Digit %d occurs more than once in column %d' % (cell, j + 1))
		    return False
		else:
		    used[cell] = True

	# Check 3x3 blocks
	for ii in range(0, 9, 3):
	    for jj in range(0, 9, 3):
		used = [ False ] * 10
		for i in range(ii, ii + 3):
		    for j in range(jj, jj + 3):
			cell = self.board[i][j]
			if cell and used[cell]:
			    self.write_error('Digit %d occurs more than once in 3x3 block at %d,%d' % (cell, ii+1, jj+1))
			    return False
			else:
			    used[cell] = True

	return True

    # Return a list of numbers that could go into cell row, col on the board.
    def get_possible(self, row, col):
	used = [ False ] * 10

	# Check row and column
	for i in range(0, 9):
	    used[self.board[row][i]] = True
	    used[self.board[i][col]] = True

	# Check 3x3 block containing this cell
	brow = row - row % 3
	bcol = col - col % 3
	for i in range(brow, brow + 3):
	    for j in range(bcol, bcol + 3):
		used[self.board[i][j]] = True

	# Return numbers that have not been used in the containing row, column,
	# and block.
	return [i for i in range(1,10) if not used[i]]

    # Recursive function to find a solution by exhaustive search.
    def try_board(self, row, col):
	if row >= 9:
	    self.write_bold("Found a solution:")
	    self.print_board()
	    return True

	self.nodecount += 1

	nextrow, nextcol = row, col + 1
	if nextcol >= 9:
	    nextrow, nextcol = row + 1, 0

	# Skip over cells that are already filled.
	if self.board[row][col] != 0:
	    return self.try_board(nextrow, nextcol)

	for cell in self.get_possible(row, col):
	    self.board[row][col] = cell
	    if self.try_board(nextrow, nextcol):
		return True

	self.board[row][col] = 0
	return False

class AjaxPage(MainPage):

    # For the AJAX handler, just output the puzzle solution without the rest of
    # the page. The Javascript will take care of adding this to the correct
    # place on the page.
    def post(self):
	input = self.request.get('input')

	self.solve_puzzle(input)
	self.response.out.write(nl2br(self.output))

# --- Main section ---

app = webapp.WSGIApplication([ 
    ('/', MainPage), 
    ('/ajax', AjaxPage) ], debug=True)

# vim:set tw=0:
