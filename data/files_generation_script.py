import random
import os

os.makedirs("inputs_closest_pair", exist_ok=True)
os.makedirs("inputs_integer_multiplication", exist_ok=True)

#Generate inputs for Closest Pair of Points
for i in range(1, 11):
    num_points = random.randint(100, 300)  # at least 100 points
    points = [(random.randint(0, 10000), random.randint(0, 10000)) for _ in range(num_points)]
    
    with open(f"inputs_closest_pair/input_{i}.txt", "w") as f:
        f.write(f"{num_points}\n")
        for x, y in points:
            f.write(f"{x} {y}\n")

print("Generated 10 input files for Closest Pair of Points in 'inputs_closest_pair/'")


#Generate inputs for Integer Multiplication
for i in range(1, 11):
    digits1 = random.randint(100, 300)  # at least 100 digits
    digits2 = random.randint(100, 300)
    
    num1 = ''.join(str(random.randint(0, 9)) for _ in range(digits1))
    num2 = ''.join(str(random.randint(0, 9)) for _ in range(digits2))
    
    with open(f"inputs_integer_multiplication/input_{i}.txt", "w") as f:
        f.write(num1 + "\n")
        f.write(num2 + "\n")

print("Generated 10 input files for Integer Multiplication in 'inputs_integer_multiplication/'")
