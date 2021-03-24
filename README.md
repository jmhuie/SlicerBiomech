# Slicer SegmentSliceGeometry

This is the repository for the Slicer SegmentSliceGeometry module for 3D Slicer.

SegmentSliceGeometry calculates geometric properties from the cross-sections of a segment. These include: 
cross-sectional area, mean voxel intensity, second moment of area, section modulus, and polar moment of inertia. 
SegmentSliceGeometry is heavily inspired by BoneJ (Doube et al. 2010), but its primary goal is to 
streamline workflows for users that already process data in 3D Slicer. The benefits to doing these calculations in 3D Slicer include 
the ability to align oblique volumes with the XYZ images axes, perform computations on models (i.e., stl, obj, and ply file types), 
and graphical plotting capabilities.

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

**Slice:** Select which orthogonal axis to perform calculations on. Based on the 3D Slicer layout: Red = slice, Green = column, and Yellow = row.

**Sample slices:** User has the option do calculations in percent intervals along the length of the segment. Enter zero 
to do calculations for every slice.

# Outputs
- Segment: Segment name.

- Percent: Percent of length along the segment.

- Length: Length of segment along the defined segmentation length.

- CSA: Cross-sectional area.

- Mean Intensity: Mean voxel intensity. Requires a volume node to calculate.

- X Centroid: X-coordinate of the centroid. Note: the centroid of the segment is currently calculated based on the smallest ROI that can be draw around the segment and not the dimensions of the volume.

- Y Centroid: Y-coordinate of the centroid. Note: the centroid of the segment is currently calculated based on the smallest ROI that can be draw around the segment and not the dimensions of the volume.

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