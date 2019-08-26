# This is a first attempt at creating a reduction workflow from raw data to
# d-spacing for LLB 5C1 powder data.
# Run this script in MantidPlot or MantidWorkbench, or as a standalone python
# script.
# Note that this is currently very slow, running through all gamma positions
# (frames), and no attempt has been made to speed it up.
# Author: Owen Arnold (ISIS/STFC) & Neil Vaytet (ESS)
# Created: 23/08/2019


import mantid.simpleapi as mantid
from mantid.api import AlgorithmManager as am
import numpy as np
import read_xml
import matplotlib.pyplot as plt


def createWorkspace(data_x, data_y, data_e, n_spec, unit=None):
     alg = am.create("CreateWorkspace")
     alg.setChild(True)
     alg.initialize()
     alg.setProperty("DataX", data_x)
     alg.setProperty("DataY", np.array(data_y, dtype=np.int32))
     alg.setProperty("DataE", data_e)
     alg.setProperty("NSpec", n_spec)
     if unit is not None:
         alg.setProperty("UnitX", unit)
     alg.setProperty("OutputWorkspace", "dummy")
     alg.execute()
     return alg.getProperty("OutputWorkspace").value


# Load the XML data file as a list of frames
frames = read_xml.load(filename="Powder_HoTi_014704.xml")

# The final workspace
final = None
# The global bins for dspacing
bins = np.arange(0.0, 5.0, 0.01)
# A 1D array for Intensity vs d-spacing
dsp = np.zeros([len(bins) - 1])

# Initialise matplotlib figure
fig = plt.figure()

# Loop over all frames
for i, f in enumerate(frames):

    print("=========================================")
    print("{}/{}".format(i, len(frames)))
    print("=========================================")

    # Create workspace for current frame
    ws_for_this_frame = createWorkspace(data_x=[f.wavelength],
                                        data_y=f.IntensityUp,
                                        data_e=np.sqrt(f.IntensityUp),
                                        n_spec=f.x*f.y,
                                        unit="Wavelength")
    # Register the workspace in the mantid ADS
    mantid.mtd.addOrReplace("ws_for_this_frame", ws_for_this_frame)
    # Load the instrument from the definition file
    mantid.LoadInstrument(ws_for_this_frame, FileName="5C1_Definition.xml",
                          RewriteSpectraMap=True)
    # Rotate the instrument to the current gamma angle (in degrees)
    mantid.RotateInstrumentComponent(ws_for_this_frame, "detector_panel",
                                     X=0, Y=1, Z=0, Angle=f.Gamma,
                                     RelativeRotation=False)
    # Normalise by monitor counts
    normalised = ws_for_this_frame / f.totalmonitorcount
    # Convert to d-spacing
    dspacing = mantid.ConvertUnits(InputWorkspace=normalised,
                                   Target="dSpacing", EMode="Elastic")

    # 1. Naive accumulation of workspace data: this does not seem to work
    rebinned = mantid.Rebin(dspacing, "0.5,0.01,5.0")
    if final is None:
        final = mantid.CloneWorkspace(rebinned)
    else:
        final += rebinned

    # 2. Try to extract 1D profile from equatorial plane

    # Get the positions of the detector pixels, and mask everything that is
    # outside of a 0.005m-wide band around the equatorial plane
    specinfo = dspacing.spectrumInfo()
    for spec in specinfo:
        if spec.isMonitor:
            spec.setMasked(True)
        else:
            y = spec.position.Y()
            if np.abs(y) > 0.005:
                spec.setMasked(True)

    # Extract the X (d-spacing) and Y (intensity/counts) data
    ws_x = dspacing.extractX()[1:, 0]
    ws_y = dspacing.extractY()[1:, 0]

    # Bin the data into a common set of d-spacing bins
    z, edges = np.histogram(ws_x, bins=bins, weights=ws_y)

    # Accumulate the intensities into a master dsp array
    dsp += z

    # Plot the figure for each frame?
    xc = 0.5* (bins[:-1] + bins[1:])
    fig.clear()
    ax = fig.add_subplot(111)
    # ax.xaxis.set_ticks(np.arange(0.0, 5.0, 0.5))
    ax.grid(True, color='gray', linestyle="dotted")
    ax.set_axisbelow(True)
    ax.plot(xc, dsp)
    ax.set_xlabel("d-spacing")
    ax.set_ylabel("Intensity")
    fig.savefig("dspacing.pdf", bbox_inches="tight")
