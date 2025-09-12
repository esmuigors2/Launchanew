#!/usr/bin/python

def shift_coords(xyzstruct, shiftstruct, shifte = '0.5'):
  """shifts coordinates"""
  shifte = float(shifte)
  xyzmas = xyzstruct.splitlines()
  sftmas = shiftstruct.splitlines()
  xyzl = len(xyzmas)
  sftl = len(sftmas)
  print("Length of the first list is "+str(xyzl))
  for line in range(0,xyzl):
      xyzlinearr = xyzmas[line].split()
      sftlinearr = sftmas[line].split()
      #print("XYZ has "+str(len(xyzlinearr))+" elements:")
      #print(xyzmas[line])
# The normal coefficients are the linear combination coeffcients of the transformation from the
# Cartesian to normal coordinates; hence they sort of show how a shift along a certain Cartesian
# (x, y or z) affects the molecule IF just the mode in interest is considered; they are
# dimentionless, as follows from the decomposition of the Hessian matrix: H = PkP^-1, where the
# k is diagonal matrix with force constants (eigenvalues of the Hessian, with the same
# dimension of kg/s^2 multiple) and the P is unitary transformation matrix (whose
# eigenvectors are the normal coordinates), hence dimensionless. See:
# Errol G. Lewars. Computational Chemistry, 3rd ed., Springer, 2016, p. 37
# Jon Baker. Molecular Structure and Vibrational Spectra. In: Handbook of Computational Chemistry, 2nd ed., Springer, 2017, p.423
# https://chemistry.stackexchange.com/questions/119941/the-concept-of-normal-coordinates-of-a-molecule
      xyzlinearr[1] = '{0:3.6f}'.format(float(xyzlinearr[1]) + shifte*float(sftlinearr[0]))
      xyzlinearr[2] = '{0:3.6f}'.format(float(xyzlinearr[2]) + shifte*float(sftlinearr[1]))
      xyzlinearr[3] = '{0:3.6f}'.format(float(xyzlinearr[3]) + shifte*float(sftlinearr[2]))
      xyzmas[line] = "   ".join(xyzlinearr)
      #print(xyzmas[line])
  return "\n".join(xyzmas)


import sys
xyz_file = sys.argv[1]
sft_file = sys.argv[2]
rxyz_file = sys.argv[3]
if len(sys.argv) > 4:
    shifta = sys.argv[4]
else:
    shifta = '0.5'
try:
    allmyxyzf = open(xyz_file,'r')
except IOError:
    print("Cannot find file "+xyz_file+"!")
    sys.exit(10)
try:
    allmysftf = open(sft_file,'r')
except IOError:
    print("Cannot find file "+sft_file+"!")
    sys.exit(10)
allmyxyz = allmyxyzf.read()
allmyxyzf.close()
allmysft = allmysftf.read()
allmysftf.close()
myxyz = allmyxyz.splitlines()
nrat = myxyz[0]
title = myxyz[1]
myxyz = myxyz[2:]
print("Length of myxyz is "+str(len(myxyz)))
allmyxyz = ""
allmyxyz = "\n".join(myxyz)
#print(allmyxyz)
allmyres = shift_coords(allmyxyz, allmysft, shifta)
try:
    rxyz = open(rxyz_file, "w+")
except IOError:
    print("Cannot write to file "+rxyz_file+"!")
    sys.exit(10)
rxyz.write(nrat+"\n")
rxyz.write(title+"\n")
rxyz.write(allmyres)
rxyz.close()
print("File "+rxyz_file+" written!")


