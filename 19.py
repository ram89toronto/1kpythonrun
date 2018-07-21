# Write a program to display even numbers between M and # N

# Create a input list M and N:
m,n = [ int(i) for i in input("Enter a max and min ex: 1,99 :___").split(',')]

#logic and display

x=m # Assign input variable to dummy variable to run the logic

if x%2 !=0:
    x+=1
while x>=m and x<=n:
    print(x)
    x+=2
