# This is a small utility to load polarised neutron data from LLB xml files.
# Author: Neil Vaytet (ESS)
# Created: 23/08/2019

# Example of use:
#
#   import read_xml
#   data = read_xml.load(filename="Powder_HoTi_014704.xml")
#   read_xml.plot(data[0], filename="Powder_HoTi_014704.pdf")


import xml.etree.ElementTree as et
import matplotlib.pyplot as plt
import numpy as np


def text_to_value(val, key=""):
    """
    If key is x, y or z, convert to int.
    Else, we try to convert to float.
    If that fails, we simply return the string.
    """
    possibles = ["x", "y", "z"]
    if key in possibles:
        out = int(val)
    else:
        # Try to convert to float
        try:
            out = float(val)
        except ValueError:
            out = val
    return out


class XMLFrame():
    """
    Class to hold the data stored in the LLB xml Frame format.
    We attempt to store values as floats where possible.
    """
    def __init__(self, frame, wavelength=0.0):
        # Start by setting the wavelength
        setattr(self, "wavelength", wavelength)
        # Then iterate through all the frame elements
        for el in frame.iter():
            # First get the metadata from dict items
            if len(el.keys()) > 0:
                for key, val in el.items():
                    setattr(self, key, text_to_value(val, key))
            # Then, read in the "text" contained inside each element
            if el.text is not None:
                if el.tag == "Data":
                    data = np.array(el.text.split(';'),
                                    dtype=np.int32).reshape(self.y, self.x)
                    setattr(self, self.name, data)
                else:
                    data = text_to_value(el.text)
                    setattr(self, el.tag, data)
        return


def load(filename=""):
    """
    Load a XML file and return a XMLData object.
    We attempt to load all the data contained in the XML file.
    """

    tree = et.parse(filename)
    root = tree.getroot()
    wavelength = float(root.findtext("wavelenght"))

    frame_list = [ XMLFrame(f, wavelength) for f in root.iter("Frame") ]

    return frame_list


def plot(frame, filename="plot.pdf", fields=["IntensityUp", "IntensityDown"],
         log=True):
    """
    Plot the data for Iup and Idown as a 2D image for a given frame,
    and save figure to file.
    """

    fig = plt.figure()
    aspect = 25.0/80./4.0

    for i, f in enumerate(fields):
        ax = fig.add_subplot(len(fields), 1, i + 1)
        z = getattr(frame, f)
        if log:
            with np.errstate(divide="ignore", invalid="ignore"):
                z = np.log10(z)
        im = ax.imshow(z.T, aspect=aspect, origin="lower")
        cb = plt.colorbar(im)
        cb.ax.set_ylabel(f)
        cb.ax.yaxis.set_label_coords(-1.7, 0.5)

    fig.savefig(filename, bbox_inches="tight")
