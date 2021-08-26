# Segment Geometry

This is the repository for Segment Geometry, an extension and module for 3D Slicer.

Segment Geometry iterates slice-by-slice through a segment to calculate the second moment of area and other cross-sectional properties. Results are exported as a table and plotted for quick visualizations.


<img width="1792" alt="Scene Schreenshot" src="https://user-images.githubusercontent.com/52302862/130000723-9d29b0e3-b973-4d62-bca4-633c4c207ae7.png">

# Installation

The official method for installing Segment Geometry is through 3D Slicer's built-in Extension Manager. To install Segment Geometry, first install the most recent stable release of <a href="https://download.slicer.org/" target ="_blank">3D Slicer</a> (r29738 or later). 
In 3D Slicer, open the Extensions Manager module and search for "Segment Geometry". Install the extension and its dependency (ExtraSegmentEditorEffects). After restarting the application, Segment Geometry should be fully functional and located in the Quantification 
module category.

# How to Cite

Citable paper for Segment Geometry is still a work in progress. Below are other relevant citations.

To cite 3D Slicer as a general image analysis platform, please use: 
* Kikinis R, Pieper, SD, Vosburgh KG. (2014) 3D Slicer: A Platform for Subject-Specific Image Analysis, Visualization, and Clinical Support. In Intraoperative Imaging and Image-Guided Therapy (pp. 277–289). Springer, New York, NY. https://doi.org/10.1007/978-1-4614-7657-3_19

To cite the length normalization method, please use: 
* Doube M, Conroy AW, Christiansen P, Hutchinson JR, Shefelbine S. (2009) Three-dimensional geometric analysis of felid limb bone allometry. PloS one. 4(3):e4742. https://doi.org/10.1371/journal.pone.0004742

To cite the material normalization method, please use: 
* Summers AP, Ketcham RA, Rowe T. (2004) Structure and function of the horn shark (Heterodontus francisci) cranium through ontogeny: development of a hard prey specialist. Journal of Morphology. 260(1):1-2. https://doi.org/10.1002/jmor.10141

Some source code was ported from BoneJ. To cite BoneJ or find out more, please use:
* Doube M, Kłosowski MM, Arganda-Carreras I, Cordeliéres F, Dougherty RP, Jackson J, Schmid B, Hutchinson JR, Shefelbine SJ. (2010) BoneJ: free and extensible bone image analysis in ImageJ. Bone 47:1076-9. https://doi.org/10.1016/j.bone.2010.08.023 
* Domander R, Felder AA, Doube M. (2021) BoneJ2 - refactoring established research software. Wellcome Open Research. 6:37. https://doi.org/10.12688/wellcomeopenres.16619.2


# Workflows
### General Use Case
1. Start 3D Slicer.
2. Load in CT Data.
3. Segment bone or structure of interest in the Segement Editor module.
6. Create a new Linear Transform in the Transforms module.
7. Move your Segmentation node and the Volume node from the "Transformable" column to the "Transformed" column.
8. Use the Rotation sliders or the interactive "Visible in 3D view" tool under display to rotate your segment. Align your segment with the three slice views based on how you would like to interatively slice through the segment. You should be able to scroll through one of the slice views and see the cross-sections you want to compute on.
* **Note:** If your data is isotropic, it does not matter which slice view is perpendicular to the long axis (z-axis). If your data is anistropic, you'll get the best results if rotate your specimen so that the long axis is perpendicular to the red slice view. You can also resample your volume to make it isotropic in the Resample Scalar Volume module for better results.

10. Go to the Segment Geometry module. Either by searching (Ctrl+F) or finding it under the Quantification category.
11. Select your inputs. "Segmentation" is the Segmentation node that contains your segment and "Volume" is the corresponding Volume node. All are required if you applied a linear transformation.
12. Click the "Snap to Center" to automatically move your segment to the center of the untransformed Volume node.
13. Click the "Toggle Bounding Box" to draw a box around the untransformed Volume node. If your segment is completely inside the box, you are OK to proceed. If part of the segment is outside of the box, you may need to manually translate your segment using the Transforms module. If the box is too small for your segment, you will need to extend the bounds of the Volume node using the Crop Volume module. Click the button again to hide the bounding box.
* **Note:** If you applied a linear transformation to your segment, it's absolutely crucial that your whole segment lies within the 3D bounding box.

15. Select the "Segment Axis". This is the slice view that contains the cross-sections you want to compute on.
16. Choose how much of the segment to sample. By default, it will sample every 1% of the segment's length. Enter "0" to compute on every slice in the segment.
17. Select an output table and chart for the results. A new table and chart will be created automatically by default.
18. Under "Advanced" choose which computations should be performed.
19. Click Apply.

### Compute Mean Pixel Brightness
If you selected "Mean Pixel Brightness" and transformed your segment, you must check the "Resample Volume" box. This will resample your volume using the Resample Scalar/Vector/DWI Volume module with linear interpolation. Because this process substaintially increases computation time, the resampled volume will be saved and may be used as the input Volume node if you need to re-run the analysis.

### Use Custom Neutral Axis
If the direction of the loading axis is known, a custom neutral axis can be used to calculate second moment of area, polar moment of inertia, section modulus, and chord length. To define the neutral axis, check the "Use custom neutral axis" box and enter a positive value that represents how much the neutral axis deviates from the horizontal in the clockwise direction. By default, the netural axis is set parallel to the horizontal.

### Compute Unitless Variables
Two methods for normalizing variables to remove the effects of size are implemented in Segment Geometry. 
* First is a length normalization from Doube et al. (2012). With this method, cross-sectional area, second moment of area, polar moment of inertia, and section modulus are corrected based on the length of the segment. First the respective root of the variables are taken to make them linear, then they are divided by total segment length. For example, cross-sectional area has a unit of mm^2 so the square root of CSA is calculated and the result is divided by segment length.
The purpose is to be able to examine proportional differences in trait values between individuals or species without the effects of size.
To use either normalization method, enable normalization check boxes. If either method can be used to normalize any of the selected computations, then normalized values will be appended to the end of the results table. If you use either method in your research please cite the relevant papers. See the "How to Cite" section.
* Second is a material normalization from Summers et al. (2004). With this method, each second moment of area value is divided by the second moment of area of a solid rod with the same cross-sectional area as that slice. The purpose is investigate how well the structure's material is distributed to maximize bending resistance relative to an idealized beam, and make comparisons between individuals or species without the effects of size.

# Output Details

- Segment: Segment name.

- Percent: Percent of segment length.

- Length: Length of segment along the defined segmentation length.

- Feret Diameter: Maximum feret diameter.

- Mean Brightness: Mean pixel brightness calculated as the average grey scale value. 

- CSA: Cross-sectional area.

- Imin: Second moment of area around the minor principal axis.

- Imax: Second moment of area around the major principal axis.

- Theta min: Angle (degrees) of how much the minor principal axis deviates from the horizontal axis in a clockwise direction.

- Theta max: Angle (degrees) of how much the major principal axis deviates from the horizontal axis in a clockwise direction.

- Zmin: Section modulus around the minor principal axis.

- Zmax: Section modulus around the major principal axis. 

- Rmin: Distance to the furthest pixel from the minor principal axis.

- Rmax: Distance to the furthest pixel from the major principal axis.

- Ina: Second moment of area around the neutral axis.

- Ila: Second moment of area around the loading axis.

- Zna: Section modulus around the neutral axis.

- Zla: Section modulus around the loading axis.

- Rna: Distance to the furthest pixel from the neutral axis.

- Rla: Distance to the furthest pixel from the force axis.

- Material Normalization: Material normalized values are indicated with "MatNorm"

- Length Normalization: Length normalized values are indicated with "LenNorm"

# Funding Acknowledgement

Jonathan Huie was funded by a NSF Graduate Research Fellowship (DGE-1746914).

