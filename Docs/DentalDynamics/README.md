## Dental Dynamics

**Summary:** The `Dental Dynamics` module is used to model vertebrate jaw function and calculate several key jaw and tooth traits. 
The module requires a segmentation file containing individually segmented teeth and user-defined anatomical landmarks (jaw joint, tip of the jaw, and the insertion and origin site of up to three jaw closing muscles). 
These inputs are used to automatically calculate jaw length and muscle in-levers, and for each tooth its position along the jaw, height, width, aspect ratio, surface area, mechanical advantage, output force, and tooth stress. 
`Dental Dynamics` can also take additional user inputs to estimate muscle parameters such as input force and insertion angle to provide more informed estimates of bite force.

### Usage

#### Inputs

**Specimen:** Name of the specimen.

**Jaw ID:** Select whether the teeth are from the upper or lower jaw.

**Side of Face:** Select whether the teeth are from the right or left side of the face.

**Tooth Segmentation:** A segmentation node containing segments that each represent an individually isolated tooth

**Flip Calculations:** If checked, the positions of all the tooth tips and bases will be flipped.

**Select Teeth:** A list of selected tooth segments that will be computed on.

**Set Reference Ponts:** A `Markups` Point List containing user-defined anatomical landmarks (jaw joint, tip of the jaw, and the insertion and origin site of up to three jaw closing muscles)

**Parameter Type:** Select whether to simulate input force and insertion angle, or to empirically estimate input force and insertion angle.

**Input Force:** Force in Newtons contributed by the jaw closing muscle.

**Insertion Angle:** Angle between the origin of the closing muscle and the jaw joint in degrees, with the insertion point at the vertex.

**Volume:** Volume of the closing muscle in mm.

**Pennation Angle:** Pennation angle of the muscle fibers in degrees.

**Fmax:** The max isometric stress of the closing muscle in Newtons per mm^2.

### How to Cite

Coming Soon

#### Tutorial

Please see: https://github.com/jmhuie/SlicerBiomech/tree/main/Tutorials/DentalDynamics



