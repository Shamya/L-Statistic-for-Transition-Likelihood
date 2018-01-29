#!/usr/local/bin/python
"""
This script calculates the average D'Mello's L for the student affect transitions. Given a sequence of observations 
for a set of students, the script calculates L value for each student and reports the mean, standard deviation, count, 
standard error for each of the 16 transitions between the 4 states of flow, confusion, frustration and boredom. 
It also runs a one sample two-tailed t-test ans reports the corresponding  t-statistic and p value. 
L value along with the p value of the test denotes whether a given transition is significantly more likely than chance, 
given the base frequency of the next state. This script could be extended to other affective states.
"""

# Author: Shamya Karumbaiah <shamya@upenn.edu>
# License: None BUT you can encourage my efforts by crediting the code in any published material and following me on GitHub 

"""
    Input File
    ----------
    affect_sequences.csv

    Check the following -
    	- check readme for input format
    	- set SELF_TRANS to False if you want to merge self-transitions (line 44)
    	- data sorted by student_id
    	- set appropriate delimiter in code below
    	- set ONE_CODER to TRUE if only one coder (line 43)
    	- you can extend the code for more than 2 coders

    Output File
    -----------
    dmello_L_stats.csv

    Reference
    ----------
	D'Mello, S., & Graesser, A. (2012). Dynamics of affective states during complex learning. Learning and Instruction, 22(2), 145-157.
"""

from collections import Counter
import numpy as np
import csv
from itertools import groupby
from scipy import stats
np.random.seed(7654567)

ONE_CODER = False
SELF_TRANS = True

#HELPER FUNCTIONS

#count the occurence of each state - count(next)
#called for per student per observer sequence by main class
def calculate_state_counts(seq, state_count):
    for st in state_count:
        if Counter(seq)[st] > 0:
            #calculated for P(next) - 
            state_count[st] = state_count[st] + Counter(seq)[st]
    return state_count

#calculate state probabilities - count(next)/total
def calculate_state_prob(state_count, stud):
    state_prob = {}
    total = sum(state_count.values())
    for st in state_count:
        try:
            state_prob[st] = float(state_count[st])/float(total)
        except:
            #happens when the student has been in the same state and you remove self transitions - there is no "next" state
            return None
    return state_prob 

#count the transitions between states - count(prev -> next)
def calculate_trans_counts(seq, transition_count):
    for (x,y), c in Counter(zip(seq, seq[1:])).iteritems():
        transition_count[(x,y)] = transition_count[(x,y)] + c if (x,y) in transition_count else c
    return transition_count

#calculate transition probabilities = count(prev -> next)/count(prev)
def calculate_trans_prob(transition_count, trans_state_count):
    transition_prob = {}
    for t in transition_count:
        try:
            transition_prob[t] = float(transition_count[t])/float(trans_state_count[t[0]])
        except:
            #happens when "prev" state is not seen for this student
            #you cannot define a transition probability for transitions out of this state
            transition_prob[t] = 'na'
            #check if exception triggered for case outside of what is known
            if transition_count[t] > 0 or trans_state_count[t[0]] >0:
                print "New Exception - CHECK"
                print t, transition_count, trans_state_count
    return transition_prob

#calculate D'Mello's L = (P(next|prev)-P(next)) / (1-P(next))
def calculate_dmello_l(transition_prob, state_prob):
    #calculate D'Mello's L
    dmello_l = {}
    for t in transition_prob:
        if transition_prob[t] != 'na':
            try:
                dmello_l[t] = (transition_prob[t]-state_prob[t[1]])/(1-state_prob[t[1]])
            except: 
                #happens when the student has only been in the "next" state 
                if state_prob[t[1]] != 1:
                    print "New Exception - CHECK"
                continue #SKIP
    return dmello_l

#write to csv
def write_to_csv(dmello_l_stats):
    fn = 'dmello_L_stats.csv'
    rows = []
    rows.append(['Prev', 'Next', 'mean', 'stdev', 'count', 'stderr', 't', 'p'])
    dmello_states = ["FLO", "CON", "FRU", "BOR"]
    for st1 in dmello_states:
        for st2 in dmello_states:
            trans = (st1, st2)
            rows.append(list(trans)+dmello_l_stats[trans])
    with open(fn, "wb") as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    print "Result written to CSV", fn

#MAIN PROGRAM SEQUENCE
#INPUT - list of lists -> lists of observations per observer for each student
#OUPUT - D'Mello L average, stddev, count for each transition

def call_dMello_L(aff_seq, stud_seq, self_trans = True):
    
    dMello_L_aggregate = {}
    count = 0
    dmello_states = ['FLO', 'CON', 'FRU', 'BOR'] 
    
    if self_trans == False:
        print "Removing self transitions"
    
    for idx, per_stud_list in enumerate(aff_seq): # for each student
        count += 1
        state_count = {'FLO':0, 'CON':0, 'FRU':0, 'BOR':0, 'NA': 0}
        transition_count = {}
        for st1 in state_count:
            for st2 in state_count:
                transition_count[(st1,st2)] = 0

        #calculate state and transition counts 
        for obs_seq in per_stud_list: #for each observer sequence for this student
            if len(obs_seq) == 0:
                continue
            #remove self transitions
            if self_trans == False:
                obs_seq = [x[0] for x in groupby(obs_seq)]
            state_count = calculate_state_counts(obs_seq[1:], state_count)#counts state only when the state is the next state (ignores the first incidence)
            transition_count = calculate_trans_counts(obs_seq, transition_count)
        
        #calculate P(next)
        state_prob = calculate_state_prob(state_count, stud_seq[idx])
        if state_prob is None:
            #happens when the student has been in the same state and you remove self transitions - there is no "next" state
            #skip the student
            print "Student only in one state, skipping stud#", stud_seq[idx]
            continue

        #calculate count(prev) - counts state only when the state has a next state (ignores last occurence)
        trans_state_count = {'FLO':0, 'CON':0, 'FRU':0, 'BOR':0, 'NA': 0}
        for st in trans_state_count:
            trans_state_count[st] = sum([transition_count[sts] for sts in transition_count if sts[0]==st])

        #calculate P(next|prev) = count(prev->next)/count(prev)
        transition_prob = calculate_trans_prob(transition_count, trans_state_count)

        #calculate D'Mello's L 
        dmello_l = calculate_dmello_l(transition_prob, state_prob)
        
        #add this student data to the aggregate
        for trans in dmello_l:
            if trans in dMello_L_aggregate:
                dMello_L_aggregate[trans].append(dmello_l[trans])
            else:
                dMello_L_aggregate[trans] = [dmello_l[trans]]

    #average, stddev, count D'Mello's L  across all students
    dMello_L_stats = {trans:[np.mean(dMello_L_aggregate[trans]), np.std(dMello_L_aggregate[trans]), len(dMello_L_aggregate[trans]), stats.sem(dMello_L_aggregate[trans]), stats.ttest_1samp(dMello_L_aggregate[trans],0)[0], stats.ttest_1samp(dMello_L_aggregate[trans],0)[1]] for trans in dMello_L_aggregate}
    #Make self transition L NA, if self transitions are removed
    if self_trans == False:
        for st in dmello_states:
            dMello_L_stats[(st, st)] = ['na']*len(dMello_L_stats[(st, st)])
    return dMello_L_stats

aff_seq = [] 
obs1 = []
obs2 = []
stud_seq = []
dmello_states = ['FLO', 'CON', 'FRU', 'BOR'] 
with open('affect_sequence.csv', 'rU') as csvfile:
    reader = csv.reader(csvfile, delimiter = '\n')
    reader.next() #skip header
    stud = 1
    delim = ',' #'\t'
        
    for row in reader:
        #Change of set 
        if int(row[0].split(delim)[0]) != stud:
            stud_seq.append(stud)
            aff_seq.append([obs1, obs2])
            stud = int(row[0].split(delim)[0])
            obs1 = []
            obs2 = []
        #Preprocess to convert non-DMello states to "NA" including undefined states
        if row[0].split(delim)[1] in dmello_states:
            obs1.append(row[0].split(delim)[1])
        else:
            obs1.append('NA') 
            
        if ONE_CODER is False:          
            if row[0].split(delim)[2] in dmello_states:
                obs2.append(row[0].split(delim)[2])
            else:
                obs2.append('NA')
            
stud_seq.append(stud)       
aff_seq.append([obs1, obs2])  
print "number of students", len(aff_seq)
print "number of coders", len(aff_seq[1])
print "number of observations per student (assumes same number for all)", len(aff_seq[0][1])
dMello_L_stats = call_dMello_L(aff_seq, stud_seq, self_trans = SELF_TRANS)
write_to_csv(dMello_L_stats)
print "COMPLETE."
