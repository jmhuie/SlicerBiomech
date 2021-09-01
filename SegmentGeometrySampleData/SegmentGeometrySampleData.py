import os
import unittest
import logging
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin

#
# SegmentGeometrySampleData
#

class SegmentGeometrySampleData(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "SegmentGeometrySampleData" 
    self.parent.categories = ["Quantification"] 
    self.parent.dependencies = ["Sample Data"]  
    self.parent.contributors = ["Jonathan Huie"]  
    self.parent.helpText = """This module adds sample data for SlicerMorph into the SampleData module"""
    self.parent.acknowledgementText = """This module was developed for Segment Geometry by Jonathan Huie, who was supported by an NSF Graduate Research Fellowship (DGE-1746914)."""

    # don't show this module - additional data will be shown in SampleData module
    parent.hidden = True

    # Add data sets to SampleData module
    iconsPath = os.path.join(os.path.dirname(self.parent.path), 'Resources/Icons')
    import SampleData
    SampleData.SampleDataLogic.registerCustomSampleDataSource(
      sampleName='Aneides lugubris forelimbs',
      category='Quantification',
      uris='https://github.com/jmhuie/Slice-SegmentGeometry/blob/master/SampleData/Aneides_Forelimbs.zip?raw=true',
      loadFiles=True,
      fileNames='Aneides_Forelimbs.zip',
      thumbnailFileName=os.path.join(iconsPath, 'SegmentGeometrySampleData.png'),
      loadFileType='ZipFile',
)
