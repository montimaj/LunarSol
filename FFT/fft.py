from scipy.fftpack import fft2
from osgeo import gdal
import  numpy as np
from Imports import surfacemapper as sm
import scipy.stats as stat

img = gdal.Open(r"E:/Heliumret.tiff")
x = img.GetRasterBand(1).ReadAsArray()
y = 10 * np.log10(np.abs(fft2(x)))
num  = max(np.abs(np.min(y)), np.abs(np.max(y)))
y /= num
sm.mat_to_image(y, "HeliumFFTPower")
y = y.reshape(y.shape[0] * y.shape[1])
print('MIN = ', np.min(y), 'MAX = ', np.max(y), 'MEAN = ', np.mean(y), 'SD = ', np.sqrt(np.var(y)), 'SKEW = ', stat.skew(y), 'KURT = ', stat.kurtosis(y))