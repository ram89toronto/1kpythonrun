# Write a program to remove duplicate values from a given list using set()

# input variables
a= [10,20,23,30,43,30,43,23,43,34,12,23,10,3,34]

# Logic
length_a = len(a)
unique_a = set(a)

# Display output
print(" Given list \n {} \n and has length of {}".format(a,length_a))
print(" Unique values of list are \n {}".format(list(unique_a)))
