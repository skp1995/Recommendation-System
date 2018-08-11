import numpy
import scipy
from sklearn.decomposition import PCA
import math
from collections import defaultdict
import MySQLdb
import sys

db = MySQLdb.connect(host="localhost", 
                      user="root", 
                      passwd="Sairam23!!%", 
                      db="MWD") 

cursor = db.cursor() 
movie=[]
suggested=[]
feedback=[]
cursor.execute("select distinct moviename from mlmovies;")
movies=cursor.fetchall()
for i in movies:
	movie.append(i[0])


inputMatrix=numpy.load("MovieTagReduced.npy")
values=[]
W=4



def H(inp,W):
	X=numpy.random.rand(500,1)
	return (numpy.dot(inp,X)/W);

def closestpositive(W,maxi):
	val=0
	for i in range(0,int(math.floor(maxi)+1),W):
		val=i+W
		if (val>=int(math.floor(maxi)+1)):
			return val

def closestnegative(W,mini):
	val=0
	for i in range(0,int(math.floor(mini)-1),-W):
		val=i-W
		if (val<=int(math.floor(mini)-1)):
			return val

	
		    
def LSH(inputvectors,L,K,moviename,R):
	temp=1
	layer=0

	for i in range(0,len(inputvectors)):
		for lr in range(0,L):
			for hashfn in range(0,K):
				temp*=H(inputvectors[i,:],W)
			layer=layer+temp
			temp=1
			
		values.append(layer)

	

	maxi=max(values)
	mini=min(values)

	
	for i in range(0,len(values)):
		values[i]=((values[i]-mini)/maxi-mini)*100

	

	highestbinvalue=closestpositive(W,maxi)
	leastbinvalue=closestnegative(W, mini)
	
	
	binNo=[]
	for i in range(0,len(values)):
		binNo.append(math.floor(values[i]/W))
	#print set(binNo)
	Zippedbins=zip(binNo,values)
	Zippedmoviebins=zip(binNo,movie)
	
	bins=defaultdict(list)
	
	for k,v in Zippedmoviebins:
		bins[k].append(v)

	
		

	#for i in range(int(min(binNo)),int(max(binNo)+1) ):
	#	print i,bins[i]
	
	

	for i in range(int(min(binNo)),int(max(binNo)+1) ):
		if moviename in (bins[i]):
			topmoviesindex=i
			
			
			print "Number of movies considered",len(bins[i])
	
	if len(bins[topmoviesindex])>R:
		
		for i in range(0,R):
			if moviename not in bins[topmoviesindex][i]:
				suggested.append(bins[topmoviesindex][i])
			else:
				suggested.append(bins[topmoviesindex][R])
	
	if len(bins[topmoviesindex])<R:
		Rem=R-len(bins[topmoviesindex])
		for i in range(0,len(bin[topmoviesindex])):
			suggested.append(bins[topmoviesindex][i])
		
		while Rem>0:
			topmoviesindex+=1
			tmp=len(bin[topmoviesindex])
			if tmp>0:
				if(tmp>=Rem):
					for i in range(0,Rem):
						suggested.append(bins[topmoviesindex][i])
					Rem=0

				if(tmp<Rem):
					for i in range(0,tmp):
						suggested.append(bins[topmoviesindex][i])
					Rem=Rem-tmp
			else:
			   Rem=Rem-tmp


	
	for i in suggested:
		print i

	if ( neighbours != len(suggested)) :
		print "not enough suggestions"

	for i in range(0,neighbours):
		print suggested[i], "\t\tpositive(1), negative(-1) or neutral(0) ??"
		feedback.append(str(raw_input()))




	feedback1=zip(feedback, suggested)
	

	count=0
	for i,j in feedback1:
				
		if i=='1':
			
			print j
			count+=1
			bins[topmoviesindex].remove(j)

			
	
		if i=='-1':
			bins[topmoviesindex].remove(j)

	remaining=R-count
	if remaining != 0:
		for i in range(0,remaining):
			print bins[topmoviesindex][i]




layers=int(sys.argv[1])
hashes=int(sys.argv[2])
movieName=sys.argv[3]
neighbours=int(sys.argv[4])
LSH(inputMatrix,layers,hashes,movieName,neighbours)



