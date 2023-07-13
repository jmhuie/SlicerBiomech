<p align="center">
  <img src="https://raw.githubusercontent.com/jmhuie/SlicerBiomech/main/SlicerBiomech.png" width="256" height="256">
</p>


This is the repository for the SlicerBiomech extension for <a href="https://slicer.org/" target ="_blank">3D Slicer</a>.

SlicerBiomech enables the collection and modeling of biomechanical data from 3D specimen data, within the 3D Slicer application. 


## Installation

The official method of obtaining SlicerBiomech is through 3D Slicer's built-in Extensions Manager. To obtain SlicerBiomech, first install the most recent stable release of <a href="https://download.slicer.org/" target ="_blank">3D Slicer</a> (currently r31382, 5.2.2). 
Use the 3D Slicer Extensions Manager module to search for SlicerBiomech and install the extension. After restarting 3D Slicer, SlicerBiomech modules will be available to use in the application. 

Future updates to SlicerBiomech can also be obtained through the Extensions Manager module. To make sure you have the latest version, use the "Check for Updates" button and restart the application.

## How to Cite

If you use SlicerBiomech in your work, please cite one or more relevant publications:

**SegmentGeometry**
* Huie JM, Summers AP, Kawano SM. (2022) SegmentGeometry: a tool for measuring second moment of area in 3D Slicer. Integrative Organismal Biology 4(1): 1-10.  https://doi.org/10.1093/iob/obac009

**Dental Dynamics**
* Coming Soon

To cite 3D Slicer as a general image analysis platform, please cite: 
* Kikinis R, Pieper, SD, Vosburgh KG. (2014) 3D Slicer: A Platform for Subject-Specific Image Analysis, Visualization, and Clinical Support. In Intraoperative Imaging and Image-Guided Therapy (pp. 277–289). Springer, New York, NY. https://doi.org/10.1007/978-1-4614-7657-3_19

## Module Descriptions

* [**SegmentGeometry:**](https://github.com/jmhuie/SlicerBiomech/main/Docs/SegmentGeometry) Iterates slice-by-slice through a segment to calculate the second moment of area and other cross-sectional properties. Results are exported to a table and plotted for quick visualizations. Inputs are a segmentation node and volume node, but the module can be used to analyze 3D models imported from outside 3D Slicer.
* [**Dental Dynamics:**](https://github.com/jmhuie/SlicerBiomech/main/Docs/DentalDynamics) Uses simple lever mechanics to automate tooth stress calculations for modeling tooth function. Results can be exported and analyzed with the functional homodonty framework.

## Dependencies
SlicerBiomech has no required dependencies, but there are a few extensions we recommend installing that are used in many SlicerBiomech workflows.

## Recommended extensions to install manually
The following extension provides many tools for Slicer that are useful for importing, visualizing, and analyzing specimen morphology data. 
* [**SlicerMorph:**](https://github.com/SlicerMorph/SlicerMorph) A segment editor effect useful for isolating endocasts or filling spaces.
The following extension provides many segmentation tools that is are often useful for SlicerBiomech users.
* [**SlicerSegmentEditorExtraEffects:**](https://github.com/lassoan/SlicerSegmentEditorExtraEffects) Provides additional segmentation effects and utilities.
The following extension is used in many workflows for  SegmentGeoemtry and Dental Dynamics.
* [**SurfaceWrapSolidify:**](https://github.com/sebastianandress/Slicer-SurfaceWrapSolidify) A segment editor effect useful for isolating endocasts or filling spaces.


## Frequently Asked Questions

1. I need help using SlicerBiomech, I received an error, or I think I found a bug. What do I do?

First, make sure that you have the most recent version of SlicerBiomech by updating the extension. If the error still persists, you can report your issues on the <a href="https://discourse.slicer.org/" target ="_blank">3D Slicer discourse page</a> and tag me (@jmhuie) or you may email me (jonathanmhuie[at]gmail.com). I will do my best to address problems in a timely manner.

2. I have a suggestion or feature request for how to improve SlicerBiomech. What do I do?

Fantastic! I am always trying to improve the ease and utility of SlicerBiomech modules and would love to hear your suggestions. Please reach out to me through 3D Slicer Discourse page or via email.

# Funding Acknowledgement

Jonathan M. Huie was funded by a NSF Graduate Research Fellowship (DGE-1746914) and a George Washington University Harlan Research Fellowship.

