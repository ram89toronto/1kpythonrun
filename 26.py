# Write a program to compute sum of squares from 1 to number entered using a function definition?

#Function for sum of squares taking list - Procedural Style
def ss(lst):
    total = 0
    for i in lst:
        total = total + int(i**2)
    return total
# functional sytle
def sss(lst):
    return sum(x**2 for x in lst) # Generator

# input variable
num = int(input(" Enter a number to get sum of squares from 1 to number entered : "))
#input a list of numbers
a = [x for x in range(0,num)]

# Compute and display the result
print("Procedural style {}".format(ss(a)))
print("Functional style {}".format(sss(a)))
