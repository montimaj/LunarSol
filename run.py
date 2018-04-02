from multiprocessing import Pool
from Imports import surfacemapper as sm, simulation as sim

#grid_size = (8694, 2081)
grid_size = (512, 512)
p = Pool(processes = 2)
omat_proc = p.apply_async(sm.generate_omat_grid, (grid_size, 0.959305, 0.024487))
to_proc = p.apply_async(sm.generate_to_grid, (grid_size, 12.522041,3.443365))
omat = omat_proc.get()
to = to_proc.get()
solarsim = sim.SurfaceImplantation(omat, to, 30)
solarsim.run_simulation()