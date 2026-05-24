# זה פייתון לגאוס תלת מימד  - הגרף שיוצא מסביר אחלה את הרעיון
# click ctrl+shift+p and look for 'Pythos: select interpeter'
#       select the Anaconda environment for the course named course-env
# in the anaconda terminal
#  >conda activate course-env
#  Using conda
# conda install -c conda-forge matplotlib

# Using pip
# pip install matplotlib

import matplotlcdib.pyplot as plt
import numpy as np
# Create a grid of x and y values
x = np.linspace(-3, 3, 100)
y = np.linspace(-3, 3, 100)
x, y = np.meshgrid(x, y)
# Calculate the Gaussian (bell curve) values
z = np.exp(-(x**2 + y**2) / 2)
# Plot
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(x, y, z, cmap='viridis')
plt.title("3D Gaussian")
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")
plt.show()