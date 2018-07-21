# Write a program to convert numbers from different numbers system to decimal system
# using int() function

# input variables
s1 = "17" # Octal
s2 = "1110010" # Binary
s3 = "1c2" # Hexadecimal

# Logic using int() function
n1 = int(s1, 8)
n2 = int(s2,2)
n3 = int(s3, 16)

# Display of output conversion
print("{} is ocatal , coverted to decimals as {}".format(s1,n1))
print("{} is binary , coverted to decimals as {}".format(s2,n2))
print("{} is hexadecimal , coverted to decimals as {}".format(s3,n3))
