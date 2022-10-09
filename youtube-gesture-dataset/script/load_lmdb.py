import lmdb
import pyarrow
import numpy as np
import sys

env = lmdb.open("C:\\Users\\makem\\ProjectHcb\\res\\Youtube_Dataset\\output\\lmdb_test",readonly=True,lock=False)

txn = env.begin()

np.set_printoptions(threshold=sys.maxsize)

for key, value in txn.cursor():
    video = pyarrow.deserialize(value)
    vid = video['vid']
    clips = video['clips']
    print("video : ", video)
    print("clips : ", clips)
    break

env.close()