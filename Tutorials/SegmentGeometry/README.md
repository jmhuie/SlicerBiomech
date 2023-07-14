## SegmentGeometry

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
