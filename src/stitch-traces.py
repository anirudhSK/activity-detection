#! /usr/bin/python
from markov import *
''' Program to stitch traces together into a larger trace '''
import sys
if ( len(sys.argv) < 2) :
	print "Usage : python markov-chain.py duration "
	exit(5)
else :
	m=MarkovChain()
	m.simulate(int(sys.argv[1]));
