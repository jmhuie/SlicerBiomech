# Segment Geometry

This is the repository for Segment Geometry, an extension for 3D Slicer.

Segment Geometry currently contains one module that iterates slice-by-slice through a segment to calculate the second moment of area and other cross-sectional properties. 

<img width="1792" alt="Scene Schreenshot" src="https://user-images.githubusercontent.com/52302862/130000723-9d29b0e3-b973-4d62-bca4-633c4c207ae7.png">

# Installation

Segment Geometry is still under development. To unofficially install Segment Geometry, you may clone the contents of this repository and save it somewhere accessible. If you downloaded this repo from Google Drive, unzip the folder and save the contents somewhere. In 3D Slicer, go to Edit >> Application Settings >> Modules. Under "Additional module paths" click the little arrow point right, and then click "Add" and navigate to and select the "SegmentGeometry" folder in the the SegmentSliceGeometry folder. Click OK and restart 3D Slicer. Now, the Segment Geometry module with automatically load in whenever you open 3D Slicer. To 
obtain the most recent version of the module, you must re-download the contents of this repository. This module is dependent on the ExtraSegmentEditorEffects extension. Official release coming soon.

Segment Geometry is dependent on the ExtraSegmentEditorEffects extension

# Workflow

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

**Note:** If your data is isotropic, it does not matter which slice view is perpendicular to the long axis (z-axis). If your data is anistropic, you get the best results if rotate your specimen so that the long axis is perpendicular to the red slice view. You can also resample your volume to make it isotropic in the Resample Scalar Volume module for better results.

10. Go to the Segment Geometry module. Either by searching (Ctrl+F) or finding it under the Quantification category.
11. Select your inputs. "Segmentation" is the Segmentation node that contains your segment and "Volume" is the corresponding Volume node. All are required if you applied a linear transformation.

**Note:** If you applied a linear transformation to your segment, it's absolutely crucial that your whole segment lies within the 3D bounds of its untransformed Volume Node. The "Snap to Center" and "Toggle Bounding Box" buttons have been added to make this easier.

12. Click the "Snap to Center" to automatically move your segment to the center of the untransformed Volume node.
13. Click the "Toggle Bounding Box" to draw a box around the untransformed Volume node. If your segment is completely inside the box, you are OK to proceed. If part of the segment is outside of the box, you may need to manually translate your segment using the Transforms module. If the box is too small for your segment, you will need to extend the bounds of the Volume node using the Crop Volume module. Click the button again to hide the bounding box.
14. Select the "Segment Axis". This is the slice view that is perpendicular to the long axis and contains the cross-sections you want to compute on.
15. Choose how frequently to sample along the length of the axis (percent intervals). By default will sample in 1% intervals along the length of the segment. Enter zero to compute on every slice in the segment.
16. Select an output table and chart for the results. By default, a new table and chart will be made automatically if one does not already exist for that segment.
17. Under "Advanced" choose which computations should be performed.

**Note:** If you selected "Mean Pixel Brightness" and transformed your segment, you must check the "Resample Volume" box. This will resample your volume using the Resample Scalar/Vector/DWI Volume module with linear interpolation. Because this process substaintially increases computation time, the resampled volume will be saved and may be used as the input Volume node if analyses need to be re-run.

18. If the direction of the loading axis is known, a custom neutral axis can be used for relevant computations. By default the netural axis is parallel to the horizontal. Enter an angle to determine how much the neutral axis deviates from the horizontal. Rotates the neutral axis in counter clockwise direction.

**Note:** To calculate total cross-sectional area or global compactness, a separate solid segment that contains the full structure is required. Recommend using the WrapSolidify tool in the Segment Editor module. Requires the ExtraSegmentEditorEffects and WrapSolidify extensions.

19. Click Apply

# List of Outputs

- Segment: Segment name.

- Percent: Percent of segment length.

- Length: Length of segment along the defined segmentation length.

- Mean Brightness: Mean pixel brightness calculated as the average grey scale value. 

- CSA: Cross-sectional area.

- Total CSA: Total cross-sectional area.

- Compactness: Global compactness calculated as CSA/Total CSA.

- Imax: Second moment of area around the major principal axis.

- Imin: Second moment of area around the minor principal axis.

- Theta: Angle (radians) between the minor principal axis and the horizontal axis.

- J: Polar moment of area using the principal axes. Calculated as Imin + Imax.

- Zmax: Section modulus around the major principal axis. 

- Zmin: Section modulus around the minor principal axis.

- Rmax: Distance to the furthest pixel from the major principal axis.

- Rmin: Distance to the furthest pixel from the minor principal axis.

- Ina: Second moment of area around the neutral axis.

- Ila: Second moment of area around the loading axis.

- Jna: Polar moment of area around the neutral and loading axes. Calculated as Ina + Ifa.

- Zna: Section modulus around the neutral axis.

- Zla: Section modulus around the loading axis.

- Rna: Distance to the furthest pixel from the neutral axis.

- Rla: Distance to the furthest pixel from the force axis.

Material normalized second moment of area variables are indicated with "MatNorm". These are calculated by dividing the calculated second moment of area value by the second moment of area of solid with the same cross-sectional area. The purpose is investigate how well the material is distributed to maximize bending resistance (Summers et al. 2004).

Length normalized variables are indicated with "LenNorm". These are calculated by taking the respective root of variable to make in linear and then dividing it by the length of the segment. The purpose is make comparisons between individuals or species while removing the effects of size (Doube et al. 2012)

# Funding Acknowledgement

Jonathan Huie was funded by a NSF Graduate Research Fellowship (DGE-1746914).

