# Segment Geometry

This is the repository for Segment Geometry, an extension for 3D Slicer.

Segment Geometry iterates slice-by-slice through a segment to calculate the second moment of area and other cross-sectional properties. Results are exported to a table and plotted for quick visualizations.

<img width="1792" alt="Screenshot" src="https://user-images.githubusercontent.com/52302862/131609394-6f44506d-967a-41c1-abff-4d235f184263.png">

# Installation

The official method for installing Segment Geometry is through 3D Slicer's built-in Extension Manager. To install Segment Geometry, first install the most recent stable release of <a href="https://download.slicer.org/" target ="_blank">3D Slicer</a> (r29738 or later). 
In 3D Slicer, open the Extensions Manager module and search for "Segment Geometry". Install the extension and its dependency (ExtraSegmentEditorEffects). After restarting the application, Segment Geometry should be fully functional and located in the Quantification 
module category.

# How to Cite

Citable paper for Segment Geometry coming soon. Below are other relevant citations.

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
4. Create a new Linear Transform in the Transforms module.
5. Move your Segmentation node and the Volume node from the "Transformable" column to the "Transformed" column.
6. Use the rotation sliders or the interactive "Visible in 3D view" tool under display to orient your segment. Align the long axis of your segment with one of the three slice views based on how you would like slice through the segment.
7. Navigate to Segment Geometry.
8. Select your inputs. "Segmentation" is the Segmentation node that contains your segment and "Volume" is the corresponding Volume node. Both are required if you applied a linear transformation.
9. Click the "Snap Segment to Center" button to automatically move your segment to the center of the untransformed Volume node.
10. Click the "Show/Hide Bounding Box" button to draw a box around the untransformed Volume node. If your segment is completely inside the box, you are OK to proceed. If part of the segment is outside of the box, you will need to manually move your segment into the box using the Transforms module. If the box is too small for your segment, you will need to extend the bounds of the Volume node using the Crop Volume module. Click the button again to hide the bounding box.
11. Select the "Long Axis". This is the slice view perpendicular to the long axis. It should contain the cross-sections you want to compute on.
12. Choose whether to compute on the whole segment or sample the segment in increments. By default, Segment Geometry will sample sections in 1% increments along the length of the segment. Enter "0" to compute on the whole segment.
13. Select output table and chart nodes.
14. Under "Advanced" choose which computations should be performed.
15. Click Apply. Loading times can vary between 1-30 seconds depending on the size of the data set.
16. Save results by exporting the table or copying and pasting the table values to a separate spreadsheet.

### Use Custom Neutral Axis
If the direction of the loading axis is known, a custom neutral axis can be used to calculate second moment of area and section modulus. To set the neutral axis, check the "Use custom neutral axis" box and enter a positive value that represents the angle be between the neutral axis and the horizontal, starting from the right side and moving in clockwise direction. By default, the netural axis is parallel to the horizontal axis.

### Compute Unitless Variables
Three methods for normalizing variables to remove the effects of size are implemented in Segment Geometry. 

* **Length normalization** from Doube et al. (2012). With this method, cross-sectional area, second moment of area, and section modulus are corrected based on the length of the segment. The respective root of the variables are taken to make them linear, and then they are divided by total segment length. For example, cross-sectional area has a unit of mm^2 so the square root of CSA is calculated and the result is divided by segment length.
The purpose is to be able to examine proportional differences in trait values between individuals or species without the effects of size.
* **Material normalization** from Summers et al. (2004). With this method, each second moment of area value is divided by the second moment of area of a solid rod with the same cross-sectional area as that slice. Normalized values represent how well the structure's material is distributed to maximize bending resistance relative to an idealized beam. The material normalization isolates the effect of shape on second moment of area.
* **Compactness** is a method for normalizing cross-sectional area. Compactness is the area of a slice occupied by the segment divided by the total area of the section (area of the segment + area of any internal vacuities). To measure compactness, the user must provide a separate segment that contains the the whole structure including the vacuities.

To normalize a variable, enable the check boxes of both the variables you want and the desired normalization method(s). If you use either the length or material normalization in your research, please cite the relevant papers. See the "How to Cite" section.

# Output Details

- Segment: Segment name.

- Slice Index: The corresponding slice number from the untransformed Volume node.

- Percent: Percent of total segment length.

- Length: Length of the segment defined as the number of slices that make up the segment, multiplied by the image spacing.

- Max Diameter: Maximum feret diameter of the section.

- Mean Brightness: Mean pixel brightness calculated as the average grey scale value. Note that calculating mean pixel brightness is the only parameter that requires resampling the Volume node. If the segment is transformed, the Volume node will be resampled automatically with the Resample Scalar/Vector/DWI Volume module and a linear interpolation. 

- CSA: Cross-sectional area.

- Compactness: Ratio between cross-sectional area and the provided total cross-sectional area.

- Cx: x-coordinate of the centroid.

- Cy: y-coordinate of the centroid.

- Theta min: Angle (degrees) between the minor principal axis and horizontal axis in the clockwise direction, starting from the right side.

- Theta max: Angle (degrees) between the major principal axis and horizontal axis in the clockwise direction, starting from the right side.

- Imin: Second moment of area around the minor principal axis.

- Imax: Second moment of area around the major principal axis.

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

# Frequently Asked Questions

**Q: My CT data has anisotropic voxels, can I use it in Segment Geometry?**

A: At this time, Segment Geometry cannot handle data with anisotropic voxels. You must resample your data to make it isotropic before using Segment Geometry.

**Q: I got an error that says "Attempted to compute on a slice with no pixels. Check for empty slices". What does that mean?**

A: It means there is a break in your segment, where some slices don't contain any pixels. Often this is caused by floating pixels that are not part of the structure. Make sure that your segment is one connected structure.

**Q: I got an error that says "The segment is outside of the volume's bounds!". What does that mean?**

A: It means that your transformed segment was moved outside the bounds of the original untransformed volume. Use the "Snap Segment to Center" and "Show/Hide Bounding Box" buttons to make sure your segment is inside the bounding box.

**Q: I got a warning that says "Warning! The no-shear assumption may not be met. Click OK to proceed.". What does that mean?**

A: It means that the length of the structure is less than 10x the narrowest diameter of the structure so the no-shear assumption of the Euler-Bernoulli beam theory may not be met. 

# Funding Acknowledgement

Jonathan Huie was funded by a NSF Graduate Research Fellowship (DGE-1746914).

