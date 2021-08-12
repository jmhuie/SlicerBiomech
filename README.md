# Slicer SegmentSliceGeometry

This is the repository for the Slicer SegmentSliceGeometry module for 3D Slicer.

SegmentSliceGeometry calculates geometric properties from segment cross-sections. These include: 
second moment of area, cross-sectional area, section modulus, polar moment of inertia, and more. 
SegmentSliceGeometry is inspired by BoneJ (Doube et al. 2010), but aims to streamline the workflow for 3D Slicer users. Additional benefits to 
using 3D Slicer include the ability to easily align oblique volumes with the XYZ images axes, resampling volumes, perform computations on models 
(i.e., stl, obj, and ply file types), and quick plotting capabilities.

# Installation

SegmentSliceGeometry is NOT currently available to the public and is still under development. To unofficially install SegmentSliceGeometry, 
clone the contents of this repository and save it somewhere accessible. If you downloaded this repo from Google Drive, unzip the folder and save the contents somewhere accessible. 
In 3D Slicer, go to Edit >> Application Settings >> Modules. Under 
"Additional module paths" click "Add" and navigate to and select the "Module" folder in the the SegmentSliceGeometry folder. 
Click OK and restart 3D Slicer. Now, the SegmentSliceGeometry module with automatically load in whenever to you open 3D Slicer. To 
obtain the most recent version of the module, you must re-download the contents of this repository. This module also requires on SlicerMorph and its dependencies to be installed.

# Inputs

**Segmentation:** Select a segmentation node. If input is a model or binary labelmap, 
first convert to a segmentation node. 

**Segment:** Select a segment to perfom computations on. 

**Volume:** Select the volume node associated with the segmentation node. Necessary if the segmentation node has been transformed. 

**Resample Volume:** Option to resample the volume. Needed when measuring mean pixel brightness from a transformed segment. 
Note: this option increases computation time but the resampled volume will be saved after the initial run and can be used in subsequent re-runs. Resample Volume uses the Resample Scalar/Vector/DWI Volume module with linear interpolation.

**Show/Hide Bounding Box:** Click button to display a blue bounding box that represents the bounds of the original, untransformed volume node. When computing on a transformed segment, the segment must be contained within the bounds of the bounding box. If the segment falls outside of the box, use the the Transforms Module to translate the segment into the bounds of the box. Click button again to hide box.

**Slice:** Select which orthogonal axis to perform computations on.

**Sample slices:** User has the option do calculations in percent intervals along the length of the segment. Enter zero 
to compute on every slice.

# Outputs

**Results Table:** A table with the results. See below for a list of computations. See "Advanced Options" for enabling and disabling computations.

**Results Plot:** A plot of the results. By default, second moment of area (Imin) is plotted with percent of segment length. If the option to use the neutral axis is enabled, then Ina is plotted as well.

**List of Calculations:** 

- Segment: Segment name.

- Percent: Percent of length along the segment.

- Length: Length of segment along the defined segmentation length.

- X Centroid: X-coordinate of the segment centroid. 

- Y Centroid: Y-coordinate of the segment centroid. 

- Mean Intensity: Mean pixel brightness. Requires a volume node to calculate. Note: if the segment has a transformation node, you will need to use a resampled volume node. Either enable Resample Volume or select an already resampled volume node as the input.

- CSA: Cross-sectional area.

- Total CSA: Total cross-sectional area. Requires a separate solid segment node.

- Compactness: Global compactness or the ratio between CSA and Total CSA. Requires a separate solid segment node.

- Imin: Second moment of area around the minor principal axis.

- Imax: Second moment of area around the major principal axis.

- Theta: Angle (radians) of how much the minor principal axis deviates from the horizontal axis.

- J: Polar moment of area around the principal axes. Assumes the slice is annular and is calculated as Imin + Imax.

- Zmax: Section modulus around the major principal axis.

- Zmin: Section modulus around the minor principal axis.

- Rmax: Distance of the furthest pixel from the major principal axis.

- Rmin: Distance of the furthest pixel from the minor principal axis.

- Ina: Second moment of area around the neutral axis.

- Ifa: Second moment of area around the force axis.

- Jna: Polar moment of area around the neutral and force axes. Assumes the slice is annular and is calculated as Ina + Ifa.

- Zna: Section modulus around the neutral axis.

- Zfa: Section modulus around the force axis.

- Rna: Distance of the furthest pixel from the neutral axis.

- Rfa: Distance of the furthest pixel from the force axis.


# Advanced Options

**Select computations:** User can toggle computations on and off. Note: A volume node must be selected to calculatie voxel intensity.

**Compute with custom neutral axis:** User can set a custom neutral axis for calculating second moment of area, polar moment of inertia, and section modulus
by entering an angle (in degrees) that represents how much the neutral axis deviates from the horizontal axis. By default, the neutral axis is set to the horizontal axis the vertical axis is considered the force axis.

**Total cross-sectional area and global compactness:** User can compute the total cross-sectional area and global compactness of their segment. Currently, this module does not automate these calculations and a separate solid segment is required. The recommended procedure is to use the Wrap Solidify tool in the Segment Editor Module to make a copy of their segment of interest and fill in the gaps.

**Calculate unitless values:** Two methods of converting some traits into unitless variables are available. 
 - Doube Method described by Doube et al. (2012). Takes the respective roots needed to convert cross-sectional area, second moment of area, section modulus, and polar moment of inertia into linear dimensions and then divides them by the length of the segment. This is effectively a size-correction. 
 - Summers Method described by Summers et al. (2004). Takes the second moment of area of the segment on a given slice and divides it by the second moment of area of an circle with the same cross-sectional area as the segment on that particular slice. This is used to assess how the distribution of material in the segment compares to that of an idealized beam.

# What to do if your segment is not-aligned

More often than not, volumes of interest are generated at oblique angles where the anatomical axes are not aligned with 
the directional axes. This can be easily accounted for in 3D Slicer by applying a linear transformation to the segmentation node. A
brief step-by-step protocol is outlined below. 

1. Import and segment your volume as you normally would.
2. Turn on the 3D rendering of your segment. The recommended scene preview is "Conventional" or "Four-Up".
3. In the "Transforms" module, create a linear transformation and apply it to your segmentation node and its corresponding volume node.
4. Under "Display" in the "Transforms" module, turn on "Visible in 3D view". This will create a box around your segment and allow you to rotate and translate you segment. Use this and/or the sliders under "Edit" to align your segment to the preferred axis. Caution: make sure the segment stays within the bounds of its original volume. Use the "Show/Hide Bounding Box" button in the "Segment Slice Geometry" Module as a reference. If part of the segment is outside of bounding box, computations will not be performed on that portion of the segment.
5. In the "Segment Slice Geometry" module, choose your transformed segmentation and volume nodes as the inputs. Note: the volume node does not need to be transformed for this to work, but the segmentation node does.
6. If you are calculating mean voxel intensity you must check Resample Volume. Alternatively, you may select an already resampled volume as the input.
7. Click Apply.
