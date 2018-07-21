# Write a python program to display and find sum of three numbers using command line arugments

# importing required pacages
import sys

#input varialbes
n1 =int(sys.argv[1])
n2 =int(sys.argv[2])
n3 =int(sys.argv[3])

# logic
sum = n1+n2+n3
len = len(sys.argv)

# Display of output
print("Length of arguments {}".format(len))
print("Diplay of arguments {}".format(sys.argv))
print("Sum of first three arguments is {}".format(sum))
