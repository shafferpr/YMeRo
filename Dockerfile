#python container
FROM python:3.6
#gcc container
FROM gcc:6.3
#cuda container
FROM nvidia/cuda:10.1-devel
WORKDIR /ymero
COPY . /ymero
#installs
RUN apt-get update
RUN apt-get install -y python3-dev
RUN apt-get install -y python3-pip
RUN pip3 install pybind11
RUN apt-get install -y python3-distutils
RUN apt-get install -y nvidia-driver-418
RUN apt-get install -y libhdf5-openmpi-dev
RUN apt-get install -y cmake
RUN apt-get install -y libopenmpi-dev
RUN apt-get install libbfd-dev
RUN export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/lib/python3.6/

#expose port for ssh
EXPOSE 20
#container name
ENV Name Test_build

#build ymero
RUN make install