import os
import unittest
import logging
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin

#
# SegmentSliceGeometry
#

class SegmentSliceGeometry(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Segment Slice Geometry"
    self.parent.categories = ["Quantification"]
    self.parent.dependencies = []
    self.parent.contributors = ["Jonathan Huie (GWU)"]
    self.parent.helpText = """This module computes segment slice geometries such as cross-sectional area, second moment of area, section modulus, and more."""
    self.parent.acknowledgementText = """
This file was developed by Jonathan Huie. Slice geometry equations from BoneJ (Doube et al. 2015). Module framework from the Segment Cross-Section Area module, initially 
developed by Hollister Herhold (AMNH) and Andras Lasso (PerkLab)."""


#
# SegmentSliceGeometryWidget
#

class SegmentSliceGeometryWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
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
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/SegmentSliceGeometry.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    # Set scene in MRML widgets. Make sure that in Qt designer
    # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget'rowCount.
    # "setMRMLScene(vtkMRMLScene*)" slot.
    uiWidget.setMRMLScene(slicer.mrmlScene)

    # Create a new parameterNode
    # This parameterNode stores all user choices in parameter values, node selections, etc.
    # so that when the scene is saved and reloaded, these settings are restored.
    self.logic = SegmentSliceGeometryLogic()
    self.ui.parameterNodeSelector.addAttribute("vtkMRMLScriptedModuleNode", "ModuleName", self.moduleName)
    self.setParameterNode(self.logic.getParameterNode())

    # Connections
    self.ui.parameterNodeSelector.connect('currentNodeChanged(vtkMRMLNode*)', self.setParameterNode)
    self.ui.applyButton.connect('clicked(bool)', self.onApplyButton)

    # These connections ensure that whenever user changes some settings on the GUI, that is saved in the MRML scene
    # (in the selected parameter node).
    self.ui.segmentationSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.volumeSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.axisSelectorBox.connect("currentIndexChanged(int)", self.updateParameterNodeFromGUI)
    self.ui.resamplespinBox.connect("valueChanged(int)", self.updateParameterNodeFromGUI)
    self.ui.tableSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.chartSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.OrientationcheckBox.connect('stateChanged(int)', self.updateParameterNodeFromGUI)
    self.ui.orientationspinBox.connect("valueChanged(int)", self.updateParameterNodeFromGUI)


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

    if inputParameterNode:
      self.logic.setDefaultParameters(inputParameterNode)
      # TODO: uncomment this when nodeFromIndex method will be available in Python
      # # Select first segmentation node by default
      # if not inputParameterNode.GetNodeReference("Segmentation"):
      #   segmentationNode = self.ui.segmentationSelector.nodeFromIndex(0)
      #   if segmentationNode:
      #     inputParameterNode.SetNodeReferenceID(segmentationNode.GetID())

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

    # Update buttons states and tooltips
    if self._parameterNode.GetNodeReference("Segmentation"):
      self.ui.segmentationSelector.toolTip = "Select output table"
      self.ui.applyButton.toolTip = "Compute slice geometries"
      self.ui.applyButton.enabled = True
    else:
      self.ui.segmentationSelector.toolTip = "Select segmentation node"
      self.ui.applyButton.toolTip = "Select input segmentation node"
      self.ui.applyButton.enabled = False
      
    if self._parameterNode.GetNodeReference("Volume"):
      self.ui.volumeSelector.toolTip = "Select output table"
      self.ui.IntensitycheckBox.toolTip = "Compute mean voxel intensity"
      self.ui.IntensitycheckBox.enabled = True
    else:
      self.ui.volumeSelector.toolTip = "Select volume node (optional)"
      self.ui.IntensitycheckBox.toolTip = "Select input volume node"
      self.ui.IntensitycheckBox.enabled = False
      
    if self._parameterNode.GetNodeReference("ResultsTable"):
      self.ui.tableSelector.toolTip = "Edit output table"
    else:
      self.ui.tableSelector.toolTip = "Select output node"
      
    if self._parameterNode.GetNodeReference("ResultsChart"):
      self.ui.tableSelector.toolTip = "Edit output chart"
    else:
      self.ui.tableSelector.toolTip = "Select output chart"
            
    if self.ui.OrientationcheckBox.checked == True:
      self.ui.orientationspinBox.toolTip = "Enter the angle (degrees) of the neutral axis. By default, the neutral axis is set parallel to the horizontal"
      self.ui.orientationspinBox.enabled = True
      self.ui.SMAcheckBox_2.toolTip = "Compute second moment of area around the neutral and force axes"
      self.ui.SMAcheckBox_2.enabled = True
      self.ui.MODcheckBox_2.toolTip = "Compute section modulus around the neutral and force axes"
      self.ui.MODcheckBox_2.enabled = True
      self.ui.PolarcheckBox_2.toolTip = "Compute polar moment of inertia around the neutral and force axes"
      self.ui.PolarcheckBox_2.enabled = True
    else:
      self.ui.orientationspinBox.toolTip = "Select option use the neutral axis"
      self.ui.orientationspinBox.enabled = False
      self.ui.SMAcheckBox_2.toolTip = "Select option to use neutral axis"
      self.ui.SMAcheckBox_2.enabled = False
      self.ui.MODcheckBox_2.toolTip = "Select option to use neutral axis"
      self.ui.MODcheckBox_2.enabled = False
      self.ui.PolarcheckBox_2.toolTip = "Select option to use neutral axis"
      self.ui.PolarcheckBox_2.enabled = False
      
    # other tooltips
    self.ui.axisSelectorBox.toolTip = "Select orthogonal axis to compute on"
    self.ui.resamplespinBox.toolTip = "Perform computations in percent intervals along the the segment. Enter zero to compute values on every slice"
    self.ui.CSAcheckBox.toolTip = "Compute cross-sectional area"
    self.ui.SMAcheckBox_1.toolTip = "Compute second moment of area around the principal axes"
    self.ui.MODcheckBox_1.toolTip = "Compute section modulus around the principal axes"
    self.ui.PolarcheckBox_1.toolTip = "Compute polar moment of inertia around the principal axes"
    self.ui.LengthcheckBox.toolTip = "Compute the length of the segment along the chosen axis"
    self.ui.CentroidcheckBox.toolTip = "Compute the XY coordinates of the segment on a given slice"
    self.ui.ThetacheckBox.toolTip = "Compute how much the major axis deviates from the horizontal axis"
    self.ui.RcheckBox.toolTip = "Compute the max distances from the principal or user-defined axes"
    self.ui.DoubecheckBox.toolTip = "Size-correct values by taking the respective roots needed to reduce them to a single linear dimension and then divinding the values by segment length following Doube et al. (2012)"
    self.ui.SummerscheckBox.toolTip = "Compute the ratio of second moment of area for a give slice over the second moment of area for a circluar beam with the same cross-sectional area following Summers et al. (2004)"
    




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


  def onApplyButton(self):
    """
    Run processing when user clicks "Apply" button.
    """
      
    try:
      import SegmentEditorEffects
      if not hasattr(SegmentEditorEffects,'SegmentEditorMaskVolumeEffect'):
      # Slicer 4.11 and earlier - Mask volume is in an extension
        import SegmentEditorMaskVolumeLib
        maskVolumeWithSegment = SegmentEditorMaskVolumeLib.SegmentEditorEffect.maskVolumeWithSegment
      else:
        maskVolumeWithSegment = SegmentEditorEffects.SegmentEditorMaskVolumeEffect.maskVolumeWithSegment

      # Create nodes for results
      tableNode = self.ui.tableSelector.currentNode()
      if not tableNode:
        tableNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTableNode", "Slice Geometry table")
        self.ui.tableSelector.setCurrentNode(tableNode)
      plotChartNode = self.ui.chartSelector.currentNode()
      if not plotChartNode:
        plotChartNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotChartNode", "Slice Geometry plot")
        self.ui.chartSelector.setCurrentNode(plotChartNode)

      self.logic.run(self.ui.segmentationSelector.currentNode(), self.ui.volumeSelector.currentNode(), self.ui.axisSelectorBox.currentText, 
                     self.ui.resamplespinBox.value, tableNode, plotChartNode, self.ui.LengthcheckBox.checked,
                     self.ui.CSAcheckBox.checked, self.ui.IntensitycheckBox.checked, self.ui.SMAcheckBox_1.checked, self.ui.MODcheckBox_1.checked,
                     self.ui.PolarcheckBox_1.checked, self.ui.OrientationcheckBox.checked, self.ui.SMAcheckBox_2.checked, 
                     self.ui.MODcheckBox_2.checked, self.ui.PolarcheckBox_2.checked, self.ui.orientationspinBox.value, 
                     self.ui.CentroidcheckBox.checked, self.ui.ThetacheckBox.checked, self.ui.RcheckBox.checked,
                     self.ui.DoubecheckBox.checked, self.ui.SummerscheckBox.checked)

    except Exception as e:
      slicer.util.errorDisplay("Failed to compute results: "+str(e))
      import traceback
      traceback.print_exc()


#
# SegmentSliceGeometryLogic
#

class SegmentSliceGeometryLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setDefaultParameters(self, parameterNode):
    """
    Initialize parameter node with default settings.
    """
    if not parameterNode.GetParameter("Axis"):
      parameterNode.SetParameter("Axis", "slice")


  def run(self, segmentationNode, volumeNode, axis, interval, tableNode, plotChartNode, LengthcheckBox, CSAcheckBox, IntensitycheckBox, SMAcheckBox_1,
  MODcheckBox_1, PolarcheckBox_1, OrientationcheckBox, SMAcheckBox_2, MODcheckBox_2, PolarcheckBox_2, angle, CentroidcheckBox, ThetacheckBox, RcheckBox,
  DoubecheckBox, SummerscheckBox):
    """
    Run the processing algorithm.
    Can be used without GUI widget.
    :param segmentationNode: cross section area will be computed on this
    :param axis: axis index to compute cross section areas along
    :param tableNode: result table node
    :param plotChartNode: result chart node
    """

    import numpy as np

    logging.info('Processing started')

    if not segmentationNode:
      raise ValueError("Segmentation node is invalid")
    
    # Get visible segment ID list.
    # Get segment ID list
    visibleSegmentIds = vtk.vtkStringArray()
    segmentationNode.GetDisplayNode().GetVisibleSegmentIDs(visibleSegmentIds)
    if visibleSegmentIds.GetNumberOfValues() == 0:
      raise ValueError("SliceAreaPlot will not return any results: there are no visible segments")

    if axis=="row":
      axisIndex = 0
    elif axis=="column":
      axisIndex = 1
    elif axis=="slice":
      axisIndex = 2
    else:
      raise ValueError("Invalid axis name: "+axis)

    # Make a table and set the first column as the slice number. 
    tableNode.RemoveAllColumns()
    table = tableNode.GetTable()
    
    # Make a plot chart node. Plot series nodes will be added to this in the
    # loop below that iterates over each segment.
    plotChartNode.SetTitle('Segment slice geometry')
    plotChartNode.SetXAxisTitle("Percent of Length")
    #plotChartNode.SetYAxisTitle('Area in mm^2')  # TODO: use length unit
    
    
    # do calculations
    try:
      # Create temporary volume node
      tempSegmentLabelmapVolumeNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLLabelMapVolumeNode', "SegmentSliceGeometryTemp")

      
      #### CREATE ARRAYS FOR ALL COLUMNS ####
      sliceNumberArray = vtk.vtkIntArray()
      sliceNumberArray.SetName("Slice")
          
      SegmentNameArray = vtk.vtkStringArray()
      SegmentNameArray.SetName("Segment")
          
      percentLengthArray = vtk.vtkFloatArray()
      percentLengthArray.SetName("Percent (%)")

      LengthArray = vtk.vtkFloatArray()
      LengthArray.SetName("Length (mm)")
        
      areaArray = vtk.vtkFloatArray()
      areaArray.SetName("CSA (mm^2)")
      
      meanIntensityArray = vtk.vtkFloatArray()
      meanIntensityArray.SetName("Mean Intensity")
      
      CxArray = vtk.vtkFloatArray()
      CxArray.SetName("X Centroid (mm)")
      
      CyArray = vtk.vtkFloatArray()
      CyArray.SetName("Y Centroid (mm)")
              
      ThetaArray = vtk.vtkFloatArray()
      ThetaArray.SetName("Theta (rad)")
              
      RmaxArray = vtk.vtkFloatArray()
      RmaxArray.SetName("Rmax (mm)")
        
      RminArray = vtk.vtkFloatArray()
      RminArray.SetName("Rmin (mm)")
      
      JxyArray = vtk.vtkFloatArray()
      JxyArray.SetName("Jna+fa (mm^4)")
        
      ImaxArray = vtk.vtkFloatArray()
      ImaxArray.SetName("Imax (mm^4)")
        
      IminArray = vtk.vtkFloatArray()
      IminArray.SetName("Imin (mm^4)")
      
      JzArray = vtk.vtkFloatArray()
      JzArray.SetName("Jmax+min (mm^4)")
        
      ZmaxArray = vtk.vtkFloatArray()
      ZmaxArray.SetName("Zmax (mm^3)")
        
      ZminArray = vtk.vtkFloatArray()
      ZminArray.SetName("Zmin (mm^3)")
      
      RnaArray = vtk.vtkFloatArray()
      RnaArray.SetName("Rna (mm)")
      
      RfaArray = vtk.vtkFloatArray()
      RfaArray.SetName("Rfa (mm)")
              
      InaArray = vtk.vtkFloatArray()
      InaArray.SetName("Ina (mm^4)")
        
      IfaArray = vtk.vtkFloatArray()
      IfaArray.SetName("Ifa (mm^4)")
        
      ZnaArray = vtk.vtkFloatArray()
      ZnaArray.SetName("Zna (mm^3)")
        
      ZfaArray = vtk.vtkFloatArray()
      ZfaArray.SetName("Zfa (mm^3)")
      
      #create arrays for unitless metrics with Doube method
      if DoubecheckBox == True:
        areaArray_Doube = vtk.vtkFloatArray()
        areaArray_Doube.SetName("CSA (Doube)")
        
        InaArray_Doube = vtk.vtkFloatArray()
        InaArray_Doube.SetName("Ina (Doube)")
        
        IfaArray_Doube = vtk.vtkFloatArray()
        IfaArray_Doube.SetName("Ifa (Doube)")
      
        JxyArray_Doube = vtk.vtkFloatArray()
        JxyArray_Doube.SetName("Iz (Doube)")
        
        ImaxArray_Doube = vtk.vtkFloatArray()
        ImaxArray_Doube.SetName("Imax (Doube)")
        
        IminArray_Doube = vtk.vtkFloatArray()
        IminArray_Doube.SetName("Imin (Doube)")
      
        JzArray_Doube = vtk.vtkFloatArray()
        JzArray_Doube.SetName("Jz (Doube)")
        
        ZmaxArray_Doube = vtk.vtkFloatArray()
        ZmaxArray_Doube.SetName("Zmax (Doube)")
        
        ZminArray_Doube = vtk.vtkFloatArray()
        ZminArray_Doube.SetName("Zmin (Doube)")
        
        ZnaArray_Doube = vtk.vtkFloatArray()
        ZnaArray_Doube.SetName("Zna (Doube)")
        
        ZfaArray_Doube = vtk.vtkFloatArray()
        ZfaArray_Doube.SetName("Zfa (Doube)")
      
      if SummerscheckBox == True:
        InaArray_Summers = vtk.vtkFloatArray()
        InaArray_Summers.SetName("Ina (Summers)")
        
        IfaArray_Summers = vtk.vtkFloatArray()
        IfaArray_Summers.SetName("Ifa (Summers)")
      
        JxyArray_Summers = vtk.vtkFloatArray()
        JxyArray_Summers.SetName("Iz (Summers)")
        
        ImaxArray_Summers = vtk.vtkFloatArray()
        ImaxArray_Summers.SetName("Imax (Summers)")
        
        IminArray_Summers = vtk.vtkFloatArray()
        IminArray_Summers.SetName("Imin (Summers)")
        
        JzArray_Summers = vtk.vtkFloatArray()
        JzArray_Summers.SetName("Jz (Summers)")
        
        ZmaxArray_Summers = vtk.vtkFloatArray()
        ZmaxArray_Summers.SetName("Zmax (Summers)")
        
        ZminArray_Summers = vtk.vtkFloatArray()
        ZminArray_Summers.SetName("Zmin (Summers)")
        
        ZnaArray_Summers = vtk.vtkFloatArray()
        ZnaArray_Summers.SetName("Zna (Summers)")
        
        ZfaArray_Summers = vtk.vtkFloatArray()
        ZfaArray_Summers.SetName("Zfa (Summers)")
      
    
      
      for segmentIndex in range(visibleSegmentIds.GetNumberOfValues()):
        segmentID = visibleSegmentIds.GetValue(segmentIndex)
        
        segment = segmentationNode.GetSegmentation().GetSegment(segmentID)
        segName = segment.GetName()

        segmentList = vtk.vtkStringArray()
        segmentList.InsertNextValue(segmentID)
        
        volumesLogic = slicer.modules.volumes.logic()
        if volumeNode != None:   
          # Create volume for output
          outputVolume = volumesLogic.CloneVolumeGeneric(volumeNode.GetScene(), volumeNode, "TempMaskVolume", False)
          volumeNodeformasking = volumeNode
          
        if volumeNode == None:
          volumeNodeformasking = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLLabelMapVolumeNode', "FullVolumeTemp")
          slicer.modules.segmentations.logic().ExportAllSegmentsToLabelmapNode(segmentationNode, volumeNodeformasking, slicer.vtkSegmentation.EXTENT_REFERENCE_GEOMETRY)
          outputVolume = volumesLogic.CloneVolumeGeneric(volumeNodeformasking.GetScene(), volumeNodeformasking, "TempMaskVolume", False)
          
        # Crop segment
        maskExtent = [0] * 6
        fillValue = 0
        #import SegmentEditorEffects
        import SegmentEditorMaskVolumeLib
        maskVolumeWithSegment = SegmentEditorMaskVolumeLib.SegmentEditorEffect.maskVolumeWithSegment
        #maskVolumeWithSegment = SegmentEditorEffects.SegmentEditorMaskVolumeEffect.maskVolumeWithSegment
        maskVolumeWithSegment(segmentationNode, segmentID, "FILL_OUTSIDE", [fillValue], volumeNodeformasking, outputVolume, maskExtent) 
          
        # Calculate padded extent of segment
        realextent=volumeNodeformasking.GetImageData().GetExtent()
        if axisIndex == 0:
          extent = [maskExtent[0],maskExtent[1],realextent[2],realextent[3],realextent[4],realextent[5]]
        elif axisIndex == 1:
          extent = [realextent[0],realextent[1],maskExtent[2],maskExtent[3],realextent[4],realextent[5]]
        elif axisIndex == 2:
          extent = [realextent[0],realextent[1],realextent[2],realextent[3],maskExtent[4],maskExtent[5]]

          
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
          voxelArray = slicer.util.arrayFromVolume(outputVolume)  
          
        # remove output volume node 
        slicer.mrmlScene.RemoveNode(outputVolume)
        
        if volumeNode == None:
          slicer.mrmlScene.RemoveNode(volumeNodeformasking)


        # volumeExtents so first and last number of images in XYZ directions. Starts with 0 not 1	
        volumeExtents = tempSegmentLabelmapVolumeNode.GetImageData().GetExtent()
        numSlices = volumeExtents[axisIndex*2+1] - volumeExtents[axisIndex*2] + 1
        
        # determine how many slices to calculate statistics for
        if interval > 0:
          resample = 100 / interval - 1
          resample = int(resample)
          sampleSlices = np.linspace(0,numSlices,num = resample+1, endpoint = False)
          sampleSlices = np.rint(sampleSlices)
          sampleSlices = sampleSlices.astype(int)
          sampleSlices = sampleSlices[1:]
          #sampleSlices = np.append(sampleSlices, (numSlices-1))
        elif interval == 0:
          resample = numSlices
          sampleSlices = np.asarray(list(range(0,numSlices)))
        percentLength = np.around(sampleSlices / numSlices * 100,1)
          
        # determines centroid of the first and last slice. Identical if only one slice
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

        if interval > 0:
          for i in range(len(sampleSlices)):
            sliceNumberArray.InsertNextValue(i + 1) # adds slice number to the array
            SegmentNameArray.InsertNextValue(segName)
            percentLengthArray.InsertNextValue(percentLength[i])
              
        else:
          for i in range(numSlices):
            sliceNumberArray.InsertNextValue(i + 1) # adds slice number to the array
            SegmentNameArray.InsertNextValue(segName)
            percentLengthArray.InsertNextValue(percentLength[i])
        
        ###### SET UP UNITS ######
        
        # Convert number of voxels to area in mm2
        spacing = tempSegmentLabelmapVolumeNode.GetSpacing()
        areaOfPixelMm2 = spacing[0] * spacing[1] * spacing[2] / spacing[axisIndex]
        
        volOfPixelMm3 = spacing[0] * spacing[1] * spacing[2]
        
        unitOfPixelMm4 = spacing[0]**2 * (spacing[1]**2) * spacing[2]**2 / spacing[axisIndex]**2
        
        ###### DO CALCULATIONS ######
        narray = slicer.util.arrayFromVolume(tempSegmentLabelmapVolumeNode)
        
        
        for i in sampleSlices:
          if axisIndex == 0:
            lengthofPixelMm = spacing[1] # get mm for length
            slicetemp = narray[:, :, i] # get the ijk coordinates for all voxels in the label map
            CSA = np.count_nonzero(narray[:,:,i])
            if volumeNode != None and IntensitycheckBox == True:
              meanIntensity = np.mean(voxelArray[:,:,i][np.where(voxelArray[:, :, i]>0)]) 
          elif axisIndex == 1:
            lengthofPixelMm = spacing[2] # get mm for length
            slicetemp = narray[:, i, :] # get the ijk coordinates for all voxels in the label map     
            CSA = np.count_nonzero(narray[:, i, :])
            if volumeNode != None and IntensitycheckBox == True:
              meanIntensity = np.mean(voxelArray[:,i,:][np.where(voxelArray[:, i, :]>0)]) 
          elif axisIndex == 2:
            lengthofPixelMm = spacing[0] # get mm for length
            slicetemp = narray[i, :, :] # get the ijk coordinates for all voxels in the label map
            CSA = np.count_nonzero(narray[i, :, :])
            if volumeNode != None and IntensitycheckBox == True:
              meanIntensity = np.mean(voxelArray[i,:,:][np.where(voxelArray[i, :, :]>0)]) 
            
          coords_Kji = np.where(slicetemp > 0)
          coords_Ijk = [coords_Kji[1], coords_Kji[0]]
            
          # set up variables for calculations
          Sn = np.count_nonzero(slicetemp)
          Sx = sum(coords_Ijk[0])
          Sxx = sum(coords_Ijk[0] * coords_Ijk[0])
          Sy = sum(coords_Ijk[1])
          Syy = sum(coords_Ijk[1] * coords_Ijk[1])
          Sxy = sum(coords_Ijk[0] * coords_Ijk[1])
            
          if Sn > 0:
            # calculate centroid coordinates
            Cx = Sx / Sn
            Cy = Sy / Sn
            
          # calculate second moment of area along horizontal and vertical axes
          Myy = Sxx - (Sx * Sx / Sn) + Sn / 12
          Mxx = Syy - (Sy * Sy / Sn) + Sn / 12
          Mxy = Sxy - (Sx * Sy / Sn)
          Jxy = Mxx + Mxy
          
          # determine how far the minor axis is from the horizontal 
          if Mxy == 0:
            Theta = 0
          else:
            Theta = np.arctan((Mxx - Myy + np.sqrt((Mxx - Myy)**2 + 4 * (Mxy)**2)) / (2 * Mxy)) * 180 / np.pi
          rot2 = Theta * np.pi /180
          
          # determine second moment of area around the principal axes
          Imin = (Mxx + Myy) / 2 + np.sqrt(((Mxx - Myy) / 2)**2 + Mxy * Mxy)
          Imax = (Mxx + Myy) / 2 - np.sqrt(((Mxx - Myy) / 2)**2 + Mxy * Mxy)
          # determine polar moment of area around the principal axes
          Jz = Imin + Imax
          
          
          # determine the max distance from each principal axis
          Rmax = 0
          Rmin = 0
          for i in range(Sn):
            Rmax = max(Rmax, abs((coords_Ijk[1][i]-Cy)*np.cos(rot2) - (coords_Ijk[0][i]-Cx)*np.sin(rot2)))
            Rmin = max(Rmin, abs((coords_Ijk[0][i]-Cx)*np.cos(rot2) + (coords_Ijk[1][i]-Cy)*np.sin(rot2)))
          
          # section moduli around principal axes
          Zmax = Imax / Rmax
          Zmin = Imin / Rmin

            
          if OrientationcheckBox == True: 
            xCosTheta = 0
            yCosTheta = 0 
            xSinTheta = 0
            ySinTheta = 0
            sxss = 0
            sys = 0
            sxxs = 0
            syys = 0
            sxys = 0

            xCosTheta = coords_Ijk[0] * np.cos(angle)
            yCosTheta = coords_Ijk[1] * np.cos(angle)
            xSinTheta = coords_Ijk[0] * np.sin(angle)
            ySinTheta = coords_Ijk[1] * np.sin(angle)
            sxss = sum(xCosTheta + ySinTheta)
            sys = sum(yCosTheta - xSinTheta)
            sxxs = sum((xCosTheta + ySinTheta) * (xCosTheta + ySinTheta))
            syys = sum((yCosTheta - xSinTheta) * (yCosTheta - xSinTheta))
            sxys = sum((yCosTheta - xSinTheta) * (xCosTheta + ySinTheta))
            pixelMoments = Sn * (np.cos(angle) * np.cos(angle) + np.sin(angle) * np.sin(angle)) / 12  
          
            Ifa = sxxs - (sxss * sxss / Sn) + Sn/12        
            Ina = syys - (sys * sys / Sn) + Sn/12
            Jxy = Ina + Ifa  
          
            # max distance from the user defined neutral axis and axis perpendicular to that 
            rot3 = angle * np.pi / 180
            maxRadna = 0
            maxRadfa = 0
            for i in range(Sn):
              maxRadna = max(maxRadna, abs((coords_Ijk[1][i]-Cy)*np.cos(rot3) - (coords_Ijk[0][i]-Cx)*np.sin(rot3)))
              maxRadfa = max(maxRadfa, abs((coords_Ijk[0][i]-Cx)*np.cos(rot3) + (coords_Ijk[1][i]-Cy)*np.sin(rot3)))
            
          
            # section moduli around horizontal and vertical axes
            Zna = Ina / maxRadna
            Zfa = Ifa / maxRadfa

            
            # add values to orientation calculations          
            RnaArray.InsertNextValue(np.around(maxRadna * lengthofPixelMm,3))
            RfaArray.InsertNextValue(np.around(maxRadfa * lengthofPixelMm,3))
            IfaArray.InsertNextValue(np.around(Ifa * unitOfPixelMm4,3))
            InaArray.InsertNextValue(np.around(Ina * unitOfPixelMm4,3))
            JxyArray.InsertNextValue(np.around(Jxy * unitOfPixelMm4,3))        
            ZnaArray.InsertNextValue(np.around(Zna * volOfPixelMm3,3))
            ZfaArray.InsertNextValue(np.around(Zfa * volOfPixelMm3,3))
            
            # do Doube size correction
            if DoubecheckBox == True:
              InaArray_Doube.InsertNextValue(np.around(Ina**(1/4) / numSlices,3))
              IfaArray_Doube.InsertNextValue(np.around(Ifa**(1/4) / numSlices,3))
              JxyArray_Doube.InsertNextValue(np.around(Jxy**(1/4) / numSlices,3))
              ZnaArray_Doube.InsertNextValue(np.around(Zna**(1/3) / numSlices,3))
              ZfaArray_Doube.InsertNextValue(np.around(Zfa**(1/3) / numSlices,3))
              
            if SummerscheckBox == True:
              InaArray_Summers.InsertNextValue(np.around(Ina*unitOfPixelMm4/((np.pi * (np.sqrt(CSA*areaOfPixelMm2/np.pi))**4) / 4),3))
          
              IfaArray_Summers.InsertNextValue(np.around(Ifa*unitOfPixelMm4/((np.pi * (np.sqrt(CSA*areaOfPixelMm2/np.pi))**4) / 4),3))
          
          
          # add computed values to the arrays
          LengthArray.InsertNextValue(np.around(numSlices * lengthofPixelMm,3))
          
          areaArray.InsertNextValue(np.around(CSA * areaOfPixelMm2,3))
          
          if volumeNode != None and IntensitycheckBox == True:
            meanIntensityArray.InsertNextValue(np.around(meanIntensity,3))
          
          CxArray.InsertNextValue(np.around(Cx * spacing[2],3))
          CyArray.InsertNextValue(np.around(Cy * spacing[1],3))
          
          ThetaArray.InsertNextValue(np.around(rot2,3))
          
          RmaxArray.InsertNextValue(np.around(Rmax * lengthofPixelMm,3))
          RminArray.InsertNextValue(np.around(Rmin * lengthofPixelMm,3))
          
          ImaxArray.InsertNextValue(np.around(Imax * unitOfPixelMm4,3))
          IminArray.InsertNextValue(np.around(Imin * unitOfPixelMm4,3))
          JzArray.InsertNextValue(np.around(Jz * unitOfPixelMm4,3))
          
          if SummerscheckBox == True:
            ImaxArray_Summers.InsertNextValue(np.around(Imax/((np.pi * (np.sqrt(CSA/np.pi))**4) / 4),3))
            IminArray_Summers.InsertNextValue(np.around(Imin/((np.pi * (np.sqrt(CSA/np.pi))**4) / 4),3))
          
          ZmaxArray.InsertNextValue(np.around(Zmax * volOfPixelMm3,3))
          ZminArray.InsertNextValue(np.around(Zmin * volOfPixelMm3,3))
            
          # do Doube size correction
          if DoubecheckBox == True:
            areaArray_Doube.InsertNextValue(np.around(np.sqrt(CSA) / numSlices,3))
            ImaxArray_Doube.InsertNextValue(np.around(Imax**(1/4) / numSlices,3))
            IminArray_Doube.InsertNextValue(np.around(Imin**(1/4) / numSlices,3))
            JzArray_Doube.InsertNextValue(np.around(Jz**(1/4) / numSlices,3))
            ZmaxArray_Doube.InsertNextValue(np.around(Zmax**(1/3) / numSlices,3))
            ZminArray_Doube.InsertNextValue(np.around(Zmin**(1/3) / numSlices,3))
        
      # adds table column for various arrays
      table.AddColumn(SegmentNameArray)
      tableNode.SetColumnDescription(SegmentNameArray.GetName(), "Segment name")  
      
      #table.AddColumn(sliceNumberArray)
      #tableNode.SetColumnDescription(sliceNumberArray.GetName(), "Index of " + axis)
      
      tableNode.AddColumn(percentLengthArray)
      tableNode.SetColumnUnitLabel(percentLengthArray.GetName(), "%")  # TODO: use length unit
      tableNode.SetColumnDescription(percentLengthArray.GetName(), "Percent of the segment length along the the user-defined axis")  
      
      if LengthcheckBox == True:
        tableNode.AddColumn(LengthArray)
        tableNode.SetColumnUnitLabel(LengthArray.GetName(), "mm")  # TODO: use length unit
        tableNode.SetColumnDescription(LengthArray.GetName(), "Segment Length")  
      
      if CSAcheckBox == True:    
        tableNode.AddColumn(areaArray)
        tableNode.SetColumnUnitLabel(areaArray.GetName(), "mm2")  # TODO: use length unit
        tableNode.SetColumnDescription(areaArray.GetName(), "Cross-sectional area")  
      
      if volumeNode != None and IntensitycheckBox == True:
        tableNode.AddColumn(meanIntensityArray)
      
      if CentroidcheckBox == True:
        tableNode.AddColumn(CxArray)
        tableNode.SetColumnUnitLabel(areaArray.GetName(), "mm")  # TODO: use length unit
        tableNode.SetColumnDescription(areaArray.GetName(), "X-coordinate of the centroid")  
      
        tableNode.AddColumn(CyArray)
        tableNode.SetColumnUnitLabel(areaArray.GetName(), "mm")  # TODO: use length unit
        tableNode.SetColumnDescription(areaArray.GetName(), "Y-coordinate of the centroid")  
        
      if ThetacheckBox == True:    
        tableNode.AddColumn(ThetaArray)
        tableNode.SetColumnUnitLabel(ThetaArray.GetName(), "rad")  # TODO: use length unit
        tableNode.SetColumnDescription(ThetaArray.GetName(), "Angle of the principal axis")
      
      if RcheckBox == True and (MODcheckBox_1 == True or SMAcheckBox_1 == True) == True:  
        tableNode.AddColumn(RmaxArray)
        tableNode.SetColumnUnitLabel(RmaxArray.GetName(), "mm")  # TODO: use length unit
        tableNode.SetColumnDescription(RmaxArray.GetName(), "Max chord length from the major principal axis") 
      
        tableNode.AddColumn(RminArray)
        tableNode.SetColumnUnitLabel(RminArray.GetName(), "mm")  # TODO: use length unit
        tableNode.SetColumnDescription(RminArray.GetName(), "Max chord length from the minor principal axis") 
       
      if SMAcheckBox_1 == True:  
        tableNode.AddColumn(ImaxArray)
        tableNode.SetColumnUnitLabel(ImaxArray.GetName(), "mm4")  # TODO: use length unit
        tableNode.SetColumnDescription(ImaxArray.GetName(), "Second moment of area around the major principal axis (smaller I)")
        
        tableNode.AddColumn(IminArray)
        tableNode.SetColumnUnitLabel(IminArray.GetName(), "mm4")  # TODO: use length unit
        tableNode.SetColumnDescription(IminArray.GetName(), "Second moment of area around the minor principal axis (larger I)")

      if MODcheckBox_1 == True:
        tableNode.AddColumn(ZmaxArray)
        tableNode.SetColumnUnitLabel(ZmaxArray.GetName(), "mm3")  # TODO: use length unit
        tableNode.SetColumnDescription(ZmaxArray.GetName(), "Section modulus around the major principal axis")
        
        tableNode.AddColumn(ZminArray)
        tableNode.SetColumnUnitLabel(ZminArray.GetName(), "mm3")  # TODO: use length unit
        tableNode.SetColumnDescription(ZminArray.GetName(), "Section modulus around the minor principal axis")
         
      if PolarcheckBox_1 == True:     
        tableNode.AddColumn(JzArray)
        tableNode.SetColumnUnitLabel(JzArray.GetName(), "mm4")  # TODO: use length unit
        tableNode.SetColumnDescription(JzArray.GetName(), "Polar moment of inertia around the principal axes")
        
      if RcheckBox == True and OrientationcheckBox == True and (SMAcheckBox_2 == True or MODcheckBox_2 == True):
        tableNode.AddColumn(RnaArray)
        tableNode.SetColumnUnitLabel(RnaArray.GetName(), "mm")  # TODO: use length unit
        tableNode.SetColumnDescription(RnaArray.GetName(), "Max chord length from the neutral axis") 
      
        tableNode.AddColumn(RfaArray)
        tableNode.SetColumnUnitLabel(RfaArray.GetName(), "mm")  # TODO: use length unit
        tableNode.SetColumnDescription(RfaArray.GetName(), "Max chord length from the force axis") 
      
      if OrientationcheckBox == True and SMAcheckBox_2 == True:  
        tableNode.AddColumn(InaArray)
        tableNode.SetColumnUnitLabel(InaArray.GetName(), "mm4")  # TODO: use length unit
        tableNode.SetColumnDescription(InaArray.GetName(), "Second moment of area around the neutral axis")
        
        tableNode.AddColumn(IfaArray)
        tableNode.SetColumnUnitLabel(IfaArray.GetName(), "mm4")  # TODO: use length unit
        tableNode.SetColumnDescription(IfaArray.GetName(), "Second moment of area around the force axis")
        
      if OrientationcheckBox == True and MODcheckBox_2 == True:
        tableNode.AddColumn(ZnaArray)
        tableNode.SetColumnUnitLabel(ZnaArray.GetName(), "mm3")  # TODO: use length unit
        tableNode.SetColumnDescription(ZnaArray.GetName(), "Section modulus around the neutral axis")
        
        tableNode.AddColumn(ZfaArray)
        tableNode.SetColumnUnitLabel(ZfaArray.GetName(), "mm3")  # TODO: use length unit
        tableNode.SetColumnDescription(ZfaArray.GetName(), "Section modulus around the force axis")
              
      if OrientationcheckBox == True and PolarcheckBox_2 == True:  
        tableNode.AddColumn(JxyArray)
        tableNode.SetColumnUnitLabel(JxyArray.GetName(), "mm4")  # TODO: use length unit
        tableNode.SetColumnDescription(JxyArray.GetName(), "Polar moment of inertia around the neutral and force axes")
        
      if DoubecheckBox == True and CSAcheckBox == True:
        tableNode.AddColumn(areaArray_Doube)
        tableNode.SetColumnUnitLabel(areaArray_Doube.GetName(), "none")  # TODO: use length unit
        tableNode.SetColumnDescription(areaArray_Doube.GetName(), "CSA^(1/2)/Length")
       
      if DoubecheckBox == True and SMAcheckBox_1 == True:
        tableNode.AddColumn(ImaxArray_Doube)
        tableNode.SetColumnUnitLabel(ImaxArray_Doube.GetName(), "none")  # TODO: use length unit
        tableNode.SetColumnDescription(ImaxArray_Doube.GetName(), "Imax^(1/4)/Length")
        
        tableNode.AddColumn(IminArray_Doube)
        tableNode.SetColumnUnitLabel(IminArray_Doube.GetName(), "none")  # TODO: use length unit
        tableNode.SetColumnDescription(IminArray_Doube.GetName(), "Imin^(1/4)/Length")
        
      if DoubecheckBox == True and PolarcheckBox_1 == True:
        tableNode.AddColumn(JzArray_Doube)
        tableNode.SetColumnUnitLabel(JzArray_Doube.GetName(), "none")  # TODO: use length unit
        tableNode.SetColumnDescription(JzArray_Doube.GetName(), "Jmax+min^(1/4)/Length")
        
      if DoubecheckBox == True and MODcheckBox_1 == True:
        tableNode.AddColumn(ZmaxArray_Doube)
        tableNode.SetColumnUnitLabel(ZmaxArray_Doube.GetName(), "none")  # TODO: use length unit
        tableNode.SetColumnDescription(ZmaxArray_Doube.GetName(), "Zmax^(1/3)/Length")
        
        tableNode.AddColumn(ZminArray_Doube)
        tableNode.SetColumnUnitLabel(ZminArray_Doube.GetName(), "none")  # TODO: use length unit
        tableNode.SetColumnDescription(ZminArray_Doube.GetName(), "Zmin^(1/3)/Length") 
        
      if DoubecheckBox == True and SMAcheckBox_2 == True and OrientationcheckBox == True:
        tableNode.AddColumn(InaArray_Doube)
        tableNode.SetColumnUnitLabel(InaArray_Doube.GetName(), "none")  # TODO: use length unit
        tableNode.SetColumnDescription(InaArray_Doube.GetName(), "Ina^(1/4)/Length")
        
        tableNode.AddColumn(IfaArray_Doube)
        tableNode.SetColumnUnitLabel(IfaArray_Doube.GetName(), "none")  # TODO: use length unit
        tableNode.SetColumnDescription(IfaArray_Doube.GetName(), "Ifa^(1/4)/Length")
        
      if DoubecheckBox == True and PolarcheckBox_2 == True and OrientationcheckBox == True:
        tableNode.AddColumn(JxyArray_Doube)
        tableNode.SetColumnUnitLabel(JxyArray_Doube.GetName(), "none")  # TODO: use length unit
        tableNode.SetColumnDescription(JxyArray_Doube.GetName(), "Jna+fa^(1/4)/Length")
        
      if DoubecheckBox == True and MODcheckBox_2 == True and OrientationcheckBox == True:
        tableNode.AddColumn(ZnaArray_Doube)
        tableNode.SetColumnUnitLabel(ZnaArray_Doube.GetName(), "none")  # TODO: use length unit
        tableNode.SetColumnDescription(ZnaArray_Doube.GetName(), "Zna^(1/3)/Length")
        
        tableNode.AddColumn(ZfaArray_Doube)
        tableNode.SetColumnUnitLabel(ZfaArray_Doube.GetName(), "none")  # TODO: use length unit
        tableNode.SetColumnDescription(ZfaArray_Doube.GetName(), "Zfa^(1/3)/Length")  
        
      if SummerscheckBox == True and SMAcheckBox_1 == True:
        tableNode.AddColumn(ImaxArray_Summers)
        tableNode.SetColumnUnitLabel(ImaxArray_Summers.GetName(), "none")  # TODO: use length unit
        tableNode.SetColumnDescription(ImaxArray_Summers.GetName(), "Imax divided by the second moment of area of a circle with the same cross-sectional area")
        
        tableNode.AddColumn(IminArray_Summers)
        tableNode.SetColumnUnitLabel(IminArray_Summers.GetName(), "none")  # TODO: use length unit
        tableNode.SetColumnDescription(IminArray_Summers.GetName(), "Imin divided by the second moment of area of a circle with the same cross-sectional area") 
        
        
      if SummerscheckBox == True and SMAcheckBox_2 == True and OrientationcheckBox == True:
        tableNode.AddColumn(InaArray_Summers)
        tableNode.SetColumnUnitLabel(InaArray_Summers.GetName(), "none")  # TODO: use length unit
        tableNode.SetColumnDescription(InaArray_Summers.GetName(), "Ina divided by the second moment of area of a circle with the same cross-sectional area")
        
        tableNode.AddColumn(IfaArray_Summers)
        tableNode.SetColumnUnitLabel(IfaArray_Summers.GetName(), "none")  # TODO: use length unit
        tableNode.SetColumnDescription(IfaArray_Summers.GetName(), "Ifa divided by the second moment of area of a circle with the same cross-sectional area") 
      
      # Make a plot series node for this column.
      plotSeriesNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotSeriesNode", "Geometry")
      plotSeriesNode.SetPlotType(plotSeriesNode.PlotTypeScatter)
      plotSeriesNode.SetAndObserveTableNodeID(tableNode.GetID())
      plotSeriesNode.SetXColumnName("Percent (%)")
      #plotChartNode.SetXAxisTitle("Percent of Length")
      if OrientationcheckBox == True and SMAcheckBox_2 == True: 
        plotSeriesNode.SetYColumnName("Ina (mm^4)")
        plotChartNode.SetYAxisTitle('Neutral Axis Second Moment of Area (mm^4)')
      else: 
        plotSeriesNode.SetYColumnName("Imin (mm^4)")
        plotChartNode.SetYAxisTitle('Minor Axis Second Moment of Area (mm^4)')
      plotSeriesNode.SetUniqueColor()

      # Add this series to the plot chart node created above.
      plotChartNode.AddAndObservePlotSeriesNodeID(plotSeriesNode.GetID())
    
    finally:
      # Remove temporary volume node
      slicer.mrmlScene.RemoveNode(tempSegmentLabelmapVolumeNode)
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

class SegmentCrossSectionAreaTest(ScriptedLoadableModuleTest):
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
    self.test_SegmentCrossSectionArea1()

  def test_SegmentCrossSectionArea1(self):
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
    masterVolumeNode = sampleDataLogic.downloadMRBrainTumor1()

    # Create segmentation
    segmentationNode = slicer.vtkMRMLSegmentationNode()
    slicer.mrmlScene.AddNode(segmentationNode)
    segmentationNode.CreateDefaultDisplayNodes()  # only needed for display
    segmentationNode.SetReferenceImageGeometryParameterFromVolumeNode(masterVolumeNode)

    # Create a sphere shaped segment
    radius = 20
    tumorSeed = vtk.vtkSphereSource()
    tumorSeed.SetCenter(-6, 30, 28)
    tumorSeed.SetRadius(radius)
    tumorSeed.SetPhiResolution(120)
    tumorSeed.SetThetaResolution(120)
    tumorSeed.Update()
    segmentId = segmentationNode.AddSegmentFromClosedSurfaceRepresentation(tumorSeed.GetOutput(), "Tumor",
                                                                           [1.0, 0.0, 0.0])

    tableNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTableNode", "Slice Geometry table")
    plotChartNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotChartNode", "Slice Geometry plot")

    logic = SegmentCrossSectionAreaLogic()
    logic.run(segmentationNode, masterVolumeNode, "slice", tableNode, plotChartNode)
    logic.showChart(plotChartNode)

    self.assertEqual(tableNode.GetNumberOfColumns(), 3)
    self.assertEqual(tableNode.GetNumberOfColumns(), 3)

    # Compute error
    crossSectionAreas = slicer.util.arrayFromTableColumn(tableNode, "Tumor")
    largestCrossSectionArea = crossSectionAreas.max()
    import math
    expectedlargestCrossSectionArea = radius*radius*math.pi
    logging.info("Largest cross-section area: {0:.2f}".format(largestCrossSectionArea))
    logging.info("Expected largest cross-section area: {0:.2f}".format(expectedlargestCrossSectionArea))
    errorPercent = 100.0 * abs(largestCrossSectionArea - expectedlargestCrossSectionArea) < expectedlargestCrossSectionArea
    logging.info("Largest cross-section area error: {0:.2f}%".format(errorPercent))

    # Error between expected and actual cross section is due to finite resolution of the segmentation.
    # It should not be more than a few percent. The actual error in this case is around 1%, but use 2% to account for
    # numerical differences between different platforms.
    self.assertTrue(errorPercent < 2.0)

    self.delayDisplay('Test passed')
