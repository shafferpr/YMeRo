#!/usr/bin/env python
import udevicex as udx

# Simulation time-step
dt = 0.001

# 1 simulation task
ranks  = (1, 1, 1)

# Domain setup
domain = (8, 16, 30)

# Applied extra force for periodic poiseuille flow
f = 1

# Create the coordinator, this should precede any other setup from udevicex package
u = udx.udevicex(ranks, domain, debug_level=2, log_filename='log')

pv = udx.ParticleVectors.ParticleVector('pv', mass = 1)   # Create a simple particle vector
ic = udx.InitialConditions.Uniform(density=8)             # Specify uniform random initial conditions
u.registerParticleVector(pv=pv, ic=ic)                    # Register the PV and initialize its particles

# Create and register DPD interaction with specific parameters
dpd = udx.Interactions.DPD('dpd', 1.0, a=10.0, gamma=10.0, kbt=1.0, dt=dt, power=0.5)
u.registerInteraction(dpd)

# Tell the simulation that the particles of pv interact with dpd interaction
u.setInteraction(dpd, pv, pv)

# Create and register Velocity-Verlet integrator with extra force
vv = udx.Integrators.VelocityVerlet_withPeriodicForce('vv', dt=dt, force=f, direction='x')
u.registerIntegrator(vv)

# This integrator will be used to advance pv particles
u.setIntegrator(vv, pv)

# Set the dumping parameters
sampleEvery = 2
dumpEvery   = 1000
binSize     = (1., 1., 1.)

# Write some simulation statistics on the screen
u.registerPlugins(udx.Plugins.createStats('stats', every=500))

# Create and register XDMF plugin
field = udx.Plugins.createDumpAverage('field', [pv],
                                      sampleEvery, dumpEvery, binSize,
                                      [("velocity", "vector_from_float8")], 'h5/solvent-')
u.registerPlugins(field)

# Run 5002 time-steps
u.run(5002)