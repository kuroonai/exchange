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


if len(sys.argv) > 4 or len(sys.argv) < 4: raise SyntaxError(' python exchange.py  <location> <from extension> <to extension>')

loc = sys.argv[1]
ext1 = sys.argv[2]
ext2 = sys.argv[3]

os.chdir(loc)

files = os.listdir(loc)
names = np.empty(len(files), dtype = object)

for i in range(len(files)):
    names[i] =   files[i].split('.')[-1]

if ext1 not in names : 
    print('\nNo file with %s extension found!'%ext1)
    exit

else :
    for file in tqdm(os.listdir(loc)):
    

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
                
       
    print ('Done!')   