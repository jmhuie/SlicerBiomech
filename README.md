# Slicer SegmentSliceGeometry

This is the repository for the Slicer SegmentSliceGeometry module for 3D Slicer.

SegmentSliceGeometry calculates geometric properties from the cross-sections of a segment. These include: 
cross-sectional area, mean voxel intensity, second moment of area, section modulus, and polar moment of inertia. 
SegmentSliceGeometry is heavily inspired by BoneJ (Doube et al. 2010). However, the primary goal of SegmentSliceGeometry is to 
reduce the number of steps needed to calculate the slice geometries for users that already use 3D Slicer for processing 3D morphology
data. There are other benefits to performing these calculations in 3D Slicer such as: the ability to align oblique volumes with the 
XYZ images axes or other preferred axes, perform computations on models (i.e., stl, obj, and ply file types), and plotting capabilities.
