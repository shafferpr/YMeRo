#include "rbcs_ic.h"

#include <random>
#include <fstream>

#include <core/pvs/particle_vector.h>
#include <core/pvs/rbc_vector.h>
#include <core/rigid_kernels/integration.h>

/**
 * Read mesh topology and initial vertices (vertices are same as particles for RBCs)
 *
 * Then read the center of mass coordinates of the cells and their orientation
 * quaternions from file #icfname.
 *
 * The format of the initial conditions file is such that each line defines
 * one RBC with the following 7 numbers separated by spaces:
 * <tt>COM.x COM.y COM.z  Q.x Q.y Q.z Q.w</tt>
 * \sa quaternion.h
 *
 * To generate an RBC from the IC file, the initial coordinate pattern will be
 * shifted to the COM and rotated according to Q.
 *
 * The RBCs with COM outside of an MPI process's domain will be discarded on
 * that process.
 *
 * Set unique id to all the particles and also write unique cell ids into
 * 'ids' per-object channel
 */
void RBC_IC::exec(const MPI_Comm& comm, ParticleVector* pv, DomainInfo domain, cudaStream_t stream)
{
	auto ov = dynamic_cast<RBCvector*>(pv);
	if (ov == nullptr)
		die("RBCs can only be generated out of rbc object vectors");

	pv->domain = domain;

	std::ifstream fic(icfname);
	int nObjs=0;

	while (true)
	{
		float3 com;
		float4 q;

		fic >> com.x >> com.y >> com.z;
		fic >> q.x >> q.y >> q.z >> q.w;

		if (fic.fail()) break;

		q = normalize(q);

		if (ov->domain.globalStart.x <= com.x && com.x < ov->domain.globalStart.x + ov->domain.localSize.x &&
		    ov->domain.globalStart.y <= com.y && com.y < ov->domain.globalStart.y + ov->domain.localSize.y &&
		    ov->domain.globalStart.z <= com.z && com.z < ov->domain.globalStart.z + ov->domain.localSize.z)
		{
			com = domain.global2local(com);
			int oldSize = ov->local()->size();
			ov->local()->resize(oldSize + ov->mesh.nvertices, stream);

			for (int i=0; i<ov->mesh.nvertices; i++)
			{
				float3 r = rotate(f4tof3(ov->mesh.vertexCoordinates[i]), q) + com;
				Particle p;
				p.r = r;
				p.u = make_float3(0);

				ov->local()->coosvels[oldSize + i] = p;
			}

			nObjs++;
		}
	}

	// Set ids
	int totalCount=0; // TODO: int64!
	MPI_Check( MPI_Exscan(&nObjs, &totalCount, 1, MPI_INT, MPI_SUM, comm) );

	auto ids = ov->local()->extraPerObject.getData<int>("ids");
	for (int i=0; i<nObjs; i++)
		(*ids)[i] = totalCount + i;

	for (int i=0; i < ov->local()->size(); i++)
		ov->local()->coosvels[i].i1 = totalCount*ov->objSize + i;


	ids->uploadToDevice(stream);
	ov->local()->coosvels.uploadToDevice(stream);

	info("Read %d %s rbcs", nObjs, ov->name.c_str());
}
