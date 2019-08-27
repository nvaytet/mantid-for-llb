# mantid-for-llb
Data reduction for LLB neutron data using Mantid

This is a first attempt at creating a reduction workflow from raw data to
d-spacing for LLB 5C1 powder data.

Run this script in MantidPlot or MantidWorkbench, or as a standalone python
script.

Note that this is currently very slow, running through all gamma positions
(frames), and no attempt has been made to speed it up.

## Example of use

```Python
   import read_xml
   data = read_xml.load(filename="Powder_HoTi_014704.xml")
   read_xml.plot(data[0], filename="Powder_HoTi_014704.pdf")
```
