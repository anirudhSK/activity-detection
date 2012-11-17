#! /usr/bin/python
#! learn a normal distribution with support (x>0) and generate it's pdf
from math import *

class Positive_Normal :
	mean=0
	sigma=0

	def mean_and_var(self,value_list) :
		if (value_list==[]) :
			return (None,None)
		meanSq=reduce(lambda acc,update : acc + update**2,value_list,0.0)/len(value_list)
		mean=reduce(lambda acc,update : acc + update,value_list,0.0)/len(value_list)
		return (mean,meanSq-mean*mean)

	def __init__ (self,mean,sigma) :
		self.mean=mean
		self.sigma=sigma

	def __init__ (self,value_list) :
		''' Poor man's ML estimation, Ref. to Cohen (1950) for the real thing '''
		(self.mean,variance)=self.mean_and_var(value_list)
		if (variance != None) :
			self.sigma=sqrt(variance)
		else :
			self.sigma=None

	def __str__(self) :
		return "Mean of distribution "+str(self.mean)+" sigma is "+str(self.sigma)

	def pdf(self,x) :
		density=phi((x-mean)/sigma)/sigma;
		norm_constant=1-Phi((-mean)/sigma)
		return density/norm_constant

	def phi(self,x) :
		''' the canonical pdf '''
		return exp(-(x**2)/2)/sqrt(2*pi)

	def Phi(self,x) :
		''' the canonical cdf '''
		return (1+erf(x/sqrt(2)))/2
