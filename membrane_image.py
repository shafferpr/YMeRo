import argparse
from dpdsimulation import DPDSimulation

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='')
    parser.add_argument('--inputfile',dest='membrane_input_file',default='qq.dat',help="sdf membrane structure inputfile")
    parser.add_argument('--membrane_output',dest='membrane_output_prefix',default='membrane/wall',help="prefix for the output h5 and xmf file of the membrane")
    parser.add_argument('--box_size', type=int, dest='box_size',default=80,help="total boxsize for cubic box, default=80")
    args=parser.parse_args()

    simulation=DPDSimulation(membrane_input_file=args.membrane_input_file,membrane_output_prefix=args.membrane_output_prefix, \
                             box_size=args.box_size)
    simulation.drawWall()
