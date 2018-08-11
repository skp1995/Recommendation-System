import MySQLdb
import csv
import sys
import operator
import math
import pandas as pd
import numpy as np
import scipy
#import MovieTagMatrix as movtag
import knn
import svm
import dtree

mode= int(sys.argv[1])
movie_label={}
tot_movies=0
'''
print("Enter number of labels:")
no_labels=int(raw_input())
for i in range(0,no_labels):
	print("Enter number of movies with this label:")
	no_movies=int(raw_input())
	tot_movies = tot_movies + no_movies
	print("Enter the label: ")
	label=raw_input()
	print("Enter the movieids:")
	for j in range(0, no_movies):
		movieid=int(raw_input())
		movie_label[movieid]=label
'''
f=open('input_task5.txt', 'rb')
labels=[]
for line in f:
	mov=int(line.split(" ")[0])
	lab=line.split(" ")[1].rstrip('\n')
	labels.append(lab)
	movie_label[mov]=lab

print "Training set read from file: "
print movie_label
no_labels=len(set(labels))
tot_movies=len(movie_label)


if mode == 1:
	print "Enter r for R-Nearest Neighbours: "
	k = int(raw_input())
	knn.predict(movie_label, k)

if mode == 2:
	print "Running SVM:"
	svm.multiclassSVM(movie_label, no_labels, tot_movies)

if mode == 3:
	print "Running Decision trees:"
	dtree.multiclassTree(movie_label, no_labels, tot_movies)	

