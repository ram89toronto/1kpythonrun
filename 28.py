# Write a program to create an array using linspace() and logspace() of numpy library

# import packages
import numpy as np

# Linspace() creating an array of 100
lin_num = np.linspace(1,100,10)
# This function represents 1 to 100 number range and dividing 10 equal parts

# logspace() creating an array 1 to 10000
log_num = np.logspace(1,4,5)
#This function represents 10**1 to 10**4 and divides into 5 equal parts

# display of output
print(lin_num)
print(log_num)
