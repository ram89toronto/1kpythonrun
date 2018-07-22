# Write a program to search for an element in th list of elements using for-else

# input variable
group1 = [2,3,4,5,6,7,8]
search = int(input("Enter a number to search :"))

#logic
for element in group1:
    if search == element:
        print("Element found")
        break
else:
    print("entered number is not in list")
