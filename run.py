from Imports import surfacemapper as sm, simulation as sim

swf = sm.generate_swf()
ae = sm.generate_ae_grid((5, 5))
to = sm.generate_to_grid((5, 5))

solarsim = sim.SurfaceImplantation(ae, to, swf, False, 48)
solarsim.run_simulation()