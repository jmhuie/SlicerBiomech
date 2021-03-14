import os
import unittest
import logging
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin

#
# SegmentCrossSectionArea
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
    self.ui.axisSelectorBox.connect("currentIndexChanged(int)", self.updateParameterNodeFromGUI)
    self.ui.tableSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)

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

    wasBlocked = self.ui.axisSelectorBox.blockSignals(True)
    self.ui.axisSelectorBox.currentText = self._parameterNode.GetParameter("Axis")
    self.ui.axisSelectorBox.blockSignals(wasBlocked)

    wasBlocked = self.ui.tableSelector.blockSignals(True)
    self.ui.tableSelector.setCurrentNode(self._parameterNode.GetNodeReference("ResultsTable"))
    self.ui.tableSelector.blockSignals(wasBlocked)

    # Update buttons states and tooltips
    if self._parameterNode.GetNodeReference("Segmentation"):
      self.ui.applyButton.toolTip = "Compute slice geometries"
      self.ui.applyButton.enabled = True
    else:
      self.ui.applyButton.toolTip = "Select input segmentation node"
      self.ui.applyButton.enabled = False

  def updateParameterNodeFromGUI(self, caller=None, event=None):
    """
    This method is called when the user makes any change in the GUI.
    The changes are saved into the parameter node (so that they are restored when the scene is saved and loaded).
    """

    if self._parameterNode is None:
      return

    self._parameterNode.SetNodeReferenceID("Segmentation", self.ui.segmentationSelector.currentNodeID)
    self._parameterNode.SetParameter("Axis", self.ui.axisSelectorBox.currentText)

    self._parameterNode.SetNodeReferenceID("ResultsTable", self.ui.tableSelector.currentNodeID)

  def onApplyButton(self):
    """
    Run processing when user clicks "Apply" button.
    """
    try:

      # Create nodes for results
      tableNode = self.ui.tableSelector.currentNode()
      if not tableNode:
        tableNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTableNode", "Slice Geometry table")
        self.ui.tableSelector.setCurrentNode(tableNode)

      self.logic.run(self.ui.segmentationSelector.currentNode(), self.ui.axisSelectorBox.currentText,
                     tableNode)

    except Exception as e:
      slicer.util.errorDisplay("Failed to compute results: "+str(e))
      import traceback
      traceback.print_exc()

  def onShowTableButton(self):
    tableNode = self.ui.tableSelector.currentNode()
    if not tableNode:
      self.onApplyButton()
    tableNode = self.ui.tableSelector.currentNode()
    if tableNode:
      self.logic.showTable(tableNode)


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

  def run(self, segmentationNode, axis, tableNode):
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

    #
    # Make a table and set the first column as the slice number. This is used
    # as the X axis for plots.
    #
    tableNode.RemoveAllColumns()
    table = tableNode.GetTable()

    #
    # For each segment, get the area and put it in the table in a new column.
    #
    try:
      # Create temporary volume node
      tempSegmentLabelmapVolumeNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLLabelMapVolumeNode', "SegmentCrossSectionAreaTemp")

      for segmentIndex in range(visibleSegmentIds.GetNumberOfValues()):
        segmentID = visibleSegmentIds.GetValue(segmentIndex)
        
        segment = segmentationNode.GetSegmentation().GetSegment(segmentID)
        segName = segment.GetName()

        segmentList = vtk.vtkStringArray()
        segmentList.InsertNextValue(segmentID)
        if not slicer.modules.segmentations.logic().ExportSegmentsToLabelmapNode(segmentationNode, segmentList, tempSegmentLabelmapVolumeNode):
          continue

        if segmentIndex == 0:
          segmentname = segmentationNode.GetSegmentation().GetNthSegmentID(0)
			
		  # volumeExtents so first and last number of images in XYZ directions. Starts with 0 not 1	
          volumeExtents = tempSegmentLabelmapVolumeNode.GetImageData().GetExtent()
          numSlices = volumeExtents[axisIndex*2+1] - volumeExtents[axisIndex*2] + 1
          
          resample = 19
          if resample > 0:
            sampleSlices = np.linspace(0,numSlices,num = resample+1, endpoint = False)
            sampleSlices = np.rint(sampleSlices)
            sampleSlices = sampleSlices.astype(int)
            sampleSlices = sampleSlices[1:]
            percentLength = np.around(sampleSlices / numSlices * 100,0)
          
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
          transformVolumeRasToRas = vtk.vtkGeneralTransform()
          slicer.vtkMRMLTransformNode.GetTransformBetweenNodes(tempSegmentLabelmapVolumeNode.GetParentTransformNode(), None, transformVolumeRasToRas)

		  # creates	array for the slice number
          sliceNumberArray = vtk.vtkIntArray()
          sliceNumberArray.SetName("Slice")
          
          SegmentNameArray = vtk.vtkStringArray()
          SegmentNameArray.SetName("Segment")
          
          percentLengthArray = vtk.vtkFloatArray()
          percentLengthArray.SetName("Percent (%)")
          

          if resample > 0:
            for i in range(resample):
              sliceNumberArray.InsertNextValue(i + 1) # adds slice number to the array
              SegmentNameArray.InsertNextValue(segName)
              percentLengthArray.InsertNextValue(percentLength[i])
              
          else:
            for i in range(numSlices):
              sliceNumberArray.InsertNextValue(i + 1) # adds slice number to the array
              SegmentNameArray.InsertNextValue(segName)
            
		  
		  # adds table column for slice number
          table.AddColumn(sliceNumberArray)
          tableNode.SetColumnDescription(sliceNumberArray.GetName(), "Index of " + axis)
          
          table.AddColumn(SegmentNameArray)
          tableNode.SetColumnDescription(SegmentNameArray.GetName(), "Segment name")



        ###### SET UP CALC ARRAYS ######
        narray = slicer.util.arrayFromVolume(tempSegmentLabelmapVolumeNode)
        
        #create array for segment length
        LengthArray = vtk.vtkFloatArray()
        LengthArray.SetName("Length (mm)")
        
        # creates array for CSA and names based the same as the segment 
        areaArray = vtk.vtkFloatArray()
        areaArray.SetName("CSA mm^2")
        
        #create array for Ix or technically Ii because IJK coord system
        IxxArray = vtk.vtkFloatArray()
        IxxArray.SetName("Ix (mm^4)")
        
        #create array for Iy or technically Ij because IJK coord system
        IyyArray = vtk.vtkFloatArray()
        IyyArray.SetName("Iy (mm^4)")
        
        ThetaArray = vtk.vtkFloatArray()
        ThetaArray.SetName("Theta (rad)")
        
        ImaxArray = vtk.vtkFloatArray()
        ImaxArray.SetName("Imax (mm^4)")
        
        IminArray = vtk.vtkFloatArray()
        IminArray.SetName("Imin (mm^4)")
        
        R1Array = vtk.vtkFloatArray()
        R1Array.SetName("R1 (mm)")
        
        R2Array = vtk.vtkFloatArray()
        R2Array.SetName("R2 (mm)")
        
        ZmaxArray = vtk.vtkFloatArray()
        ZmaxArray.SetName("Zmax (mm^3)")
        
        ZminArray = vtk.vtkFloatArray()
        ZminArray.SetName("Zmin (mm^3)")
        
        ZxxArray = vtk.vtkFloatArray()
        ZxxArray.SetName("Zx (mm^3)")
        
        ZyyArray = vtk.vtkFloatArray()
        ZyyArray.SetName("Zy (mm^3)")
        
        ###### SET UP UNITS ######
        
        # Convert number of voxels to area in mm2
        spacing = tempSegmentLabelmapVolumeNode.GetSpacing()
        areaOfPixelMm2 = spacing[0] * spacing[1] * spacing[2] / spacing[axisIndex]
        
        volOfPixelMm3 = spacing[0] * spacing[1] * spacing[2]
        
        # Convert number of voxels to a unit of mm4
        unitOfPixelMm4 = spacing[0]**2 * (spacing[1]**2) * spacing[2]**2 / spacing[axisIndex]**2
        
        
        ###### DO CALCULATIONS ######
        
        for i in sampleSlices:
          if axisIndex == 0:
          	lengthofPixelMm = spacing[1] # get mm for length
          	slicetemp = narray[:, :, i] # get the ijk coordinates for all voxels in the label map
          	areaBySliceInVoxels = np.count_nonzero(narray[:,:,i])
          elif axisIndex == 1:
          	lengthofPixelMm = spacing[2] # get mm for length
          	slicetemp = narray[:, i, :] # get the ijk coordinates for all voxels in the label map     
          	areaBySliceInVoxels = np.count_nonzero(narray[:, i, :])
          elif axisIndex == 2:
          	lengthofPixelMm = spacing[0] # get mm for length
          	slicetemp = narray[i, :, :] # get the ijk coordinates for all voxels in the label map
          	areaBySliceInVoxels = np.count_nonzero(narray[i, :, :]) 
            
          coords_Kji = np.where(slicetemp > 0)
          coords_Ijk = [coords_Kji[1], coords_Kji[0]]
            
          # set up variables
          Sn = np.count_nonzero(slicetemp)
          Sx = sum(coords_Ijk[0])
          Sxx = sum(coords_Ijk[0] * coords_Ijk[0])
          Sy = sum(coords_Ijk[1])
          Syy = sum(coords_Ijk[1] * coords_Ijk[1])
          Sxy = sum(coords_Ijk[0] * coords_Ijk[1])
            
          if Sn > 0:
            # centroid coordinates
            Cx = Sx / Sn
            Cy = Sy / Sn
            
          #calculate second moment of area along x and y
          Myy = Sxx - (Sx * Sx / Sn) + Sn / 12
          Mxx = Syy - (Sy * Sy / Sn) + Sn / 12
          Mxy = Sxy - (Sx * Sy / Sn)
          
          
          if Mxy == 0:
            Theta = 0
          else:
            Theta = np.arctan((Mxx - Myy + np.sqrt((Mxx - Myy)**2 + 4 * (Mxy)**2)) / (2 * Mxy)) * 180 / np.pi
          rot2 = Theta * np.pi /180
          
          Imin = (Mxx + Myy) / 2 + np.sqrt(((Mxx - Myy) / 2)**2 + Mxy * Mxy)
          Imax = (Mxx + Myy) / 2 - np.sqrt(((Mxx - Myy) / 2)**2 + Mxy * Mxy)
          
          
          maxRadMax = 0
          maxRadMin = 0
          for i in range(Sn):
            maxRadMin = max(maxRadMin, abs((coords_Ijk[0][i]-Cx)*np.cos(rot2) + (coords_Ijk[1][i]-Cy)*np.sin(rot2)))
            maxRadMax = max(maxRadMax, abs((coords_Ijk[1][i]-Cy)*np.cos(rot2) - (coords_Ijk[0][i]-Cx)*np.sin(rot2)))
          
          Zmax = Imax / maxRadMax
          Zmin = Imin / maxRadMin
          
          
          rot3 = 270 * np.pi / 180
          maxRad1 = 0
          maxRad2 = 0
          for i in range(Sn):
            maxRad2 = max(maxRad2, abs((coords_Ijk[0][i]-Cx)*np.cos(rot3) + (coords_Ijk[1][i]-Cy)*np.sin(rot3)))
            maxRad1 = max(maxRad1, abs((coords_Ijk[1][i]-Cy)*np.cos(rot3) - (coords_Ijk[0][i]-Cx)*np.sin(rot3)))
          
          
          Zxx = Mxx / maxRad2
          Zyy = Myy / maxRad1
          
          
          LengthArray.InsertNextValue(np.around(numSlices * lengthofPixelMm,3))
          
          areaArray.InsertNextValue(np.around(areaBySliceInVoxels * areaOfPixelMm2,3))
          
          IxxArray.InsertNextValue(np.around(Mxx * unitOfPixelMm4,3))
          IyyArray.InsertNextValue(np.around(Myy * unitOfPixelMm4,3))
          
          ThetaArray.InsertNextValue(np.around(rot2,3))
          
          ImaxArray.InsertNextValue(np.around(Imax * unitOfPixelMm4,3))
          IminArray.InsertNextValue(np.around(Imin * unitOfPixelMm4,3))
          
          R1Array.InsertNextValue(np.around(maxRadMax * lengthofPixelMm,3))
          R2Array.InsertNextValue(np.around(maxRadMin * lengthofPixelMm,3))
          
          ZmaxArray.InsertNextValue(np.around(Zmax * volOfPixelMm3,3))
          ZminArray.InsertNextValue(np.around(Zmin * volOfPixelMm3,3))
          
          ZxxArray.InsertNextValue(np.around(Zxx * volOfPixelMm3,3))
          ZyyArray.InsertNextValue(np.around(Zyy * volOfPixelMm3,3))
          
        
        tableNode.AddColumn(LengthArray)
        tableNode.SetColumnUnitLabel(LengthArray.GetName(), "mm")  # TODO: use length unit
        tableNode.SetColumnDescription(LengthArray.GetName(), "Segment Length")  
        
        tableNode.AddColumn(percentLengthArray)
        tableNode.SetColumnUnitLabel(percentLengthArray.GetName(), "%")  # TODO: use length unit
        tableNode.SetColumnDescription(percentLengthArray.GetName(), "Percent of length along the segment")  
          
        tableNode.AddColumn(areaArray)
        tableNode.SetColumnUnitLabel(areaArray.GetName(), "mm2")  # TODO: use length unit
        tableNode.SetColumnDescription(areaArray.GetName(), "Cross-sectional area")  
        
        tableNode.AddColumn(ThetaArray)
        tableNode.SetColumnUnitLabel(ThetaArray.GetName(), "rad")  # TODO: use length unit
        tableNode.SetColumnDescription(ThetaArray.GetName(), "Angle of the principal axes")
        
        tableNode.AddColumn(R1Array)
        tableNode.SetColumnUnitLabel(R1Array.GetName(), "mm")  # TODO: use length unit
        tableNode.SetColumnDescription(R1Array.GetName(), "length of the minor axis") 
        
        tableNode.AddColumn(R2Array)
        tableNode.SetColumnUnitLabel(R2Array.GetName(), "mm")  # TODO: use length unit
        tableNode.SetColumnDescription(R2Array.GetName(), "length of the major axis") 
        
        tableNode.AddColumn(IminArray)
        tableNode.SetColumnUnitLabel(IminArray.GetName(), "mm4")  # TODO: use length unit
        tableNode.SetColumnDescription(IminArray.GetName(), "Second moment of area around the minor principal axis (larger I)")
        
        tableNode.AddColumn(ImaxArray)
        tableNode.SetColumnUnitLabel(ImaxArray.GetName(), "mm4")  # TODO: use length unit
        tableNode.SetColumnDescription(ImaxArray.GetName(), "Second moment of area around the major principal axis (smaller I)")
         
        tableNode.AddColumn(ZminArray)
        tableNode.SetColumnUnitLabel(ZminArray.GetName(), "mm3")  # TODO: use length unit
        tableNode.SetColumnDescription(ZminArray.GetName(), "Section modulus around the minor principal axis")
        
        tableNode.AddColumn(ZmaxArray)
        tableNode.SetColumnUnitLabel(ZmaxArray.GetName(), "mm3")  # TODO: use length unit
        tableNode.SetColumnDescription(ZmaxArray.GetName(), "Section modulus around the major principal axis")
        
        tableNode.AddColumn(IxxArray)
        tableNode.SetColumnUnitLabel(IxxArray.GetName(), "mm4")  # TODO: use length unit
        tableNode.SetColumnDescription(IxxArray.GetName(), "Second moment of area around the X axis")
        
        tableNode.AddColumn(IyyArray)
        tableNode.SetColumnUnitLabel(IyyArray.GetName(), "mm4")  # TODO: use length unit
        tableNode.SetColumnDescription(IyyArray.GetName(), "Second moment of area around the Y axis")
        
        tableNode.AddColumn(ZxxArray)
        tableNode.SetColumnUnitLabel(ZxxArray.GetName(), "mm3")  # TODO: use length unit
        tableNode.SetColumnDescription(ZxxArray.GetName(), "Section modulus around the X axis")
        
        tableNode.AddColumn(ZyyArray)
        tableNode.SetColumnUnitLabel(ZyyArray.GetName(), "mm3")  # TODO: use length unit
        tableNode.SetColumnDescription(ZyyArray.GetName(), "Section modulus around the Y axis")

    
    
    finally:
      # Remove temporary volume node
      colorNode = tempSegmentLabelmapVolumeNode.GetDisplayNode().GetColorNode()
      if colorNode:
        slicer.mrmlScene.RemoveNode(colorNode)
      slicer.mrmlScene.RemoveNode(tempSegmentLabelmapVolumeNode)
      
      layoutManager = slicer.app.layoutManager()
      layoutWithPlot = slicer.modules.tables.logic().GetLayoutWithTable(layoutManager.layout)
      layoutManager.setLayout(layoutWithPlot)
      # Select chart in plot view
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
