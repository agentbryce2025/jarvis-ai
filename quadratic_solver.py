import math

def quadratic_solver(a, b, c):
    discriminant = b**2 - 4*a*c
    if discriminant > 0:
        root1 = (-b + math.sqrt(discriminant)) / (2*a)
        root2 = (-b - math.sqrt(discriminant)) / (2*a)
        print("The roots are:", root1, "and", root2)
    elif discriminant == 0:
        root = -b / (2*a)
        print("The root is:", root)
    else:
        real_part = -b / (2*a)
        imaginary_part = math.sqrt(abs(discriminant)) / (2*a)
        print("The roots are complex:", real_part, "+", imaginary_part, "i and", real_part, "-", imaginary_part, "i")
