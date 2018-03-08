from PIL import Image
import numpy as np
import random

class SurfaceImplantation():

    def __init__(self, ae, to, swf, particles, running_time_hrs):
        self.__activation_energy = ae
        self.__titanium_oxide = to
        self.__solar_wind_flux = swf
        self.__hgrid = Image.new('L', np.shape(ae))
        self.__tgrid = Image.new('L', np.shape(ae))
        self.__heliumgrid = Image.new('L', np.shape(ae))
        self.__particles = particles
        self.__lunar_oxygen = 0
        self.__running_time = running_time_hrs

    def qualify_activation_energy(self, ae):
        if ae < 0.2:
            return 'LOW'
        elif ae > 0.9:
            return 'HIGH'
        return 'MEDIUM'

    def qualify_to(self, to):
        if to < 0.008:
            return 'LOW'
        elif to > 0.06:
            return 'HIGH'
        return 'MEDIUM'

    def qualify_surface_temp(self, time):
        if time >= 6 and time <= 18:
            return 'DAY'
        return 'NIGHT'

    def qualify_swf(self, swf):
        if swf < 0.3:
            return 'LOW'
        elif swf > 0.7:
            return 'HIGH'
        return 'MEDIUM'

    def lunar_oxygen(self):
        self.__lunar_oxygen += 1

    def hydrotrace_implantation(self, time, grid, is_hydrogen = True):
        ae = self.__activation_energy
        to = self.__titanium_oxide
        cols, rows = np.shape(ae)
        for i in range(rows):
            for j in range(cols):
                pos = (j, i)
                qae = self.qualify_activation_energy(ae[i, j])
                if qae == 'LOW':
                    grid.putpixel(pos, (random.randint(200, 255),))
                elif qae == 'HIGH':
                    grid.putpixel(pos, (random.randint(0, 50),))
                    qto = self.qualify_to(to[i, j])
                    if qto == 'HIGH' and is_hydrogen:
                        self.lunar_oxygen()
                else:
                    qst = self.qualify_surface_temp(time)
                    if qst == 'DAY':
                        if time == 12:
                            grid.putpixel(pos, (255,))
                        else:
                            grid.putpixel(pos, (random.randint(150, 200),))
                    else:
                        if time == 0:
                            grid.putpixel(pos, (0,))
                        else:
                            grid.putpixel(pos, (random.randint(20, 70),))
                        qto = self.qualify_to(to[i, j])
                        if qto == 'HIGH' and is_hydrogen:
                            self.lunar_oxygen()

    def hydrogren_implantation(self, time):
        self.hydrotrace_implantation(time, self.__hgrid)


    def heavy_trace_implantation(self, time):
        self.hydrotrace_implantation(time, self.__tgrid, False)

    def helium_implantation(self, time):
        ae = self.__activation_energy
        to = self.__titanium_oxide
        swf = self.__solar_wind_flux
        cols, rows = np.shape(ae)
        for i in range(rows):
            for j in range(cols):
                qae = self.qualify_activation_energy(ae[i,j])
                qto = self.qualify_to(to[i,j])
                qswf = self.qualify_swf(swf[time])
                if qae == 'HIGH' and qto == 'HIGH' and qswf == 'HIGH':
                    self.__heliumgrid.putpixel((j,i), (random.randint(0, 50),))
                else:
                    self.__heliumgrid.putpixel((j, i), (random.randint(200, 255),))

    def run_simulation(self):
        for t in range(self.__running_time):
            r = random.random()
            if r <= 0.95:
                self.hydrogren_implantation(t)
            elif r >= 0.96 and r <= 0.98:
                self.helium_implantation(t)
            else:
                self.heavy_trace_implantation(t)
        print('Lunar O2 = ', self.__lunar_oxygen)
        self.__hgrid.save('Hydrogen.png')
        self.__heliumgrid.save('Helium.png')
        self.__tgrid.save('Trace.png')