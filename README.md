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

# Inputs and Outputs

### Inputs

**Segmentation:** Select a segmentation node. Calculations will be performed on a visible segments. If input is a model or binary labelmap, 
first convert to a segmentation node.
**Volume:** Select the volume node associated with the segmentation node (optional). Used for calculating mean voxel intensity.
**Slice:** Select which orthogonal axis to perform calculations on. Based on the 3D Slicer layout: Red = slice, Green = column, and Yellow = row.
**Sample slices:** User has the option do calculations in percent intervals along the length of the segment. Enter zero 
to do calculations for every slice.

### Outputs


### Advanced

**Edit selected calculations:** User can toggle main calculations on and off. By default second moment of area, section modulus, 
and polar moment of inertia are calculated around the principal axes. Note: A volume node must be selected to calculatie voxel intensity.
**Set a user-defined neutral axis:** User can define a custom neutral axis for calculating second moment of area, section modulus, 
and polar moment of inertia by entering an angle (in degrees) that represents how much the neutral axis deviates from the horizontal axis. 
By default, the neutral axis is parallel to the horizontal axis and the "force" axis is perpendicular to that.
**Extra calculations:** User can toggle on and off extra calculations such as the length of the axis along the user-defined segment axis, 
the centroid coordinates, how far the major axis deviates from the horizontal (radians), and the maximum chord length perpendicular to the principal axes 
and the neutral and force axes (if selected). Note: the centroid is calculated based on the smallest box that can be drawn around the segment and not the overall 
dimensions of the slice.
**Calculate unitless values:** Two methods of converting some traits into unitless variables. First, is the Doube Method described in Doube et al. (2012). 
It takes the respective roots needed to convert cross-sectional area, second moment of area, section modulus, and polar moment of inertia in linear dimensions 
and then divides them the length of the segment. This is use to account for the effects of size. Next, is the Summers Method described by Summers et al. (2004). 
This procedure takes the second moment of area of the segment on a given slice and divides it by the second moment of area of an circle with the same cross-sectional area as 
the segment on that particular slice. This is used to assess how the distribution of material in the segment compares to that of an idealized beam.