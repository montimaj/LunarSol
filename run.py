from Imports import surfacemapper as sm, simulation as sim

swf = sm.generate_swf(5E+6, 4E+5)
ae = sm.generate_ae_grid((512,512))
to = sm.generate_to_grid((512, 512))

solarsim = sim.SurfaceImplantation(ae, to, swf, 24)
solarsim.run_simulation()