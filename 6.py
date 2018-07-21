# A program to accept two numbers and return sum and incorporate trunc() from math module.

#importing requried pacakges
import math as m

# Input variables
n1 = float(input("Enter the first number :"))
n2 = float(input("Enter the second number :"))

# Logic
n3 = n1+n2

# Display to console
print(" Given first number : {} \n Given second number : {} \
 \n Sum of two numbers :{} \n Truncate of their sum : {}" \
 .format(n1,n2,n3,m.trunc(n3)))
