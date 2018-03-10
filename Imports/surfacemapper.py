import math
from PIL import Image
from colour import Color
import matplotlib.pyplot as plt
import numpy as np

def is_day(time):
    return time >= 6 and time <= 18

def get_theta(time):
    return (12 - time)/24.

def get_temperature(time):
    return 280*math.cos(get_theta(time))**0.25 + 100.

def get_total_particles(time, cme):
    total_particles = np.random.randint(int(4E+3), int(5E+3))
    if cme:
        total_particles *= 10
    if not is_day(time):
        total_particles /= 5.
    return total_particles

def get_velocity(time, cme):
    v = (np.random.random()*100) % 4
    if v < 3:
        v += 3.
    v *= 1E+5
    if cme:
        v *= 2
    if not is_day(time):
        v /= 5.
    velocity.append(v)
    return v

def get_solar_flux(time, cme):
    nsw = get_total_particles(time, cme)
    vsw = get_velocity(time, cme)
    return nsw*vsw*math.cos(get_theta(time))

def generate_graphs():
    val1 = []
    val2 = []
    t = range(0, 25)
    for time in t:
        temp = get_temperature(time)
        sf = get_solar_flux(time, False)
        val1.append(temp)
        val2.append(sf)

    plt.subplot(121)
    plt.plot(t, val1)
    plt.subplot(122)
    plt.plot(t, val2)
    plt.show()

def get_colors():
    red = Color("red")
    blue = Color("blue")
    yellow = Color("yellow")
    c = []
    c.append(list(blue.range_to(yellow, 6)))
    c.append(list(yellow.range_to(red, 6)))
    c.append(list(red.range_to(yellow, 6)))
    c.append(list(yellow.range_to(blue, 6)))
    colors = []
    for l in c:
        for v in l:
            r, g, b = v.get_rgb()
            r = round(r*255)
            g = round(g * 255)
            b = round(b * 255)
            colors.append((r,g,b))
    return colors

def colorize(img, time):
    for i in range(img.size[1]):
        for j in range(img.size[0]):
            img.putpixel((j,i), COLOR[time])
    return img

def generate_surface(size):
    t = range(24)
    for time in t:
        img = Image.new('RGB', size)
        colorize(img, time).save('T'+str(time)+'.png')

def generate_swf(cme = False):
    swf = []
    t = range(24)
    for time in t:
        swf.append(get_solar_flux(time, cme))
    plt.subplot(121)
    plt.plot(t, swf)
    plt.title("SWF")
    plt.xlabel("Hr")
    plt.ylabel("swf (/m^2)")
    plt.subplot(122)
    plt.plot(t, velocity)
    plt.title("Velocity")
    plt.xlabel("Hr")
    plt.ylabel("V (m/s)")
    plt.show()
    return swf

def generate_ae_grid(size):
    mat = []
    for i in range(size[0]):
        ae= np.random.normal(0, 1, size[1])
        row = []
        for a in ae:
            a = np.abs(a)
            row.append(a)
        mat.append(row)
    return np.matrix(mat)

def generate_to_grid(size):
    mat = []
    for i in range(size[0]):
        row = []
        to = np.random.normal(0,1, size[1])
        for t in to:
            t = np.abs(t)/10.
            row.append(t)
        mat.append(row)
    return np.matrix(mat)

velocity = []
COLOR = get_colors()

