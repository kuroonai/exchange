#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep  7 21:22:31 2019

@author:Naveen Kumar Vasudevan, 
        Doctoral Student, 
        The Xi Research Group, 
        McMaster University, 
        Hamilton, 
        Canada.
        
        naveenovan@gmail.com
        https://naveenovan.wixsite.com/kuroonai
"""

'''
required packages : numpy, tqdm

Usage: python exchange.py   <location> <from extension> <to extension>

'''

import os
import sys
from tqdm import tqdm
import numpy as np
import multiprocessing
import itertools
from contextlib import contextmanager
from functools import partial

loc = sys.argv[1]
ext1 = sys.argv[2]
ext2 = sys.argv[3]

n_cpu = multiprocessing.cpu_count()

files = list(filter(lambda f: f.endswith(ext1),  os.listdir(loc)))
names = np.empty(len(files), dtype = object)

    
@contextmanager
def poolcontext(*args, **kwargs):
    pool = multiprocessing.Pool(*args, **kwargs)
    yield pool
    pool.terminate()  

def namearray(i):
    names[i] =   files[i].split('.')[-1]

def extchange(file):
    if file.endswith(ext1):
        src = os.path.abspath(file)
        
        if os.name == 'posix':
            dst_filename = src.split('/')[-1].split('.')
            dst = src.split('/')[:-1]
            s = '/'
            dst = s.join(dst)+'/'+dst_filename[0]+'.%s'%ext2
            os.rename(src,dst)
            
        elif os.name =='nt':
            dst_filename = src.split('\\')[-1].split('.')
            dst = src.split('\\')[:-1]
            s = '\\'
            dst = s.join(dst)+'\\'+dst_filename[0]+'.%s'%ext2
            os.rename(src,dst)
    
if __name__ == "__main__":
    
    #if len(sys.argv) > 4 or len(sys.argv) < 4: raise SyntaxError(' python exchange.py  <location> <from extension> <to extension>')

    os.chdir(loc)
    
    
    # with poolcontext(processes=n_cpu) as pool:
    #     pool.map(namearray, (i for i in tqdm(range(len(files)))))
    
    for i in range(len(files)):
        namearray(i)

    if ext1 not in names : 
        print('\nNo file with %s extension found!'%ext1)
        

    else :
        with poolcontext(processes=n_cpu) as pool:
            pool.map(extchange, (file for file in tqdm(list(filter(lambda f: f.endswith(ext1),  os.listdir(loc))))))                   
           
        print ('Done!')   