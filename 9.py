# Write a python program to accepting a list and tuple from keyboard \
# and display it in their respective formats?

# input list and tuple
lst = input("Enter a list :")
tpl = input("Enter a tuple")

# logic
list_lst = eval(lst)
tuple_tpl = eval(tpl)

# display output

print("Given input list is of type  {} and is {}" .format(type(list_lst),list_lst))

print("Given input tuple is of type  {} and is {}" .format(type(tuple_tpl),tpl))
