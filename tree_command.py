import os
from glob import glob
a=glob(os.getcwd() + "/*/", recursive = True)
print(a)
