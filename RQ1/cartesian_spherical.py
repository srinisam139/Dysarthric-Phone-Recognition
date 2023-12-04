import math
import pickle

def cartesian_to_spherical(x, y, z):
    r = math.sqrt(x ** 2 + y ** 2 + z ** 2)
    theta = math.atan2(y, x)
    phi = math.acos(z / r) if r != 0 else 0  # Ensure r is not zero to avoid division by zero

    return r, theta, phi


def spherical_to_cartesian(r, theta, phi):
    x = r * math.sin(phi) * math.cos(theta)
    y = r * math.sin(phi) * math.sin(theta)
    z = r * math.cos(phi)
    return x, y, z


# Example usage
x_coord = -37.6605  # Replace with your x-coordinate
y_coord = -29.4712  # Replace with your y-coordinate
z_coord = 3.5062  # Replace with your z-coordinate

# Example usage
radius = 47.949  # Replace with your radial distance
theta = math.radians(-32.3646)  # Replace with your polar angle in radians
phi = math.radians(75.0436)  # Replace with your azimuthal angle in radians

x, y, z = spherical_to_cartesian(radius, theta, phi)
print(f"Cartesian Coordinates: ({x}, {y}, {z})")

r, theta, phi = cartesian_to_spherical(x_coord, y_coord, z_coord)
print(f"Spherical Coordinates: (r={r}, theta={theta}, phi={phi})")

try:
    with open(f'/Users/shrinivassampathmuthupalaniyappan/Desktop/Courses/Capstone/Local_Copy/Output/phone_data/M04/dh_list.pkl','rb') as file:
        loaded_list = pickle.load(file)
        print(loaded_list)
except FileNotFoundError:
    print(f"The file 'M03' does not exist.")

