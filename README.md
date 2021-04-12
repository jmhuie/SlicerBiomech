# Slicer SegmentSliceGeometry

This is the repository for the Slicer SegmentSliceGeometry module for 3D Slicer.

SegmentSliceGeometry calculates geometric properties from segment cross-sections. These include: 
cross-sectional area, mean voxel intensity, second moment of area, section modulus, and polar moment of inertia. 
SegmentSliceGeometry is inspired by BoneJ (Doube et al. 2010), but aims to reduce the number of necessary programs for users 
that already use 3D Slicer. Additional benefits to doing these calculations in 3D Slicer include 
the ability to easily align oblique volumes with the XYZ images axes, perform computations on models 
(i.e., stl, obj, and ply file types), and plotting capabilities.

# Installation

SegmentSliceGeometry is NOT currently available to the public and is still under development. To unofficially install SegmentSliceGeometry, 
clone the contents of this repository and save it somewhere accessible. In 3D Slicer, go to Edit >> Application Settings >> Modules. Under 
"Additional module paths" click "Add" and navigate to and select the "Module" folder in the the SegmentSliceGeometry folder. 
Click OK and restart 3D Slicer. Now, the SegmentSliceGeometry module with automatically load in whenever to you open 3D Slicer. To 
obtain the most recent version of the module, you must re-download the contents of this repository.

# Inputs

**Segmentation:** Select a segmentation node. Calculations will be performed on a visible segments. If input is a model or binary labelmap, 
first convert to a segmentation node.

**Volume:** Select the volume node associated with the segmentation node (optional). Used for calculating mean voxel intensity.

**Slice:** Select which orthogonal axis to perform calculations on.

**Sample slices:** User has the option do calculations in percent intervals along the length of the segment. Enter zero 
to do calculations for every slice.

# Outputs

**Results Table:** A table with calculations. See below for a list of traits. See "Advanced Options" for enabling and disabling calculations.

**Results Plot:** A plot of the table results. By default, Imin is plotted over percent of length. If the 
option to use the neutral axis is enabled, then Ina is plotted instead.

**List of Calculations:** 

- Segment: Segment name.

- Percent: Percent of length along the segment.

- Length: Length of segment along the defined segmentation length.

- CSA: Cross-sectional area.

- Mean Intensity: Mean voxel intensity. Requires a volume node to calculate. Note: This currently does not work with a linear transformed segment.

- X Centroid: X-coordinate of the centroid. 

- Y Centroid: Y-coordinate of the centroid. 

- Theta: Angle of the major principal axis from the horizontal.

- Rmax: Maximum chord length from the major principal axis.

- Rmin: Maximum chord length from minor principal axis.

- Imax: Second moment of area around the major principal axis.

- Imin: Second moment of area around the minor principal axis.

- Zmax: Section modulus around the major principal axis.

- Zmin: Section modulus around the minor principal axis.

- Jmax+min: Polar moment of area around the principal axes.

- Rna: Maximum chord length from the neutral axis.

- Rfa: Maximum chord length from force axis.

- Ina: Second moment of area around the neutral axis.

- Ifa: Second moment of area around the force axis.

- Zna: Section modulus around the neutral axis.

- Zfa: Section modulus around the force axis.

- Jna+fa: Polar moment of area around the neutral and force axes.

# Advanced Options

**Edit selected calculations:** User can toggle main calculations on and off. Note: A volume node must be selected to calculatie voxel intensity.

**Set the neutral axis:** User can set a custom neutral axis for calculating second moment of area, section modulus, and polar moment of inertia 
by entering an angle (in degrees) that represents how much the neutral axis deviates from the horizontal axis. By default, the neutral axis is parallel to the horizontal axis and 
the axis perpendicular to it is called the force axis.

**Extra calculations:** User can toggle on and off extra calculations such segment length, centroid coordinates, theta, and chord length.

**Calculate unitless values:** Two methods of converting some traits into unitless variables. 
 - Doube Method described by Doube et al. (2012). Takes the respective roots needed to convert cross-sectional area, second moment of area, section modulus, and polar moment of inertia in linear dimensions 
and then divides them the length of the segment. This is use to account for the effects of size. 
 - Summers Method described by Summers et al. (2004). Takes the second moment of area of the segment on a given slice and divides it by the second moment of area of an circle with the same cross-sectional area as 
the segment on that particular slice. This is used to assess how the distribution of material in the segment compares to that of an idealized beam.

# What to do if your segment is not-aligned

More often than not, volumes of interest are generated at oblique angles where the anatomical axes are not aligned with 
the directional axes. This can be easily accounted for in 3D Slicer by applying a linear transformation to the segmentation node. A
brief step-by-step protocol is outlined below. 

1. Import and segment your volume as you normally would.
2. Turn on the 3D rendering of your segment. The recommended scene preview is "Conventional" or "Four-Up".
3. In the "Transforms" module, create a linear transformation and apply it to your segmentation node.
4. Under "Display", turn on "Visible in 3D view". This will create a box around your segment and allow you to rotate and translate you segment. 
Use this and/or the sliders under "Edit" to align your segment to preferred axis. Caution: make sure the segment stays within the bounds of its original volume. 
The purple bounding box should indicate this or you can turn on the AnnotationROI associated with the segment's native volume. If part of segment is outside of 
the bounds of the native volume, calculations will not be performed on that section of the segment.
5. In the "Segment Slice Geometry" module, choose your transformed segmentation node and original, untransformed volume as the inputs. 
Note: At this time, a reference volume node is required for this procedure to work. Also, calculating the mean voxel intensity does not work when applying a transform.