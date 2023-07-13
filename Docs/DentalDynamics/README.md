<p align="center">
  <img src="https://raw.githubusercontent.com/jmhuie/Slicer-DentalDynamics/main/DentalDynamics/Resources/Icons/DentalDynamics.png" width="256" height="256">
</p>

# Dental Dynamics

This is the repository for Dental Dynamics, an extension for <a href="https://slicer.org/" target ="_blank">3D Slicer</a>.

Dental Dynamics automates tooth stress calculations for modeling and analyzing tooth function.

![image](https://raw.githubusercontent.com/jmhuie/Slicer-DentalDynamics/main/DentalDynamics/Resources/Icons/DentalDynamicsScreenshot1.png)

# Installation

The official method for installing Dental Dynamics is through 3D Slicer's built-in Extensions Manager. First, install the most recent stable or preview release of <a href="https://download.slicer.org/" target ="_blank">3D Slicer</a>. 
In 3D Slicer, open the Extensions Manager module and search for "Dental Dynamics". Install the extension and restart the application. After, Dental Dynamics should be fully functional and located in the Quantification 
module category. If using the current stable release of Slicer, Dental Dynamics can be updated in the Extension Manager. If using the Preview Release of Slicer, the most recent build must be downloaded and installed to update Dental Dynamics.

# Workflow Example
Below are brief instructions on how to use Dental Dynamics.

### General Use Case
1. Load CT scan into 3D Slicer.
3. Segment out each tooth on the jaw of interest with the Segment Editor module.
4. Switch to the Dental Dynamics module.
5. Provide relevant metadata about the jaw (ie. species name, upper or lower jaw, left or right side of the face)
6. Select your input segmentation node that contains the isolated teeth.
7. Create a "New Reference Point List" and use the GUI to place points on the jaw joint, tip of the jaw, and the jaw closing muscle insertion site.
8. Manipulate the values for the input force and insertion angle of the jaw closing muscle (if desired).
9. Select an output table. 
10. Click Apply. Loading times can vary between 1-30 seconds depending on the size of the data set.
11. Verify that the out-lever lines connect the jaw joint to the tip of each tooth. If not, use the Advanced tools to make changes.
11. Save results by exporting the table or copying and pasting the table values to a separate spreadsheet.


# How to Cite

Coming Soon


# Funding Acknowledgement

Jonathan M. Huie was funded by a NSF Graduate Research Fellowship (DGE-1746914).