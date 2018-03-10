from Imports import surfacemapper as sm, simulation as sim

swf = sm.generate_swf()
grid_size = (8694, 2081)
#grid_size = (10,10)
omat = sm.generate_omat_grid(grid_size, 0.959305, 0.024487)
to = sm.generate_to_grid(grid_size, 12.522041,3.443365)

solarsim = sim.SurfaceImplantation(omat, to, swf, 30)
solarsim.run_simulation()