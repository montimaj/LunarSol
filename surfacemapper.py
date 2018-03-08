import math
from PIL import Image
from colour import Color
import matplotlib.pyplot as plt
import random
import numpy as np

def is_day(time):
    return time >= 6 and time <= 18

def get_theta(time):
    return (12 - time)/24.

def get_temperature(time):
    return 280*math.cos(get_theta(time))**0.25 + 100.

def get_solar_flux(nsw, vsw, time):
    if not is_day(time):
        nsw /= 500
        vsw /= 500
    return nsw*vsw*math.cos(get_theta(time))

def generate_graphs(nsw, vsw):
    val1 = []
    val2 = []
    t = range(0, 25)
    for time in t:
        temp = get_temperature(time)
        sf = get_solar_flux(nsw, vsw, time)
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
    t = range(0, 24)
    for time in t:
        img = Image.new('RGB', size)
        colorize(img, time).save('T'+str(time)+'.png')

def generate_swf(nsw, vsw):
    swf = []
    for time in range(0, 24):
        swf.append(get_solar_flux(nsw, vsw, time))
    return swf

def generate_ae_grid(size):
    mat = []
    for i in range(size[0]):
        row = []
        for j in range(size[1]):
            row.append(random.random())
        mat.append(row)
    return np.matrix(mat)

def generate_to_grid(size):
    mat = []
    for i in range(size[0]):
        row = []
        for j in range(size[1]):
            row.append(random.random()/10.)
        mat.append(row)
    return np.matrix(mat)


COLOR = get_colors()

