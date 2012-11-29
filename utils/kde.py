from scipy.stats.kde import gaussian_kde
import matplotlib.pyplot as plt
from numpy import *
from scipy.stats import norm
import numpy
import pickle
fh=open('test_list','r')
feature_list = pickle.load(fh);
x = linspace(min(feature_list),max(feature_list),300)

''' trunc_pdf 60% slower than scipy.stats.gaussian_kde '''
bw=0.003
def trunc_pdf (x,samples) :
	x_repeated=array([x]*len(samples))
	norm_pdfs=norm.pdf((x_repeated-samples)/bw)/(norm.sf((-samples)/bw))
	return numpy.sum(norm_pdfs)/(bw*len(samples))
plt.plot(x,map(lambda y : trunc_pdf(y,array(feature_list)), x ),'r')

''' untrunc_pdf 30% slower than scipy.stats.gaussian_kde '''
def untrunc_pdf (x,samples) :
	x_repeated=array([x]*len(samples))
	norm_pdfs=norm.pdf((x_repeated-samples)/bw)
	return numpy.sum(norm_pdfs)/(bw*len(samples))
plt.plot(x,map(lambda y : untrunc_pdf(y,array(feature_list)), x ),'g')

''' scipy.stats.gaussian_kde '''
kernel_pdf = gaussian_kde(feature_list)
plt.plot(x,kernel_pdf(x),'b')

''' actual data '''
plt.plot(feature_list,[0.1]*len(feature_list),"x")
plt.show()
