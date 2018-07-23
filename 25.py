# Write a python program to take a input number and print prime number series
num = int(input("Enter a number "))
prime=[]
if num > 1:
    for j in range(2,num+1):
        for i in range(2, j):
            if j%i==0:
                break
        else:
            prime.append(j)

x= set(prime)
for k in x:
    print(k, end=" ")
print("\n")
