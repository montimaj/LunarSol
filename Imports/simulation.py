import numpy as np
import random
from Imports import surfacemapper as sm
from threading import Thread
from collections import defaultdict
from multiprocessing import cpu_count

class SurfaceImplantation():

    def __init__(self, omat, to, days):
        self.__omat = omat
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
        elif omat > 0.95:
            return 'HIGH'
        return 'MEDIUM'

    def qualify_to(self, to):
        if to > 13:
            return 'HIGH'
        return 'LOW'

    def qualify_surface_temp(self, time):
        if time >= 6 and time <= 18:
            return 'DAY'
        return 'NIGHT'

    def qualify_swf(self, swf, swfmean):
        if swf > swfmean:
            return 'HIGH'
        return 'LOW'

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
                                self.__logrid[i, j] += 1
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
            swfmean = np.mean(swf)
            for i in range(rows):
                for j in range(cols):
                    particles = numhe
                    while particles:
                        qomat = self.qualify_omat(omat[i, j])
                        qto = self.qualify_to(to[i, j])
                        qswf = self.qualify_swf(swf[0, time[1]], swfmean)
                        if qomat == 'HIGH' and qto == 'HIGH' and qswf == 'HIGH':
                            self.__helium_particles_retained[time] += 1
                            self.__heliumretgrid[i, j] += 1
                        else:
                            self.__helium_particles_reflected[time] += 1
                            self.__heliumrefgrid[i, j] += 1
                        particles -= 1
            print("He = ", numhe)

    def get_particle_proportions(self):
        numh = {}
        numhe = {}
        numtrace = {}
        swf = {}
        for time in range(24):
            cme = self.__cme
            total_particles = sm.get_total_particles(time, cme)
            velocity = sm.get_velocity(cme)
            swf[time] = sm.get_solar_flux(total_particles, velocity, time)
            if not cme:
                numh[time] = round(0.95 * total_particles)
                numhe[time] = (random.random() * 100) % 4
                if numhe[time] < 2:
                    numhe[time] += 2.
                numhe[time] = round(numhe[time]/100. * total_particles)
            else:
                numh[time] = round(0.8 * total_particles)
                numhe[time] = (random.random() * 100) % random.randint(10, 20)
                if numhe[time] < 10:
                    numhe[time] += 10.
                numhe[time] = round(numhe[time]/100. * total_particles)
            numtrace[time] = round(total_particles - numh[time] - numhe[time])
        swf = np.matrix(list(swf.values()))
        self.__solar_wind_flux = swf/np.max(swf)
        return numh, numhe, numtrace

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
        file_names = ["Lunar", "Href", "Hret", "Heliumref", "Heliumret", "Tref", "Tret"]
        for index, grid in enumerate(grids):
            sm.save_img_16(np.array(grid), file_names[index])

    def run_simulation(self):
        days = range(self.__days)
        threads = []
        cme_day = round((np.random.random() * 100)) % self.__days
        solar_blackout = self.get_solar_blackout_days(cme_day)
        for d in days:
            self.__cme = False
            if d == cme_day or d == cme_day + 1:
                self.__cme = True
            numh, numhe, numtrace = self.get_particle_proportions()
            for t in range(24):
                self.init_dicts((d,t))
                if d in solar_blackout:
                    self.lunar_oxygen((d,t), True)
                    print("Blackout")
                else:
                    print("Hydrogen =", numh[t], "Helium =", numhe[t], "Trace =", numtrace[t])
                    thread1 = Thread(target = self.hydrogen_implantation, args = ((d, t), numh[t]))
                    thread2 = Thread(target = self.heavy_trace_implantation, args = ((d, t), numtrace[t]))
                    thread3 = Thread(target = self.helium_implantation, args = ((d, t), numhe[t]))
                    threads.append(thread1)
                    threads.append(thread2)
                    threads.append(thread3)
                    thread1.start()
                    thread2.start()
                    thread3.start()
                    if len(threads) == cpu_count():
                        for t in threads:
                            t.join()
                        threads.clear()
        self.grid_to_image()
        self.write_to_file()

        print('\nHydrogen Retained High OMAT: ', self.__hydrogen_ret_high)
        print('\nHydrogen Retained Medium OMAT Night Side: ', self.__hydrogen_ret_med)

        print('\nHydrogen Reflected Low OMAT: ', self.__hydrogen_ref_low)
        print('\nHydrogen Reflected Medium OMAT Day Side: ', self.__hydrogen_ref_med)