#  Write a program to create an array using arange() to write even numbers 1 to 100?

# importing packages
import numpy as np

# logic for creating array of even and odd numbers between 1 and 100
ar_num_even= np.arange(0,101,2)
ar_num_odd= np.arange(1,101,2)
# Display of even numbers
print(ar_num_even)
print(ar_num_odd)
