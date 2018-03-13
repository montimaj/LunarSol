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

    def lunar_oxygen(self, time, num_particles = 0, solar_blackout = False):
        if solar_blackout:
            self.__lunar_oxygen[time] = np.random.randint(200, 500)
        else:
            self.__hydrogen_particles_retained[time] -= num_particles
            self.__lunar_oxygen[time] += num_particles

    def hydrotrace_implantation(self, time, refgrid, retgrid, num_particles, is_hydrogen = True):
        omat = self.__omat
        to = self.__titanium_oxide
        rows, cols = np.shape(omat)
        for i in range(rows):
            for j in range(cols):
                qomat = self.qualify_omat(omat[i, j])
                if qomat == 'LOW':
                    if is_hydrogen:
                        self.__hydrogen_particles_reflected[time] += num_particles
                        self.__hydrogen_ref_low += num_particles
                    else:
                        self.__trace_particles_reflected[time] += num_particles
                    refgrid[i, j] += num_particles
                elif qomat == 'HIGH':
                    if is_hydrogen:
                        self.__hydrogen_particles_retained[time] += num_particles
                        self.__hydrogen_ret_high += num_particles
                    else:
                        self.__trace_particles_retained[time] += num_particles
                    retgrid[i, j] += num_particles
                    if is_hydrogen:
                        qto = self.qualify_to(to[i, j])
                        if qto == 'HIGH':
                            self.__logrid[i, j] += num_particles
                            retgrid[i, j] -= num_particles
                            self.lunar_oxygen(time, num_particles)
                else:
                    qst = self.qualify_surface_temp(time[1])
                    if qst == 'DAY':
                        if (is_hydrogen):
                            self.__hydrogen_particles_reflected[time] += num_particles
                            self.__hydrogen_ref_med += num_particles
                        else:
                            self.__trace_particles_reflected[time] += num_particles
                        refgrid[i, j] += num_particles
                    else:
                        if (is_hydrogen):
                            self.__hydrogen_particles_retained[time] += num_particles
                            self.__hydrogen_ret_med += num_particles
                        else:
                            self.__trace_particles_retained[time] += num_particles
                        retgrid[i, j] += num_particles
                        if is_hydrogen:
                            qto = self.qualify_to(to[i, j])
                            if qto == 'HIGH':
                                self.__logrid[i, j] += num_particles
                                retgrid[i, j] -= num_particles
                                self.lunar_oxygen(time, num_particles)

    def hydrogen_implantation(self, time, numh):
        if numh > 0:
            self.hydrotrace_implantation(time, self.__hrefgrid, self.__hretgrid, numh)
        print("Done Hydrogen")

    def heavy_trace_implantation(self, time, numtrace):
        if numtrace > 0:
            self.hydrotrace_implantation(time, self.__trefgrid, self.__tretgrid, numtrace, False)
        print("Done Trace")

    def helium_implantation(self, time, swf, numhe):
        if numhe > 0:
            omat = self.__omat
            to = self.__titanium_oxide
            rows, cols = np.shape(omat)
            swfmean = np.mean(swf)
            for i in range(rows):
                for j in range(cols):
                    qomat = self.qualify_omat(omat[i, j])
                    qto = self.qualify_to(to[i, j])
                    qswf = self.qualify_swf(swf[0, time[1]], swfmean)
                    if qomat == 'HIGH' and qto == 'HIGH' and qswf == 'HIGH':
                        self.__helium_particles_retained[time] += numhe
                        self.__heliumretgrid[i, j] += numhe
                    else:
                        self.__helium_particles_reflected[time] += numhe
                        self.__heliumrefgrid[i, j] += numhe
        print("Done Helium")

    def get_particle_proportions(self, cme):
        numh = {}
        numhe = {}
        numtrace = {}
        swf = {}
        for time in range(24):
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
        swf = swf/np.max(swf)
        return numh, numhe, numtrace, swf

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
            cme = False
            if d == cme_day or d == cme_day + 1:
                cme = True
            numh, numhe, numtrace, swf = self.get_particle_proportions(cme)
            for t in range(24):
                self.init_dicts((d,t))
                if d in solar_blackout:
                    self.lunar_oxygen((d,t), solar_blackout = True)
                    print("Blackout")
                else:
                    print("(D, T) =", (d,t), "Hydrogen =", numh[t], "Helium =", numhe[t], "Trace =", numtrace[t])
                    thread1 = Thread(target = self.hydrogen_implantation, args = ((d, t), numh[t]))
                    thread2 = Thread(target = self.heavy_trace_implantation, args = ((d, t), numtrace[t]))
                    thread3 = Thread(target = self.helium_implantation, args = ((d, t), swf, numhe[t]))
                    threads.append(thread1)
                    threads.append(thread2)
                    threads.append(thread3)
                    thread1.start()
                    thread2.start()
                    thread3.start()
                    if len(threads) > cpu_count():
                        for thread in threads:
                            print("Waiting")
                            thread.join()
                        threads.clear()

        self.grid_to_image()
        self.write_to_file()

        print('\nHydrogen Retained High OMAT: ', self.__hydrogen_ret_high)
        print('\nHydrogen Retained Medium OMAT Night Side: ', self.__hydrogen_ret_med)

        print('\nHydrogen Reflected Low OMAT: ', self.__hydrogen_ref_low)
        print('\nHydrogen Reflected Medium OMAT Day Side: ', self.__hydrogen_ref_med)