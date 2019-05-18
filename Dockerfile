#gcc container
FROM gcc:6.3

#cuda container
FROM nvidia/cuda:10.1-devel


#conda container
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV PATH /opt/conda/bin:$PATH

RUN apt-get update --fix-missing && \
    apt-get install -y wget bzip2 ca-certificates curl git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-4.5.11-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh && \
    /opt/conda/bin/conda clean -tipsy && \
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc

ENV TINI_VERSION v0.16.1
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /usr/bin/tini
RUN chmod +x /usr/bin/tini


RUN conda install -c clawpack hdf5-parallel
#RUN conda install gxx_linux-64
#RUN conda install -c conda-forge binutils
RUN conda install -c conda-forge/label/cf201901 binutils
RUN conda update conda
WORKDIR /ymero
COPY . /ymero
#installs
RUN apt-get update
#RUN apt-get install -y python3-dev
#RUN apt-get install -y python3-pip
#RUN pip3 install pybind11
#RUN apt-get install -y python3-distutils
#RUN apt-get install -y nvidia-418
RUN apt-get install -y libhdf5-openmpi-dev
RUN apt-get install -y cmake
RUN apt-get install -y libopenmpi-dev
RUN apt-get install -y libbfd-dev
RUN apt-get install -y ssh



#expose port for ssh
EXPOSE 20
#container name
ENV Name Test_build

#build ymero
#RUN make install