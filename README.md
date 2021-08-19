# Segment Geometry

This is the repository for Segment Geometry, an extension for 3D Slicer.

Segment Geometry currently contains one module that iterates slice-by-slice through a segment to calculate the second moment of area and other cross-sectional properties. 

<img width="1792" alt="Screen Shot 2021-08-18 at 10 44 58 PM" src="https://user-images.githubusercontent.com/52302862/130000723-9d29b0e3-b973-4d62-bca4-633c4c207ae7.png">

# Installation

Segment Geometry is still under development. To unofficially install Segment Geometry, you may clone the contents of this repository and save it somewhere accessible. If you downloaded this repo from Google Drive, unzip the folder and save the contents somewhere. In 3D Slicer, go to Edit >> Application Settings >> Modules. Under "Additional module paths" click the little arrow point right, and then click "Add" and navigate to and select the "SegmentGeometry" folder in the the SegmentSliceGeometry folder. Click OK and restart 3D Slicer. Now, the Segment Geometry module with automatically load in whenever you open 3D Slicer. To 
obtain the most recent version of the module, you must re-download the contents of this repository. This module is dependent on the ExtraSegmentEditorEffects extension. Official release coming soon.

# Typical Workflow

1. Start 3D Slicer.
2. Load in CT Data.
3. Go to the Segment Editor module.
4. Segment bone or structure of interest. 

**Note:** Workflow assumes that your segment is not already orientated along the desired long axis. If it is, skip to Step 10.
5. Go to the Transforms module.
6. Create a new Linear Transform. 
7. Move your Segmentation and the Volume from the "Transformable" column to the "Transformed" column.
8. Use the Rotation sliders or the interactive "Visible in 3D view" tool under display to rotate your segment.
9. Align your segment with the three slice views based on how you would like to interatively slice through the segment. 

Note: If your data is isotropic, it does not matter which slice view is perpendicular to the long axis (z-axis). If your data is anistropic, you get the best results if rotate your specimen so that the long axis is perpendicular to the red slice view. You can also resample your volume to make it isotropic in the Resample Scalar Volume module for better results.
10. Go to the Segment Geometry module. Either by searching (Ctrl+F) or finding it under the Quantification category.
11. Select your inputs. "Segmentation" is the Segmentation node that contains your segment and "Volume" is the corresponding Volume node. All are required if you applied a linear transformation.

Note: If you applied a linear transformation to your segment, it's absolutely crucial that your whole segment lies within the 3D bounds of its untransformed Volume Node. The "Snap to Center" and "Toggle Bounding Box" buttons have been added to make this easier.
12. Click the "Snap to Center" to automatically move your segment to the center of the untransformed Volume node.
13. Click the "Toggle Bounding Box" to draw a box around the untransformed Volume node. If your segment is completely inside the box, you are OK to proceed. If part of the segment is outside of the box, you may need to manually translate your segment using the Transforms module. If the box is too small for your segment, you will need to extend the bounds of the Volume node using the Crop Volume module. Click the button again to hide the bounding box.
14. Select an output table and chart for the results. By default, a new table and chart will be made automatically if one does not already exist for that segment.
15. Under "Advanced" choose which computations should be performed.

Note: If you selected "Mean Pixel Brightness" and transformed your segment, you must check the "Resample Volume" box. This will resample your volume using the Resample Scalar/Vector/DWI Volume module. Because this process substaintially increases computation time, the resampled volume will be saved and may be used as the input Volume node if analyses need to be re-run.

Note: If the direction of the loading axis is known, a custom neutral axis can be used for relevant computations.

Note: To calculate total cross-sectional area or global compactness, a separate solid segment that contains the full structure is required.
16. Click Apply

# List of Computations

- Segment: Segment name.

- Percent: Percent of length along the segment.

- Length: Length of segment along the defined segmentation length.

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

