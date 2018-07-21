# Write a program to evaluate an expression entered from keyboard using eval()

# input variables

a,b = 4,5
c = input(" Enter a numerical expression for evaluation :")

# logic
d = eval(c)
logic = "a**b - 3"
result = eval(logic)

# Display of result
print(" Entered Expression is {} and answer is {}".format(c,d))
print("a is {}, b is {} and Computation of {} is {}".format(a,b,logic,result))
