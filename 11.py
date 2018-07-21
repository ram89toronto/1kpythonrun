# Write a program using moudle argparse and find square of integer number

# Imp logic : p= ap.ArgumentParser(description= "Hello"), p.add_argument("var_name",type=int,help="lol")
# Imp logic : object2 = p.parse_args()
# Imp logic : Multiple args  -> add_argument("var_name", nargs='+')


# Import packages
import argparse as ap

# Creating object
parse = ap.ArgumentParser(description="This program displays square of given number")

# Adding an arugment
parse.add_argument("num", type=int, help="Please input only integer")

# Creating an object (retrieve the arguments passed to the programs)
args = parse.parse_args()

# logic
result = args.num**2

# Display of output
print("Square of the value = ", result)
