# SegmentGeometry

This is the repository for SegmentGeometry, an extension for <a href="https://slicer.org/" target ="_blank">3D Slicer</a>.

SegmentGeometry iterates slice-by-slice through a segment to calculate the second moment of area and other cross-sectional properties. Results are exported to a table and plotted for quick visualizations.

![image](https://raw.githubusercontent.com/jmhuie/Slicer-SegmentGeometry/main/SegmentGeometry/Resources/Icons/SegmentGeometryScreenshot1.png)

# Installation

The official method for installing SegmentGeometry is through 3D Slicer's built-in Extensions Manager. First, install the most recent stable or preview release of <a href="https://download.slicer.org/" target ="_blank">3D Slicer</a> (r29738 or later). 
In 3D Slicer, open the Extensions Manager module and search for "SegmentGeometry". Install the extension and restart the application. After, SegmentGeometry should be fully functional and located in the Quantification 
module category. If using the current stable release of Slicer, SegmentGeometry can be updated in the Extension Manager. If using the Preview Release of Slicer, the most recent build must be downloaded and installed to update SegmentGeometry.

# How to Cite

If you use SegmentGeometry in your work, please cite the follow publication:
* Huie JM, Summers AP, Kawano SM. (2022) SegmentGeometry: a tool for measuring second moment of area in 3D Slicer. Integrative Organismal Biology. https://doi.org/10.1093/iob/obac009

To cite 3D Slicer as a general image analysis platform, please use: 
* Kikinis R, Pieper, SD, Vosburgh KG. (2014) 3D Slicer: A Platform for Subject-Specific Image Analysis, Visualization, and Clinical Support. In Intraoperative Imaging and Image-Guided Therapy (pp. 277–289). Springer, New York, NY. https://doi.org/10.1007/978-1-4614-7657-3_19

To cite the length normalization method, please use: 
* Doube M, Conroy AW, Christiansen P, Hutchinson JR, Shefelbine S. (2009) Three-dimensional geometric analysis of felid limb bone allometry. PloS one. 4(3):e4742. https://doi.org/10.1371/journal.pone.0004742

To cite the material normalization method, please use: 
* Summers AP, Ketcham RA, Rowe T. (2004) Structure and function of the horn shark (Heterodontus francisci) cranium through ontogeny: development of a hard prey specialist. Journal of Morphology. 260(1):1-2. https://doi.org/10.1002/jmor.10141

Some source code was ported from BoneJ. To cite BoneJ or find out more, please use:
* Doube M, Kłosowski MM, Arganda-Carreras I, Cordeliéres F, Dougherty RP, Jackson J, Schmid B, Hutchinson JR, Shefelbine SJ. (2010) BoneJ: free and extensible bone image analysis in ImageJ. Bone 47:1076-9. https://doi.org/10.1016/j.bone.2010.08.023 
* Domander R, Felder AA, Doube M. (2021) BoneJ2 - refactoring established research software. Wellcome Open Research. 6:37. https://doi.org/10.12688/wellcomeopenres.16619.2


# Workflow Example
Below are general instructions on how to use SegmentGeometry, including a step-by-step guide for general use cases and a demo video. SegmentGeometry provides an example dataset in the Sample Data module that consists of a salamander 
CT scan from <a href="https://www.morphosource.org/media/000049486" target ="_blank">MorphoSource</a> and a segmentation file that contains an 
isolated humerus and solid humerus segment for measuring compactness. New users are encouraged to follow along with guide and demo video using the sample data set or their own.

### General Use Case
1. Start 3D Slicer.
2. Load in CT Data.
3. Isolate and segment the bone or structure of interest in the Segment Editor module.
4. Switch to the SegmentGeometry module.
5. Select your inputs. "Segmentation" is the Segmentation node that contains your segment and "Volume" is the corresponding Volume node. Both are required.
6. Select the "Slice View" that will run along the length of the desired measurement (long) axis. Generally, it is easier to use the default "Slice View" and rotate the segment accordingly. Changing the "Slice View" is only recommended when no transformations are needed, but the desired cross-sections are not visibile in the red view (default).
7. Use the provided Transform Tools to rotate the segment and align it with the desired long axis/slice view. You should be able to scroll through the selected "Slice View" and see the exact cross-sections you want to compute on. For most beam-like structures, using the "Align w/ Principal Axes" button should be sufficient.
8. Choose whether to compute on every slice in the segment or only some of them and change the "Percent Interval". For large datasets, it may be beneficial to sample slices in intervals representing some percentage of segment length. By default, SegmentGeometry will sample sections in 1% increments. Enter "0" to compute on every slice.
9. Choose which computations should be performed.
10. Select an output table and a chart node. 
11. Click Apply. Loading times can vary between 1-30 seconds depending on the size of the data set.
12. Save results by exporting the table or copying and pasting the table values to a separate spreadsheet.

### Using a Pre-made Mesh
Sometimes the raw image data are not available and you only have a segmented 3D model/mesh (.stl, .obj, .ply) downloaded or created elsewhere. SegmentGeometry can still be used to analyze the mesh so long as the internal geometry of the mesh reflects the actual structure. Note: some mesh file formats do not retain information about size, but using the material normalization method circumvents this problem. When possible, exporting as a .ply is recommended.
1. Load in mesh file.
2. In the Data module, right click the mesh and click "Convert model to segmentation node"
3. A segmentation node with your model should have been made. Right click it and click "Export visible segments to binary labelmap"
4. A labelmap should have been made. Right click it and click "Edit properties" or navigate to the Volume module.
5. In the Volume module, ensure the labelmap is the Active volume, and expand the "Volume Information"
6. Navigate to where it says "Convert to scalar volume" and click the "Convert" button.
7. Now you have a Segmentation node and a Volume node that can be used with SegmentGeometry like normal.

### Demo Videos
Here are some example videos that demonstrate how to use SegmentGeometry for different purposes.
1. <a href="https://youtu.be/fBaTM5utQC0" target ="_blank">How to calculate second moment of area and compactness of a salamander limb bone</a> 
2. <a href="https://youtu.be/fI5xFT7_81I" target ="_blank">How to calculate second moment of area of a cat mandible</a> 

# Advanced Tools

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

# Output Details
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

# Frequently Asked Questions

1. I need help using SegmentGeometry, I received an error, or I think I found a bug. What do I do?

First, make sure that you have the most recent version of SegmentGeometry by updating the extension (stable release) or re-downloading 3D Slicer (preview release). If the error still persists, you can report your issues on the <a href="https://discourse.slicer.org/" target ="_blank">3D Slicer discourse page</a> and tag me (@jmhuie) or you may email me (jonathanmhuie[at]gmail.com). I will do my best to address problems in a timely manner.

2. I have a suggestion or feature request for how to improve SegmentGeometry. What do I do?

Fantastic! I am always trying to improve the ease and utility of SegmentGeometry and would love to hear your suggestions. Please reach out to me through 3D Slicer Discourse page or via email.

# Funding Acknowledgement

Jonathan M. Huie was funded by a NSF Graduate Research Fellowship (DGE-1746914) and a George Washington University Harlan Research Fellowship.

