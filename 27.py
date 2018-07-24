# Write a program to create a numpy array with numbers and characters?

# import libraries
import numpy as np

#  Enter input variables
num= [123,212,231,23,1233,343]
ch = ["Hyderabad","Mumbai","Delhi","Kolkata"]

# Converting into numpy array
numpy_num = np.array(num)
numpy_ch = np.array(ch, dtype=str)

# Display the array
print(numpy_num)
print(numpy_ch)
