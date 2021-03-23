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