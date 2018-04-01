import math
from osgeo import gdal
import numpy as np

def is_day(time):
    return time >= 6 and time <= 18

def get_theta(time):
    return (12 - time)/24.

def get_temperature(time):
    return 280*math.cos(get_theta(time))**0.25 + 100.

def get_total_particles(time, cme):
    total_particles = np.random.randint(MIN_PARTICLES, MAX_PARTICLES)
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

def mat_to_image(arr_out, outfile):
    cols, rows = arr_out.shape
    max_val = np.max(arr_out)
    np.savetxt(outfile + "_table.csv", arr_out)
    if max_val != 0:
        arr_out = arr_out/np.max(arr_out)
    np.savetxt(outfile + "_norm_table.csv", arr_out)
    driver = gdal.GetDriverByName("GTiff")
    outfile += '.tiff'
    outdata = driver.Create(outfile, rows, cols, 1, gdal.GDT_Float32)
    outdata.GetRasterBand(1).WriteArray(arr_out)
    outdata.FlushCache()

def generate_omat_grid(size, mean, sd):
    mat = []
    for i in range(size[0]):
        omat = np.random.normal(mean, sd, size[1])
        mat.append(omat)
    mat = np.matrix(mat)
    mat_to_image(np.array(mat), 'OMAT')
    return mat

def generate_to_grid(size, mean, sd):
    mat = []
    for i in range(size[0]):
        to = np.random.normal(mean, sd, size[1])
        mat.append(to)
    mat = np.matrix(mat)
    mat_to_image(np.array(mat), 'TiO2')
    return mat

MIN_PARTICLES = int(4E+6)
MAX_PARTICLES = int(5E+6)