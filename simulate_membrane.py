import argparse
from dpdsimulation import DPDSimulation

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='generate a membrane structure')
    parser.add_argument('--inputfile',dest='membrane_input_file',default='qq.dat',help="sdf membrane structure inputfile")
    parser.add_argument('--membrane_ouput',dest='membrane_output_prefix',default='membrane/wall',help="prefix for the output h5 and xmf file of the membrane")
    parser.add_argument('--particle_output',dest='particle_output_prefix',default='h5',help="directory for the output particle trajectory files")
    parser.add_argument('--box_size', type=int, dest='box_size',default=80,help="total boxsize for cubic box, default=80")
    parser.add_argument('--solvent_radius',type=float,dest='solvent_radius',default=1.0,help="size of the solvent particles, default=1.0")
    parser.add_argument('--solute_radius',type=float,dest='solute_radius', default=0.0, help="size of the solute particles, default=0.0, which corresponds to no solute")
    parser.add_argument('--solvent_density',type=float, dest='solvent_density', default=1.0, help="density of the solvent, default=1.0")
    parser.add_argument('--solute_density',type=float, dest='solute_density', default=0.1, help="density of the solute, default=0.1")
    parser.add_argument('--solvent_force', type=float, dest='solvent_force', default=0.05, help="force acting on the solvent particles pushing them through the membrane, default=0.05")
    parser.add_argument('--solute_force', type=float, dest='solute_force', default=0.1, help="force acting on the solute particles pushing the through the membrane, default=0.1")
    args=parser.parse_args()

    simulation=DPDSimulation(membrane_input_file=args.membrane_input_file,membrane_output_prefix=args.membrane_output_prefix, \
                            particle_output_prefix=args.particle_output_prefix, box_size=args.box_size)

    simulation.initializeSolute(density=args.solute_density,radius=args.solute_radius,force=args.solute_force)
    simulation.initializeSolvent(density=args.solvent_density,radius=args.solvent_radius,force=args.solvent_force)
    simulation.setSoluteSolventInteration()
    simulation.initializeWall()
    simulation.initializeIntegrators()
    simulation.createOutput()
    simulation.runSimulation()
