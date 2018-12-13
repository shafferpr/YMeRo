#include "force_saver.h"

#include <core/simulation.h>
#include <core/pvs/particle_vector.h>
#include <core/utils/kernel_launch.h>
#include <core/pvs/views/pv.h>

const std::string ForceSaverPlugin::fieldName = "forces";

__global__ void copyForces(PVview view, float3 *savedForces)
{
    int pid = blockIdx.x * blockDim.x + threadIdx.x;
    if (pid >= view.size) return;

    float3 f = Float3_int(view.forces[pid]).v;
    savedForces[pid] = f;
}

ForceSaverPlugin::ForceSaverPlugin(std::string name, std::string pvName) :
    SimulationPlugin(name), pvName(pvName), pv(nullptr)
{}

void ForceSaverPlugin::beforeIntegration(cudaStream_t stream)
{
    auto savedForces  = pv->local()->extraPerParticle.getData<float3>(fieldName);
    PVview view(pv, pv->local());
    const int nthreads = 128;

    SAFE_KERNEL_LAUNCH(
            copyForces,
            getNblocks(view.size, nthreads), nthreads, 0, stream,
            view, savedForces->devPtr() );
}
    
bool ForceSaverPlugin::needPostproc()
{
    return false;
}

void ForceSaverPlugin::setup(Simulation* simulation, const MPI_Comm& comm, const MPI_Comm& interComm)
{
    SimulationPlugin::setup(simulation, comm, interComm);

    pv = simulation->getPVbyNameOrDie(pvName);

    pv->requireDataPerParticle<float3>(fieldName, ExtraDataManager::CommunicationMode::None, ExtraDataManager::PersistenceMode::None);
}

    
