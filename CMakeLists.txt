cmake_minimum_required(VERSION 3.13.4)

project(Segment Geometry)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://www.slicer.org/wiki/Documentation/Nightly/Extensions/SlicerSegmentGeometry_build")
set(EXTENSION_CATEGORY "Quantification")
set(EXTENSION_CONTRIBUTORS "Jonathan Huie (George Washington University)")
set(EXTENSION_DESCRIPTION "This module iterates slice-by-slice through a segment to compute second moment of area and other cross-sectional properties.")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/SlicerSegmentGeometry_build.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/SlicerSegmentGeometry_build/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(SegmentGeometry)
add_subdirectory(Atestmodule)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
