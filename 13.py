# Write a python program to find the power value of a number when it raised to a particular power
# using argparse package using command line input

# import packages
import argparse as ap

# Creating object
parser = ap.ArgumentParser(description=" Enter value and power to be raised")

# Adding Arguments
parser.add_argument("nums", nargs=2)

# Retrieving Arguments
x = parser.parse_args()

# logic
result = float(x.nums[0])*int(x.nums[1])

# Displaying
print("The value is {}".format(x.nums[0]))
print("The power to be raised is {} ".format(x.nums[1]))
print(" The result {} ".format(result))
