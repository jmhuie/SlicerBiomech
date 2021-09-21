# Segment Geometry

This is the repository for Segment Geometry, an extension for <a href="https://slicer.org/" target ="_blank">3D Slicer</a>.

Segment Geometry iterates slice-by-slice through a segment to calculate the second moment of area and other cross-sectional properties. Results are exported to a table and plotted for quick visualizations. 

<img width="1792" alt="overview" src="https://raw.githubusercontent.com/jmhuie/Slicer-SegmentGeometry/main/SegmentGeometry/Resources/Icons/SegmentGeometryScreenshot1.png">

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
Below are instructions for how to use Segment Geometry, including a step-by-step guide for general use cases and 
details on the more technical tools. Segment Geometry provides an example dataset in the Sample Data module. It consists of a salamander 
CT scan from <a href="https://www.morphosource.org/media/000049486" target ="_blank">MorphoSource</a>, a segmentation file that contains an 
isolated humerus and solid humerus segment for measuring compactness, and a linear transformation node. You may choose to follow along with the instructions using 
the sample data set or your own.
 

### General Use Case
1. Start 3D Slicer.
2. Load in CT Data.
3. Segment bone or structure of interest in the Segment Editor module.
4. Create a new Linear Transform in the Transforms module.
5. Switch to the Segment Geometry module.
6. Select your inputs. "Segmentation" is the Segmentation node that contains your segment and "Volume" is the corresponding Volume node. Both are required.
7. Use the provided Transform Tools to rotate the segment and align it with the desired long axis/slice view. 
8. Select the "Slice View" perpendicular to the desired measurement axis. It should be the slice view that contains the cross-sections you want to compute on.
9. Choose whether to compute on every slice in the segment or only some of them. For large datasets, it may be beneficial to sample slices in intervals representing some percentage of segment length. By default, Segment Geometry will sample sections in 1% increments. Enter "0" to compute on every slice.
10. Choose which computations should be performed.
11. Select an output table and a chart node. 
12. Click Apply. Loading times can vary between 1-30 seconds depending on the size of the data set.
13. Save results by exporting the table or copying and pasting the table values to a separate spreadsheet.

### Transform Tools
Segment Geometry provides three tools for rotating and aligning segments with the desired long axis. 
* **Align With Principal Axes** will use the Segment Statistics module to calculate the segment's principal axes and align them with the XYZ axes.
* **Rotate Segment In 3D View** will generate an interactive 3D bounding box that can be used to rotate the segment in 3D space. Click+Drag the sides of the box to rotate it. Click button again to disable rotation in 3D view.
* **Initialize Rotation Sliders** click to initialize the sliders that will rotate the segment around its centroid.

### Use Custom Neutral Axis
If the direction of the loading axis is known, a custom neutral axis can be used to calculate second moment of area and section modulus. To set the neutral axis, check the "Use custom neutral axis" box and enter a positive value that represents the angle be between the neutral axis and the horizontal, starting from the right side and moving in clockwise direction. By default, the netural axis is parallel to the horizontal axis.

### Compute Unitless Variables
Three methods for normalizing variables to remove the effects of size are implemented in Segment Geometry. 

* **Length normalization** from Doube et al. (2009). With this method, cross-sectional area, second moment of area, and section modulus are corrected based on the length of the segment. The respective root of the variables are taken to make them linear; then they are divided by total segment length. For example, cross-sectional area has a unit of mm^2 so the square root of CSA is calculated and the result is divided by segment length.
* **Material normalization** from Summers et al. (2004). With this method, second moment of area/section modulus values are divided by the second moment of area/section modulus of a solid circle with the same cross-sectional area. Normalized values represent how well the structure's material is distributed relative to an idealized beam. 
* **Compactness** is a method for normalizing cross-sectional area. Compactness is the area of a slice occupied by the segment divided by the total area of the section (area of the segment + area of any internal vacuities). To measure compactness, the user must provide a separate segment that contains the the whole structure including the vacuities. The <a href="https://github.com/sebastianandress/Slicer-SurfaceWrapSolidify" target ="_blank">SurfaceWrapSolidify</a> extension, implemented in the Segment Editor module (with the ExtraSegmentEditorEffects extension), 
can automatically generate a segment with the vacuities filled in. 

To normalize a variable, enable the check boxes of both the variables you want and the desired normalization method(s). If you use either the length or material normalization in your research, please cite the relevant papers. See the "How to Cite" section.

# Output Details
Segment Geometry presents the results as a table and automatically plots second moment of area over percent length of the segment. Segment Geometry also generates a resampled and cropped volume of the segment for easy visualization of the individual slice geometries. 
When calculating second moment of area or section modulus, Segment Geometry will approximate the segment's aspect ratio and alert the user when the no-shear assumption of Euler-Bernoulli's beam theory may not be met. 
Below contains brief information on the possible computations.

- Segment: Segment name.

- Slice Index: Segment slice numbers that correspond to the resampled and cropped volume exported by Segment Geometry.

- Percent: Percent of total segment length.

- Length: Length of the segment is defined as the number of slices that make up the segment, multiplied by the image spacing.

- Max Diameter: Maximum Feret diameter of the section.

- Perimeter: Perimeter of the section. Note that calculation may be incorrect for cross-sections where inner vacuities connect to the outer edge or there is more than one island in the section. Perimeter calculations are intended to be conducted on closed form cross-sections.

- Mean Brightness: Mean voxel brightness or average grey scale value of the section. 

- CSA: Cross-sectional area.

- Compactness: Ratio between cross-sectional area and the provided total cross-sectional area.

- Cx: Centroid x-coordinates that correspond to the resampled and cropped volume exported by Segment Geometry. Presented in IJK format.

- Cy: Centroid y-coordinates that correspond to the resampled and cropped volume exported by Segment Geometry. Presented in IJK format.

- Theta minor: Angle (degrees) between the minor principal axis and horizontal axis in the clockwise direction, starting from the right side.

- Theta major: Angle (degrees) between the major principal axis and horizontal axis in the clockwise direction, starting from the right side.

- Iminor: Second moment of area around the minor principal axis.

- Imajor: Second moment of area around the major principal axis.

- Zminor: Section modulus around the minor principal axis.

- Zmajor: Section modulus around the major principal axis. 

- Rminor: Distance to the furthest pixel from the minor principal axis.

- Rmajor: Distance to the furthest pixel from the major principal axis.

- Ina: Second moment of area around the neutral axis.

- Ila: Second moment of area around the loading axis.

- Zna: Section modulus around the neutral axis.

- Zla: Section modulus around the loading axis.

- Rna: Distance to the furthest pixel from the neutral axis.

- Rla: Distance to the furthest pixel from the force axis.

- Material Normalization: Material normalized values are indicated with "MatNorm"

- Length Normalization: Length normalized values are indicated with "LenNorm"

# Funding Acknowledgement

Jonathan Huie was funded by a NSF Graduate Research Fellowship (DGE-1746914) and a Harlan Research Fellowship.

