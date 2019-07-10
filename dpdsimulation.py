import ymero as ymr
import ctypes
ctypes.CDLL("libmpi.so", mode=ctypes.RTLD_GLOBAL)


class DPDSimulation(object):
    def __init__(self, membrane_input_file, membrane_output_prefix, particle_output_prefix, box_size):
        self.membrane_input_file=membrane_input_file
        self.membrane_output_prefix=membrane_output_prefix
        self.particle_output_prefix=particle_output_prefix
        self.box_size=box_size
        self.dt=0.001
        self.domain=(self.box_size,self.box_size,self.box_size)
        self.u=ymr.ymero((1,1,1),self.domain,self.dt,debug_level=1,log_filename='log')

    def initializeSolute(self, density, radius, force):
        self.solute_density=density
        self.solute_radius=radius
        self.solute_force=force
        self.solute_pv  = ymr.ParticleVectors.ParticleVector('solute_pv', mass = 1.0)
        self.solute_ic  = ymr.InitialConditions.Uniform(self.solute_density)
        self.solute_dpd = ymr.Interactions.DPD('solute_dpd', self.solute_radius, a=10.0, gamma=10.0, kbt=1.0, power=0.5)
        self.solute_vv = ymr.Integrators.VelocityVerlet_withConstForce('solute_vv',force=[self.solute_force,0.0,0.0])
        self.u.registerInteraction(self.solute_dpd)
        self.u.registerParticleVector(self.solute_pv, self.solute_ic)
        self.u.registerIntegrator(self.solute_vv)
        self.u.setInteraction(self.solute_dpd,self.solute_pv,self.solute_pv)

    def initializeSolvent(self, density, radius, force):
        self.solvent_density=density
        self.solvent_radius=radius
        self.solvent_force=force
        self.solvent_pv  = ymr.ParticleVectors.ParticleVector('solvent_pv', mass = 1.0)
        self.ic  = ymr.InitialConditions.Uniform(self.solvent_density)
        self.solvent_dpd = ymr.Interactions.DPD('solvent_dpd', self.solvent_radius, a=10.0, gamma=10.0, kbt=1.0, power=0.5)
        self.solvent_vv = ymr.Integrators.VelocityVerlet_withConstForce('solvent_vv',force=[self.solvent_force,0.0,0.0])
        self.u.registerInteraction(self.solvent_dpd)
        self.u.registerParticleVector(self.solvent_pv, self.ic)
        self.u.registerIntegrator(self.solvent_vv)
        self.u.setInteraction(self.solvent_dpd,self.solvent_pv,self.solvent_pv)

    def setSoluteSolventInteraction(self):
        if self.solute_radius > 0.0:
            self.solute_solvent_dpd=ymr.Interactions.DPD('solute_solvent_dpd', (self.solvent_radius+self.solute_radius)/2, a=10.0, gamma=10.0, kbt=1.0, power=0.5)
            self.u.registerInteraction(self.solute_solvent_dpd)
            self.u.setInteraction(self.solute_solvent_dpd,self.solvent_pv,self.solute_pv)

    def initializeWall(self):
        self.wall = ymr.Walls.SDF("sdfwall",sdfFilename=self.membrane_input_file)
        self.u.registerWall(self.wall) # register the wall in the coordinator
        # we now create the frozen particles of the walls
        self.pv_wall = self.u.makeFrozenWallParticles(pvName="wall", walls=[self.wall], interactions=[self.solvent_dpd,self.solute_dpd], integrator=self.solvent_vv, density=self.solute_density)
        # set the wall for pv
        # this is required for non-penetrability of the solvent thanks to bounce-back
        # this will also remove the initial particles which are not inside the wall geometry
        self.u.setWall(self.wall, self.solvent_pv)
        if self.solute_radius > 0.0:
            self.u.setWall(self.wall, self.solute_pv)
        #set the interaction between the solute particle vector and the wall pv, and the interaction between the solvent particle vectors and the wall particle vectors
        self.u.setInteraction(self.solvent_dpd, self.solvent_pv, self.pv_wall)
        if self.solute_radius > 0.0:
            self.u.setInteraction(self.solute_dpd, self.solute_pv, self.pv_wall)

    def initializeIntegrators(self):
        self.u.setIntegrator(self.solvent_vv, self.solvent_pv)
        if self.solute_radius > 0.0 :
            self.u.setIntegrator(self.solute_vv, self.solute_pv)

    def createOutput(self):
        self.u.registerPlugins(ymr.Plugins.createStats('stats', every=200))
        dump_every = 5
        self.u.registerPlugins(ymr.Plugins.createDumpParticles('part_dump', self.solvent_pv, dump_every, [], '%s/solvent_particles-'%self.particle_output_prefix))
        if self.solute_radius > 0.0:
            self.u.registerPlugins(ymr.Plugins.createDumpParticles('part_dump_solute', self.solute_pv, dump_every, [], '%s/solute_particles-'%self.particle_output_prefix))
        # we can also dump the frozen particles for visualization purpose
        self.u.registerPlugins(ymr.Plugins.createDumpParticles('part_dump_wall', self.pv_wall, dump_every, [], '%s/wall_particles-'%self.particle_output_prefix))
        print("plugins registered")
        # we can dump the wall sdf in xdmf + h5 format for visualization purpose
        # the dumped file is a grid with spacings h containing the SDF values
        self.u.dumpWalls2XDMF([self.wall], h = (0.5, 0.5, 0.5), filename = self.membrane_output_prefix)

    def statistics(self):
        pass

    def runSimulation(self):
        print("running")
        self.u.run(50)
