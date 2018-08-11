import MySQLdb
import sys
import operator
import math
import pandas as pd
import numpy as np
import scipy
from collections import Counter
from collections import defaultdict

movie_tag=np.load("MovieTag.npy")#movtag.get_movie_tag()
movie_map=np.load("MovieDict.npy")
movie_dict={}
for i in movie_map:
	movie_dict[i[0]]=i[1]

conn = MySQLdb.connect(user='root', passwd='Sairam23!!%', host='localhost', db="MWD1")
#conn = MySQLdb.connect(user='root', passwd='haha123', host='127.0.0.1', db="mwdb")
cur=conn.cursor();

def predict(movie_label, k):
	result_labels={}
	all_labels=[]
	print "Running rnn:"
	cur.execute("SELECT movieid FROM mlmovies;")
	all_movies=cur.fetchall()
	for mov in all_movies:
		if movie_label.has_key(mov[0]):
			#print str(mov[0])+" "+str(movie_label[mov[0]])
			continue
			#print movie_tag[mov[0]]
		else:
			distances=[]
			for movie, label in movie_label.iteritems():
				from scipy import spatial
				dist=spatial.distance.euclidean(movie_tag[movie_dict[mov[0]]], movie_tag[movie_dict[movie]])
				distances.append([dist, label])
				all_labels.append(label)
			count=[i[1] for i in sorted(distances)[:k]]			
			res=Counter(count).most_common(1)[0][0]		
			#print res	
			result_labels[mov[0]]=res
	#print result_labels
	f=open('outputknn.txt', 'w')
	label_movies=defaultdict(list)
	for movie, label in result_labels.iteritems():
		label_movies[label].append(movie)
	for label in set(all_labels):	
		f.write("\nLabel: "+str(label)+"\n")
		for index in label_movies[label]:
			cur.execute("SELECT moviename from mlmovies where movieid=%s",(index,))
			moviename=cur.fetchone()[0]
			f.write('\n'+str(moviename))
		f.write("\n")
	f.close()
	print "Written to file outputknn.txt"
	return
