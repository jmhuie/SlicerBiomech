import os
import unittest
import logging
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin

#
# SegmentGeometry
#

class SegmentGeometry(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Segment Geometry"
    self.parent.categories = ["Quantification"]
    self.parent.dependencies = []
    self.parent.contributors = ["Jonathan Huie"]
    self.parent.helpText = """This module iterates slice-by-slice through a segment to compute second moment of area and other cross-sectional properties.
    For more information please see the <a href="https://github.com/jmhuie/Slicer-SegmentGeometry">online documentation</a>."""
    self.parent.acknowledgementText = """This module was developed by Jonathan Huie, who was supported by an NSF Graduate Research Fellowship (DGE-1746914)."""


#
# SegmentGeometryWidget
#

class SegmentGeometryWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent=None):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.__init__(self, parent)
    VTKObservationMixin.__init__(self)  # needed for parameter node observation
    self.logic = None
    self._parameterNode = None

  def setup(self):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.setup(self)

    # Load widget from .ui file (created by Qt Designer)
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/SegmentGeometry.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    # Set scene in MRML widgets. Make sure that in Qt designer
    # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget'rowCount.
    # "setMRMLScene(vtkMRMLScene*)" slot.
    uiWidget.setMRMLScene(slicer.mrmlScene)

    # Create a new parameterNode
    # This parameterNode stores all user choices in parameter values, node selections, etc.
    # so that when the scene is saved and reloaded, these settings are restored.
    self.logic = SegmentGeometryLogic()
    self.ui.parameterNodeSelector.addAttribute("vtkMRMLScriptedModuleNode", "ModuleName", self.moduleName)
    self.setParameterNode(self.logic.getParameterNode())

    # Connections
    self.ui.parameterNodeSelector.connect('currentNodeChanged(vtkMRMLNode*)', self.setParameterNode)
    self.ui.applyButton.connect('clicked(bool)', self.onApplyButton)

    # These connections ensure that whenever user changes some settings on the GUI, that is saved in the MRML scene
    # (in the selected parameter node).
    self.ui.segmentationSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.regionSegmentSelector.connect('currentNodeChanged(vtkMRMLNode*)', self.updateParameterNodeFromGUI)
    self.ui.volumeSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.axisSelectorBox.connect("currentIndexChanged(int)", self.updateParameterNodeFromGUI)
    self.ui.resamplespinBox.connect("valueChanged(int)", self.updateParameterNodeFromGUI)
    self.ui.tableSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.chartSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.OrientationcheckBox.connect('stateChanged(int)', self.updateParameterNodeFromGUI)
    self.ui.orientationspinBox.connect("valueChanged(int)", self.updateParameterNodeFromGUI)
    self.ui.CenterSegButton.connect("clicked(bool)", self.onCenterSeg)
    self.ui.BoundingBoxButton.connect("clicked(bool)", self.onBoundingBox)
    self.ui.CompactnesscheckBox.connect('stateChanged(int)', self.updateParameterNodeFromGUI)
    self.ui.areaSegmentSelector.connect('currentNodeChanged(vtkMRMLNode*)', self.updateParameterNodeFromGUI)
    


    # Initial GUI update
    self.updateGUIFromParameterNode()

  def cleanup(self):
    """
    Called when the application closes and the module widget is destroyed.
    """
    self.removeObservers()

  def setParameterNode(self, inputParameterNode):
    """
    Adds observers to the selected parameter node. Observation is needed because when the
    parameter node is changed then the GUI must be updated immediately.
    """

    # Set parameter node in the parameter node selector widget
    wasBlocked = self.ui.parameterNodeSelector.blockSignals(True)
    self.ui.parameterNodeSelector.setCurrentNode(inputParameterNode)
    self.ui.parameterNodeSelector.blockSignals(wasBlocked)

    if inputParameterNode == self._parameterNode:
      # No change
      return

    # Unobserve previously selected parameter node and add an observer to the newly selected.
    # Changes of parameter node are observed so that whenever parameters are changed by a script or any other module
    # those are reflected immediately in the GUI.
    if self._parameterNode is not None:
      self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
    if inputParameterNode is not None:
      self.addObserver(inputParameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
    self._parameterNode = inputParameterNode

    # Initial GUI update
    self.updateGUIFromParameterNode()

  def updateGUIFromParameterNode(self, caller=None, event=None):
    """
    This method is called whenever parameter node is changed.
    The module GUI is updated to show the current state of the parameter node.
    """

    # Disable all sections if no parameter node is selected
    self.ui.basicCollapsibleButton.enabled = self._parameterNode is not None
    if self._parameterNode is None:
      return

    # Update each widget from parameter node
    # Need to temporarily block signals to prevent infinite recursion (MRML node update triggers
    # GUI update, which triggers MRML node update, which triggers GUI update, ...)
    
    wasBlocked = self.ui.segmentationSelector.blockSignals(True)
    self.ui.segmentationSelector.setCurrentNode(self._parameterNode.GetNodeReference("Segmentation"))
    self.ui.segmentationSelector.blockSignals(wasBlocked)
    
    wasBlocked = self.ui.regionSegmentSelector.blockSignals(True)
    self.ui.regionSegmentSelector.setCurrentNode(self._parameterNode.GetNodeReference("Segmentation"))
    self.ui.regionSegmentSelector.blockSignals(wasBlocked)

    wasBlocked = self.ui.volumeSelector.blockSignals(True)
    self.ui.volumeSelector.setCurrentNode(self._parameterNode.GetNodeReference("Volume"))
    self.ui.volumeSelector.blockSignals(wasBlocked)

    wasBlocked = self.ui.axisSelectorBox.blockSignals(True)
    self.ui.axisSelectorBox.currentText = self._parameterNode.GetParameter("Axis")
    self.ui.axisSelectorBox.blockSignals(wasBlocked)
    
    wasBlocked = self.ui.tableSelector.blockSignals(True)
    self.ui.tableSelector.setCurrentNode(self._parameterNode.GetNodeReference("ResultsTable"))
    self.ui.tableSelector.blockSignals(wasBlocked)
    
    wasBlocked = self.ui.axisSelectorBox.blockSignals(True)
    self.ui.chartSelector.setCurrentNode(self._parameterNode.GetNodeReference("ResultsChart"))
    self.ui.axisSelectorBox.blockSignals(wasBlocked)

    wasBlocked = self.ui.areaSegmentSelector.blockSignals(True)
    self.ui.areaSegmentSelector.setCurrentNode(self._parameterNode.GetNodeReference("Segmentation"))
    self.ui.areaSegmentSelector.blockSignals(wasBlocked)

    # Update buttons states and tooltips
    if self._parameterNode.GetNodeReference("Segmentation") and not self.ui.regionSegmentSelector.currentSegmentID == None:
      self.ui.applyButton.toolTip = "Compute slice geometries"
      self.ui.applyButton.enabled = True
    else:
      self.ui.applyButton.toolTip = "Select input segmentation node"
      self.ui.applyButton.enabled = False
    
    if self._parameterNode.GetNodeReference("Segmentation"):
      self.ui.regionSegmentSelector.toolTip = "Select segment"
    else:
      self.ui.regionSegmentSelector.toolTip = "Select input segmentation node"  
  
      
    if self._parameterNode.GetNodeReference("Volume"):
      self.ui.volumeSelector.toolTip = "Select output table"
      self.ui.IntensitycheckBox.toolTip = "Compute mean pixel brightness. Will automatically resample volume if segment is transformed."
      self.ui.IntensitycheckBox.enabled = True
      self.ui.BoundingBoxButton.enabled = True
      self.ui.CenterSegButton.toolTip = "Move segment to the center of the volume"  
      self.ui.BoundingBoxButton.toolTip = "Show box that represents the bounds of the volume"
    else:
      self.ui.volumeSelector.toolTip = "Select input volume node"
      self.ui.IntensitycheckBox.toolTip = "Select input volume node"
      self.ui.IntensitycheckBox.enabled = False
      self.ui.BoundingBoxButton.enabled = False
      self.ui.CenterSegButton.toolTip = "Select input volume node"  
      self.ui.BoundingBoxButton.toolTip = "Select input volume node"
       
    if self._parameterNode.GetNodeReference("Volume") and self._parameterNode.GetNodeReference("Segmentation") and self.ui.regionSegmentSelector.currentSegmentID != None:
      self.ui.CenterSegButton.enabled = True
    else:
      self.ui.CenterSegButton.enabled = False
      
    if self._parameterNode.GetNodeReference("ResultsTable"):
      self.ui.tableSelector.toolTip = "Edit output table"
    else:
      self.ui.tableSelector.toolTip = "Select output table"
      
    if self._parameterNode.GetNodeReference("ResultsChart"):
      self.ui.chartSelector.toolTip = "Edit output chart"
    else:
      self.ui.chartSelector.toolTip = "Select output chart"
            
    if self.ui.OrientationcheckBox.checked == True:
      self.ui.OrientationcheckBox.toolTip = "Check to use custom neutral axis"
      self.ui.orientationspinBox.toolTip = "Enter the angle (degrees) of the neutral axis. By default, the neutral axis is set parallel to the horizontal"
      self.ui.orientationspinBox.enabled = True
      self.ui.SMAcheckBox_2.toolTip = "Compute second moment of area around the neutral and loading axes"
      self.ui.SMAcheckBox_2.enabled = True
      self.ui.MODcheckBox_2.toolTip = "Compute section modulus around the neutral and loading axes"
      self.ui.MODcheckBox_2.enabled = True
      self.ui.RcheckBox_2.toolTip = "Compute the max distances from the neutral and loading axes"
      self.ui.RcheckBox_2.enabled = True
      self.ui.DegradioButton.enabled = True
      self.ui.DegradioButton.toolTip = "Define netural axis angle in degrees"
      self.ui.RadradioButton.enabled = True
      self.ui.RadradioButton.toolTip = "Define netural axis angle in radians"

    else:
      self.ui.OrientationcheckBox.toolTip = "Uncheck to use custom neutral axis"
      self.ui.orientationspinBox.toolTip = "Select option use the neutral axis"
      self.ui.orientationspinBox.enabled = False
      self.ui.SMAcheckBox_2.toolTip = "Select option to use neutral axis"
      self.ui.SMAcheckBox_2.enabled = False
      self.ui.MODcheckBox_2.toolTip = "Select option to use neutral axis"
      self.ui.MODcheckBox_2.enabled = False
      self.ui.RcheckBox_2.toolTip = "Select option to use neutral axis"
      self.ui.RcheckBox_2.enabled = False
      self.ui.DegradioButton.enabled = False      
      self.ui.DegradioButton.toolTip = "Select option to use neutral axis"
      self.ui.RadradioButton.enabled = False
      self.ui.RadradioButton.toolTip = "Select option to use neutral axis"
    
    if self.ui.CompactnesscheckBox.checked == True:
      self.ui.areaSegmentSelector.toolTip = "Select solid segment to measure total area and compactness"
      self.ui.areaSegmentSelector.enabled = True
    else: 
      self.ui.areaSegmentSelector.toolTip = "Select option to compute compactness" 
      self.ui.areaSegmentSelector.enabled = False     
    # other tooltips
    self.ui.segmentationSelector.toolTip = "Select input segmentation node"
    self.ui.axisSelectorBox.toolTip = "Select slice view to compute on. Should be perpendicular to the long axis"
    self.ui.resamplespinBox.toolTip = "Perform computations in percent increments along the length of the segment. Enter zero to compute values on every slice"
    self.ui.CSAcheckBox.toolTip = "Compute cross-sectional area"
    self.ui.SMAcheckBox_1.toolTip = "Compute second moment of area around the principal axes"
    self.ui.MODcheckBox_1.toolTip = "Compute section modulus around the principal axes"
    self.ui.LengthcheckBox.toolTip = "Compute the length of the segment along the chosen axis"
    self.ui.ThetacheckBox.toolTip = "Compute how much the minor axis deviates from the horizontal axis in a clockwise direction"
    self.ui.RcheckBox.toolTip = "Compute the max distances from the principal axes"
    self.ui.DoubecheckBox.toolTip = "Normalize values by taking the respective roots needed to reduce them to a linear dimension and then divinding themy by segment length following Doube et al. (2009)"
    self.ui.SummerscheckBox.toolTip = "Normalize second moment of area by dividing the calculated value by the second moment of area for a solid circle with the same cross-sectional area following Summers et al. (2004)"
    self.ui.FeretcheckBox.toolTip = "Compute the maximum feret diameter"
    self.ui.CompactnesscheckBox.toolTip = "Compute slice compactness as the CSA/TCSA. Needs a separate solid segment to measure TCSA"
    self.ui.CentroidcheckBox.toolTip = "Compute the XY coordinates for the centroid of the section"


  def updateParameterNodeFromGUI(self, caller=None, event=None):
    """
    This method is called when the user makes any change in the GUI.
    The changes are saved into the parameter node (so that they are restored when the scene is saved and loaded).
    """

    if self._parameterNode is None:
      return
      
    self._parameterNode.SetNodeReferenceID("Segmentation", self.ui.segmentationSelector.currentNodeID)  
    self._parameterNode.SetNodeReferenceID("Volume", self.ui.volumeSelector.currentNodeID)
    self._parameterNode.SetParameter("Axis", self.ui.axisSelectorBox.currentText)
    self._parameterNode.SetParameter("Resample", str(self.ui.resamplespinBox.value))
    self._parameterNode.SetNodeReferenceID("ResultsTable", self.ui.tableSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("ResultsChart", self.ui.chartSelector.currentNodeID)
    self._parameterNode.SetParameter("Orientation", str(self.ui.OrientationcheckBox.checked))
    self._parameterNode.SetParameter("Angle", str(self.ui.orientationspinBox.value))
    self._parameterNode.SetParameter("Compactness", str(self.ui.CompactnesscheckBox.checked))
  
  
  def onCenterSeg(self):
    """
    Run processing when user clicks "Snap to Center" button.
    """   
    import numpy as np
    
    segmentationNode = self.ui.segmentationSelector.currentNode()
    segmentId = self.ui.regionSegmentSelector.currentSegmentID()
    masterVolumeNode = self.ui.volumeSelector.currentNode()

    segcentroid_ras = segmentationNode.GetSegmentCenterRAS(segmentId)

    reconstructedVolumeNode = masterVolumeNode
    volumeExtent = reconstructedVolumeNode.GetImageData().GetExtent()
    ijkToRas = vtk.vtkMatrix4x4()
    reconstructedVolumeNode.GetIJKToRASMatrix(ijkToRas)
    ras = ijkToRas.MultiplyPoint([volumeExtent[0],volumeExtent[2],volumeExtent[4],1])
    volumeBounds = [ras[0], ras[0], ras[1], ras[1], ras[2], ras[2]]
    for iCoord in [volumeExtent[0], volumeExtent[1]]:
      for jCoord in [volumeExtent[2], volumeExtent[3]]:
        for kCoord in [volumeExtent[4], volumeExtent[5]]:
          ras = ijkToRas.MultiplyPoint([iCoord, jCoord, kCoord, 1])
          for i in range(0,3):
            volumeBounds[i*2] = min(volumeBounds[i*2], ras[i])
            volumeBounds[i*2+1] = max(volumeBounds[i*2+1], ras[i])      
          
          
    roiCenter = [0.0, 0.0, 0.0]
    for i in range(0,3):
      roiCenter[i] = (volumeBounds[i*2+1] + volumeBounds[i*2])/2 
    slicer.modules.markups.logic().JumpSlicesToLocation(roiCenter[0], roiCenter[1], roiCenter[2], True)    

  
    Centroid_diff = [0.0, 0.0, 0.0]  
    for i in range(0,3):
      Centroid_diff[i] = (segcentroid_ras[i] -  roiCenter[i])
  
    trans = segmentationNode.GetTransformNodeID()
    if trans != None:
      trans = slicer.mrmlScene.GetNodeByID(segmentationNode.GetTransformNodeID())
      matrix = vtk.vtkMatrix4x4()
      trans.GetMatrixTransformToParent(matrix)
      matrix.SetElement(0,3, trans.GetMatrixTransformToParent().GetElement(0,3) - Centroid_diff[0]) 
      matrix.SetElement(1,3, trans.GetMatrixTransformToParent().GetElement(1,3) - Centroid_diff[1])
      matrix.SetElement(2,3, trans.GetMatrixTransformToParent().GetElement(2,3) - Centroid_diff[2]) 
      trans.SetMatrixTransformToParent(matrix) 

  
  def onBoundingBox(self):
    """
    Run processing when user clicks "Bounding Box" button.
    """  
    import numpy as np
    
    roiNode = slicer.mrmlScene.GetFirstNodeByName("Segment Geometry Bounding Box")
    if self.ui.BoundingBoxButton.checked == True:
      if roiNode == None:
        reconstructedVolumeNode = self.ui.volumeSelector.currentNode()
        volumeExtent = reconstructedVolumeNode.GetImageData().GetExtent()
        ijkToRas = vtk.vtkMatrix4x4()
        reconstructedVolumeNode.GetIJKToRASMatrix(ijkToRas)
        ras = ijkToRas.MultiplyPoint([volumeExtent[0],volumeExtent[2],volumeExtent[4],1])
        volumeBounds = [ras[0], ras[0], ras[1], ras[1], ras[2], ras[2]]
        for iCoord in [volumeExtent[0], volumeExtent[1]]:
          for jCoord in [volumeExtent[2], volumeExtent[3]]:
            for kCoord in [volumeExtent[4], volumeExtent[5]]:
              ras = ijkToRas.MultiplyPoint([iCoord, jCoord, kCoord, 1])
              for i in range(0,3):
                volumeBounds[i*2] = min(volumeBounds[i*2], ras[i])
                volumeBounds[i*2+1] = max(volumeBounds[i*2+1], ras[i])

        
        roiCenter = [0.0, 0.0, 0.0]
        roiRadius = [0.0, 0.0, 0.0]
        for i in range(0,3):
          roiCenter[i] = (volumeBounds[i*2+1] + volumeBounds[i*2])/2
          roiRadius[i] = (volumeBounds[i*2+1] - volumeBounds[i*2])/2
        roiNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsROINode", "Segment Geometry Bounding Box")
        roiNode.SetXYZ(roiCenter[0], roiCenter[1], roiCenter[2])
        roiNode.SetRadiusXYZ(roiRadius[0], roiRadius[1], roiRadius[2])
        roiNode.SetLocked(1) 
        mDisplayNode = roiNode.GetDisplayNode()
        mDisplayNode.SetSelectedColor(0,1,0)
        mDisplayNode.SetFillOpacity(0.05)
        mDisplayNode.SetPropertiesLabelVisibility(False)
        mDisplayNode.SetGlyphScale(0)
        mDisplayNode.SetHandlesInteractive(False)
        roiNode.SetDisplayVisibility(1)
               
      if not roiNode == None: 
        reconstructedVolumeNode = self.ui.volumeSelector.currentNode()
        volumeExtent = reconstructedVolumeNode.GetImageData().GetExtent()
        ijkToRas = vtk.vtkMatrix4x4()
        reconstructedVolumeNode.GetIJKToRASMatrix(ijkToRas)
        ras = ijkToRas.MultiplyPoint([volumeExtent[0],volumeExtent[2],volumeExtent[4],1])
        volumeBounds = [ras[0], ras[0], ras[1], ras[1], ras[2], ras[2]]
        for iCoord in [volumeExtent[0], volumeExtent[1]]:
          for jCoord in [volumeExtent[2], volumeExtent[3]]:
            for kCoord in [volumeExtent[4], volumeExtent[5]]:
              ras = ijkToRas.MultiplyPoint([iCoord, jCoord, kCoord, 1])
              for i in range(0,3):
                volumeBounds[i*2] = min(volumeBounds[i*2], ras[i])
                volumeBounds[i*2+1] = max(volumeBounds[i*2+1], ras[i])
                
                
        roiCenter = [0.0, 0.0, 0.0]
        roiRadius = [0.0, 0.0, 0.0]
        for i in range(0,3):
          roiCenter[i] = (volumeBounds[i*2+1] + volumeBounds[i*2])/2
          roiRadius[i] = (volumeBounds[i*2+1] - volumeBounds[i*2])/2
        #roiNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsROINode", "Segment Geometry Bounding Box")
        roiNode.SetXYZ(roiCenter[0], roiCenter[1], roiCenter[2])
        roiNode.SetRadiusXYZ(roiRadius[0], roiRadius[1], roiRadius[2])
        roiNode.SetLocked(1) 
        mDisplayNode = roiNode.GetDisplayNode()
        mDisplayNode.SetSelectedColor(0,1,1)
        mDisplayNode.SetFillOpacity(0.05)
        mDisplayNode.SetPropertiesLabelVisibility(False)
        mDisplayNode.SetGlyphScale(0)
        mDisplayNode.SetHandlesInteractive(False)
        roiNode.SetDisplayVisibility(1)
        
    if self.ui.BoundingBoxButton.checked == False:
      roiNode.SetDisplayVisibility(0)
        
  def onApplyButton(self):
    """
    Run processing when user clicks "Apply" button.
    """
      
    try:
      # Create nodes for results
      segment = self.ui.regionSegmentSelector.currentNode().GetSegmentation().GetSegment(self.ui.regionSegmentSelector.currentSegmentID())
      segName = segment.GetName()
      
      tableNode = self.ui.tableSelector.currentNode()
      expTable = segName + " Segment Geometry table"
      if not tableNode:
        tableNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTableNode", expTable)
        self.ui.tableSelector.setCurrentNode(tableNode)
      if tableNode.GetName() != expTable and slicer.mrmlScene.GetFirstNodeByName(expTable) != None:
        tableNode = slicer.mrmlScene.GetFirstNodeByName(expTable)
        self.ui.tableSelector.setCurrentNode(tableNode)
      if tableNode.GetName() != expTable and slicer.mrmlScene.GetFirstNodeByName(expTable) == None:
        tableNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTableNode", expTable)
        self.ui.tableSelector.setCurrentNode(tableNode)
      
      
      plotChartNode = self.ui.chartSelector.currentNode()
      expChart = segName + " Segment Geometry plot"
      if not plotChartNode:
        plotChartNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotChartNode", segName + " Segment Geometry plot")
        self.ui.chartSelector.setCurrentNode(plotChartNode)
      if plotChartNode.GetName() != expChart and slicer.mrmlScene.GetFirstNodeByName(expChart) != None:
        plotChartNode = slicer.mrmlScene.GetFirstNodeByName(expChart)
        self.ui.chartSelector.setCurrentNode(plotChartNode)
      if plotChartNode.GetName() != expChart and slicer.mrmlScene.GetFirstNodeByName(expChart) == None:
        plotChartNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotChartNode", segName + " Segment Geometry plot")
        self.ui.chartSelector.setCurrentNode(plotChartNode)  
          

      self.logic.run(self.ui.regionSegmentSelector.currentNode(), self.ui.regionSegmentSelector.currentSegmentID(), self.ui.volumeSelector.currentNode(), 
                     self.ui.BoundingBoxButton.checked, self.ui.axisSelectorBox.currentText, 
                     self.ui.resamplespinBox.value, tableNode, plotChartNode, self.ui.LengthcheckBox.checked, self.ui.FeretcheckBox.checked,
                     self.ui.CSAcheckBox.checked, self.ui.IntensitycheckBox.checked, self.ui.SMAcheckBox_1.checked, self.ui.MODcheckBox_1.checked,
                     self.ui.OrientationcheckBox.checked, self.ui.SMAcheckBox_2.checked, 
                     self.ui.MODcheckBox_2.checked, self.ui.RcheckBox_2.checked, self.ui.orientationspinBox.value, 
                     self.ui.DegradioButton.checked, self.ui.RadradioButton.checked, self.ui.ThetacheckBox.checked, self.ui.RcheckBox.checked,
                     self.ui.DoubecheckBox.checked, self.ui.SummerscheckBox.checked, 
                     self.ui.CompactnesscheckBox.checked, self.ui.areaSegmentSelector.currentNode(),self.ui.areaSegmentSelector.currentSegmentID(),
                     self.ui.CentroidcheckBox.checked,)

    except Exception as e:
      slicer.util.errorDisplay("Failed to compute results: "+str(e))
      import traceback
      traceback.print_exc()


#
# SegmentGeometryLogic
#

class SegmentGeometryLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """


  def run(self, segmentationNode, segmentNode, volumeNode, BoundingBox, axis, interval, tableNode, plotChartNode, LengthcheckBox, FeretcheckBox, CSAcheckBox, IntensitycheckBox, SMAcheckBox_1,
  MODcheckBox_1, OrientationcheckBox, SMAcheckBox_2, MODcheckBox_2, RcheckBox_2, angle, DegButton, RadButton, ThetacheckBox, RcheckBox, DoubecheckBox, SummerscheckBox,
  CompactnesscheckBox, areaSegementationNode, areaSegmentID, CentroidcheckBox):
    """
    Run the processing algorithm.
    """

    import numpy as np

    logging.info('Processing started')

    if not segmentationNode:
      raise ValueError("Segmentation node is invalid")
    

    if axis=="R (Yellow)":
      axisIndex = 0
    elif axis=="A (Green)":
      axisIndex = 1
    elif axis=="S (Red)":
      axisIndex = 2
    else:
      raise ValueError("Invalid axis name: "+axis)

    # Make a table and set the first column as the slice number. 
    tableNode.RemoveAllColumns()
    table = tableNode.GetTable()
    
    # Make a plot chart node. Plot series nodes will be added to this in the
    # loop below that iterates over each segment.
    segment = segmentationNode.GetSegmentation().GetSegment(segmentNode)
    segName = segment.GetName()
    plotChartNode.SetTitle(segName)
    plotChartNode.SetXAxisTitle("Percent of Length")
    plotChartNode.SetYAxisTitle('Second Moment of Area (mm^4)')
    
    
    # do calculations
    try:
      # Create temporary volume node
      tempSegmentLabelmapVolumeNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLLabelMapVolumeNode', "SegmentGeometryTemp")
      FdiamMin = None
      eulerflag = 1  

      
      #### CREATE ARRAYS FOR ALL COLUMNS ####
      sliceNumberArray = vtk.vtkIntArray()
      sliceNumberArray.SetName("Slice Index")
          
      SegmentNameArray = vtk.vtkStringArray()
      SegmentNameArray.SetName("Segment")
          
      percentLengthArray = vtk.vtkFloatArray()
      percentLengthArray.SetName("Percent (%)")

      LengthArray = vtk.vtkFloatArray()
      LengthArray.SetName("Length (mm)")
        
      areaArray = vtk.vtkFloatArray()
      areaArray.SetName("CSA (mm^2)")
      
      meanIntensityArray = vtk.vtkFloatArray()
      meanIntensityArray.SetName("Mean Brightness")
      
      CxArray = vtk.vtkFloatArray()
      CxArray.SetName("Cx (mm)")
      
      CyArray = vtk.vtkFloatArray()
      CyArray.SetName("Cy (mm)")
              
      ImajorArray = vtk.vtkFloatArray()
      ImajorArray.SetName("Imajor (mm^4)")
        
      IminorArray = vtk.vtkFloatArray()
      IminorArray.SetName("Iminor (mm^4)")
                    
      ThetaMinArray = vtk.vtkFloatArray()
      ThetaMinArray.SetName("Theta minor (deg)")
      
      ThetaMaxArray = vtk.vtkFloatArray()
      ThetaMaxArray.SetName("Theta major (deg)")
      
      ZmajorArray = vtk.vtkFloatArray()
      ZmajorArray.SetName("Zmajor (mm^3)")
        
      ZminorArray = vtk.vtkFloatArray()
      ZminorArray.SetName("Zminor (mm^3)")
              
      RmajorArray = vtk.vtkFloatArray()
      RmajorArray.SetName("Rmajor (mm)")
        
      RminorArray = vtk.vtkFloatArray()
      RminorArray.SetName("Rminor (mm)")
              
      InaArray = vtk.vtkFloatArray()
      InaArray.SetName("Ina (mm^4)")
        
      IlaArray = vtk.vtkFloatArray()
      IlaArray.SetName("Ila (mm^4)")
      
      ZnaArray = vtk.vtkFloatArray()
      ZnaArray.SetName("Zna (mm^3)")
        
      ZlaArray = vtk.vtkFloatArray()
      ZlaArray.SetName("Zla (mm^3)")
      
      RnaArray = vtk.vtkFloatArray()
      RnaArray.SetName("Rna (mm)")
      
      RlaArray = vtk.vtkFloatArray()
      RlaArray.SetName("Rla (mm)")

      FeretArray = vtk.vtkFloatArray()
      FeretArray.SetName("Max Diameter (mm)")
      
      TotalAreaArray = vtk.vtkFloatArray()
      TotalAreaArray.SetName("TCSA (mm^2)")
            
      CompactnessArray = vtk.vtkFloatArray()
      CompactnessArray.SetName("Compactness")
      
      #create arrays for unitless metrics with Doube method
      if DoubecheckBox == True:
        areaArray_Doube = vtk.vtkFloatArray()
        areaArray_Doube.SetName("CSA (LenNorm)")

        ImajorArray_Doube = vtk.vtkFloatArray()
        ImajorArray_Doube.SetName("Imajor (LenNorm)")
        
        IminorArray_Doube = vtk.vtkFloatArray()
        IminorArray_Doube.SetName("Iminor (LenNorm)")

        ZmajorArray_Doube = vtk.vtkFloatArray()
        ZmajorArray_Doube.SetName("Zmajor (LenNorm)")
        
        ZminorArray_Doube = vtk.vtkFloatArray()
        ZminorArray_Doube.SetName("Zminor (LenNorm)")
                
        InaArray_Doube = vtk.vtkFloatArray()
        InaArray_Doube.SetName("Ina (LenNorm)")
        
        IlaArray_Doube = vtk.vtkFloatArray()
        IlaArray_Doube.SetName("Ila (LenNorm)")
        
        ZnaArray_Doube = vtk.vtkFloatArray()
        ZnaArray_Doube.SetName("Zna (LenNorm)")
        
        ZlaArray_Doube = vtk.vtkFloatArray()
        ZlaArray_Doube.SetName("Zla (LenNorm)")

      if SummerscheckBox == True:
        ImajorArray_Summers = vtk.vtkFloatArray()
        ImajorArray_Summers.SetName("Imajor (MatNorm)")
        
        IminorArray_Summers = vtk.vtkFloatArray()
        IminorArray_Summers.SetName("Iminor (MatNorm)")
        
        ZminorArray_Summers = vtk.vtkFloatArray()       
        ZminorArray_Summers.SetName("Zminor (MatNorm)")
        
        ZmajorArray_Summers = vtk.vtkFloatArray()       
        ZmajorArray_Summers.SetName("Zmajor (MatNorm)")
        
        InaArray_Summers = vtk.vtkFloatArray()
        InaArray_Summers.SetName("Ina (MatNorm)")
        
        IlaArray_Summers = vtk.vtkFloatArray()
        IlaArray_Summers.SetName("Ila (MatNorm)") 
        
        ZnaArray_Summers = vtk.vtkFloatArray()       
        ZnaArray_Summers.SetName("Zna (MatNorm)")
        
        ZlaArray_Summers = vtk.vtkFloatArray()       
        ZlaArray_Summers.SetName("Zla (MatNorm)")

      
      # leave in the capabilities to go back to multiple segments
      if CompactnesscheckBox == True:
        segmentindex = [segmentNode, areaSegmentID]
      else:
        segmentindex = [segmentNode]
      for segmentID in segmentindex:
              
        segment = segmentationNode.GetSegmentation().GetSegment(segmentID)
        segName = segment.GetName()

        segmentList = vtk.vtkStringArray()
        segmentList.InsertNextValue(segmentID)
        
        volumesLogic = slicer.modules.volumes.logic()
        if volumeNode != None:   
          # Create volume for output
          volumetransformNode = volumeNode.GetTransformNodeID()
          volumeNode.SetAndObserveTransformNodeID(None)
          outputVolume = volumesLogic.CloneVolumeGeneric(volumeNode.GetScene(), volumeNode, "TempMaskVolume")
          
          transformNode = segmentationNode.GetNodeReferenceID('transform')
          if IntensitycheckBox == True and transformNode != None and segmentID == segmentNode:
            parameters = {}
            parameters["inputVolume"] = volumeNode
            parameters["outputVolume"] = outputVolume
            parameters["referenceVolume"] = volumeNode
            parameters["transformationFile"] = transformNode
            resampleScalarVectorDWI = slicer.modules.resamplescalarvectordwivolume
            cliNode = slicer.cli.runSync(resampleScalarVectorDWI, None, parameters)
            if cliNode.GetStatus() & cliNode.ErrorsMask:
              # error
              errorText = cliNode.GetErrorText()
              slicer.mrmlScene.RemoveNode(cliNode)
              raise ValueError("CLI execution failed: " + errorText)
  
            outputvolume = slicer.vtkSlicerVolumesLogic().CloneVolume(slicer.mrmlScene,outputVolume, segName + " Resampled Volume",True)
            slicer.mrmlScene.RemoveNode(cliNode)
            slicer.mrmlScene.RemoveNode(outputvolume)
          volumeNodeformasking = outputVolume
          volumeNode.SetAndObserveTransformNodeID(volumetransformNode)
          
        if volumeNode == None:
          volumeNodeformasking = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLLabelMapVolumeNode', "FullVolumeTemp")
          slicer.modules.segmentations.logic().ExportAllSegmentsToLabelmapNode(segmentationNode, volumeNodeformasking, slicer.vtkSegmentation.EXTENT_REFERENCE_GEOMETRY)
          outputVolume = volumesLogic.CloneVolumeGeneric(volumeNodeformasking.GetScene(), volumeNodeformasking, "TempMaskVolume", False)
          
        # Crop segment
        maskExtent = [0] * 6
        fillValue = 0
        import SegmentEditorMaskVolumeLib
        maskVolumeWithSegment = SegmentEditorMaskVolumeLib.SegmentEditorEffect.maskVolumeWithSegment
        maskVolumeWithSegment(segmentationNode, segmentID, "FILL_OUTSIDE", [fillValue], volumeNodeformasking, outputVolume, maskExtent) 
          
        # Calculate padded extent of segment
        realextent=volumeNodeformasking.GetImageData().GetExtent()
        if axisIndex == 0:
          extent = [maskExtent[0],maskExtent[1],realextent[2],realextent[3],realextent[4],realextent[5]]
          extentoffset = abs(realextent[0] - maskExtent[0])
        elif axisIndex == 1:
          extent = [realextent[0],realextent[1],maskExtent[2],maskExtent[3],realextent[4],realextent[5]]
          extentoffset = abs(realextent[2] - maskExtent[2])
        elif axisIndex == 2:
          extent = [realextent[0],realextent[1],realextent[2],realextent[3],maskExtent[4],maskExtent[5]]
          extentoffset = abs(realextent[4] - maskExtent[4])

          
        # Calculate the new origin
        ijkToRas = vtk.vtkMatrix4x4()
        outputVolume.GetIJKToRASMatrix(ijkToRas)
        origin_IJK = [extent[0], extent[2], extent[4], 1]
        origin_RAS = ijkToRas.MultiplyPoint(origin_IJK)
          
        # Pad and crop
        padFilter = vtk.vtkImageConstantPad()
        padFilter.SetInputData(outputVolume.GetImageData())
        padFilter.SetOutputWholeExtent(extent)
        padFilter.Update()
        paddedImg = padFilter.GetOutput()

        # Normalize output image
        paddedImg.SetOrigin(0,0,0)
        paddedImg.SetSpacing(1.0, 1.0, 1.0)
        paddedImg.SetExtent(0, extent[1]-extent[0], 0, extent[3]-extent[2], 0, extent[5]-extent[4])
        outputVolume.SetAndObserveImageData(paddedImg)
        outputVolume.SetOrigin(origin_RAS[0], origin_RAS[1], origin_RAS[2])
        
            
        if not slicer.modules.segmentations.logic().ExportSegmentsToLabelmapNode(segmentationNode, segmentList, tempSegmentLabelmapVolumeNode, outputVolume):
          continue
          
        if volumeNode != None:  
          # create array to calculate intensity
          while True:
            try:
              voxelArray = slicer.util.arrayFromVolume(outputVolume)
              break
            except ValueError:
              raise ValueError("The segment is outside of the volume's bounds!")   


        # remove output volume node 
        slicer.mrmlScene.RemoveNode(outputVolume)
        
        if volumeNode == None:
          slicer.mrmlScene.RemoveNode(volumeNodeformasking)


        # volumeExtents so first and last number of images in XYZ directions. Starts with 0 not 1	
        volumeExtents = tempSegmentLabelmapVolumeNode.GetImageData().GetExtent()
        numSlices = volumeExtents[axisIndex*2+1] - volumeExtents[axisIndex*2] + 1
        
        # deteRminore how many slices to calculate statistics for
        if interval > 0:
          #resample = np.rint(100/interval)
          resample = np.arange(interval, stop = 101, step = interval)
          #resample = np.linspace(interval,100,num = resample.astype(int),endpoint = True) 
          sampleSlices = numSlices * (resample / 100)
          sampleSlices = sampleSlices - 1
          sampleSlices = np.rint(sampleSlices)
          sampleSlices = sampleSlices.astype(int)
          if numSlices < 100:
            resample = numSlices
            sampleSlices = np.asarray(list(range(0,numSlices)))

        elif interval == 0:
          resample = numSlices
          sampleSlices = np.asarray(list(range(0,numSlices)))
        percentLength = np.around((sampleSlices+1) / numSlices * 100,1)
          
        # deteRminores centroid of the first and last slice. Identical if only one slice
        startPosition_Ijk = [
          (volumeExtents[0]+volumeExtents[1])/2.0 if axisIndex!=0 else volumeExtents[0],
          (volumeExtents[2]+volumeExtents[3])/2.0 if axisIndex!=1 else volumeExtents[2],
          (volumeExtents[4]+volumeExtents[5])/2.0 if axisIndex!=2 else volumeExtents[4],
          1
        ]
        endPosition_Ijk = [
          (volumeExtents[0]+volumeExtents[1])/2.0 if axisIndex!=0 else volumeExtents[1],
          (volumeExtents[2]+volumeExtents[3])/2.0 if axisIndex!=1 else volumeExtents[3],
          (volumeExtents[4]+volumeExtents[5])/2.0 if axisIndex!=2 else volumeExtents[5],
          1
        ]
        # Get physical coordinates from voxel coordinates
        volumeIjkToRas = vtk.vtkMatrix4x4()
        tempSegmentLabelmapVolumeNode.GetIJKToRASMatrix(volumeIjkToRas)
        startPosition_Ras = np.array([0.0,0.0,0.0,1.0])
        volumeIjkToRas.MultiplyPoint(startPosition_Ijk, startPosition_Ras)
        endPosition_Ras = np.array([0.0,0.0,0.0,1.0])
        volumeIjkToRas.MultiplyPoint(endPosition_Ijk, endPosition_Ras)
        volumePositionIncrement_Ras = np.array([0,0,0,1])
        if numSlices > 1:
          volumePositionIncrement_Ras = (endPosition_Ras - startPosition_Ras) / (numSlices - 1.0)

        # If volume node is transformed, apply that transform to get volume's RAS coordinates
        # doesn't work???
        transformVolumeRasToRas = vtk.vtkGeneralTransform()
        slicer.vtkMRMLTransformNode.GetTransformBetweenNodes(tempSegmentLabelmapVolumeNode.GetParentTransformNode(), None, transformVolumeRasToRas)

        if segmentID == segmentNode:
          if interval > 0:
            for i in range(len(sampleSlices)):
              sliceNumberArray.InsertNextValue(sampleSlices[i]+extentoffset) # adds slice number to the array
              SegmentNameArray.InsertNextValue(segName)
              percentLengthArray.InsertNextValue(percentLength[i])
              
          else:
            for i in range(numSlices):
              sliceNumberArray.InsertNextValue(sampleSlices[i]+extentoffset) # adds slice number to the array
              SegmentNameArray.InsertNextValue(segName)
              percentLengthArray.InsertNextValue(percentLength[i])


        ###### DO CALCULATIONS ######
        spacing = tempSegmentLabelmapVolumeNode.GetSpacing()
        narray = slicer.util.arrayFromVolume(tempSegmentLabelmapVolumeNode)
        
        transformNode = segmentationNode.GetNodeReferenceID('transform')
        if transformNode != None:
          if spacing[0] != spacing[1] or spacing[0] != spacing[2] or spacing[1] != spacing[2]:
            raise ValueError("Voxels are anisotropic! Resample the volume")
          
        for i in sampleSlices:
          if axisIndex == 0:
            PixelDepthMm = spacing[0] # get mm for length
            PixelHeightMm = spacing[2]
            PixelWidthMm = spacing[1]
            areaOfPixelMm2 = spacing[1] * spacing[2]
            unitOfPixelMm4 = spacing[1]**3 * spacing[2]**1
            slicetemp = narray[:, :, i] # get the ijk coordinates for all voxels in the label map
            CSA = np.count_nonzero(narray[:,:,i])
            if volumeNode != None and IntensitycheckBox == True:
              meanIntensity = np.mean(voxelArray[:,:,i][np.where(voxelArray[:, :, i]>0)]) 
          elif axisIndex == 1:
            PixelDepthMm = spacing[1] # get mm for length
            PixelHeightMm = spacing[2]
            PixelWidthMm = spacing[0]
            areaOfPixelMm2 = spacing[0] * spacing[2]
            unitOfPixelMm4 = spacing[0]**3 * spacing[2]**1
            slicetemp = narray[:, i, :] # get the ijk coordinates for all voxels in the label map     
            CSA = np.count_nonzero(narray[:, i, :])
            if volumeNode != None and IntensitycheckBox == True:
              meanIntensity = np.mean(voxelArray[:,i,:][np.where(voxelArray[:, i, :]>0)]) 
          elif axisIndex == 2:
            PixelDepthMm = spacing[2] # get mm for length
            PixelHeightMm = spacing[1]
            PixelWidthMm = spacing[0]
            areaOfPixelMm2 = spacing[0] * spacing[1]
            unitOfPixelMm4 = spacing[0]**3 * spacing[1]**1
            slicetemp = narray[i, :, :] # get the ijk coordinates for all voxels in the label map
            CSA = np.count_nonzero(narray[i, :, :])
            if volumeNode != None and IntensitycheckBox == True:
              meanIntensity = np.mean(voxelArray[i,:,:][np.where(voxelArray[i, :, :]>0)]) 

          if segmentID == segmentNode:
          # add values to calculations 
            LengthArray.InsertNextValue((numSlices * PixelDepthMm))         
            Length = (numSlices * PixelDepthMm)
            areaArray.InsertNextValue((CSA * areaOfPixelMm2))
            if volumeNode != None and IntensitycheckBox == True:
              meanIntensityArray.InsertNextValue((meanIntensity)) 
            # do size correction
            if DoubecheckBox == True:
              areaArray_Doube.InsertNextValue((np.sqrt(CSA) / numSlices))
              
          if segmentID == areaSegmentID:
            TotalAreaArray.InsertNextValue((CSA * areaOfPixelMm2))    
           
          coords_Kji = np.where(slicetemp > 0)
          coords_Ijk = [coords_Kji[1], coords_Kji[0]]
          
          #for calculating a convex hull area and perimeter
          if segmentID == segmentNode:
            from scipy.spatial.qhull import ConvexHull
            from scipy.spatial.distance import euclidean
            points = np.concatenate((coords_Ijk[0][:,None],coords_Ijk[1][:,None]),axis = 1)
            if len(points) == 1:
              Fdiam = 1
            if len(points) == 2:
              Fdiam = 2
            if len(points) >= 3: 
              hull = ConvexHull(points)
              Fdiam = 0
              for h in hull.vertices:
                pt1 = points[h]
                for j in hull.vertices:
                  pt2 = points[j]
                  Fdiam = max(Fdiam, np.sqrt((pt2[0]-pt1[0])**2 +(pt2[1]-pt1[1])**2) * PixelWidthMm)
            FeretArray.InsertNextValue(Fdiam)
            sampleMin = int(max(sampleSlices)*.05)
            sampleMax = int(max(sampleSlices)*.95)
            if i >= sampleMin and i <= sampleMax:
              if FdiamMin == None:
                FdiamMin = (numSlices * PixelDepthMm)
              if FdiamMin != None:
                FdiamMin = min(FdiamMin,Fdiam)
                AR = (numSlices * PixelDepthMm)/FdiamMin
                if AR > 10:
                  eulerflag = 0

            
          # set up variables for calculations
          Sn = np.count_nonzero(slicetemp)
          Sx = sum(coords_Ijk[0])
          Sy = sum(coords_Ijk[1])
            
          if Sn > 0:
            # calculate centroid coordinates
            Cx = Sx / Sn
            Cy = Sy / Sn 
          if Sn == 0:
           raise ValueError("Attempted to compute on a slice with no pixels. Check for empty slices")   
          if segmentID == segmentNode:
          # add values to calculations                       
            CxArray.InsertNextValue((Cx * PixelWidthMm))
            CyArray.InsertNextValue((Cy * PixelHeightMm))
            
          # calculate second moment of area along horizontal and vertical axes
          Ix = 0
          for  s in range(Sn):
            Ix = Ix + 1/12 + (Cy - coords_Ijk[1][s])**2
            
          Iy = 0
          for  s in range(Sn):
            Iy = Iy + 1/12 + (Cx - coords_Ijk[0][s])**2

          # deteRminore how far the major principal axis is from the horizontal 
          Ixy = 0
          for s in range(Sn):
            Ixy = Ixy + (Cx - coords_Ijk[0][s]) * (Cy - coords_Ijk[1][s])

          if Ixy == 0:
            Theta = 0
          else:
            Theta = np.arctan((Ix - Iy + np.sqrt((Ix - Iy) * (Ix - Iy) + 4 * Ixy * Ixy)) / (2 * Ixy))
                     
          #major axis
          Imajor = 0
          Rmajor = 0
          for s in range(Sn): 
            rad = ((coords_Ijk[1][s]-Cy)*np.cos(Theta) - (coords_Ijk[0][s]-Cx)*np.sin(Theta))**2
            Imajor = [Imajor]+ (rad + 1/12)
            Rmajor = max(Rmajor,np.sqrt(rad))
          if Rmajor == 0:
            Zmajor = Imajor
          else:    
            Zmajor = Imajor/Rmajor
            
          # minor axis
          Iminor = 0
          Rminor = 0
          for s in range(Sn):
            rad = ((coords_Ijk[0][s]-Cx)*np.cos(Theta) + (coords_Ijk[1][s]-Cy)*np.sin(Theta))**2
            Iminor = [Iminor]+ (rad + 1/12)
            Rminor = max(Rminor,np.sqrt(rad))
          if Rminor == 0:
            Zminor = Iminor
          else:    
            Zminor = Iminor/Rminor 
                       
          if segmentID == segmentNode:
          # add values to calculations                       
            ThetaMinArray.InsertNextValue((Theta + np.pi/2)*180/np.pi )       
            ThetaMaxArray.InsertNextValue((Theta*180/np.pi) + 180)       
            ImajorArray.InsertNextValue(Imajor * unitOfPixelMm4)
            IminorArray.InsertNextValue(Iminor * unitOfPixelMm4)
            RmajorArray.InsertNextValue(Rmajor * PixelWidthMm)
            RminorArray.InsertNextValue(Rminor * PixelWidthMm)
            ZmajorArray.InsertNextValue(Zmajor * unitOfPixelMm4 / PixelWidthMm)
            ZminorArray.InsertNextValue(Zminor * unitOfPixelMm4 / PixelWidthMm)
            
            # do material normalization          
            if SummerscheckBox == True:
              ImajorArray_Summers.InsertNextValue(Imajor/((np.pi * (np.sqrt(CSA/np.pi))**4) / 4))
              IminorArray_Summers.InsertNextValue(Iminor/((np.pi * (np.sqrt(CSA/np.pi))**4) / 4))
              ZmajorArray_Summers.InsertNextValue(Zmajor/((np.pi * (np.sqrt(CSA/np.pi))**3) / 4))
              ZminorArray_Summers.InsertNextValue(Zminor/((np.pi * (np.sqrt(CSA/np.pi))**3) / 4))
              
            # do size correction
            if DoubecheckBox == True:
              ImajorArray_Doube.InsertNextValue(Imajor**(1/4) / numSlices)
              IminorArray_Doube.InsertNextValue(Iminor**(1/4) / numSlices)
              ZmajorArray_Doube.InsertNextValue(Zmajor**(1/3) / numSlices)
              ZminorArray_Doube.InsertNextValue(Zminor**(1/3) / numSlices)
           
          # use custom neutral axis  
          if OrientationcheckBox == True: 
            if RadButton == True:
              Theta = angle 
            if DegButton == True:
              Theta = angle * np.pi/180  

            #neutral axis
            Ina = 0
            Rna = 0
            for s in range(Sn): 
              rad = ((coords_Ijk[1][s]-Cy)*np.cos(Theta) - (coords_Ijk[0][s]-Cx)*np.sin(Theta))**2
              Ina = [Ina] +(rad + 1/12)
              Rna = max(Rna,np.sqrt(rad))
            if Rna == 0:
              Zna = Ina
            else:  
              Zna = Ina/Rna
            
            
            #loading axis
            Ila = 0
            Rla = 0
            for s in range(Sn):
              rad = ((coords_Ijk[0][s]-Cx)*np.cos(Theta) + (coords_Ijk[1][s]-Cy)*np.sin(Theta))**2
              Ila = [Ila]+ (rad + 1/12)
              Rla = max(Rla,np.sqrt(rad))
            if Rla == 0:
              Zla = Ila  
            else:  
              Zla = Ila/Rla
            

            if segmentID == segmentNode:
              # add values to orientation calculations 
              IlaArray.InsertNextValue(Ila * unitOfPixelMm4)
              InaArray.InsertNextValue(Ina * unitOfPixelMm4)
              ZnaArray.InsertNextValue(Zna * unitOfPixelMm4/PixelWidthMm)
              ZlaArray.InsertNextValue(Zla * unitOfPixelMm4/PixelWidthMm)
              RnaArray.InsertNextValue(Rna * PixelWidthMm)
              RlaArray.InsertNextValue(Rla * PixelWidthMm)

              # do Doube size correction
              if DoubecheckBox == True:
                InaArray_Doube.InsertNextValue(Ina**(1/4) / numSlices)
                IlaArray_Doube.InsertNextValue(Ila**(1/4) / numSlices)
                ZnaArray_Doube.InsertNextValue(Zna**(1/3) / numSlices)
                ZlaArray_Doube.InsertNextValue(Zla**(1/3) / numSlices)
              
              if SummerscheckBox == True:
                InaArray_Summers.InsertNextValue(Ina/((np.pi * (np.sqrt(CSA/np.pi))**4) / 4))
                IlaArray_Summers.InsertNextValue(Ila/((np.pi * (np.sqrt(CSA/np.pi))**4) / 4))
                ZnaArray_Summers.InsertNextValue(Zna/((np.pi * (np.sqrt(CSA/np.pi))**3) / 4))
                ZlaArray_Summers.InsertNextValue(Zla/((np.pi * (np.sqrt(CSA/np.pi))**3) / 4))
      
      if CompactnesscheckBox == True:
       for s in range(TotalAreaArray.GetNumberOfTuples()):
         CompactnessArray.InsertNextValue(float(areaArray.GetTuple(s)[0])/float(TotalAreaArray.GetTuple(s)[0]))
      
      print("Segment aspect ratio:", round(AR,2))
      if SMAcheckBox_1 == True or MODcheckBox_1 == True:
        if eulerflag == 1:
          slicer.util.errorDisplay("Warning! The no-shear assumption may not be met.  Click OK to proceed.")
      elif SMAcheckBox_1 == True or MODcheckBox_1 == True and OrientationcheckBox == True: 
        if eulerflag == 1:
          slicer.util.errorDisplay("Warning! The no-shear assumption may not be met. Click OK to proceed.")  
        
      # adds table column for various arrays
      tableNode.AddColumn(SegmentNameArray)
      tableNode.SetColumnDescription(SegmentNameArray.GetName(), "Segment name")  
      
      tableNode.AddColumn(sliceNumberArray)
      tableNode.SetColumnDescription(sliceNumberArray.GetName(), "Corresponding slice index on the untransformed volume")
      
      tableNode.AddColumn(percentLengthArray)
      tableNode.SetColumnUnitLabel(percentLengthArray.GetName(), "%")  # TODO: use length unit
      tableNode.SetColumnDescription(percentLengthArray.GetName(), "Percent of the segment length")  
      
      if LengthcheckBox == True:
        tableNode.AddColumn(LengthArray)
        tableNode.SetColumnUnitLabel(LengthArray.GetName(), "mm")  # TODO: use length unit
        tableNode.SetColumnDescription(LengthArray.GetName(), "Segment Length")  
      
      if FeretcheckBox == True:
        tableNode.AddColumn(FeretArray)
        tableNode.SetColumnUnitLabel(FeretArray.GetName(), "mm")  # TODO: use length unit
        tableNode.SetColumnDescription(FeretArray.GetName(), "Maximum feret diameter")    

      if volumeNode != None and IntensitycheckBox == True:
        tableNode.AddColumn(meanIntensityArray)
        tableNode.SetColumnDescription(LengthArray.GetName(), "Mean pixel brightness") 

      if CSAcheckBox == True:    
        tableNode.AddColumn(areaArray)
        tableNode.SetColumnUnitLabel(areaArray.GetName(), "mm2")  # TODO: use length unit
        tableNode.SetColumnDescription(areaArray.GetName(), "Cross-sectional area")  

      if CompactnesscheckBox == True:    
        tableNode.AddColumn(CompactnessArray)
        tableNode.SetColumnDescription(CompactnessArray.GetName(), "Compactness calculated as CSA/TCSA")    

      if CentroidcheckBox == True:    
        tableNode.AddColumn(CxArray)
        tableNode.SetColumnUnitLabel(CxArray.GetName(), "mm")  # TODO: use length unit
        tableNode.SetColumnDescription(CxArray.GetName(), "x-coordinate of the centroid")  
        
        tableNode.AddColumn(CyArray)
        tableNode.SetColumnUnitLabel(CyArray.GetName(), "mm")  # TODO: use length unit
        tableNode.SetColumnDescription(CyArray.GetName(), "y-coordinate of the centroid")         
                
      if ThetacheckBox == True:    
        tableNode.AddColumn(ThetaMinArray)
        tableNode.SetColumnUnitLabel(ThetaMinArray.GetName(), "degrees")  # TODO: use length unit
        tableNode.SetColumnDescription(ThetaMinArray.GetName(), "Angle of the minor principal axis")  
        
        tableNode.AddColumn(ThetaMaxArray)
        tableNode.SetColumnUnitLabel(ThetaMaxArray.GetName(), "degrees")  # TODO: use length unit
        tableNode.SetColumnDescription(ThetaMaxArray.GetName(), "Angle of the major principal axis")  
      
      if SMAcheckBox_1 == True:  
        tableNode.AddColumn(IminorArray)
        tableNode.SetColumnUnitLabel(IminorArray.GetName(), "mm4")  # TODO: use length unit
        tableNode.SetColumnDescription(IminorArray.GetName(), "Second moment of area around the minor principal axis (larger I)")
       
        tableNode.AddColumn(ImajorArray)
        tableNode.SetColumnUnitLabel(ImajorArray.GetName(), "mm4")  # TODO: use length unit
        tableNode.SetColumnDescription(ImajorArray.GetName(), "Second moment of area around the major principal axis (smaller I)")

      if MODcheckBox_1 == True:
        tableNode.AddColumn(ZminorArray)
        tableNode.SetColumnUnitLabel(ZminorArray.GetName(), "mm3")  # TODO: use length unit
        tableNode.SetColumnDescription(ZminorArray.GetName(), "Section modulus around the minor principal axis (larger Z)")
      
        tableNode.AddColumn(ZmajorArray)
        tableNode.SetColumnUnitLabel(ZmajorArray.GetName(), "mm3")  # TODO: use length unit
        tableNode.SetColumnDescription(ZmajorArray.GetName(), "Section modulus around the major principal axis (smaller Z)")

      if RcheckBox == True:  
        tableNode.AddColumn(RminorArray)
        tableNode.SetColumnUnitLabel(RminorArray.GetName(), "mm")  # TODO: use length unit
        tableNode.SetColumnDescription(RminorArray.GetName(), "Max distance from the minor principal axis") 
         
        tableNode.AddColumn(RmajorArray)
        tableNode.SetColumnUnitLabel(RmajorArray.GetName(), "mm")  # TODO: use length unit
        tableNode.SetColumnDescription(RmajorArray.GetName(), "Max distance from the major principal axis") 
   
      if OrientationcheckBox == True and SMAcheckBox_2 == True:  
        tableNode.AddColumn(InaArray)
        tableNode.SetColumnUnitLabel(InaArray.GetName(), "mm4")  # TODO: use length unit
        tableNode.SetColumnDescription(InaArray.GetName(), "Second moment of area around the neutral axis")
        
        tableNode.AddColumn(IlaArray)
        tableNode.SetColumnUnitLabel(IlaArray.GetName(), "mm4")  # TODO: use length unit
        tableNode.SetColumnDescription(IlaArray.GetName(), "Second moment of area around the loading axis")
              
      if OrientationcheckBox == True and MODcheckBox_2 == True:
        tableNode.AddColumn(ZnaArray)
        tableNode.SetColumnUnitLabel(ZnaArray.GetName(), "mm3")  # TODO: use length unit
        tableNode.SetColumnDescription(ZnaArray.GetName(), "Section modulus around the neutral axis")
        
        tableNode.AddColumn(ZlaArray)
        tableNode.SetColumnUnitLabel(ZlaArray.GetName(), "mm3")  # TODO: use length unit
        tableNode.SetColumnDescription(ZlaArray.GetName(), "Section modulus around the loading axis")
        
      if RcheckBox_2 == True and OrientationcheckBox == True:
        tableNode.AddColumn(RnaArray)
        tableNode.SetColumnUnitLabel(RnaArray.GetName(), "mm")  # TODO: use length unit
        tableNode.SetColumnDescription(RnaArray.GetName(), "Max distance from the neutral axis") 
      
        tableNode.AddColumn(RlaArray)
        tableNode.SetColumnUnitLabel(RlaArray.GetName(), "mm")  # TODO: use length unit
        tableNode.SetColumnDescription(RlaArray.GetName(), "Max distance from the loading axis") 
        
      if DoubecheckBox == True and CSAcheckBox == True:
        tableNode.AddColumn(areaArray_Doube)
        tableNode.SetColumnUnitLabel(areaArray_Doube.GetName(), "none")  # TODO: use length unit
        tableNode.SetColumnDescription(areaArray_Doube.GetName(), "CSA^(1/2)/Length")
        
      if DoubecheckBox == True and SMAcheckBox_1 == True:
        tableNode.AddColumn(IminorArray_Doube)
        tableNode.SetColumnUnitLabel(IminorArray_Doube.GetName(), "none")  # TODO: use length unit
        tableNode.SetColumnDescription(IminorArray_Doube.GetName(), "Iminor^(1/4)/Length")
        
        tableNode.AddColumn(ImajorArray_Doube)
        tableNode.SetColumnUnitLabel(ImajorArray_Doube.GetName(), "none")  # TODO: use length unit
        tableNode.SetColumnDescription(ImajorArray_Doube.GetName(), "Imajor^(1/4)/Length")

      if DoubecheckBox == True and MODcheckBox_1 == True:
        tableNode.AddColumn(ZminorArray_Doube)
        tableNode.SetColumnUnitLabel(ZminorArray_Doube.GetName(), "none")  # TODO: use length unit
        tableNode.SetColumnDescription(ZminorArray_Doube.GetName(), "Zminor^(1/3)/Length") 
  
        tableNode.AddColumn(ZmajorArray_Doube)
        tableNode.SetColumnUnitLabel(ZmajorArray_Doube.GetName(), "none")  # TODO: use length unit
        tableNode.SetColumnDescription(ZmajorArray_Doube.GetName(), "Zmajor^(1/3)/Length")
      
      if DoubecheckBox == True and SMAcheckBox_2 == True and OrientationcheckBox == True:
        tableNode.AddColumn(InaArray_Doube)
        tableNode.SetColumnUnitLabel(InaArray_Doube.GetName(), "none")  # TODO: use length unit
        tableNode.SetColumnDescription(InaArray_Doube.GetName(), "Ina^(1/4)/Length")
        
        tableNode.AddColumn(IlaArray_Doube)
        tableNode.SetColumnUnitLabel(IlaArray_Doube.GetName(), "none")  # TODO: use length unit
        tableNode.SetColumnDescription(IlaArray_Doube.GetName(), "Ila^(1/4)/Length")

      if DoubecheckBox == True and MODcheckBox_2 == True and OrientationcheckBox == True:
        tableNode.AddColumn(ZlaArray_Doube)
        tableNode.SetColumnUnitLabel(ZlaArray_Doube.GetName(), "none")  # TODO: use length unit
        tableNode.SetColumnDescription(ZlaArray_Doube.GetName(), "Zla^(1/3)/Length")  
        
        tableNode.AddColumn(ZnaArray_Doube)
        tableNode.SetColumnUnitLabel(ZnaArray_Doube.GetName(), "none")  # TODO: use length unit
        tableNode.SetColumnDescription(ZnaArray_Doube.GetName(), "Zna^(1/3)/Length")

      if SummerscheckBox == True and SMAcheckBox_1 == True:
        tableNode.AddColumn(IminorArray_Summers)
        tableNode.SetColumnUnitLabel(IminorArray_Summers.GetName(), "none")  # TODO: use length unit
        tableNode.SetColumnDescription(IminorArray_Summers.GetName(), "Iminor divided by the second moment of area of a solid circle with the same cross-sectional area") 
        
        tableNode.AddColumn(ImajorArray_Summers)
        tableNode.SetColumnUnitLabel(ImajorArray_Summers.GetName(), "none")  # TODO: use length unit
        tableNode.SetColumnDescription(ImajorArray_Summers.GetName(), "Imajor divided by the second moment of area of a solid circle with the same cross-sectional area")        

      if SummerscheckBox == True and MODcheckBox_1 == True:
        tableNode.AddColumn(ZminorArray_Summers)
        tableNode.SetColumnUnitLabel(ZminorArray_Summers.GetName(), "none")  # TODO: use length unit
        tableNode.SetColumnDescription(ZminorArray_Summers.GetName(), "Zminor divided by the section modulus of a solid circle with the same cross-sectional area")
        
        tableNode.AddColumn(ZmajorArray_Summers)
        tableNode.SetColumnUnitLabel(ZmajorArray_Summers.GetName(), "none")  # TODO: use length unit
        tableNode.SetColumnDescription(ZmajorArray_Summers.GetName(), "Zmajor divided by the section modulus of a solid circle with the same cross-sectional area")    
        
      if SummerscheckBox == True and SMAcheckBox_2 == True and OrientationcheckBox == True:
        tableNode.AddColumn(InaArray_Summers)
        tableNode.SetColumnUnitLabel(InaArray_Summers.GetName(), "none")  # TODO: use length unit
        tableNode.SetColumnDescription(InaArray_Summers.GetName(), "Ina divided by the second moment of area of a solid circle with the same cross-sectional area")
        
        tableNode.AddColumn(IlaArray_Summers)
        tableNode.SetColumnUnitLabel(IlaArray_Summers.GetName(), "none")  # TODO: use length unit
        tableNode.SetColumnDescription(IlaArray_Summers.GetName(), "Ila divided by the second moment of area of a solid circle with the same cross-sectional area") 
        
      if SummerscheckBox == True and MODcheckBox_2 == True and OrientationcheckBox == True:
        tableNode.AddColumn(ZnaArray_Summers)
        tableNode.SetColumnUnitLabel(ZnaArray_Summers.GetName(), "none")  # TODO: use length unit
        tableNode.SetColumnDescription(ZnaArray_Summers.GetName(), "Zna divided by the section modulus of a solid circle with the same cross-sectional area")
        
        tableNode.AddColumn(ZlaArray_Summers)
        tableNode.SetColumnUnitLabel(ZlaArray_Summers.GetName(), "none")  # TODO: use length unit
        tableNode.SetColumnDescription(ZlaArray_Summers.GetName(), "Zla divided by the section modulus of a solid circle with the same cross-sectional area")         
      
      # Make a plot series node for this column.
      segment = segmentationNode.GetSegmentation().GetSegment(segmentNode)
      segName = segment.GetName()
      if SMAcheckBox_1 == True: 
        if slicer.mrmlScene.GetFirstNodeByName(segName + " Iminor (mm^4)") != None and plotChartNode.GetPlotSeriesNodeID() != None:
          plotSeriesNode = slicer.mrmlScene.GetFirstNodeByName(segName + " Iminor (mm^4)")
        else:
          plotSeriesNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotSeriesNode", segName + " Iminor (mm^4)")
          plotSeriesNode.SetPlotType(plotSeriesNode.PlotTypeScatter)
          plotSeriesNode.SetAndObserveTableNodeID(tableNode.GetID())
          plotSeriesNode.SetYColumnName("Iminor (mm^4)")
          plotSeriesNode.SetXColumnName("Percent (%)")
          plotSeriesNode.SetUniqueColor()

          # Add this series to the plot chart node created above.
          plotChartNode.AddAndObservePlotSeriesNodeID(plotSeriesNode.GetID())
      
      #plotChartNode.SetXAxisTitle("Percent of Length")
      if OrientationcheckBox == True and SMAcheckBox_2 == True: 
        if slicer.mrmlScene.GetFirstNodeByName(segName + " Ina (mm^4)") != None and plotChartNode.GetPlotSeriesNodeID() != None:
          plotSeriesNode2 = slicer.mrmlScene.GetFirstNodeByName(segName + " Ina (mm^4)")
        else:
          plotSeriesNode2 = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotSeriesNode", segName + " Ina (mm^4)")
          plotSeriesNode2.SetPlotType(plotSeriesNode2.PlotTypeScatter)
          plotSeriesNode2.SetAndObserveTableNodeID(tableNode.GetID())
          plotSeriesNode2.SetYColumnName("Ina (mm^4)")
          plotSeriesNode2.SetXColumnName("Percent (%)")
          plotSeriesNode2.SetUniqueColor()
        
          # Add this series to the plot chart node created above.
          plotChartNode.AddAndObservePlotSeriesNodeID(plotSeriesNode2.GetID())
          
      if OrientationcheckBox == False and SMAcheckBox_1 == False and CSAcheckBox == True: 
        plotChartNode.SetYAxisTitle('Cross-Sectional Area (mm^2)') 
        if slicer.mrmlScene.GetFirstNodeByName(segName + " CSA (mm^2)") != None and plotChartNode.GetPlotSeriesNodeID() != None:
          plotSeriesNode3 = slicer.mrmlScene.GetFirstNodeByName(segName + " CSA (mm^2)")
        else:
          plotSeriesNode3 = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotSeriesNode", segName + " CSA (mm^4)")
          plotSeriesNode3.SetPlotType(plotSeriesNode3.PlotTypeScatter)
          plotSeriesNode3.SetAndObserveTableNodeID(tableNode.GetID())
          plotSeriesNode3.SetYColumnName("CSA (mm^2)")
          plotSeriesNode3.SetXColumnName("Percent (%)")
          plotSeriesNode3.SetUniqueColor()
        
          # Add this series to the plot chart node created above.
          plotChartNode.AddAndObservePlotSeriesNodeID(plotSeriesNode3.GetID())
         
       
    finally:
      # Remove temporary volume node
      slicer.mrmlScene.RemoveNode(tempSegmentLabelmapVolumeNode)
      slicer.mrmlScene.RemoveNode(slicer.mrmlScene.GetFirstNodeByName("SegmentGeometryTemp_ColorTable"))
      slicer.mrmlScene.RemoveNode(slicer.mrmlScene.GetFirstNodeByName("SegmentGeometryTemp_ColorTable"))
      slicer.mrmlScene.RemoveNode(slicer.mrmlScene.GetFirstNodeByName("FullVolumeTemp_ColorTable"))
      slicer.mrmlScene.RemoveNode(slicer.mrmlScene.GetFirstNodeByName("FullVolumeTemp_ColorTable"))
      # Change layout to include plot and table
      layoutManager = slicer.app.layoutManager()
      layoutWithPlot = slicer.modules.plots.logic().GetLayoutWithPlot(layoutManager.layout)
      layoutManager.setLayout(layoutWithPlot)
      # Select chart in plot view
      plotWidget = layoutManager.plotWidget(0)
      plotViewNode = plotWidget.mrmlPlotViewNode()
      plotViewNode.SetPlotChartNodeID(plotChartNode.GetID())
      
      layoutWithPlot = slicer.modules.tables.logic().GetLayoutWithTable(layoutManager.layout)
      layoutManager.setLayout(layoutWithPlot)
      # Select chart in table view
      tableWidget = layoutManager.tableWidget(0)
      tableWidget.tableView().setMRMLTableNode(tableNode)



    logging.info('Processing completed')


#
# SegmentCrossSectionAreaTest
#

class SegmentGeometryTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """
  
  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_SegmentGeometry1()

  def test_SegmentGeometry1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")

    # Load master volume
    import SampleData
    sampleDataLogic = SampleData.SampleDataLogic()
    sampleDataLogic.downloadDentalSurgery()
    masterVolumeNode = slicer.util.getFirstNodeByName("PreDentalSurgery")

    # Create segmentation
    segmentationNode = slicer.vtkMRMLSegmentationNode()
    slicer.mrmlScene.AddNode(segmentationNode)
    segmentationNode.CreateDefaultDisplayNodes()  # only needed for display
    segmentationNode.SetReferenceImageGeometryParameterFromVolumeNode(masterVolumeNode)

    # Create a sphere shaped segment
    radius = 20
    tumorSeed = vtk.vtkSphereSource()
    tumorSeed.SetCenter(-90, -90, 80)
    tumorSeed.SetRadius(radius)
    tumorSeed.SetPhiResolution(120)
    tumorSeed.SetThetaResolution(120)
    tumorSeed.Update()
    segmentId = segmentationNode.AddSegmentFromClosedSurfaceRepresentation(tumorSeed.GetOutput(), "Tumor",
                                                                           [1.0, 0.0, 0.0])
    segmentNode = segmentationNode.GetSegmentation().GetSegment(segmentId)                                                                       

    tableNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTableNode", "Segment Geometry test table")
    plotChartNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotChartNode", "Segment Geometry test plot")

    logic = SegmentGeometryLogic()
    logic.run(segmentationNode, segmentId, masterVolumeNode, False, "S (Red)", 1, tableNode, plotChartNode, True, True, True, True, True,
    True, True, True, True, True, True, 0, True, True, True, True, True, True,segmentationNode, segmentId, True)
    #self.assertEqual(tableNode.GetNumberOfColumns(), 38)

    import math
    # Compute CSA error
    crossSectionAreas = slicer.util.arrayFromTableColumn(tableNode, "CSA (mm^2)")
    largestCrossSectionArea = crossSectionAreas.max()
    expectedlargestCrossSectionArea = radius*radius*math.pi
    logging.info("Largest cross-section area: {0:.2f}".format(largestCrossSectionArea))
    logging.info("Expected largest cross-section area: {0:.2f}".format(expectedlargestCrossSectionArea))
    errorPercent = 100.0 * abs(1-(largestCrossSectionArea /expectedlargestCrossSectionArea))
    logging.info("Largest cross-section area error: {0:.2f}%".format(errorPercent))
    
    # Compute Iminor error
    crossSectionSecondMom = slicer.util.arrayFromTableColumn(tableNode, "Iminor (mm^4)")
    largestSecondMom  = crossSectionSecondMom.max()
    expectedlargestSecondMom = radius*radius*radius*radius*math.pi/4
    logging.info("Largest second moment of area: {0:.2f}".format(largestSecondMom))
    logging.info("Expected largest second moment of area: {0:.2f}".format(expectedlargestSecondMom))
    errorPercent2 = 100.0 * abs(1- (largestSecondMom/expectedlargestSecondMom))
    logging.info("Largest second moment of area error: {0:.2f}%".format(errorPercent2))
    
    # Compute Section modulus error
    crossSectionModulus = slicer.util.arrayFromTableColumn(tableNode, "Zminor (mm^3)")
    largestModulus  = crossSectionModulus.max()
    expectedlargestModulus = radius*radius*radius*math.pi/4
    logging.info("Largest section modulus: {0:.2f}".format(largestModulus))
    logging.info("Expected largest section modulus: {0:.2f}".format(expectedlargestModulus))
    errorPercent3 = 100.0 * abs(1- (largestModulus/expectedlargestModulus))
    logging.info("Largest section modulus area error: {0:.2f}%".format(errorPercent3))

    # Error between expected and actual cross section is due to finite resolution of the segmentation.
    # It should not be more than a few percent. The actual error in this case is around 1%, but use 2% to account for
    # numerical differences between different platforms.
    # Note: that error tends to be higher for anistropic data
    self.assertTrue(errorPercent < 3.0)
    self.assertTrue(errorPercent2 < 3.0)
    self.assertTrue(errorPercent3 < 3.0)

    self.delayDisplay('Test passed')
