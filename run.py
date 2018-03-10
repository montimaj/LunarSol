from Imports import surfacemapper as sm, simulation as sim

grid_size = (8694, 2081)
#grid_size = (5,5)
omat = sm.generate_omat_grid(grid_size, 0.959305, 0.024487)
to = sm.generate_to_grid(grid_size, 12.522041,3.443365)

solarsim = sim.SurfaceImplantation(omat, to, 30)
solarsim.run_simulation()