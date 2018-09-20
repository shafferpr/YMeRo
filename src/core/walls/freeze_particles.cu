#include "freeze_particles.h"

#include <core/logger.h>
#include <core/pvs/particle_vector.h>
#include <core/pvs/views/pv.h>
#include <core/utils/cuda_common.h>
#include <core/utils/kernel_launch.h>

#include <core/walls/simple_stationary_wall.h>

static const cudaStream_t default_stream = 0;

template<bool QUERY>
__global__ void collectFrozen(PVview view, const float *sdfs, float minVal, float maxVal, float4* frozen, int* nFrozen)
{
    const int pid = blockIdx.x * blockDim.x + threadIdx.x;
    if (pid >= view.size) return;

    Particle p(view.particles, pid);
    p.u = make_float3(0);

    const float val = sdfs[pid];
    
    if (val > minVal && val < maxVal)
    {
        const int ind = atomicAggInc(nFrozen);

        if (!QUERY)
            p.write2Float4(frozen, ind);
    }
}

static void extract_particles(ParticleVector *pv, const float *sdfs, float minVal, float maxVal)
{
    PinnedBuffer<int> nFrozen(1);
    
    PVview view(pv, pv->local());
    const int nthreads = 128;
    const int nblocks = getNblocks(view.size, nthreads);

    nFrozen.clear(default_stream);

    SAFE_KERNEL_LAUNCH
        (collectFrozen<true>,
         nblocks, nthreads, 0, default_stream,
         view, sdfs, minVal, maxVal, nullptr, nFrozen.devPtr());

    nFrozen.downloadFromDevice(default_stream);

    PinnedBuffer<Particle> frozen(nFrozen[0]);
    info("Freezing %d particles", nFrozen[0]);

    pv->local()->resize(nFrozen[0], default_stream);

    nFrozen.clear(default_stream);
    
    SAFE_KERNEL_LAUNCH
        (collectFrozen<false>,
         nblocks, nthreads, 0, default_stream,
         view, sdfs, minVal, maxVal, (float4*)frozen.devPtr(), nFrozen.devPtr());

    CUDA_Check( cudaDeviceSynchronize() );
    std::swap(frozen, pv->local()->coosvels);
}

void freezeParticlesInWall(SDF_basedWall* wall, ParticleVector *pv, float minVal, float maxVal)
{
    CUDA_Check( cudaDeviceSynchronize() );

    DeviceBuffer<float> sdfs(pv->local()->size());

    wall->sdfPerParticle(pv->local(), &sdfs, nullptr, default_stream);

    extract_particles(pv, sdfs.devPtr(), minVal, maxVal);
}


