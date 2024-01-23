# DentalDynamics Tutorial

This tutorial explains how to use `Dental Dynamics` to measure and calculate jaw and tooth mechanical traits. This is a SlicerBiomech specific function and in this example we are using the *Aneides lugubris* sample data set from the SlicerBiomech tab of the  `Sample Data`  module.

Features of DentalDynamics:

-  Designed to calculate several jaw and tooth traits using a 3D Slicer segmentation with user-defined anatomical landmarks (jaw joint, tip of the jaw, and the insertion and origin of up to three jaw closing muscles). 
- These inputs calculate jaw length and muscle in-levers, and for each tooth its position along the jaw, height, width, aspect ratio, surface area, mechanical advantage, output force, and tooth stress.
- Optional user-defined muscle parameters can be provided to calculate more biologically accurate estimates of bite force.
- Equipped with an easy-to-use graphical user interface that allows the user to edit specimen metadata, select inputs and place landmarks, and adjust additional muscle parameters. 
- Results can then be readily imported into other statistical software 
- The module may also be run on imported 3D mesh files (.obj, .ply, .stl) by easily converting them into segmentation nodes.


## 

1.  After segmenting your teeth and jaws, go to the  `Dental Dynamics`  module. Chose the segmentation node you want to modify, identify the jaw and click   **Create new reference point list** .

2.  Every side of a jaw should get its own segmentation node. For example, if you were to use the left and right sides of the lower jaw, they and their teeth should be separated into two different segmentation nodes. To copy or move segments between segmentation nodes, use the `Segementations`  module. You can also drag segments into different segmentation nodes in the `Data`  module.

3. The first segment of each segmentation node should be the jaw segment, followed by the individual tooth segments.

4. Be sure to name each tooth in a way that it can be easily found and controlled. For example, **Lower left tooth 1** should represent the same tooth in each species of your data set.

5. Skip first segment – check this box if the first visible segment is the jaw segment. This will cause `DentalDynamics` to ignore the jaw segment when attempting compute traits for the individual teeth segments

## Setting your points

The reference list will populate with three empty variables: 

 1. Jaw Joint
 2. Tip of Jaw
 3. Muscle insertion site

Click on the first point item so that it is highlighted, then use the provided control point tool to place a point on the jaw joint. Repeat this step for the tip of the jaw and the muscle insertion site. 

You can next desired your muscle input force and insertion angle. Muscle input force is defined as the magnitude of closing force supplied by the jaw closing muscles. If force is not known, `DentalDynamics` assumes a default of 1 N.

 If muscle insertion angle is not known, `DentalDynamics` assumes a default of 90 degrees
 
## Outputs

Set the results table to *create new table*. You can rename the table file by clicking the drop down menu and selecting *rename current table* 

Before hitting apply, make sure  **only** the desired jaw and tooth layers are visible and any unwanted segments are hidden. `DentalDynamics` will only perform calculations on the teeth segments are turned on and will ignore any that are turned off or invisible.  Leave all teeth visible.

The output will be a table of values and points drawn that represents the point stress (red) and position of the teeth (blue). 

To check your results, that all calculations are drawn properly toggle on visibility of tooth-levers and positions under the Advanced tab. If any point need to be moved simply drag them to the correct spot and hit apply. The table will be regenerated and overwrite the previous information

## Exporting data

To save your table we recommend navigating to the `Data` module, highlighting you table and exporting it directly as a .csv file. Alternatively, you can copy all cells in the generated table and paste it directly into a separate spreadsheet. 


# Citation

If you use this module please cite the following references in your posters, presentations, and manuscripts. 








