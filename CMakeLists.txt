cmake_minimum_required(VERSION 3.13.4)

project(SegmentGeometry)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://github.com/jmhuie/SlicerSegmentGeometry")
set(EXTENSION_CATEGORY "Quantification")
set(EXTENSION_CONTRIBUTORS "Jonathan Huie (George Washington University)")
set(EXTENSION_DESCRIPTION "This module iterates slice-by-slice through a segment to compute second moment of area and other cross-sectional properties.")
set(EXTENSION_ICONURL "https://raw.githubusercontent.com/jmhuie/SlicerSegmentGeometry/master/SlicerSegmentGeometry.png")
set(EXTENSION_SCREENSHOTURLS "https://user-images.githubusercontent.com/52302862/130000723-9d29b0e3-b973-4d62-bca4-633c4c207ae7.png")
set(EXTENSION_DEPENDS "SegmentEditorExtraEffects") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(SegmentGeometry)

## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
