## L-Statistic-for-Transition-Likelihood
This script calculates the average D'Mello's L for the student affect transitions. Given a sequence of observations for a set of students, the script calculates L value for each student and reports the mean, standard deviation, count, standard error for each of the 16 transitions between the 4 states of flow, confusion, frustration and boredom. It also runs a one sample two-tailed t-test ans reports the corresponding  t-statistic and p value. L value along with the p value of the test denotes whether a given transition is significantly more likely than chance, given the base frequency of the next state. This script could be extended to other affective states.

### How to run the code?
Like any other py script!

Input File - affect\_sequences.csv <br>
The file should contain sequence of affect observations for each student and each observer if there are multiple observers. Format your input file to read <student ID>,<observer1>,<observer2> in each line. Check sample file for example. <br>
Verify the following before running the code -
- data should be sorted by student_id
- set appropriate delimiter in code 
- set SELF_TRANS to False if you want to merge self-transitions (line 44)
- set ONE_CODER to TRUE if only one coder (line 43)
- you can extend the code for more than 2 coders and other affective states with some minimal code changes

Output File - dmello\_L_stats.csv
    
Reference: D'Mello, S., & Graesser, A. (2012). Dynamics of affective states during complex learning. Learning and Instruction, 22(2), 145-157.

License: None BUT I would appreciate if you credit the code in any published material and follow me on GitHub 
