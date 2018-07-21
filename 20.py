# Write a python to display and sum of a list of numbeers using while loop , generate list using range()

# input variable
lst = [i for i in range(0,101,10)]

# Assigning dummy variables
sum=0
i=0

#logic
while i< len(lst):
    sum+=lst[i]
    i+=1

#Display
print("The list is {}".format(lst))
print(" The sum of list is {}".format(sum))
