# SegmentGeometry

**Summary:** SegmentGeometry iterates slice-by-slice through a segment to calculate the second moment of area and other cross-sectional properties. Results are exported to a table and plotted for quick visualizations.

## Usage

### Segment Transformation Tools
SegmentGeometry provides three tools for rotating and aligning segments with the desired long axis. 
* **Align With Principal Axes** - will use the Segment Statistics module to calculate the segment's principal axes and align them with the XYZ axes.
* **Rotate Segment In 3D View** - will generate an interactive 3D bounding box that can be used to rotate the segment in 3D space. Click+Drag the sides of the box to rotate it. Click button again to disable rotation in 3D view.
* **Initialize Rotation Sliders** - will initialize the sliders that can be used to rotate the segment around its centroid.
* **Reset** - will reset transformations applied through SegmentGeometry and the custom neutral axis, if defined.

### Use Custom Neutral Axis
If the direction of the loading axis is known or hypothesized, a custom neutral axis can be used to calculate second moment of area and other relevant computations. Checking the "Use custom neutral axis" box with enable the option and draw a line that represents the neutral axis. This line can be manually rotated by clicking and dragging the closed end of the line 
in either the slice view or 3D view. Alternatively, the user may enter a value between 0 and 180 that represents the angle (in degrees) between the horizontal and the neutral axis, starting from the right and moving in clockwise direction. 
The centroidal neutral axis line is presented at the centroid of the current slice by default, but the "Update Neutral Axis" button can be used to view the line on any slice of the segment or move it back to the centroid if is not longer there (e.g., after applying a transformation to the segment). 

### Compute Unitless Variables
Three methods for normalizing variables to remove the effects of size are implemented in SegmentGeometry. 

* **Length normalization** -  from Doube et al. (2009). With this method, cross-sectional area, second moment of area, and section modulus are corrected based on the length of the segment. The respective root of the variables are taken to make them linear; then they are divided by total segment length. For example, cross-sectional area has a unit of mm^2 so the square root of CSA is calculated and the result is divided by segment length.
* **Material normalization** -  from Summers et al. (2004). With this method, second moment of area/section modulus values are divided by the second moment of area/section modulus of a solid circle with the same cross-sectional area. Normalized values represent how well the structure's material is distributed relative to an idealized beam. 
* **Compactness** - is a method for normalizing cross-sectional area. Compactness is the area of a slice occupied by the segment divided by the total area of the section (area of the segment + area of any internal vacuities). To measure compactness, the user must provide a separate segment that contains the the whole structure including the vacuities. The <a href="https://github.com/sebastianandress/Slicer-SurfaceWrapSolidify" target ="_blank">SurfaceWrapSolidify</a> extension, implemented in the Segment Editor module (with the ExtraSegmentEditorEffects extension), 
can automatically generate a segment with the vacuities filled in. 

To normalize a variable, enable the check boxes of both the variables you want and the desired normalization method(s). If you use either the length or material normalization in your research, please cite the relevant papers. See the "How to Cite" section.

### Output Details
SegmentGeometry presents the results as a table and automatically plots second moment of area over percent length of the segment. SegmentGeometry also generates a resampled and cropped volume of the segment for easy visualization of the individual slice geometries. 
When calculating second moment of area or section modulus, SegmentGeometry will approximate the segment's aspect ratio and alert the user when the no-shear assumption of Euler-Bernoulli's beam theory may not be met. 
Below contains brief information on the possible computations.

- Segment: Segment name.

- Slice Index: Segment slice numbers that correspond to the resampled and cropped volume exported by SegmentGeometry.

- Percent: Percent of total segment length.

- Length: Length of the segment is defined as the number of slices that make up the segment, multiplied by the image spacing.

- Max Diameter: Maximum Feret diameter of the section.

- Perimeter: Perimeter of the section. Note that calculation may be incorrect for cross-sections where inner vacuities connect to the outer edge or there is more than one island in the section. Perimeter calculations are intended to be conducted on closed form cross-sections.

- Mean Brightness: Mean voxel brightness or average grey scale value of the section. 

- CSA: Cross-sectional area.

- Compactness: Ratio between cross-sectional area and the provided total cross-sectional area.

- Cx: Centroid x-coordinates that correspond to the resampled and cropped volume exported by SegmentGeometry. Presented in IJK format.

- Cy: Centroid y-coordinates that correspond to the resampled and cropped volume exported by SegmentGeometry. Presented in IJK format.

- Theta: Angle (degrees) between the minor principal axis and horizontal axis in the clockwise direction, starting from the right side.

- Iminor: Second moment of area around the minor principal axis.

- Imajor: Second moment of area around the major principal axis.

- Zminor: Section modulus around the minor principal axis.

- Zmajor: Section modulus around the major principal axis. 

- Rminor: Distance to the furthest pixel from the minor principal axis.

- Rmajor: Distance to the furthest pixel from the major principal axis.

- Ina: Second moment of area around the custom neutral axis.

- Ila: Second moment of area around the loading axis perpendicular to the custom neutral axis.

- Zna: Section modulus around the custom neutral axis.

- Zla: Section modulus around the loading axis perpendicular to the custom neutral axis.

- Rna: Distance to the furthest pixel from the custom neutral axis.

- Rla: Distance to the furthest pixel from the loading axis perpendicular to the custom neutral axis.

- Jz: Polar moment of inertia.

- Zpol: Polar section modulus.

- Rmax: Maximum radius 

- Material Normalization: Material normalized values are indicated with "MatNorm"

- Length Normalization: Length normalized values are indicated with "LenNorm"

## How to Cite

If you use SegmentGeometry in your work, please cite the follow publication:
* Huie JM, Summers AP, Kawano SM. (2022) SegmentGeometry: a tool for measuring second moment of area in 3D Slicer. Integrative Organismal Biology. https://doi.org/10.1093/iob/obac009

Some source code was ported from BoneJ. To cite BoneJ or find out more, please use:
* Doube M, Kłosowski MM, Arganda-Carreras I, Cordeliéres F, Dougherty RP, Jackson J, Schmid B, Hutchinson JR, Shefelbine SJ. (2010) BoneJ: free and extensible bone image analysis in ImageJ. Bone 47:1076-9. https://doi.org/10.1016/j.bone.2010.08.023 
* Domander R, Felder AA, Doube M. (2021) BoneJ2 - refactoring established research software. Wellcome Open Research. 6:37. https://doi.org/10.12688/wellcomeopenres.16619.2

## Tutorials