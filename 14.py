#  Write a program to accept 1 or more arguments and display them as a list
# using argparse via command line

# import required packages
import argparse as ap

# Create object
parser = ap.ArgumentParser(description=" Please enter any number of list items")

# add arguments to object
parser.add_argument("lst", nargs="+")

# retrieving Arguments
x = parser.parse_args()

# Displaying the result of list one by one
for i in x.lst:
    print(i)
