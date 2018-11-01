#!/usr/bin/env python

import udevicex as udx
import numpy as np
import trimesh, argparse

parser = argparse.ArgumentParser()
parser.add_argument("--mesh", type=str, required=True)
args = parser.parse_args()

ranks  = (1, 1, 1)
domain = (12, 8, 10)

rc=1.0

u = udx.udevicex(ranks, domain, debug_level=8, log_filename='log')

m = trimesh.load(args.mesh);
mesh = udx.ParticleVectors.MembraneMesh(m.vertices.tolist(), m.faces.tolist())

rbc  = udx.ParticleVectors.MembraneVector("rbc", mass=1.0, mesh=mesh)
icrbc = udx.InitialConditions.Membrane([[6.0, 4.0, 5.0,   1.0, 0.0, 0.0, 0.0]])
u.registerParticleVector(pv=rbc, ic=icrbc)

box_lo = (          - domain[0],           - domain[1],             rc)
box_hi = (domain[0] + domain[0], domain[1] + domain[1], domain[2] - rc)
plates = udx.Walls.Box("plates", box_lo, box_hi, inside=True)
u.registerWall(plates, 0)

# fake repulsion module to force sdf computation
wallRep = udx.Plugins.createWallRepulsion("wallRepulsion", rbc, plates, C=500, h=rc, max_force=500) 
u.registerPlugins(wallRep)

dumpEvery = 1
ovDump = udx.Plugins.createDumpParticlesWithMesh('partDump', rbc, dumpEvery, [["sdf", "scalar"]], 'h5/rbc-')
u.registerPlugins(ovDump)

u.run(2)

# nTEST: dump.h5.mesh.sdf
# cd dump
# rm -rf h5
# mesh="../../data/rbc_mesh.off"
# udx.run --runargs "-n 2" ./h5.mesh.sdf.py --mesh $mesh > /dev/null
# udx.post h5dump -d sdf h5/rbc-00000.h5 | awk '{print $2}' > h5.mesh.sdf.out.txt