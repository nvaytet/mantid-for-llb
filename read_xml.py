# This is a small utility to load polarised neutron data from LLB xml files.
# Author: Neil Vaytet (ESS)
# Created: 23/08/2019

# Example of use:
#
#   import read_xml
#   data = read_xml.load(filename="Powder_HoTi_014704.xml")
#   read_xml.plot(data, filename="Powder_HoTi_014704.pdf")


import xml.etree.ElementTree as et
import matplotlib.pyplot as plt
import numpy as np


class XMLData():
    """
    Class to hold the data stored in the LLB xml format.
    """
    def __init__(self, Iup, Idn, Phi, Omega, Gamma, monitor_counts, wavelength,
                 nx, ny, nz):
        self.Iup = Iup
        self.Idn = Idn
        self.Phi = Phi
        self.Omega = Omega
        self.Gamma = Gamma
        self.monitor_counts = monitor_counts
        self.wavelength = wavelength
        self.nx = nx
        self.ny = ny
        self.nz = nz
        return


def load(filename=""):
    """
    Load a XML file and return a XMLData object.
    The information read is:
    - Iup: the "up" intensity (counts): a 3D numpy array [nz, ny, nx]
    - Idn: the "down" intensity (counts): a 3D numpy array [nz, ny, nx]
    - Phi: the "phi" angle for all the frames: a 1D numpy array [nz]
    - Omega: the "omega" angle for all the frames: a 1D numpy array [nz]
    - Gamma: the "gamma" detector rotation angle for all the frames: a 1D numpy array [nz]
    - monitor_counts: the counts recorded by the monitor for each frame: a 1D numpy array [nz]
    - wavelength: the wavelength for the current measurement: a float (applies to all frames)
    - nx: number of pixels in the "x" direction: an integer (applies to all frames)
    - ny: number of pixels in the "y" direction: an integer (applies to all frames)
    - nz: number of frames: an integer
    """

    tree = et.parse(filename)
    root = tree.getroot()
    wavelength = float(root[1].text)

    jstart = 2

    # Get pixel numbers
    nx = int(root[jstart][6].attrib["x"])
    ny = int(root[jstart][6].attrib["y"])
    nz = len(root) - jstart

    # Allocate arrays
    Iup = np.zeros([nz, ny, nx])
    Idn = np.zeros([nz, ny, nx])

    Phi = np.zeros([nz])
    Omega = np.zeros([nz])
    Gamma = np.zeros([nz])
    monitor_counts = np.zeros([nz])

    for i in range(jstart, len(root)):
        Iup[i - jstart, :, :] += np.array(root[i][5].text.split(';'),
                                          dtype=np.int32).reshape(ny, nx)
        Idn[i - jstart, :, :] += np.array(root[i][6].text.split(';'),
                                          dtype=np.int32).reshape(ny, nx)
        Phi[i - jstart] = np.float(root[i][4][0].text)
        Omega[i - jstart] = np.float(root[i][4][1].text)
        Gamma[i - jstart] = np.float(root[i][4][2].text)
        monitor_counts[i - jstart] = np.float(root[i][3][2].text)

    return XMLData(Iup, Idn, Phi, Omega, Gamma, monitor_counts, wavelength, nx,
                   ny, nz)


def plot(data, n=0, filename="plot.pdf"):
    """
    Plot the data for Iup and Idn as a 2D image for a given frame number n,
    and save figure as pdf file.
    """

    fig = plt.figure()
    aspect = 25.0/80./4.0
    ax1 = fig.add_subplot(211)
    im1 = ax1.imshow(np.log10(data.Iup[n, :, :]).T, aspect=aspect,
                     origin="lower")
    cb1 = plt.colorbar(im1)
    ax2 = fig.add_subplot(212)
    im2 = ax2.imshow(np.log10(data.Idn[n, :, :]).T, aspect=aspect,
                     origin="lower")
    cb2 = plt.colorbar(im2)
    ax1.text(0, 1.1*data.nx, "I_up")
    ax2.text(0, 1.1*data.nx, "I_dn")
    fig.savefig(filename, bbox_inches="tight")
