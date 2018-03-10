import numpy as np
import random
from Imports import surfacemapper as sm
import matplotlib.pyplot as plt
from threading import Thread
from collections import defaultdict

class SurfaceImplantation():

    def __init__(self, omat, to, days):
        self.__omat = omat
        self.__solar_wind_flux = {}
        self.__titanium_oxide = to
        self.__hrefgrid = self.generate_empty_matrix(np.shape(omat))
        self.__trefgrid = self.generate_empty_matrix(np.shape(omat))
        self.__heliumrefgrid = self.generate_empty_matrix(np.shape(omat))
        self.__hretgrid = self.generate_empty_matrix(np.shape(omat))
        self.__tretgrid = self.generate_empty_matrix(np.shape(omat))
        self.__heliumretgrid = self.generate_empty_matrix(np.shape(omat))
        self.__logrid = self.generate_empty_matrix(np.shape(omat))
        self.__days = days
        self.__lunar_oxygen = {}
        self.__hydrogen_particles_reflected = {}
        self.__helium_particles_reflected = {}
        self.__trace_particles_reflected = {}
        self.__hydrogen_particles_retained = {}
        self.__helium_particles_retained = {}
        self.__trace_particles_retained = {}
        self.__hydrogen_ref_low = 0
        self.__hydrogen_ref_med = 0
        self.__hydrogen_ret_high = 0
        self.__hydrogen_ret_med = 0

    def generate_empty_matrix(self, size):
        mat = []
        for i in range(size[0]):
            mat.append([0] * size[1])
        return np.matrix(mat)

    def qualify_omat(self, omat):
        if omat < 0.93:
            return 'LOW'
        elif omat > 0.96:
            return 'HIGH'
        return 'MEDIUM'

    def qualify_to(self, to):
        if to < 10:
            return 'LOW'
        elif to > 15:
            return 'HIGH'
        return 'MEDIUM'

    def qualify_surface_temp(self, time):
        if time >= 6 and time <= 18:
            return 'DAY'
        return 'NIGHT'

    def qualify_swf(self, swf):
        if swf < 3:
            return 'LOW'
        elif swf > 6:
            return 'HIGH'
        return 'MEDIUM'

    def lunar_oxygen(self, time, solar_blackout = False):
        if not solar_blackout:
            self.__hydrogen_particles_retained[time] -= 1
            self.__lunar_oxygen[time] += 1
        else:
            self.__lunar_oxygen[time] += np.random.randint(200, 500)

    def hydrotrace_implantation(self, time, refgrid, retgrid, num_particles, is_hydrogen = True):
        omat = self.__omat
        to = self.__titanium_oxide
        rows, cols = np.shape(omat)
        for i in range(rows):
            for j in range(cols):
                particles = num_particles
                while particles:
                    qomat = self.qualify_omat(omat[i, j])
                    if qomat == 'LOW':
                        if is_hydrogen:
                            self.__hydrogen_particles_reflected[time] += 1
                            self.__hydrogen_ref_low += 1
                        else:
                            self.__trace_particles_reflected[time] +=1
                        refgrid[i, j] += 1
                    elif qomat == 'HIGH':
                        if is_hydrogen:
                            self.__hydrogen_particles_retained[time] += 1
                            self.__hydrogen_ret_high += 1
                        else:
                            self.__trace_particles_retained[time] += 1
                        retgrid[i, j] += 1
                        if is_hydrogen:
                            qto = self.qualify_to(to[i, j])
                            if qto == 'HIGH':
                                self.__logrid[i,j] += 1
                                self.lunar_oxygen(time)
                    else:
                        qst = self.qualify_surface_temp(time[1])
                        if qst == 'DAY':
                            if (is_hydrogen):
                                self.__hydrogen_particles_reflected[time] += 1
                                self.__hydrogen_ref_med += 1
                            else:
                                self.__trace_particles_reflected[time] += 1
                            refgrid[i, j] += 1
                        else:
                            if (is_hydrogen):
                                self.__hydrogen_particles_retained[time] += 1
                                self.__hydrogen_ret_med += 1
                            else:
                                self.__trace_particles_retained[time] += 1
                            retgrid[i, j] += 1
                            if is_hydrogen:
                                qto = self.qualify_to(to[i, j])
                                if qto == 'HIGH':
                                    self.__logrid[i, j] += 1
                                    self.lunar_oxygen(time)
                    particles -= 1
        print("Num particles = ", num_particles)

    def hydrogen_implantation(self, time, numh):
        self.__lunar_oxygen[time] = 0
        if numh > 0:
            self.hydrotrace_implantation(time, self.__hrefgrid, self.__hretgrid, numh)

    def heavy_trace_implantation(self, time, numtrace):
        if numtrace > 0:
            self.hydrotrace_implantation(time, self.__trefgrid, self.__tretgrid, numtrace, False)

    def helium_implantation(self, time, numhe):
        if numhe > 0:
            omat = self.__omat
            to = self.__titanium_oxide
            swf = self.__solar_wind_flux
            rows, cols = np.shape(omat)
            for i in range(rows):
                for j in range(cols):
                    particles = numhe
                    while particles:
                        qomat = self.qualify_omat(omat[i, j])
                        qto = self.qualify_to(to[i, j])
                        qswf = self.qualify_swf(swf[time[1]])
                        if qomat == 'HIGH' and qto == 'HIGH' and qswf == 'HIGH':
                            self.__helium_particles_retained[time] += 1
                            self.__heliumretgrid[i, j] += 1
                        else:
                            self.__helium_particles_reflected[time] += 1
                            self.__heliumrefgrid[i, j] += 1
                        particles -= 1
            print("He = ", numhe)

    def get_particle_proportions(self, time):
        cme = self.__cme
        total_particles = sm.get_total_particles(time, cme)
        velocity = sm.get_velocity(cme)
        self.__solar_wind_flux[time] = sm.get_solar_flux(total_particles, velocity, time) % 10
        if not cme:
            numh = round(0.95 * total_particles)
            numhe = (random.random() * 100) % 4
            if numhe < 2:
                numhe += 2.
            numhe = round(numhe/100. * total_particles)
        else:
            numh = round(0.8 * total_particles)
            numhe = (random.random() * 100) % random.randint(10, 20)
            if numhe < 10:
                numhe += 10.
            numhe = round(numhe/100. * total_particles)
        numtrace = round(total_particles - numh - numhe)
        return numh, numhe, numtrace

    def show_reflection_plots(self, time):
        plt.subplot(311)
        plt.xticks(np.arange(min(time), max(time) + 1, 1.0))
        plt.tight_layout()
        plt.title("Hydrogen Reflected")
        plt.plot(time, list(self.__hydrogen_particles_reflected.values()), 'b-')
        plt.xlabel("Hr")
        plt.ylabel("Particles")
        plt.subplot(312)
        plt.xticks(np.arange(min(time), max(time) + 1, 1.0))
        plt.tight_layout()
        plt.xlabel("Hr")
        plt.ylabel("Particles")
        plt.title("Helium Reflected")
        plt.plot(time, list(self.__helium_particles_reflected.values()), 'b-')
        plt.subplot(313)
        plt.xticks(np.arange(min(time), max(time) + 1, 1.0))
        plt.tight_layout()
        plt.xlabel("Hr")
        plt.ylabel("Particles")
        plt.title("Trace Reflected")
        plt.plot(time, list(self.__trace_particles_reflected.values()), 'b-')
        plt.show()

    def show_retain_plots(self, time):
        plt.subplot(311)
        plt.xticks(np.arange(min(time), max(time) + 1, 1.0))
        plt.tight_layout()
        plt.xlabel("Hr")
        plt.ylabel("Particles")
        plt.title("Hydrogen Retained")
        plt.plot(time, list(self.__hydrogen_particles_retained.values()), 'r-')
        plt.subplot(312)
        plt.xticks(np.arange(min(time), max(time) + 1, 1.0))
        plt.tight_layout()
        plt.xlabel("Hr")
        plt.ylabel("Particles")
        plt.title("Helium Retained")
        plt.plot(time, list(self.__helium_particles_retained.values()), 'r-')
        plt.subplot(313)
        plt.xticks(np.arange(min(time), max(time) + 1, 1.0))
        plt.tight_layout()
        plt.xlabel("Hr")
        plt.ylabel("Particles")
        plt.title("Trace Retained")
        plt.plot(time, list(self.__trace_particles_retained.values()), 'r-')
        plt.show()

    def show_oxygen_plot(self, time):
        plt.title("O2 Liberated")
        plt.xticks(np.arange(min(time), max(time) + 1, 1.0))
        plt.plot(time, list(self.__lunar_oxygen.values()))
        plt.show()

    def show_plots(self, time):
        self.show_reflection_plots(time)
        self.show_retain_plots(time)
        self.show_oxygen_plot(time)

    def daily_particles(self, time_dict):
        daily_dict = defaultdict(lambda: 0)
        for k in time_dict.keys():
            daily_dict[k[0]] += time_dict[k]
        return daily_dict

    def write_to_file(self):
        dicts = [self.__lunar_oxygen, self.__hydrogen_particles_reflected, self.__hydrogen_particles_retained,
                 self.__helium_particles_reflected, self.__helium_particles_retained, self.__trace_particles_reflected, self.__trace_particles_retained]
        file_names = ['lo', 'href', 'hret', 'heref', 'heret', 'tref', 'tret']
        for index, dict in enumerate(dicts):
            fp = open('Hourly_' + file_names[index] + '.csv', 'w')
            for k in dict.keys():
                fp.write(str(k[0]) + "," + str(k[1]) + "," + str(dict[k]) + "\n")
            fp.close()

        for index, dict in enumerate(dicts):
            fp = open('Daily_' + file_names[index] + '.csv', 'w')
            dict = self.daily_particles(dict)
            for k in dict.keys():
                fp.write(str(k) + "," + str(dict[k]) + "\n")
            fp.close()

    def get_solar_blackout_days(self, cme_day):
        while True:
            d = round((np.random.random() * 100)) % (self.__days - 5)
            d = range(d, d+5)
            if cme_day not in d and cme_day + 1 not in d:
                return d

    def init_dicts(self, time):
        dicts = [self.__lunar_oxygen, self.__hydrogen_particles_reflected, self.__hydrogen_particles_retained,
                 self.__helium_particles_reflected, self.__helium_particles_retained, self.__trace_particles_reflected,
                 self.__trace_particles_retained]
        for dict in dicts:
            dict[time] = 0

    def grid_to_image(self):
        grids = [self.__logrid, self.__hrefgrid, self.__hretgrid, self.__heliumrefgrid, self.__heliumretgrid, self.__trefgrid, self.__tretgrid]
        file_names = ["Lunar.png", "Href.png", "Hret.png", "Heliumref.png", "Heliumret.png", "Tref.png", "Tret.png"]
        for index, grid in enumerate(grids):
            #print(file_names[index] + ": ",  grid)
            sm.mat_to_image(grid, file_names[index])

    def run_simulation(self):
        days = range(self.__days)
        threads = []
        cme_day = round((np.random.random() * 100)) % self.__days
        solar_blackout = self.get_solar_blackout_days(cme_day)
        for d in days:
            self.__cme = False
            if d == cme_day or d == cme_day + 1:
                self.__cme = True
            for t in range(24):
                self.init_dicts((d,t))
                if d in solar_blackout:
                    self.lunar_oxygen((d,t), True)
                else:
                    numh, numhe, numtrace = self.get_particle_proportions(t)
                    print(numh, numhe, numtrace)
                    thread1 = Thread(target = self.hydrogen_implantation, args = ((d, t), numh))
                    thread2 = Thread(target = self.heavy_trace_implantation, args = ((d, t), numtrace))
                    thread3 = Thread(target = self.helium_implantation, args = ((d, t), numhe))
                    threads.append(thread1)
                    threads.append(thread2)
                    threads.append(thread3)
                    thread1.start()
                    thread2.start()
                    thread3.start()

        for t in threads:
            t.join()

        self.grid_to_image()
        self.write_to_file()
        #self.show_plots(days)
        print('\nHydrogen Retained High OMAT: ', self.__hydrogen_ret_high)
        print('\nHydrogen Retained Medium OMAT Night Side: ', self.__hydrogen_ret_med)

        print('\nHydrogen Reflected Low OMAT: ', self.__hydrogen_ref_low)
        print('\nHydrogen Reflected Medium OMAT Day Side: ', self.__hydrogen_ref_med)