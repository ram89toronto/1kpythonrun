# write a program to display Equilateral Triangle using *

# input variable
star = int(input(" Enter number lines of Equilateral triangle :"))
n=star+2
# Logic & display
for i in range(1,star):
    print(" "*(n-i) + "* "*(i))
