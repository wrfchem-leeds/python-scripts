#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 19 10:41:36 2019

Runs instead of normal post.bash. 
Edit splits = to change the number of times the post.bash loop is split
Runs in the run folder, no inputs needed

fl = for loop

@author: eebjs
"""

#import os
import re
from random import randint
import subprocess

# choose how many times to split post.bash loop
splits = 8

# open post.bash
nl  = open('post.bash', 'r')
lines = nl.read().split('\n')

# extract line of outer for loop
fl = [l for l in lines if l.startswith('for hour in')][0]

# extract index of line of outer for loop in 'lines'
fl_i = lines.index(fl)

# get iterations in loop
its = [int(w) for w in re.findall(r"[\w']+", fl) if w.isdigit()][1]

# create list of loop iterators
divisor = round(its / splits)
its_list = [divisor] * (splits)

# add the remainder to the list
while sum(its_list) < its:
    idx = randint(0, splits-1)
    its_list[idx] += 1

split_fl_list = []
count = 0
for it in its_list:
    nit1 = count+it
    if count == 0:
        nit0 = count
    else:
        nit0 = count+1

    split_fl_list.append('for hour in $(seq -w '\
                         +str(int(nit0))+' '+str(int(nit1))+')')
    count += it

# write split post.bash files
for i, split_fl in enumerate(split_fl_list):
    # deep copy original lines
    new_lines = lines[:]
    # replace old fl with split
    new_lines[fl_i] = split_fl
    
    with open('post_split_'+str(i)+'.bash', 'w') as file:
        file.write('\n'.join(new_lines))
    
# qsub the post.bash_split* files
for i in range(len(split_fl_list)):
    subprocess.call(['qsub', 'post_split_'+str(i)+'.bash'])
