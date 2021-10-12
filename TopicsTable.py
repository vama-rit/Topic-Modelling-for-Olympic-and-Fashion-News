#!/usr/bin/env python
# coding: utf-8

# In[447]:


import re
import pandas as pd
lines=[]
with open('topics.txt') as file:
    next(file)
    for line in file:
        lines.append(re.split(';|,|\+|\)|\n', line))


# In[448]:


for i in lines:
    for j in range(len(i)):
        i[j]=re.sub('[(\\\\!@\'#$/\" "]', '', i[j])
        if "*" in i[j]:
            i[j]=i[j].partition("*")[2]
    i.pop(0)
    i.remove('')
    if '' in i:
        i.remove('')


# In[449]:


dictlist={i[len(i)-1]: i[0:(len(i)-1)] for i in lines}


# In[450]:


df=pd.DataFrame.from_dict(dictlist,orient='index').transpose()


# In[455]:


print(df.to_latex(index=True)) 

