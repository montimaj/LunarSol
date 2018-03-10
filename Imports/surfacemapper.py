import math
from PIL import Image
import numpy as np

def is_day(time):
    return time >= 6 and time <= 18

def get_theta(time):
    return (12 - time)/24.

def get_temperature(time):
    return 280*math.cos(get_theta(time))**0.25 + 100.

def get_total_particles(time, cme):
    total_particles = np.random.randint(int(4E+6), int(5E+6))
    if cme:
        total_particles *= 10
    if not is_day(time):
        total_particles /= 500.
    return total_particles

def get_velocity(cme):
    v = (np.random.random()*100) % 4
    if v < 3:
        v += 3.
    v *= 1E+5
    if cme:
        v *= 2
    return v

def get_solar_flux(nsw, vsw, time):
    return nsw*vsw*math.cos(get_theta(time))

def mat_to_image(mat, imgname):
    rows, cols = np.shape(mat)
    outimg = Image.new('L', (cols, rows))
    for i in range(rows):
        for j in range(cols):
            val = int((mat[i, j] / np.max(mat)) * 255)
            outimg.putpixel((j,i), (val,))
    outimg.save(imgname)

def generate_omat_grid(size, mean, sd):
    mat = []
    for i in range(size[0]):
        omat = np.random.normal(mean, sd, size[1])
        mat.append(omat)
    mat = np.matrix(mat)
    mat_to_image(mat, 'OMAT.png')
    return mat

def generate_to_grid(size, mean, sd):
    mat = []
    for i in range(size[0]):
        to = np.random.normal(mean,sd, size[1])
        mat.append(to)
    mat = np.matrix(mat)
    mat_to_image(mat, 'TiO2.png')
    return mat

