import MySQLdb
import csv
import sys
import operator
import math
import pandas as pd
import numpy as np
import scipy
from collections import Counter
from collections import defaultdict
import cvxopt
from cvxopt import solvers, matrix
import copy
import random

movie_tag=np.load("MovieTag.npy")#movtag.get_movie_tag()
movie_map=np.load("MovieDict.npy")
movie_dict={}
index_dict={}
for i in movie_map:
	movie_dict[i[0]]=i[1]
	index_dict[i[1]]=i[0]

conn = MySQLdb.connect(user='root', passwd='Sairam23!!%', host='localhost', db="MWD1")
cur=conn.cursor();

def multiclassSVM(movie_label, no_labels, labeled_movies):
	y=[]	
	n_movies, n_tags= movie_tag.shape
	train=np.zeros((labeled_movies, n_tags))
	train_i=0
	train_dict={}
	for mov, lab in movie_label.iteritems():
		y.append(lab)
		train[train_i]=movie_tag[movie_dict[mov]]
		train_dict[mov]=train_i
		train_i= train_i+1
	t=twoClassSVM(1000.1)
	train=np.array(train)
	tot_movies=len(movie_tag)
	n_train_movies=len(train)
	n_test=tot_movies-n_train_movies
	test_data=np.zeros(( n_test, n_tags))
	test_dict={}
	test_i=0
	for j in movie_map:
		if train_dict.has_key(j[0]) == False:
			test_data[test_i]=movie_tag[movie_dict[j[0]]]
			test_dict[j[0]]=test_i
			test_i= test_i +1
	#print test_data
	test_labels=defaultdict(list)
	done_labels=[]
	for lab in y:
		temp_y=copy.copy(y)
		if lab in done_labels:
			continue
		print "Doing for label "+ str(lab)+" vs all:"
		for i in range(0, len(y)):
			if y[i] == lab:
				temp_y[i]=1
			else:
				temp_y[i]=-1
		temp_y=np.array(temp_y) 	
		w,b=t.train_SVM(train,temp_y,train_dict)				
		t_labels=[]
		test_predict=np.sign(np.dot(test_data , w) + b)
		for ll in test_predict:
			if ll==1:
				t_labels.append(lab)
			else:
				t_labels.append(-1)
		it=0
		for ll in t_labels:
			test_labels[it].append(ll)
			it= it +1
		done_labels.append(lab)
		print "\n"
	result_label={}
	for mov_index, labels in test_labels.iteritems():
		rr=Counter(test_labels[mov_index]).most_common(1)[0][0]
		if rr<=0:
			result_label[mov_index]=random.choice(y)
		else:
			result_label[mov_index]=str(rr)
	f=open('outputsvm.txt', 'w')
	label_movies=defaultdict(list)
	for index, label in result_label.iteritems():
		label_movies[label].append(index)
	for label in set(y):	
		f.write("\nLabel: "+str(label)+"\n")
		for index in label_movies[label]:
			cur.execute("SELECT moviename from mlmovies where movieid=%s",(index_dict[index],))
			moviename=cur.fetchone()[0]
			f.write('\n'+str(moviename))
		f.write("\n")
	f.close()
	print "Written to file outputsvm.txt"
	return result_label
class twoClassSVM(object):
	def __init__(self, C=None):
		self.C=C
		if self.C is None: 
			self.C=1000.1	

	def train_SVM(self,X,y,X_dict):
		n_movies, n_tags=X.shape
		m=n_movies
		n=n_tags	
		
		problem_matrix=matrix(0.0, (m+n+1, m+n+1), 'd')
		for i in range(n):
			problem_matrix[i,i]=1.0
		
		problem_vector=matrix(0.0, (m+n+1, 1))
		for i in range(n, n+m):
			problem_vector[i]=self.C
		problem_vector[-1]=1.0
		
		inequal_vector=matrix(-1.0, (m+m, 1))
		inequal_vector[m:]=0.0
		
		inequal_matrix = matrix(0.0, (m+m,n+m+1), 'd')
		for i in range(m):
			inequal_matrix[i,:n] = -np.dot(y[i] , X[i])
			inequal_matrix[i,n+i] = -1
			inequal_matrix[i,-1] = -y[i]
		for i in range(m,m+m):
			inequal_matrix[i,n+i-m] = -1.0
		
		solution=solvers.qp(problem_matrix,problem_vector,inequal_matrix,inequal_vector)['x']
		w=solution[0:n]
		b=solution[-1]
		return w,b


