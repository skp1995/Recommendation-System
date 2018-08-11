import MySQLdb
import sys
import operator
import math
import pandas as pd
import numpy as np
import scipy
from collections import Counter
from collections import defaultdict

movie_tag=np.load("MovieTag.npy")
movie_map=np.load("MovieDict.npy")
movie_dict={}
for i in movie_map:
	movie_dict[i[0]]=i[1]

conn = MySQLdb.connect(user='root', passwd='Sairam23!!%', host='localhost', db="MWD1")
#conn = MySQLdb.connect(user='root', passwd='haha123', host='127.0.0.1', db="mwdb")
cur=conn.cursor();

def multiclassTree(movie_label, no_labels, labeled_movies):
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
	#print train.shape
	y1=np.asarray(y).reshape(1,len(y)).T
	#print y.shape
	train_set=np.hstack((train, y1))

	tot_movies=len(movie_tag)
	n_train_movies=len(train_set)
	n_test=tot_movies-n_train_movies

	test_data=np.zeros(( n_test, n_tags))
	test_dict={}
	test_i=0
	for j in movie_map:
		if train_dict.has_key(j[0]) == False:
			test_data[test_i]=movie_tag[movie_dict[j[0]]]
			test_dict[test_i]=j[0]
			test_i= test_i +1
	#print test_data

	minimum_size=100
	maximum_depth=32
	#for rows in train_set:
	#	print rows
	root=fit(train_set, maximum_depth,minimum_size)
	#print root['best_split1']

	test_labels=predict(test_data, root)
	res_it=0
	result_labels=defaultdict(list)
	movie_labels={}
	for r in test_labels:
		movie=test_dict[res_it]		
		result_labels[r].append(movie)
		res_it =res_it+1
		movie_labels[movie]=r
	f=open('outputdtree.txt', 'w')
	for label in set(y):
		f.write("\nLabel: "+str(label)+"\n")
		for index in result_labels[label]:
			cur.execute("SELECT moviename from mlmovies where movieid=%s",(index,))
			moviename=cur.fetchone()[0]
			f.write('\n'+str(moviename))
		f.write("\n")
	f.close()
	print "Written to file outputdtree.txt"
	return result_labels

def split_crit(train, split_1, split_2, labels):
	len1=len(split_1)	
	len2=len(split_2)
	if len1==0 or len2==0:
		return -1
	totlen=len(train)
	gain_before_split=0
	for l in set(labels):
		tot_l=[rows[-1] for rows in train].count(l)
		p=tot_l/totlen
		if p == 0:
			continue
		gain_before_split = gain_before_split + (p * math.log(p))
	gain_before_split=-1*gain_before_split
	gain_after_split=0	
	gain_split1=gain_split2=0
	for l in set(labels):
		l_in_1=[rows[-1] for rows in split_1 ].count(l)
		p1_l=float(l_in_1)/len1
		if p1_l == 0:
			continue
		else:
			wt1=p1_l * math.log(p1_l)
		gain_split1=gain_split1 + (wt1)
		l_in_2=[rows[-1] for rows in split_2 ].count(l)		
		p2_l=float(l_in_2)/len2
		if p2_l == 0:
			continue
		else:	
			wt2=p2_l * math.log(p2_l)				
		gain_split2=gain_split2 + (wt2)
	gain_split1=-1*gain_split1
	gain_split2=-1*gain_split2
	gain_after_split=(float(len1/totlen)*gain_split1 + float(len2/totlen) * gain_split2)
	info_gain=gain_before_split-gain_after_split
	return info_gain

def check_split(train, feature_i, value):
	left, right=[] ,[]
	for row in train:
		if row[feature_i]<value:
			left.append(row)
		else:
			right.append(row)
	return left, right

def get_best_split(train):
	labels=[row[-1] for row in train]
	best_gain=-1
	best_index=-1
	best_split1, best_split2 = list(), list()
	best_split_val=-1
	for feature_index in range(len(train[0])-1):
		for row in train:
			split_1, split_2=check_split(train, feature_index, row[feature_index])
			curr_gain=split_crit(train, split_1, split_2, labels)
			if curr_gain > best_gain:
				best_gain=curr_gain
				best_split1, best_split2= split_1, split_2
				best_index=feature_index
				best_split_val=row[feature_index]			
	return {'best_index':best_index, 'best_gain':best_gain, 'best_split1':best_split1, 'best_split2':best_split2, 'best_split_val':float(best_split_val)}	

def make_leaf(node):
	labels=[row[-1] for row in node]
	return Counter(labels).most_common(1)[0][0]

def do_split(node, maximum_depth, minimum_size, curr_depth):
	split1, split2=node['best_split1'], node['best_split2']
	del(node['best_split1'])
	del(node['best_split2'])
	if not split1 or not split2:
		node['best_split1']=node['best_split2']=make_leaf(split1+split2)
		return
	if curr_depth > maximum_depth:
		node['best_split1']=node['best_split2']=make_leaf(split1), make_leaf(split2)
		return

	if len(split1)<minimum_size:
		node['best_split1']=make_leaf(split1)
	else:
		node['best_split1']=get_best_split(split1)
		do_split(split1, maximum_depth, minimum_size, curr_depth+1)
	
	if len(split2)<minimum_size:
		node['best_split2']=make_leaf(split2)
	else:
		node['best_split2']=get_best_split(split2)
		do_split(split2, maximum_depth, minimum_size, curr_depth+1)

def fit(train_set, maximum_depth, minimum_size):
	root=get_best_split(train_set)
	do_split(root, maximum_depth, minimum_size, 1)
	return root

def predict_row(row, node):
	if row[node['best_index']] < node['best_split_val']:
		if isinstance(node['best_split1'], dict):			
			return predict(test_set, node['best_split1'])
		else:
			return node['best_split1']
	else:
		if isinstance(node['best_split2'], dict):			
			return predict(test_set, node['best_split2'])
		else:
			return node['best_split2']

def predict(test_set, root):
	result_labels=[]
	for row in test_set:
		result_labels.append(predict_row(row, root))
	return result_labels

