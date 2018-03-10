from PIL import Image
import numpy as np
import random
from Imports import surfacemapper as sm
import matplotlib.pyplot as plt
from threading import Thread

class SurfaceImplantation():

    def __init__(self, ae, to, swf, cme, running_time_hrs):
        self.__activation_energy = ae
        self.__titanium_oxide = to
        self.__solar_wind_flux = swf
        self.__hgrid = Image.new('L', np.shape(ae))
        self.__tgrid = Image.new('L', np.shape(ae))
        self.__heliumgrid = Image.new('L', np.shape(ae))
        self.__running_time = running_time_hrs
        self.__cme = cme
        self.__lunar_oxygen = {}
        self.__hydrogen_particles_reflected = {}
        self.__helium_particles_reflected = {}
        self.__trace_particles_reflected = {}
        self.__hydrogen_particles_retained = {}
        self.__helium_particles_retained = {}
        self.__trace_particles_retained = {}

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

    def lunar_oxygen(self, time):
        self.__hydrogen_particles_retained[time] -= 1
        self.__lunar_oxygen[time] += 1

    def hydrotrace_implantation(self, time, grid, num_particles, is_hydrogen = True):
        ae = self.__activation_energy
        to = self.__titanium_oxide
        cols, rows = np.shape(ae)
        for i in range(rows):
            for j in range(cols):
                particles = num_particles
                while particles:
                    pos = (j, i)
                    qae = self.qualify_activation_energy(ae[i, j])
                    if qae == 'LOW':
                        if is_hydrogen:
                            self.__hydrogen_particles_reflected[time] += 1
                        else:
                            self.__trace_particles_reflected[time] +=1
                        self.__hgrid.putpixel(pos, (random.randint(200, 255),))
                    elif qae == 'HIGH':
                        if is_hydrogen:
                            self.__hydrogen_particles_retained[time] += 1
                        else:
                            self.__trace_particles_retained[time] += 1
                        grid.putpixel(pos, (random.randint(0, 50),))
                        if is_hydrogen:
                            qto = self.qualify_to(to[i, j])
                            if qto == 'HIGH':
                                self.lunar_oxygen(time)
                    else:
                        qst = self.qualify_surface_temp(time)
                        if (is_hydrogen):
                            self.__hydrogen_particles_reflected[time] += 1
                        else:
                            self.__trace_particles_reflected[time] += 1
                        if qst == 'DAY':
                            if time == 12:
                                grid.putpixel(pos, (255,))
                            else:
                                grid.putpixel(pos, (random.randint(150, 200),))
                        else:
                            if (is_hydrogen):
                                self.__hydrogen_particles_retained[time] += 1
                            else:
                                self.__trace_particles_retained[time] += 1
                            if time == 0:
                                grid.putpixel(pos, (0,))
                            else:
                                grid.putpixel(pos, (random.randint(20, 70),))
                            if is_hydrogen:
                                qto = self.qualify_to(to[i, j])
                                if qto == 'HIGH':
                                    self.lunar_oxygen(time)
                    particles -= 1
        print("Num particles = ", num_particles)

    def hydrogen_implantation(self, time, numh):
        self.__hydrogen_particles_retained[time] = 0
        self.__hydrogen_particles_reflected[time] = 0
        self.__lunar_oxygen[time] = 0
        if numh > 0:
            self.hydrotrace_implantation(time, self.__hgrid, numh)

    def heavy_trace_implantation(self, time, numtrace):
        self.__trace_particles_retained[time] = 0
        self.__trace_particles_reflected[time] = 0
        if numtrace > 0:
            self.hydrotrace_implantation(time, self.__tgrid, numtrace, False)

    def helium_implantation(self, time, numhe):
        self.__helium_particles_retained[time] = 0
        self.__helium_particles_reflected[time] = 0
        if numhe > 0:
            ae = self.__activation_energy
            to = self.__titanium_oxide
            swf = self.__solar_wind_flux
            cols, rows = np.shape(ae)
            for i in range(rows):
                for j in range(cols):
                    particles = numhe
                    while particles:
                        qae = self.qualify_activation_energy(ae[i,j])
                        qto = self.qualify_to(to[i,j])
                        qswf = self.qualify_swf(swf[time%24])
                        if qae == 'HIGH' and qto == 'HIGH' and qswf == 'HIGH':
                            self.__helium_particles_retained[time] += 1
                            self.__heliumgrid.putpixel((j,i), (random.randint(0, 50),))
                        else:
                            self.__helium_particles_reflected[time] += 1
                            self.__heliumgrid.putpixel((j, i), (random.randint(200, 255),))
                        particles -= 1
            print("He = ", numhe)

    def get_particle_proportions(self, time):
        cme = self.__cme
        total_particles = sm.get_total_particles(time, cme)
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

    def run_simulation(self):
        time = range(self.__running_time)
        threads = []
        for t in time:
            numh, numhe, numtrace = self.get_particle_proportions(t%24)
            print(numh, numhe, numtrace)
            thread1 = Thread(target = self.hydrogen_implantation, args = (t, numh))
            thread2 = Thread(target = self.heavy_trace_implantation, args = (t, numtrace))
            thread3 = Thread(target = self.helium_implantation, args = (t, numhe))
            threads.append(thread1)
            threads.append(thread2)
            threads.append(thread3)
            thread1.start()
            thread2.start()
            thread3.start()

        for t in threads:
            t.join()

        self.__hgrid.save('Hydrogen.png')
        self.__heliumgrid.save('Helium.png')
        self.__tgrid.save('Trace.png')

        self.show_plots(time)
