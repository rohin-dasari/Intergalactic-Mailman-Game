import numpy as np
import matplotlib.pyplot as plt

thing = [[0,0], [5,5]] 
thing = np.array(thing)

other_thing = [[0, 0], [0, 10]]
other_thing = np.array(other_thing)
proj = other_thing*np.dot(other_thing, thing)/(np.linalg.norm(other_thing)**2)
plt.plot(thing[:, 0], thing[:, 1], color='blue')
plt.plot(other_thing[:, 0], other_thing[:, 1], color='darkorange')
plt.plot(proj[:, 0], proj[:, 1], color='purple')
plt.show()



