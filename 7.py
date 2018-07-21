#  Write a python program to accept 3 numbers in the same line  and display their sum?
#  Also, write a logic to accept 3 numbers separated by comma.

# Input Varialbe
var1 , var2 , var3 = [int(i) for i in input(" Enter three numbers : ").split()]
var_1, var_2, var_3 = [int(j) for j in input(" Enter three numbers separated by ',' :").split(',')]
# Logic
var4 = var1 + var2 + var3
var_4 = var_1 + var_2 + var_3

# Display of values
print(" Given Numbers are {} {} {} and their sum is {}".format(var1,var2,var3,var4))
print(" Given Numbers separated by ',' are {} {} {} and their sum is {}" .format(var_1,var_2,var_3,var_4))
