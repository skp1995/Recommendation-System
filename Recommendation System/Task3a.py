import numpy
from scipy import linalg
mat=numpy.load("MovieTag.npy")
U, s, V = linalg.svd(mat, full_matrices=False)
reduced=U[:,0:500]
print reduced
numpy.save("MovieTagReduced.npy", reduced)
