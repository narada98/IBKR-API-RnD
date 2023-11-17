import pandas as pd
import numpy as np

ll = [1,4,2,6,5,8,9]

srs = pd.Series(ll)
print(srs)

print(srs.nsmallest(3).index)

l2 = [10,20,30,40,50]

print((pd.Series(l2).iloc[srs.nsmallest(3).index]).to_list())