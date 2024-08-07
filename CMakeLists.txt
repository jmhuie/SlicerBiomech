cmake_minimum_required(VERSION 3.5)

project(SlicerBiomech)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://github.com/jmhuie/SlicerBiomech")
set(EXTENSION_CATEGORY "Quantification")
set(EXTENSION_CONTRIBUTORS "Jonathan Huie (George Washington University)")
set(EXTENSION_DESCRIPTION "This extension enables the calculation of biomechanical traits and properties from 3D specimen data.")
set(EXTENSION_ICONURL "https://raw.githubusercontent.com/jmhuie/SlicerBiomech/main/SlicerBiomech.png")
set(EXTENSION_SCREENSHOTURLS "https://raw.githubusercontent.com/jmhuie/SlicerBiomech/main/SegmentGeometry/Resources/Icons/SegmentGeometryScreenshot1.png https://raw.githubusercontent.com/jmhuie/SlicerBiomech/main/DentalDynamics/Resources/Icons/DentalDynamicsScreenshot1.png")
set(EXTENSION_DEPENDS "SlicerMorph") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(SegmentGeometry)
add_subdirectory(DentalDynamics)
add_subdirectory(FractalDimension)
add_subdirectory(SaveImageStack)

## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
