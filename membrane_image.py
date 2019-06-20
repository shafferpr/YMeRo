import ymero as ymr
import ctypes
ctypes.CDLL("libmpi.so", mode=ctypes.RTLD_GLOBAL)
rc = 1.0      # cutoff radius
density = 2.0 # number density
dt = 0.001
ranks  = (1, 1, 1)
domain = (15.0, 30.0, 30.0)

u = ymr.ymero(ranks, domain, dt, debug_level=3, log_filename='log')

pv  = ymr.ParticleVectors.ParticleVector('pv', mass = 1.0)
ic  = ymr.InitialConditions.Uniform(density)
dpd = ymr.Interactions.DPD('dpd', rc, a=10.0, gamma=10.0, kbt=1.0, power=0.5)
#vv  = ymr.Integrators.VelocityVerlet('vv')
vv = ymr.Integrators.VelocityVerlet_withConstForce('vv',force=[3.0,0.0,0.0])
#vv  = ymr.Integrators.VelocityVerlet_withPeriodicForce('vv',force=1.0,direction="x")
u.registerInteraction(dpd)
u.registerParticleVector(pv, ic)
u.registerIntegrator(vv)

# creation of the walls
# we create a cylindrical pipe passing through the center of the domain along
center = (domain[1]*0.5, domain[2]*0.5) # center in the (yz) plane
radius = 0.5 * domain[1] - rc           # radius needs to be smaller than half of the domain
                                        # because of the frozen particles

#wall2 = ymr.Walls.Cylinder("cylinder", center=center, radius=radius, axis="x", inside=True)
wall2 = ymr.Walls.SDF("sdfwall",sdfFilename="qq.dat")
#u.dumpWalls2XDMF([wall2], h = (0.5, 0.5, 0.5), filename = 'h5/wall') 
u.registerWall(wall2) # register the wall in the coordinator
print("wall registered")
# we now create the frozen particles of the walls
# the following command is running a simulation of a solvent with given density equilibrating with dpd interactions and vv integrator
# for 1000 steps.
# It then selects the frozen particles according to the walls geometry, register and returns the newly created particle vector.
pv_frozen = u.makeFrozenWallParticles(pvName="wall", walls=[wall2], interactions=[dpd], integrator=vv, density=density)
print("wall frozen")
# set the wall for pv
# this is required for non-penetrability of the solvent thanks to bounce-back
# this will also remove the initial particles which are not inside the wall geometry
u.setWall(wall2, pv)
print("wall set")
# now the pv also interacts with the frozen particles!
u.setInteraction(dpd, pv, pv)
u.setInteraction(dpd, pv, pv_frozen)
print("interactiosns set")
# pv_frozen do not move, only pv needs an integrator in this case
u.setIntegrator(vv, pv)

u.registerPlugins(ymr.Plugins.createStats('stats', every=50))
dump_every = 50
u.registerPlugins(ymr.Plugins.createDumpParticles('part_dump', pv, dump_every, [], 'h5/solvent_particles-'))

# we can also dump the frozen particles for visualization purpose
u.registerPlugins(ymr.Plugins.createDumpParticles('part_dump_wall', pv_frozen, dump_every, [], 'h5/wall_particles-'))
print("plugins registered")
# we can dump the wall sdf in xdmf + h5 format for visualization purpose
# the dumped file is a grid with spacings h containing the SDF values
u.dumpWalls2XDMF([wall2], h = (0.05, 0.05, 0.05), filename = 'h5/wall')
print("walls dumped")

