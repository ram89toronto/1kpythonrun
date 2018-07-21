# Write a python program to add two numbers using argument parser

# import requried packages
import argparse as ap

# create a object
parser = ap.ArgumentParser(description="Enter Two Numbers to return sum")

# Adding arguments
parser.add_argument("n1", type=float, help="Please enter first numbers")
parser.add_argument("n2", type=float, help="Please enter second number")

# Retrieve the arguments
x= parser.parse_args()

# logic
result = float(x.n1) + float(x.n2)

# Display out
print(" The sum of {} and {} is {}".format(x.n1,x.n2,result))
