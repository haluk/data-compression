import random
import string
import re
import time

from bisect import bisect
from collections import defaultdict
from itertools import product
from sys import argv
from fileinput import input

def randomStr(l):
	return ''.join(random.choice(string.ascii_lowercase) for x in range(l))

def randomWordSet(n, l):	
	return "-".join(randomStr(l) for x in range(n))

def occurrenceTable(file):
	freq_table = defaultdict(lambda : 0)
	total_char = 0.0

	with open(file) as f:
		for word in f:
			word = word.strip().lower()
			freq_table.update((c, freq_table[c] + word.count(c)) for c in set(word))
			total_char += len(word)	

	result = []
	last = 0.0
	for k,v in sorted(freq_table.items()):
		result.append((k, last + v, (last + v) / total_char, v, v / total_char))
		last += v

	return result

def pickLetter(occurrence_table):
	breakpoints = []
	for e in occurrence_table:
		breakpoints.append(e[2])

	r = random.random()	
	idx = bisect(breakpoints, r)	
	if breakpoints[idx-1] <= r and r < breakpoints[idx]:
		return string.ascii_lowercase[idx]
		
def generateWord(n, occurrence_table):
	result = []	
	for i in range(n):
		word = ""
		while len(word) != 4:
			letter = pickLetter(occurrence_table)
			if  letter != None:
				word += letter

		result.append(word)

	return '-'.join(result)

def singleLetterContext(file):
	n = len(string.ascii_lowercase)
	occurrence_table = [[0.0 for x in xrange(n)] for x in xrange(n)]
		
	with open(file) as f:		
		text = f.read().strip().lower()		

	contents = input(file)

	pattern = "%s(%s+)"
	for i in string.ascii_lowercase:
		i_idx = string.ascii_lowercase.index(i)		
		match1 = re.findall("(?=%s(.))" % i, text)
		total_char = float(len(match1))		
		last = 0.0
		for j in string.ascii_lowercase:						
			j_idx = string.ascii_lowercase.index(j)
			match2 = re.findall(pattern % (i, j), text)			
			if total_char != 0:
				occurrence_table[i_idx][j_idx] = (len(match2) + last) / total_char
				last += len(match2)								

	word = ''
	while word == '':
		tmp = pickLetter(occurrenceTable(file))
		if tmp != None:
			word += tmp		

	while len(word) != 4:		
		breakpoints = occurrence_table[string.ascii_lowercase.index(word[-1])]		
		r = random.random()	
		idx = bisect(breakpoints, r)
		if idx == len(string.ascii_lowercase):
			pass
		elif breakpoints[idx-1] <= r and r < breakpoints[idx]:
			word += string.ascii_lowercase[idx]

	return word

def callSingleLetterContext(file, n):
	result = []
	for i in range(n):
		result.append(singleLetterContext(file))

	return '-'.join(result)


def twoLetterContext(file, trial):
	n = len(string.ascii_lowercase)
	occurrence_table = [[0.0 for x in xrange(n)] for x in xrange(n*n)]
		
	with open(file) as f:		
		text = f.read().strip().lower()
		total_char = float(len(text.replace('\n', '')))

	contents = input(file)

	pattern = "(?=(%s)(%s*))"
	cnt = 0
	for i in string.ascii_lowercase:
		for j in string.ascii_lowercase:			
			match1 = re.findall("(?=%s(.))" % (i+j), text)			
			total_char = float(len(match1))					
			last = 0.0		

			for z in string.ascii_lowercase:
				z_idx = string.ascii_lowercase.index(z)
				match2 = re.findall(pattern % (i+j, z), text)				
				match2 = filter(lambda x: x != '', map(lambda x: x[1], match2))	
				if total_char != 0:
					occurrence_table[cnt][z_idx] = (len(match2) + last) / total_char
					last += len(match2)
			cnt+=1

	alph = list(product(string.ascii_lowercase, string.ascii_lowercase))
	alph = map(lambda x: ''.join(x), alph)

	word = ''
	tried = 0		

	while tried < trial:	
		while len(word) < 2:
			tmp = pickLetter(occurrenceTable(file))
			if tmp != None:
				word += tmp			

		breakpoints = occurrence_table[alph.index(word[-2:])]
		r = random.random()	
		idx = bisect(breakpoints, r)				
		if idx == len(string.ascii_lowercase) or idx == 0:							
			tried += 1						
		elif breakpoints[idx-1] <= r and r < breakpoints[idx]:
			word += string.ascii_lowercase[idx]

		if len(word) == 4:			
			return word

		if tried >= trial:
			tried = 0
			word = ''

def callTwoLetterContext(file, n, k):
	result = []
	for i in range(n):
		result.append(twoLetterContext(file, k))		

	return '-'.join(result)


def pretty_print(occurrence_table):	
	print "%s \t %s \t %s \t %s \t %s" % ("Letter", "Cumulative Frequency", \
		"Cumulative Relative Frequency", "Frequency", "Relative Frequency")

	for e in occurrence_table:
		print "%s \t %d \t %0.3f \t %d \t %0.3f \t" \
		% (e[0], e[1], e[2], e[3], e[4])

if __name__ == "__main__":
	
	start_time = time.time()
	print "Random Model:"
	print "============="
	print randomWordSet(100, 4)
	print time.time() - start_time, "seconds"

	start_time = time.time()
	print "CDF Model:"
	print "=========="
	occurrence_table = occurrenceTable(argv[1])
	print generateWord(100, occurrence_table)
	print time.time() - start_time, "seconds"

	
	start_time = time.time()
	print "Single Letter Context:"
	print "======================"
	print callSingleLetterContext(argv[1], 100)
	print time.time() - start_time, "seconds"
	
	start_time = time.time()
	print "Two Letter Context:"
	print "==================="
	print callTwoLetterContext(argv[1], 100, 10)
	print time.time() - start_time, "seconds"