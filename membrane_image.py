import ymero as ymr
import ctypes
import argparse
ctypes.CDLL("libmpi.so", mode=ctypes.RTLD_GLOBAL)
parser=argparse.ArgumentParser(description='generate a membrane structure')
parser.add_argument('--inputfile',dest='sdf_input',default='qq.dat',help="sdf membrane structure inputfile")
parser.add_argument('--outputprefix',dest='outputprefix',default='membrane/wall',help="prefix for the output h5 and xmf file")
parser.add_argument('--boxsize', type=int, dest='boxsize',default=80,help="total boxsize for cubic box, default=80")
                    
args=parser.parse_args()

rc = 1.0      # cutoff radius
density = 2.0 # number density
dt = 0.001
ranks  = (1, 1, 1)
domain = (args.boxsize,args.boxsize,args.boxsize)

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




wall2 = ymr.Walls.SDF("sdfwall",sdfFilename=args.sdf_input)

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
u.dumpWalls2XDMF([wall2], h = (0.5, 0.5, 0.5), filename = args.outputprefix)
print("walls dumped")

