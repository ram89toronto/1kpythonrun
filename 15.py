# Write a python to caluclate the area of circle using math package

# import required packages
import math

# input variables
r = float(input(" Enter the radius of Circle :"))

# logic
area = math.pi * r ** 2

# Display of output
print(" The area of circle is {}".format(area))
#Expressing the area till two decimal points
print(" The area of circle is {:0.2f}".format(area))
