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
    self.parent.title = "SegmentGeometry"
    self.parent.categories = ["Quantification"]
    self.parent.dependencies = []
    self.parent.contributors = ["Jonathan Huie"]
    self.parent.helpText = """This module iterates slice-by-slice through a segment to compute second moment of area and other cross-sectional properties.
    For more information please see the <a href="https://github.com/jmhuie/Slicer-SegmentGeometry">online documentation</a>."""
    self.parent.acknowledgementText = """This module was developed by Jonathan Huie, who was supported by an NSF Graduate Research Fellowship (DGE-1746914) and a George Washington University Harlan Research Fellowship."""

    # Additional initialization step after application startup is complete
    slicer.app.connect("startupCompleted()", registerSampleData)

#
# Register sample data sets in Sample Data module
#

def registerSampleData():
    """
    Add data sets to Sample Data module.
    """
    # It is always recommended to provide sample data for users to make it easy to try the module,
    # but if no sample data is available then this method (and associated startupCompeted signal connection) can be removed.

    import SampleData
    iconsPath = os.path.join(os.path.dirname(__file__), 'Resources/Icons')

    # To ensure that the source code repository remains small (can be downloaded and installed quickly)
    # it is recommended to store data sets that are larger than a few MB in a Github release.

    
    # load demo SegmentGeometry data
    
    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        category="SegmentGeometry",
        sampleName='DemoForelimb',
        uris='https://github.com/jmhuie/Slicer-SegmentGeometry/releases/download/SampleData/Aneides_lugubris_mvz_249828_forelimbs.nrrd',
        fileNames='DemoForelimb.nrrd',
        nodeNames='DemoForelimb',
        thumbnailFileName=os.path.join(iconsPath, 'SegmentGeometryDemoForelimb.png'),
        loadFileType='VolumeFile',
        )
    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        category="SegmentGeometry",
        sampleName='DemoSegment',
        uris='https://github.com/jmhuie/Slicer-SegmentGeometry/releases/download/SampleData/Aneides_lugubris_mvz_249828_forelimbs_Segmentation.seg.nrrd',
        fileNames='DemoSegment.seg.nrrd',
        nodeNames='DemoSegment',
        thumbnailFileName=os.path.join(iconsPath, 'SegmentGeometryDemoSegment.png'),
        loadFileType='SegmentationFile',
        )

#

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
    self.ui.segmentationSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onChangeAxis)
    self.ui.regionSegmentSelector.connect("currentSegmentChanged(QString)", self.updateParameterNodeFromGUI)
    self.ui.regionSegmentSelector.connect("currentSegmentChanged(QString)", self.onChangeAxis)
    self.ui.volumeSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.axisSelectorBox.connect("currentIndexChanged(int)", self.updateParameterNodeFromGUI)
    self.ui.axisSelectorBox.connect("currentIndexChanged(int)", self.onChangeAxis)
    self.ui.resamplespinBox.connect("valueChanged(int)", self.updateParameterNodeFromGUI)
    self.ui.tableSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.chartSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.OrientationcheckBox.connect('stateChanged(int)', self.updateParameterNodeFromGUI)
    self.ui.OrientationcheckBox.connect('stateChanged(int)', self.initializeAxisLine)
    self.ui.orientationspinBox.connect("valueChanged(double)", self.updateParameterNodeFromGUI)
    self.ui.orientationspinBox.connect("valueChanged(double)", self.updateAxisLineAngle)
    self.ui.CompactnesscheckBox.connect('stateChanged(int)', self.updateParameterNodeFromGUI)
    self.ui.areaSegmentSelector.connect('currentSegmentChanged(QString)', self.updateParameterNodeFromGUI)
    self.ui.PrincipalButton.connect("clicked(bool)", self.onPrincipalAxes)
    self.ui.Interactive3DButton.connect("clicked(bool)", self.onInteractive3DBox)
    self.ui.RotatorSliders.connect("valueChanged(double)", self.initializeSliders)
    self.ui.RotationInitButton.connect("clicked(bool)", self.initializeSliders)
    self.ui.ShowAxisButton.connect("clicked(bool)", self.ShowAxis)
    self.ui.ResetButton.connect("clicked(bool)", self.ResetButton)

    
    # initialize the result label under the apply button
    self.ui.ResultsText.setStyleSheet("background: transparent; border: transparent")


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
    
    #wasBlocked = self.ui.orientationspinBox.blockSignals(True)
    #float(self.ui.orientationspinBox.value) = self._parameterNode.GetParameter("Angle")
    #self.ui.orientationspinBox.blockSignals(wasBlocked)    
    
    wasBlocked = self.ui.tableSelector.blockSignals(True)
    self.ui.tableSelector.setCurrentNode(self._parameterNode.GetNodeReference("ResultsTable"))
    self.ui.tableSelector.blockSignals(wasBlocked)
    
    wasBlocked = self.ui.chartSelector.blockSignals(True)
    self.ui.chartSelector.setCurrentNode(self._parameterNode.GetNodeReference("ResultsChart"))
    self.ui.chartSelector.blockSignals(wasBlocked)

    wasBlocked = self.ui.areaSegmentSelector.blockSignals(True)
    self.ui.areaSegmentSelector.setCurrentNode(self._parameterNode.GetNodeReference("Segmentation"))
    self.ui.areaSegmentSelector.setCurrentSegmentID(self._parameterNode.GetNodeReference("AreaSegment"))
    self.ui.areaSegmentSelector.blockSignals(wasBlocked)


    # Update buttons states and tooltips
    if self._parameterNode.GetNodeReference("Segmentation") and not self.ui.regionSegmentSelector.currentSegmentID == None and self._parameterNode.GetNodeReference("Volume"):
      self.ui.applyButton.toolTip = "Compute slice geometries"
      self.ui.applyButton.enabled = True
      self.ui.PrincipalButton.enabled = True
      self.ui.PrincipalButton.toolTip = "Align segment with the principal axes"
      self.ui.Interactive3DButton.enabled = True
      self.ui.Interactive3DButton.toolTip = "Interactively rotate segment in 3D view"
      self.ui.RotationInitButton.enabled = True
      self.ui.RotationInitButton.toolTip = "Initialize rotation sliders"
      self.ui.OrientationcheckBox.enabled = True
      self.ui.OrientationcheckBox.toolTip = "Defne and use custom neutral axis"
      self.ui.ResetButton.enabled = True
      self.ui.ResetButton.toolTip = "Reset segment transformation"
      if self.ui.CompactnesscheckBox.checked == True:
        self.ui.areaSegmentSelector.toolTip = "Select solid segment to measure total area and compactness"
        self.ui.areaSegmentSelector.enabled = True
      else: 
       self.ui.areaSegmentSelector.toolTip = "Select option to compute compactness" 
       self.ui.areaSegmentSelector.enabled = False     

      
    else:
      self.ui.applyButton.toolTip = "Select segmentation and volume nodes"
      self.ui.applyButton.enabled = False
      self.ui.PrincipalButton.enabled = False
      self.ui.PrincipalButton.toolTip = "Select segmentation and volume nodes"
      self.ui.Interactive3DButton.enabled = False
      self.ui.Interactive3DButton.toolTip = "Select segmentation and volume nodes"
      self.ui.RotationInitButton.enabled = False
      self.ui.RotationInitButton.toolTip = "Select segmentation and volume nodes"
      self.ui.OrientationcheckBox.enabled = False
      self.ui.OrientationcheckBox.toolTip = "Select segmentation and volume nodes"
      self.ui.ResetButton.enabled = False
      self.ui.ResetButton.toolTip = "Select segmentation and volume nodes"

    
    if self._parameterNode.GetNodeReference("Segmentation"):
      self.ui.regionSegmentSelector.toolTip = "Select segment"
    else:
      self.ui.regionSegmentSelector.toolTip = "Select input segmentation node"  
  
      
    if self._parameterNode.GetNodeReference("Volume"):
      self.ui.volumeSelector.toolTip = "Select output table"
      self.ui.IntensitycheckBox.toolTip = "Compute mean pixel brightness."
      self.ui.IntensitycheckBox.enabled = True
    else:
      self.ui.volumeSelector.toolTip = "Select input volume node"
      self.ui.IntensitycheckBox.toolTip = "Select input volume node"
      self.ui.IntensitycheckBox.enabled = False
       
      
    if self._parameterNode.GetNodeReference("ResultsTable"):
      self.ui.tableSelector.toolTip = "Edit output table"
    else:
      self.ui.tableSelector.toolTip = "Select output table"
      
    if self._parameterNode.GetNodeReference("ResultsChart"):
      self.ui.chartSelector.toolTip = "Edit output chart"
    else:
      self.ui.chartSelector.toolTip = "Select output chart"
            
   
    lineNode = slicer.mrmlScene.GetFirstNodeByName("SegmentGeometry Neutral Axis A")
    lineNode2 = slicer.mrmlScene.GetFirstNodeByName("SegmentGeometry Neutral Axis B")
    if lineNode != None:
      def CopyLine(unused1 = None, unused2 = None):
        import numpy as np
        centroid_ras = np.zeros(3)
        lineNode.GetNthControlPointPosition(0,centroid_ras)
        lineA_newpos = np.zeros(3)
        lineNode.GetNthControlPointPosition(1,lineA_newpos)
        lineNode2.SetNthControlPointPosition(1,centroid_ras[0]-lineA_newpos[0]+centroid_ras[0], centroid_ras[1]-lineA_newpos[1]+centroid_ras[1], centroid_ras[2]-lineA_newpos[2]+centroid_ras[2])
      copycat = lineNode.AddObserver(slicer.vtkMRMLMarkupsLineNode.PointModifiedEvent,CopyLine)

            
    if self.ui.OrientationcheckBox.checked == True and self.ui.OrientationcheckBox.enabled == True:
      self.ui.OrientationcheckBox.toolTip = "Check to use custom neutral axis"
      self.ui.orientationspinBox.toolTip = "Enter the angle between the horizontal and neutral axes. By default, the neutral axis is the horizontal axis."
      self.ui.orientationspinBox.enabled = True
      self.ui.ShowAxisButton.enabled = True
      self.ui.ShowAxisButton.toolTip = "Move the neutral axis to the current slice view"
      lineNode = slicer.mrmlScene.GetFirstNodeByName("SegmentGeometry Neutral Axis A")
      if lineNode != None:
        lineNode.SetDisplayVisibility(1)
      lineNode2 = slicer.mrmlScene.GetFirstNodeByName("SegmentGeometry Neutral Axis B")
      if lineNode2 != None:
        lineNode2.SetDisplayVisibility(1)
        
    else:
      self.ui.OrientationcheckBox.toolTip = "Select segmentation and volum nodes"
      self.ui.orientationspinBox.toolTip = "Select option use the neutral axis"
      self.ui.orientationspinBox.enabled = False
      self.ui.ShowAxisButton.enabled = False
      self.ui.ShowAxisButton.toolTip = "Select option use the neutral axis"   
      lineNode = slicer.mrmlScene.GetFirstNodeByName("SegmentGeometry Neutral Axis A")
      if lineNode != None:
        lineNode.SetDisplayVisibility(0)
      lineNode2 = slicer.mrmlScene.GetFirstNodeByName("SegmentGeometry Neutral Axis B")
      if lineNode2 != None:
        lineNode2.SetDisplayVisibility(0)

      
    # other tooltips
    self.ui.segmentationSelector.toolTip = "Select input segmentation node"
    self.ui.axisSelectorBox.toolTip = "Select slice view to compute on. Should be perpendicular to the long axis"
    self.ui.resamplespinBox.toolTip = "Perform computations in percent increments along the length of the segment. Enter zero to compute values on every slice"
    self.ui.CSAcheckBox.toolTip = "Compute cross-sectional area"
    self.ui.SMAcheckBox_1.toolTip = "Compute second moment of area around the principal axes"
    self.ui.JzcheckBox.toolTip = "Compute polar moment of area"
    self.ui.MODcheckBox_1.toolTip = "Compute section modulus around the principal axes"
    self.ui.ZpolcheckBox.toolTip = "Compute the polar section modulus"
    self.ui.ThetacheckBox.toolTip = "Compute how much the minor axis deviates from the horizontal axis in a clockwise direction"
    self.ui.RcheckBox.toolTip = "Compute the max distances from the principal axes"
    self.ui.DoubecheckBox.toolTip = "Normalize values by taking the respective roots needed to reduce them to a linear dimension and then divinding themy by segment length following Doube et al. (2009)"
    self.ui.SummerscheckBox.toolTip = "Normalize second moment of area by dividing the calculated value by the second moment of area for a solid circle with the same cross-sectional area following Summers et al. (2004)"
    self.ui.FeretcheckBox.toolTip = "Compute the maximum feret diameter"
    self.ui.CompactnesscheckBox.toolTip = "Compute slice compactness as the CSA/TCSA. Needs a separate solid segment to measure TCSA"
    self.ui.CentroidcheckBox.toolTip = "Compute the XY coordinates for the centroid of the section"
    self.ui.PerimcheckBox.toolTip = "Compute the perimeter of the section"


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
 
  def onChangeAxis(self): 
    """
    Run processing when user changes axis or segment.
    """
    
    self.ui.OrientationcheckBox.checked = False  

    lineNode = slicer.mrmlScene.GetFirstNodeByName("SegmentGeometry Neutral Axis A")
    if lineNode != None:
      slicer.mrmlScene.RemoveNode(lineNode)
    lineNode2 = slicer.mrmlScene.GetFirstNodeByName("SegmentGeometry Neutral Axis B")
    if lineNode2 != None:
      slicer.mrmlScene.RemoveNode(lineNode2)  

    self.ui.orientationspinBox.value = 0

 
  def onPrincipalAxes(self):
    """
    Run processing when user clicks "Align Segment with Principal Axes" button.
    """
    
    segmentationNode = self.ui.regionSegmentSelector.currentNode()
    volumeNode = self.ui.volumeSelector.currentNode()
    segmentId = self.ui.regionSegmentSelector.currentSegmentID()
    segName = segmentationNode.GetName()
        
    transformNode = slicer.mrmlScene.GetFirstNodeByName(segName + " SegmentGeometry Transformation")
    if transformNode == None:
      transformNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTransformNode", segName + " SegmentGeometry Transformation")
      shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
      newFolder = shNode.GetItemByName("SegmentGeometry Misc")
      if newFolder == 0:
        newFolder = shNode.CreateFolderItem(shNode.GetSceneItemID(), "SegmentGeometry Misc")      
      transformItem = shNode.GetItemByDataNode(transformNode)
      shNode.SetItemParent(transformItem, newFolder)
      shNode.SetItemExpanded(newFolder,0)
    segmentationNode.SetAndObserveTransformNodeID(None)
    segcentroid_ras = segmentationNode.GetSegmentCenterRAS(segmentId)

    pointNode = slicer.mrmlScene.GetFirstNodeByName("SegmentGeometry Point Transformation")
    if pointNode != None:
      def updateFinalTransform(unusedArg1=None, unusedArg2=None, unusedArg3=None):
        rotationMatrix = vtk.vtkMatrix4x4()
        pointNode.GetMatrixTransformToParent(rotationMatrix)
        rotationCenterPointCoord = segcentroid_ras
        finalTransform = vtk.vtkTransform()
        finalTransform.Translate(rotationCenterPointCoord)
        finalTransform.Concatenate(rotationMatrix)
        finalTransform.Translate(-rotationCenterPointCoord[0], -rotationCenterPointCoord[1], -rotationCenterPointCoord[2])
        transformNode.SetAndObserveMatrixTransformToParent(finalTransform.GetMatrix())

      rotationTransformNodeObserver = pointNode.AddObserver(slicer.vtkMRMLTransformNode.TransformModifiedEvent, updateFinalTransform)
      pointNode.RemoveObserver(rotationTransformNodeObserver)

      transform = transformNode.GetDisplayNode()
      if transform != None:  
        if transform.GetEditorVisibility() == False:
          sliders=self.ui.RotatorSliders
          sliders.setMRMLScene(slicer.mrmlScene)
          sliders.TypeOfTransform = slicer.qMRMLTransformSliders.ROTATION
          sliders.TypeOfTransform = slicer.qMRMLTransformSliders.TRANSLATION
          sliders.TypeOfTransform = slicer.qMRMLTransformSliders.ROTATION
          
      if transform == None:  
        sliders=self.ui.RotatorSliders
        sliders.setMRMLScene(slicer.mrmlScene)
        sliders.TypeOfTransform = slicer.qMRMLTransformSliders.ROTATION
        sliders.TypeOfTransform = slicer.qMRMLTransformSliders.TRANSLATION
        sliders.TypeOfTransform = slicer.qMRMLTransformSliders.ROTATION    
        #sliders.setMRMLTransformNode(slicer.mrmlScene.GetFirstNodeByName("SegmentGeometry Point Transformation"))

    import SegmentStatistics
    segmentationNode.GetDisplayNode().SetSegmentVisibility(segmentId, True)
    segStatLogic = SegmentStatistics.SegmentStatisticsLogic()
    segStatLogic.getParameterNode().SetParameter("Segmentation", segmentationNode.GetID())
    segStatLogic.getParameterNode().SetParameter("LabelmapSegmentStatisticsPlugin.obb_origin_ras.enabled",str(True))
    segStatLogic.getParameterNode().SetParameter("LabelmapSegmentStatisticsPlugin.obb_diameter_mm.enabled",str(True))
    segStatLogic.getParameterNode().SetParameter("LabelmapSegmentStatisticsPlugin.obb_direction_ras_x.enabled",str(True))
    segStatLogic.getParameterNode().SetParameter("LabelmapSegmentStatisticsPlugin.obb_direction_ras_y.enabled",str(True))
    segStatLogic.getParameterNode().SetParameter("LabelmapSegmentStatisticsPlugin.obb_direction_ras_z.enabled",str(True))
    segStatLogic.computeStatistics()
    stats = segStatLogic.getStatistics()

    # Draw ROI for each oriented bounding box
    import numpy as np
    # Get bounding box
    obb_origin_ras = np.array(stats[segmentId,"LabelmapSegmentStatisticsPlugin.obb_origin_ras"])
    obb_diameter_mm = np.array(stats[segmentId,"LabelmapSegmentStatisticsPlugin.obb_diameter_mm"])
    obb_direction_ras_x = np.array(stats[segmentId,"LabelmapSegmentStatisticsPlugin.obb_direction_ras_x"])
    obb_direction_ras_y = np.array(stats[segmentId,"LabelmapSegmentStatisticsPlugin.obb_direction_ras_y"])
    obb_direction_ras_z = np.array(stats[segmentId,"LabelmapSegmentStatisticsPlugin.obb_direction_ras_z"])
    # Position and orient ROI using a transform
    obb_center_ras = obb_origin_ras+0.5*(obb_diameter_mm[0] * obb_direction_ras_x + obb_diameter_mm[1] * obb_direction_ras_y + obb_diameter_mm[2] * obb_direction_ras_z)
    boundingBoxToRasTransform = np.row_stack((np.column_stack((obb_direction_ras_x, obb_direction_ras_y, obb_direction_ras_z, [0,0,0])), (0, 0, 0, 1)))
    boundingBoxToRasTransformMatrix = slicer.util.vtkMatrixFromArray(boundingBoxToRasTransform)
    transformNode = slicer.mrmlScene.GetFirstNodeByName(segName + " SegmentGeometry Transformation")
    transformNode.SetAndObserveMatrixTransformFromParent(boundingBoxToRasTransformMatrix)
    segmentationNode.SetAndObserveTransformNodeID(transformNode.GetID())
    volumeNode.SetAndObserveTransformNodeID(transformNode.GetID())
    slicer.modules.markups.logic().JumpSlicesToLocation(segcentroid_ras[0], segcentroid_ras[1], segcentroid_ras[2], True)

    segcentroid_ras_new = segmentationNode.GetSegmentCenterRAS(segmentId)
    Centroid_diff = [0.0, 0.0, 0.0]  
    for i in range(0,3):
      Centroid_diff[i] = (segcentroid_ras_new[i] -  segcentroid_ras[i])

    trans_new = slicer.mrmlScene.GetNodeByID(segmentationNode.GetTransformNodeID())
    matrix = vtk.vtkMatrix4x4()
    trans_new.GetMatrixTransformToParent(matrix)
    matrix.SetElement(0,3, trans_new.GetMatrixTransformToParent().GetElement(0,3) - Centroid_diff[0]) 
    matrix.SetElement(1,3, trans_new.GetMatrixTransformToParent().GetElement(1,3) - Centroid_diff[1])
    matrix.SetElement(2,3, trans_new.GetMatrixTransformToParent().GetElement(2,3) - Centroid_diff[2]) 
    trans_new.SetMatrixTransformToParent(matrix)
    pointNode = slicer.mrmlScene.GetFirstNodeByName("SegmentGeometry Point Transformation")
    if pointNode != None:
      pointNode.SetAndObserveMatrixTransformFromParent(boundingBoxToRasTransformMatrix)  

    self.ui.OrientationcheckBox.checked = False  
    lineNode = slicer.mrmlScene.GetFirstNodeByName("SegmentGeometry Neutral Axis A")
    if lineNode != None:
      slicer.mrmlScene.RemoveNode(lineNode)
    lineNode2 = slicer.mrmlScene.GetFirstNodeByName("SegmentGeometry Neutral Axis B")
    if lineNode2 != None:
      slicer.mrmlScene.RemoveNode(lineNode2)  
    self.ui.orientationspinBox.value = 0

        
  def onInteractive3DBox(self):
    """
    Run processing when user clicks "Interactive Rotate 3D View" button.
    """    
    segmentationNode = self.ui.regionSegmentSelector.currentNode()
    volumeNode = self.ui.volumeSelector.currentNode()
    volumeNode.SetAndObserveTransformNodeID(None)
    segmentId = self.ui.regionSegmentSelector.currentSegmentID()
    segName = segmentationNode.GetName()
            
    segtransformNode = segmentationNode.GetTransformNodeID()
    if segtransformNode != None:
      segtransformNode = slicer.mrmlScene.GetNodeByID(segmentationNode.GetTransformNodeID())
      matrix = vtk.vtkMatrix4x4()
      segtransformNode.GetMatrixTransformToParent(matrix)
      transformNode = slicer.mrmlScene.GetFirstNodeByName(segName + " SegmentGeometry Transformation")
      if transformNode == None:
        transformNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTransformNode", segName + " SegmentGeometry Transformation")
        shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
        newFolder = shNode.GetItemByName("SegmentGeometry Misc")
        if newFolder == 0:
          newFolder = shNode.CreateFolderItem(shNode.GetSceneItemID(), "SegmentGeometry Misc")      
        transformItem = shNode.GetItemByDataNode(transformNode)
        shNode.SetItemParent(transformItem, newFolder)
        shNode.SetItemExpanded(newFolder,0)
      transformNode.SetMatrixTransformToParent(matrix)
    elif segtransformNode == None:
      transformNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTransformNode", segName + " SegmentGeometry Transformation")
      shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
      newFolder = shNode.GetItemByName("SegmentGeometry Misc")
      if newFolder == 0:
        newFolder = shNode.CreateFolderItem(shNode.GetSceneItemID(), "SegmentGeometry Misc")      
      transformItem = shNode.GetItemByDataNode(transformNode)
      shNode.SetItemParent(transformItem, newFolder)
      shNode.SetItemExpanded(newFolder,0)
      segmentationNode.SetAndObserveTransformNodeID(transformNode.GetID())
    
    transform = transformNode.GetDisplayNode()
    if transform == None:
      transformNode.CreateDefaultDisplayNodes()
      transform = transformNode.GetDisplayNode()
    transform.UpdateEditorBounds() 
    transform.SetEditorTranslationEnabled(0)
    if transform.GetEditorVisibility() == False:
      transform.SetEditorVisibility(1)
      self.ui.RotatorSliders.enabled = False
    elif transform.GetEditorVisibility() == True:
      transform.SetEditorVisibility(0)  
      pointNode = slicer.mrmlScene.GetFirstNodeByName("SegmentGeometry Point Transformation")
      if pointNode != None:
        self.ui.RotatorSliders.enabled = True
        og_matrix = vtk.vtkMatrix4x4()
        transformNode = slicer.mrmlScene.GetFirstNodeByName(segName + " SegmentGeometry Transformation")
        transformNode.GetMatrixTransformToParent(og_matrix)    
        for i in range(0,3):
          og_matrix.SetElement(i,3,0)
        pointNode.SetAndObserveMatrixTransformToParent(og_matrix)  
        sliders=self.ui.RotatorSliders
        sliders.setMRMLScene(slicer.mrmlScene)
        sliders.TypeOfTransform = slicer.qMRMLTransformSliders.ROTATION
        sliders.TypeOfTransform = slicer.qMRMLTransformSliders.TRANSLATION
        sliders.TypeOfTransform = slicer.qMRMLTransformSliders.ROTATION
    volumeNode.SetAndObserveTransformNodeID(transformNode.GetID())
  
  def initializeSliders(self):
    """
    Run processing when user clicks "Initialize Sliders".
    """  
    self.ui.RotatorSliders.enabled = True
    segmentationNode = self.ui.regionSegmentSelector.currentNode()
    volumeNode = self.ui.volumeSelector.currentNode()
    segmentId = self.ui.regionSegmentSelector.currentSegmentID()
    segName = segmentationNode.GetName()
    
    transformNode = slicer.mrmlScene.GetFirstNodeByName(segName + " SegmentGeometry Transformation")
    if transformNode != None:
      transform = transformNode.GetDisplayNode()
      if transform != None:  
        transformNode.GetDisplayNode().SetEditorVisibility(0)
        self.ui.Interactive3DButton.checked = False    
    if transformNode == None:
      transformNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTransformNode", segName + " SegmentGeometry Transformation")
      segmentationNode.SetAndObserveTransformNodeID(transformNode.GetID())
      volumeNode.SetAndObserveTransformNodeID(transformNode.GetID())
      shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
      newFolder = shNode.GetItemByName("SegmentGeometry Misc")
      if newFolder == 0:
        newFolder = shNode.CreateFolderItem(shNode.GetSceneItemID(), "SegmentGeometry Misc")      
      transformItem = shNode.GetItemByDataNode(transformNode)
      shNode.SetItemParent(transformItem, newFolder)
      shNode.SetItemExpanded(newFolder,0)
    pointNode = slicer.mrmlScene.GetFirstNodeByName("SegmentGeometry Point Transformation")
    pointflag = 0
    if pointNode != None:
      pointflag = 1
    if pointNode == None:
      pointNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTransformNode", "SegmentGeometry Point Transformation")
      shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
      newFolder = shNode.GetItemByName("SegmentGeometry Misc")
      if newFolder == 0:
        newFolder = shNode.CreateFolderItem(shNode.GetSceneItemID(), "SegmentGeometry Misc")      
      pointItem = shNode.GetItemByDataNode(pointNode)
      shNode.SetItemParent(pointItem, newFolder)
      shNode.SetItemExpanded(newFolder,0)
    segcentroid_ras = segmentationNode.GetSegmentCenterRAS(segmentId)  

    og_matrix = vtk.vtkMatrix4x4()
    transformNode.GetMatrixTransformToParent(og_matrix)    
    for i in range(0,3):
      og_matrix.SetElement(i,3,0)
    pointNode.SetAndObserveMatrixTransformToParent(og_matrix)  

    def updateFinalTransform(unusedArg1=None, unusedArg2=None, unusedArg3=None):
      rotationMatrix = vtk.vtkMatrix4x4()
      pointNode = slicer.mrmlScene.GetFirstNodeByName("SegmentGeometry Point Transformation")
      pointNode.GetMatrixTransformToParent(rotationMatrix)
      rotationCenterPointCoord = segcentroid_ras
      finalTransform = vtk.vtkTransform()
      finalTransform.Translate(rotationCenterPointCoord)
      finalTransform.Concatenate(rotationMatrix)
      finalTransform.Translate(-rotationCenterPointCoord[0], -rotationCenterPointCoord[1], -rotationCenterPointCoord[2])
      transformNode.SetAndObserveMatrixTransformToParent(finalTransform.GetMatrix())
     
    if pointflag == 1:
      rotationTransformNodeObserver = pointNode.AddObserver(slicer.vtkMRMLTransformNode.TransformModifiedEvent, updateFinalTransform)
      pointNode.RemoveObserver(rotationTransformNodeObserver)

    # Manual initial update
    updateFinalTransform()  
    # Automatic update when point is moved or transform is modified
    rotationTransformNodeObserver = pointNode.AddObserver(slicer.vtkMRMLTransformNode.TransformModifiedEvent, updateFinalTransform)

    #initialize the sliders
    sliders=self.ui.RotatorSliders
    sliders.setMRMLScene(slicer.mrmlScene)
    sliders.TypeOfTransform = slicer.qMRMLTransformSliders.ROTATION
    sliders.TypeOfTransform = slicer.qMRMLTransformSliders.TRANSLATION
    sliders.TypeOfTransform = slicer.qMRMLTransformSliders.ROTATION
    sliders.setMRMLTransformNode(slicer.mrmlScene.GetFirstNodeByName("SegmentGeometry Point Transformation"))


  def ResetButton(self):
    """
    Clears everything in the Misc folder.
    """ 
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    shFolderItemId = shNode.GetItemByName("SegmentGeometry Misc")
    childIds = vtk.vtkIdList()
    shNode.GetItemChildren(shFolderItemId, childIds)
    self.ui.OrientationcheckBox.checked = False
    self.ui.OrientationcheckBox.enabled = True
    self.ui.applyButton.enabled = True
    self.ui.axisSelectorBox.enabled = True
    self.ui.RotatorSliders.enabled = False
    self.ui.Interactive3DButton.checked = False
    self.ui.orientationspinBox.value = 0


    if childIds.GetNumberOfIds() > 0:
      for itemIdIndex in range(childIds.GetNumberOfIds()):
        shItemId = childIds.GetId(itemIdIndex)
        dataNode = shNode.GetItemDataNode(shItemId)
        slicer.mrmlScene.RemoveNode(dataNode)
    shNode.RemoveItem(shFolderItemId)    

  def initializeAxisLine(self):
    """
    Draws initial neutral axis line when user clicks the button.
    """  
    segmentationNode = self.ui.regionSegmentSelector.currentNode()
    segmentId = self.ui.regionSegmentSelector.currentSegmentID()
    volumeNode = self.ui.volumeSelector.currentNode()
    segName = segmentationNode.GetName()
    axis = self.ui.axisSelectorBox.currentText
    
    lineNode = slicer.mrmlScene.GetFirstNodeByName("SegmentGeometry Neutral Axis A")
    if lineNode == None and volumeNode != None:
      spacing = volumeNode.GetSpacing()
      #determine the centroid of the current slice
      segcentroid_ras = segmentationNode.GetSegmentCenterRAS(segmentId)
      #slicer.modules.markups.logic().JumpSlicesToLocation(segcentroid_ras[0], segcentroid_ras[1], segcentroid_ras[2], True)
      if axis=="R (Yellow)":     
        sliceNodeID = "vtkMRMLSliceNodeYellow"
      if axis=="A (Green)":
        sliceNodeID = "vtkMRMLSliceNodeGreen"
      if axis=="S (Red)":      
        sliceNodeID = "vtkMRMLSliceNodeRed"
      
      # Get image data from slice view
      sliceNode = slicer.mrmlScene.GetNodeByID(sliceNodeID)
      appLogic = slicer.app.applicationLogic()
      sliceLogic = appLogic.GetSliceLogic(sliceNode)
      sliceLayerLogic = sliceLogic.GetBackgroundLayer()
      reslice = sliceLayerLogic.GetReslice()
      reslicedImage = vtk.vtkImageData()
      reslicedImage.DeepCopy(reslice.GetOutput())

      # Create new volume node using resliced image
      newVolume = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode","MyNewVolume")
      newVolume.SetIJKToRASMatrix(sliceNode.GetXYToRAS())
      newVolume.SetAndObserveImageData(reslicedImage)
      newVolume.CreateDefaultDisplayNodes()
      newVolume.CreateDefaultStorageNode()
      labelmapVolumeNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLabelMapVolumeNode")
      segmentIds = vtk.vtkStringArray()
      segmentIds.InsertNextValue(segmentId)
      slicer.vtkSlicerSegmentationsModuleLogic.ExportSegmentsToLabelmapNode(segmentationNode, segmentIds, labelmapVolumeNode, newVolume)

      seg = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode")
      slicer.modules.segmentations.logic().ImportLabelmapToSegmentationNode(labelmapVolumeNode, seg)
      segName = segmentationNode.GetSegmentation().GetSegment(segmentId).GetName()
      linecenter = seg.GetSegmentCenterRAS(segName)
      
      # if tried to draw line not over the segment, jump to the center
      if linecenter == None:
        segcentroid_ras = segmentationNode.GetSegmentCenterRAS(segmentId)
        slicer.modules.markups.logic().JumpSlicesToLocation(segcentroid_ras[0], segcentroid_ras[1], segcentroid_ras[2], True)
        if axis=="R (Yellow)":     
          sliceNodeID = "vtkMRMLSliceNodeYellow"
        if axis=="A (Green)":
          sliceNodeID = "vtkMRMLSliceNodeGreen"
        if axis=="S (Red)":      
          sliceNodeID = "vtkMRMLSliceNodeRed"
      
        # Get image data from slice view
        sliceNode = slicer.mrmlScene.GetNodeByID(sliceNodeID)
        appLogic = slicer.app.applicationLogic()
        sliceLogic = appLogic.GetSliceLogic(sliceNode)
        sliceLayerLogic = sliceLogic.GetBackgroundLayer()
        reslice = sliceLayerLogic.GetReslice()
        reslicedImage = vtk.vtkImageData()
        reslicedImage.DeepCopy(reslice.GetOutput())
  
        # Create new volume node using resliced image
        newVolume = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode","MyNewVolume")
        newVolume.SetIJKToRASMatrix(sliceNode.GetXYToRAS())
        newVolume.SetAndObserveImageData(reslicedImage)
        newVolume.CreateDefaultDisplayNodes()
        newVolume.CreateDefaultStorageNode()
        labelmapVolumeNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLabelMapVolumeNode")
        segmentIds = vtk.vtkStringArray()
        segmentIds.InsertNextValue(segmentId)
        slicer.vtkSlicerSegmentationsModuleLogic.ExportSegmentsToLabelmapNode(segmentationNode, segmentIds, labelmapVolumeNode, newVolume)

        seg = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode")
        slicer.modules.segmentations.logic().ImportLabelmapToSegmentationNode(labelmapVolumeNode, seg)
        segName = segmentationNode.GetSegmentation().GetSegment(segmentId).GetName()
        linecenter = seg.GetSegmentCenterRAS(segName)
    
      slicer.mrmlScene.RemoveNode(labelmapVolumeNode)
      slicer.mrmlScene.RemoveNode(newVolume)
      slicer.mrmlScene.RemoveNode(seg)
      
    elif lineNode != None:
      spacing = volumeNode.GetSpacing()
      linecenter = [0,]*3
      lineNode.GetNthControlPointPosition(0,linecenter)

    linevalue = (50 * spacing[0])
    if axis=="R (Yellow)" and linecenter[1] >= 0:
      horiz_point = linecenter[1] + linevalue
    if axis=="R (Yellow)" and linecenter[1] < 0: 
      horiz_point = linecenter[1] - linevalue
    if axis=="A (Green)" and linecenter[0] >= 0:
      horiz_point = linecenter[0] + linevalue
    if axis=="A (Green)" and linecenter[0] < 0: 
      horiz_point = linecenter[0] - linevalue
    if axis=="S (Red)" and linecenter[0] >= 0:
      horiz_point = linecenter[0] + linevalue
    if axis=="S (Red)" and linecenter[0] < 0: 
      horiz_point = linecenter[0] - linevalue

    def CopyLine(unused1 = None, unused2 = None):
      linecenter = [0,]*3
      lineNode.GetNthControlPointPosition(0,linecenter)
      lineA_newpos = [0,]*3
      lineNode.GetNthControlPointPosition(1,lineA_newpos)
      lineNode2.SetNthControlPointPosition(1,linecenter[0]-lineA_newpos[0]+linecenter[0], linecenter[1]-lineA_newpos[1]+linecenter[1], linecenter[2]-lineA_newpos[2]+linecenter[2])

    def ShowAngle(unused1 = None, unused2 = None):
      import numpy as np
      lineDirectionVectors = []
      #lineStartPos = np.asarray(segmentationNode.GetSegmentCenterRAS(segmentId))
      lineStartPos = np.zeros(3)
      lineNode.GetNthControlPointPosition(0,lineStartPos)
      if axis=="R (Yellow)":
        lineEndPos = np.asarray((lineStartPos[0],horiz_point, lineStartPos[2]))
      if axis=="A (Green)":
        lineEndPos = np.asarray((horiz_point,lineStartPos[1],lineStartPos[2])) 
      if axis=="S (Red)":
        lineEndPos = np.asarray((horiz_point,lineStartPos[1],lineStartPos[2])) 
      lineDirectionVector = (lineEndPos - lineStartPos)/np.linalg.norm(lineEndPos-lineStartPos)
      lineDirectionVectors.append(lineDirectionVector)
      lineEndPos = np.zeros(3)
      lineNode.GetNthControlPointPositionWorld(1,lineEndPos)
      lineDirectionVector = (lineEndPos - lineStartPos)/np.linalg.norm(lineEndPos-lineStartPos)
      lineDirectionVectors.append(lineDirectionVector)
      angleRad = vtk.vtkMath.AngleBetweenVectors(lineDirectionVectors[0],lineDirectionVectors[1])
      angleDeg = vtk.vtkMath.DegreesFromRadians(angleRad)
      if axis=="R (Yellow)" and lineDirectionVectors[1][2] > lineDirectionVectors[0][2]:
        angleDeg = (180 - angleDeg) 
      if axis=="A (Green)" and lineDirectionVectors[1][2] > lineDirectionVectors[0][2]:
        angleDeg = (180 - angleDeg)
      if axis=="S (Red)" and lineDirectionVectors[1][1] > lineDirectionVectors[0][1]:
        angleDeg = (180 - angleDeg) 
      angleDeg = np.around(angleDeg,5)
      self.ui.orientationspinBox.value = angleDeg 


    lineNode = slicer.mrmlScene.GetFirstNodeByName("SegmentGeometry Neutral Axis A")
    if lineNode == None:
      lineNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", "SegmentGeometry Neutral Axis A")
      lineNode.GetDisplayNode().SetPropertiesLabelVisibility(False)
      lineNode.GetDisplayNode().SetSelectedColor((1.0, 0.5000076295109483, 0.5000076295109483))
      lineNode.GetDisplayNode().SetActiveColor((1.0, 0.5000076295109483, 0.5000076295109483))
      lineNode.AddControlPoint(vtk.vtkVector3d(linecenter))
      if axis=="R (Yellow)":
        lineNode.AddControlPoint(vtk.vtkVector3d(linecenter[0],horiz_point, linecenter[2]))
        lineNode.GetDisplayNode().SetViewNodeIDs(('vtkMRMLViewNode1', 'vtkMRMLSliceNodeYellow'))
      if axis=="A (Green)":
        lineNode.AddControlPoint(vtk.vtkVector3d(horiz_point,linecenter[1],linecenter[2]))
        lineNode.GetDisplayNode().SetViewNodeIDs(('vtkMRMLViewNode1', 'vtkMRMLSliceNodeGreen'))
      if axis=="S (Red)":
        lineNode.AddControlPoint(vtk.vtkVector3d(horiz_point,linecenter[1],linecenter[2]))
        lineNode.GetDisplayNode().SetViewNodeIDs(('vtkMRMLViewNode1', 'vtkMRMLSliceNodeRed'))
      lineNode.SetNthControlPointLocked(0,1)
      lineNode.SetNthControlPointLocked(1,0)
    anglewatcher = lineNode.AddObserver(slicer.vtkMRMLMarkupsLineNode.PointModifiedEvent,ShowAngle)


    lineNode2 = slicer.mrmlScene.GetFirstNodeByName("SegmentGeometry Neutral Axis B")
    if lineNode2 == None:
      lineNode2 = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", "SegmentGeometry Neutral Axis B")
      lineNode2.GetDisplayNode().SetPropertiesLabelVisibility(False)
      lineNode2.GetDisplayNode().SetActiveColor((1.0, 0.5000076295109483, 0.5000076295109483))
      lineNode2.GetDisplayNode().SetColor((1.0, 0.5000076295109483, 0.5000076295109483))
      lineNode2.GetDisplayNode().SetGlyphType(2)
      lineNode2.AddControlPoint(vtk.vtkVector3d(linecenter))
      if axis=="R (Yellow)":
        lineNode2.AddControlPoint(vtk.vtkVector3d(linecenter[0],linecenter[1]+linevalue,linecenter[2]))
        lineNode2.GetDisplayNode().SetViewNodeIDs(('vtkMRMLViewNode1', 'vtkMRMLSliceNodeYellow'))
      if axis=="A (Green)":
        lineNode2.AddControlPoint(vtk.vtkVector3d(linecenter[0]+linevalue,linecenter[1],linecenter[2]))
        lineNode2.GetDisplayNode().SetViewNodeIDs(('vtkMRMLViewNode1', 'vtkMRMLSliceNodeGreen'))
      if axis=="S (Red)":
        lineNode2.AddControlPoint(vtk.vtkVector3d(linecenter[0]+linevalue,linecenter[1],linecenter[2]))
        lineNode2.GetDisplayNode().SetViewNodeIDs(('vtkMRMLViewNode1', 'vtkMRMLSliceNodeRed'))
      lineNode2.SetNthControlPointLocked(0,1)
      lineNode2.SetNthControlPointLocked(1,1)
    copycat = lineNode.AddObserver(slicer.vtkMRMLMarkupsLineNode.PointModifiedEvent,CopyLine)


    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    newFolder = shNode.GetItemByName("SegmentGeometry Misc")
    if newFolder == 0:
      newFolder = shNode.CreateFolderItem(shNode.GetSceneItemID(), "SegmentGeometry Misc")      
    shNode.SetItemParent(shNode.GetItemByDataNode(lineNode), newFolder)
    shNode.SetItemParent(shNode.GetItemByDataNode(lineNode2), newFolder)
    shNode.SetItemExpanded(newFolder,0)    


  def updateAxisLineAngle(self):
    """
    Update axis line with angle 
    """
    import numpy as np
    import math
    segmentationNode = self.ui.regionSegmentSelector.currentNode()
    segmentId = self.ui.regionSegmentSelector.currentSegmentID()
    segName = segmentationNode.GetName()
    axis = self.ui.axisSelectorBox.currentText
    
    lineNode = slicer.mrmlScene.GetFirstNodeByName("SegmentGeometry Neutral Axis A")
    if lineNode != None:
      linecenter = [0,]*3
      lineNode.GetNthControlPointPosition(0,linecenter)
      slicer.modules.markups.logic().JumpSlicesToLocation(linecenter[0], linecenter[1], linecenter[2], True)
      if axis=="R (Yellow)" and linecenter[1] >= 0:
        horiz_point = linecenter[1] + 2
      if axis=="R (Yellow)" and linecenter[1] < 0: 
        horiz_point = linecenter[1] - 2
      if axis=="A (Green)" and linecenter[0] >= 0:
        horiz_point = linecenter[0] + 2
      if axis=="A (Green)" and linecenter[0] < 0: 
        horiz_point = linecenter[0] - 2
      if axis=="S (Red)" and linecenter[0] >= 0:
        horiz_point = linecenter[0] + 2
      if axis=="S (Red)" and linecenter[0] < 0: 
        horiz_point = linecenter[0] - 2
        

      def GetAngle(unused1 = None, unused2 = None):
        import numpy as np
        lineDirectionVectors = []
        lineStartPos = [0,]*3
        lineNode.GetNthControlPointPosition(0,lineStartPos)
        if axis=="R (Yellow)":
          lineEndPos = np.asarray((lineStartPos[0],horiz_point, lineStartPos[2]))
        if axis=="A (Green)":
          lineEndPos = np.asarray((horiz_point,lineStartPos[1],lineStartPos[2])) 
        if axis=="S (Red)":
          lineEndPos = np.asarray((horiz_point,lineStartPos[1],lineStartPos[2])) 
        lineDirectionVector = (lineEndPos - lineStartPos)/np.linalg.norm(lineEndPos-lineStartPos)
        lineDirectionVectors.append(lineDirectionVector)
        lineEndPos = np.zeros(3)
        lineNode.GetNthControlPointPositionWorld(1,lineEndPos)
        lineDirectionVector = (lineEndPos - lineStartPos)/np.linalg.norm(lineEndPos-lineStartPos)
        lineDirectionVectors.append(lineDirectionVector)
        angleRad = vtk.vtkMath.AngleBetweenVectors(lineDirectionVectors[0],lineDirectionVectors[1])
        angleDeg = vtk.vtkMath.DegreesFromRadians(angleRad)
        if axis=="R (Yellow)" and lineDirectionVectors[1][2] > lineDirectionVectors[0][2]:
          angleDeg = (180 - angleDeg) 
        if axis=="A (Green)" and lineDirectionVectors[1][2] > lineDirectionVectors[0][2]:
          angleDeg = (180 - angleDeg) 
        if axis=="S (Red)" and lineDirectionVectors[1][1] > lineDirectionVectors[0][1]:
          angleDeg = (180 - angleDeg) 
        angleDeg = np.around(angleDeg,5)
        return angleDeg
    
      currentangle = GetAngle()
      newangle = self.ui.orientationspinBox.value
      Theta = newangle - currentangle
      Theta = Theta * np.pi/180 * -1

      if axis == "R (Yellow)":
        Xras = [0,]*3
        lineNode.GetNthControlPointPosition(1,Xras)
        ogX = Xras[1] - linecenter[1]
        Yras = [0,]*3
        lineNode.GetNthControlPointPosition(1,Yras)
        ogY = Yras[2] - linecenter[2]
        newX = (ogX*math.cos(Theta) + ogY*math.sin(Theta)) + linecenter[1]
        newY = (-1*ogX*math.sin(Theta) + ogY*math.cos(Theta)) + linecenter[2] 
        lineNode.SetNthControlPointPosition(1, linecenter[0], newX,newY)
   
      if axis == "A (Green)":
        Xras = [0,]*3
        lineNode.GetNthControlPointPosition(1,Xras)
        ogX = Xras[0] - linecenter[0]
        Yras = [0,]*3
        lineNode.GetNthControlPointPosition(1,Yras)
        ogY = Yras[2] - linecenter[2]
        newX = (ogX*math.cos(Theta) + ogY*math.sin(Theta)) + linecenter[0]
        newY = (-1*ogX*math.sin(Theta) + ogY*math.cos(Theta)) + linecenter[2] 
        lineNode.SetNthControlPointPosition(1, newX, linecenter[1],newY)
    
      if axis == "S (Red)":
        Xras = [0,]*3
        lineNode.GetNthControlPointPosition(1,Xras)
        ogX = Xras[0] - linecenter[0]
        Yras = [0,]*3
        lineNode.GetNthControlPointPosition(1,Yras)
        ogY = Yras[1] - linecenter[1]
        newX = (ogX*math.cos(Theta) + ogY*math.sin(Theta)) + linecenter[0]
        newY = (-1*ogX*math.sin(Theta) + ogY*math.cos(Theta)) + linecenter[1] 
        lineNode.SetNthControlPointPosition(1, newX, newY, linecenter[2])
      
  def ShowAxis(self):
    """
    Update the neutral axis to display on current slice.
    """    
    segmentationNode = self.ui.regionSegmentSelector.currentNode()
    segmentId = self.ui.regionSegmentSelector.currentSegmentID()
    segName = segmentationNode.GetName()
    volumeNode = self.ui.volumeSelector.currentNode()
    spacing = volumeNode.GetSpacing() 
    axis = self.ui.axisSelectorBox.currentText
    lineNode = slicer.mrmlScene.GetFirstNodeByName("SegmentGeometry Neutral Axis A")
    lineNode2 = slicer.mrmlScene.GetFirstNodeByName("SegmentGeometry Neutral Axis B")
    if lineNode != None:
      if axis=="R (Yellow)":     
        sliceNodeID = "vtkMRMLSliceNodeYellow"
      if axis=="A (Green)":
        sliceNodeID = "vtkMRMLSliceNodeGreen"
      if axis=="S (Red)":      
        sliceNodeID = "vtkMRMLSliceNodeRed"
      
      # Get image data from slice view
      sliceNode = slicer.mrmlScene.GetNodeByID(sliceNodeID)
      appLogic = slicer.app.applicationLogic()
      sliceLogic = appLogic.GetSliceLogic(sliceNode)
      sliceLayerLogic = sliceLogic.GetBackgroundLayer()
      reslice = sliceLayerLogic.GetReslice()
      reslicedImage = vtk.vtkImageData()
      reslicedImage.DeepCopy(reslice.GetOutput())

      # Create new volume node using resliced image
      newVolume = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode","MyNewVolume")
      newVolume.SetIJKToRASMatrix(sliceNode.GetXYToRAS())
      newVolume.SetAndObserveImageData(reslicedImage)
      newVolume.CreateDefaultDisplayNodes()
      newVolume.CreateDefaultStorageNode()
      labelmapVolumeNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLabelMapVolumeNode")
      segmentIds = vtk.vtkStringArray()
      segmentIds.InsertNextValue(segmentId)
      slicer.vtkSlicerSegmentationsModuleLogic.ExportSegmentsToLabelmapNode(segmentationNode, segmentIds, labelmapVolumeNode, newVolume)

      seg = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode")
      slicer.modules.segmentations.logic().ImportLabelmapToSegmentationNode(labelmapVolumeNode, seg)
      segName = segmentationNode.GetSegmentation().GetSegment(segmentId).GetName()
      linecenter_new = seg.GetSegmentCenterRAS(segName)
    
      slicer.mrmlScene.RemoveNode(labelmapVolumeNode)
      slicer.mrmlScene.RemoveNode(newVolume)
      slicer.mrmlScene.RemoveNode(seg)
      
      if linecenter_new != None:
        linecenter = [0,]*3
        lineNode.GetNthControlPointPosition(0,linecenter)
        lineA_pos = [0,]*3
        lineNode.GetNthControlPointPosition(1,lineA_pos)
        lineNode.SetNthControlPointPosition(0,linecenter_new[0],linecenter_new[1],linecenter_new[2])
        lineNode2.SetNthControlPointPosition(0,linecenter_new[0],linecenter_new[1],linecenter_new[2])
        change = (linecenter_new[0]-linecenter[0],linecenter_new[1]-linecenter[1],linecenter_new[2]-linecenter[2])
        lineNode.SetNthControlPointPosition(1,lineA_pos[0]+change[0],lineA_pos[1]+change[1],lineA_pos[2]+change[2])

  def onApplyButton(self):
    """
    Run processing when user clicks "Apply" button.
    """
      
    try:
      # Create nodes for results
      segment = self.ui.regionSegmentSelector.currentNode().GetSegmentation().GetSegment(self.ui.regionSegmentSelector.currentSegmentID())
      segName = segment.GetName()
      
      tableNode = self.ui.tableSelector.currentNode()
      expTable = segName + " SegmentGeometry table"
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
      expChart = segName + " SegmentGeometry plot"
      if not plotChartNode:
        plotChartNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotChartNode", segName + " SegmentGeometry plot")
        self.ui.chartSelector.setCurrentNode(plotChartNode)
      if plotChartNode.GetName() != expChart and slicer.mrmlScene.GetFirstNodeByName(expChart) != None:
        plotChartNode = slicer.mrmlScene.GetFirstNodeByName(expChart)
        self.ui.chartSelector.setCurrentNode(plotChartNode)
      if plotChartNode.GetName() != expChart and slicer.mrmlScene.GetFirstNodeByName(expChart) == None:
        plotChartNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotChartNode", segName + " SegmentGeometry plot")
        self.ui.chartSelector.setCurrentNode(plotChartNode)  

     
      self.logic.run(self.ui.regionSegmentSelector.currentNode(), self.ui.regionSegmentSelector.currentSegmentID(), self.ui.volumeSelector.currentNode(), 
                     self.ui.axisSelectorBox.currentText, 
                     self.ui.resamplespinBox.value, tableNode, plotChartNode, self.ui.LengthcheckBox.checked, self.ui.FeretcheckBox.checked,
                     self.ui.CSAcheckBox.checked, self.ui.IntensitycheckBox.checked, self.ui.SMAcheckBox_1.checked, self.ui.MODcheckBox_1.checked, self.ui.JzcheckBox.checked,
                     self.ui.ZpolcheckBox.checked, self.ui.OrientationcheckBox.checked, self.ui.orientationspinBox.value, 
                     self.ui.ThetacheckBox.checked, self.ui.RcheckBox.checked,
                     self.ui.DoubecheckBox.checked, self.ui.SummerscheckBox.checked, 
                     self.ui.CompactnesscheckBox.checked, self.ui.areaSegmentSelector.currentNode(),self.ui.areaSegmentSelector.currentSegmentID(),
                     self.ui.CentroidcheckBox.checked,self.ui.PerimcheckBox.checked,self.ui.ResultsText)
      
    except Exception as e:
      slicer.util.errorDisplay("Failed to compute results: "+str(e))
      import traceback
      traceback.print_exc()
      

    segmentationNode = self.ui.regionSegmentSelector.currentNode()
    segmentId = self.ui.regionSegmentSelector.currentSegmentID()
    segName = segmentationNode.GetName()
    axis = self.ui.axisSelectorBox.currentText
    lineNode = slicer.mrmlScene.GetFirstNodeByName("SegmentGeometry Neutral Axis A")
    lineNode2 = slicer.mrmlScene.GetFirstNodeByName("SegmentGeometry Neutral Axis B")


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


  def run(self, segmentationNode, segmentNode, volumeNode, axis, interval, tableNode, plotChartNode, LengthcheckBox, FeretcheckBox, CSAcheckBox, IntensitycheckBox, SMAcheckBox_1,
  MODcheckBox_1, JzcheckBox, ZpolcheckBox, OrientationcheckBox, angle, ThetacheckBox, RcheckBox, DoubecheckBox, SummerscheckBox,
  CompactnesscheckBox, areaSegementationNode, areaSegmentID, CentroidcheckBox, PerimcheckBox, ResultsText):
    """
    Run the processing algorithm.
    """

    import numpy as np
    import time

    start = time.time()
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
    
    # move segment to the center of the volume
    segcentroid_ras = segmentationNode.GetSegmentCenterRAS(segmentNode)
    volumeBounds = [0,]*6
    volumeNode.GetBounds(volumeBounds)
                
    roiCenter = [0.0, 0.0, 0.0]
    for i in range(0,3):
      roiCenter[i] = (volumeBounds[i*2+1] + volumeBounds[i*2])/2 

    Centroid_diff = [0.0, 0.0, 0.0]  
    for i in range(0,3):
      Centroid_diff[i] = (segcentroid_ras[i] -  roiCenter[i])
      
    trans = segmentationNode.GetTransformNodeID()
    if trans != None:
      trans = slicer.mrmlScene.GetNodeByID(segmentationNode.GetTransformNodeID())
      og_matrix = vtk.vtkMatrix4x4()
      trans.GetMatrixTransformToParent(og_matrix)
      trans_new = slicer.mrmlScene.GetNodeByID(segmentationNode.GetTransformNodeID())
      matrix = vtk.vtkMatrix4x4()
      trans_new.GetMatrixTransformToParent(matrix)
      matrix.SetElement(0,3, trans_new.GetMatrixTransformToParent().GetElement(0,3) - Centroid_diff[0]) 
      matrix.SetElement(1,3, trans_new.GetMatrixTransformToParent().GetElement(1,3) - Centroid_diff[1])
      matrix.SetElement(2,3, trans_new.GetMatrixTransformToParent().GetElement(2,3) - Centroid_diff[2]) 
      trans_new.SetMatrixTransformToParent(matrix) 
    
    # use crop volume to expand volume if segment is partially outside
    segmentBounds = [0,]*6
    segmentationNode.GetRASBounds(segmentBounds)
    combinedBounds = [0,]*6   
    for i in (0,2,4):
      combinedBounds[i] = min(volumeBounds[i],segmentBounds[i])
    for i in (1,3,5):
      combinedBounds[i] = max(volumeBounds[i],segmentBounds[i])
    roiCenter = [0.0, 0.0, 0.0]
    roiRadius = [0.0, 0.0, 0.0]  
    for i in range(0,3):
      roiCenter[i] = (combinedBounds[i*2+1] + combinedBounds[i*2])/2
      roiRadius[i] = (combinedBounds[i*2+1] - combinedBounds[i*2])/2
    # use annotation node because cropvolume doesn't use the markupsROI  
    roi=slicer.mrmlScene.AddNewNodeByClass("vtkMRMLAnnotationROINode", "TempAnnotationROI")
    roi.SetDisplayVisibility(0)
    roi.SetXYZ(roiCenter[0], roiCenter[1], roiCenter[2])
    roi.SetRadiusXYZ(roiRadius[0], roiRadius[1], roiRadius[2])        

    boxflag = 0
    for i in range(6):
      if combinedBounds[i] != volumeBounds[i]:
        boxflag = 1  
    
    # assess whether volume is anisotropic
    spacingflag = 0
    spacing = volumeNode.GetSpacing() 
    trans = segmentationNode.GetTransformNodeID()
    if spacing[0] != spacing[1] or spacing[0] != spacing[2] or spacing[1] != spacing[2]:
      spacingflag = 1
   
    # if segment is outside volume or volume is anisotropic, use crop volume
    if boxflag == 1 or spacingflag == 1:
      volumetransformNode = volumeNode.GetTransformNodeID()
      volumeNode.SetAndObserveTransformNodeID(None)
      volumesLogic = slicer.modules.volumes.logic()
      newVolume = volumesLogic.CloneVolumeGeneric(volumeNode.GetScene(), volumeNode, "TempMaskVolume")
      parameters = slicer.vtkMRMLCropVolumeParametersNode()
      slicer.mrmlScene.AddNode(parameters)
      parameters.SetInputVolumeNodeID(volumeNode.GetID())
      parameters.SetOutputVolumeNodeID(newVolume.GetID())
      parameters.SetROINodeID(roi.GetID())
      if volumetransformNode != None and spacingflag == 1:
        parameters.SetIsotropicResampling(True)
      slicer.modules.cropvolume.logic().Apply(parameters)
      volumeNode.SetAndObserveTransformNodeID(volumetransformNode)
      newVolume.SetAndObserveTransformNodeID(volumetransformNode)

      volumeNode = newVolume
      slicer.mrmlScene.RemoveNode(newVolume)
      slicer.mrmlScene.RemoveNode(parameters)

    
    # do calculations
    try:
      # Create temporary volume node
      tempSegmentLabelmapVolumeNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLLabelMapVolumeNode', "SegmentGeometryTemp")
      # Create flag for the aspect ratio check
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
      CxArray.SetName("Cx")
      
      CyArray = vtk.vtkFloatArray()
      CyArray.SetName("Cy")
      
      JzArray = vtk.vtkFloatArray()
      JzArray.SetName("Jz (mm^4)")
              
      ImajorArray = vtk.vtkFloatArray()
      ImajorArray.SetName("Imajor (mm^4)")
        
      IminorArray = vtk.vtkFloatArray()
      IminorArray.SetName("Iminor (mm^4)")
                    
      ThetaMinArray = vtk.vtkFloatArray()
      ThetaMinArray.SetName("Theta (deg)")
      
      ThetaMaxArray = vtk.vtkFloatArray()
      ThetaMaxArray.SetName("Theta major (deg)")
      
      ZmajorArray = vtk.vtkFloatArray()
      ZmajorArray.SetName("Zmajor (mm^3)")
        
      ZminorArray = vtk.vtkFloatArray()
      ZminorArray.SetName("Zminor (mm^3)")
      
      ZpolArray = vtk.vtkFloatArray()
      ZpolArray.SetName("Zpol (mm^3)")
                    
      RmajorArray = vtk.vtkFloatArray()
      RmajorArray.SetName("Rmajor (mm)")
        
      RminorArray = vtk.vtkFloatArray()
      RminorArray.SetName("Rminor (mm)")
      
      RmaxArray = vtk.vtkFloatArray()
      RmaxArray.SetName("Rmax (mm)")
              
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
      
      PerimArray = vtk.vtkFloatArray()
      PerimArray.SetName("Perimeter (mm)")
      
      TotalAreaArray = vtk.vtkFloatArray()
      TotalAreaArray.SetName("TCSA (mm^2)")
            
      CompactnessArray = vtk.vtkFloatArray()
      CompactnessArray.SetName("Compactness")
      
      CircularityArray = vtk.vtkFloatArray()
      CircularityArray.SetName("Circularity")
      
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
        
        JzArray_Doube = vtk.vtkFloatArray()
        JzArray_Doube.SetName("Jz (LenNorm)")
        
        ZpolArray_Doube = vtk.vtkFloatArray()
        ZpolArray_Doube.SetName("Zpol (LenNorm)")


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

        JzArray_Summers = vtk.vtkFloatArray()
        JzArray_Summers.SetName("Jz (MatNorm)")

        ZpolArray_Summers = vtk.vtkFloatArray()
        ZpolArray_Summers.SetName("Zpol (MatNorm)")
              
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
          outputVolume = slicer.util.getFirstNodeByName(segName + " SegmentGeometry Resampled Volume")
          if outputVolume != None:
            slicer.mrmlScene.RemoveNode(outputVolume) 
          outputVolume = volumesLogic.CloneVolumeGeneric(slicer.mrmlScene, volumeNode, segName + " SegmentGeometry Resampled Volume")
          outputVolume.SetName(segName + " SegmentGeometry Resampled Volume")
          
          
          # resample volume if user is calculating mean pixel brightness and has a transformed segment
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
  
            outputvolume = slicer.vtkSlicerVolumesLogic().CloneVolume(slicer.mrmlScene,outputVolume, segName + " Resampled Brightness Volume",True)
            slicer.mrmlScene.RemoveNode(cliNode)
            slicer.mrmlScene.RemoveNode(outputvolume)
          volumeNodeformasking = outputVolume
          volumeNode.SetAndObserveTransformNodeID(volumetransformNode)
          
        # Crop temporary volume to avoid computing on empty slices
        maskExtent = [0] * 6
        fillValue = 0
        import SegmentEditorMaskVolumeLib
        maskVolumeWithSegment = SegmentEditorMaskVolumeLib.SegmentEditorEffect.maskVolumeWithSegment
        if IntensitycheckBox == True:
          maskVolumeWithSegment(segmentationNode, segmentID, "FILL_OUTSIDE", [0], volumeNodeformasking, outputVolume, maskExtent) 
        else: maskVolumeWithSegment(segmentationNode, segmentID, "FILL_INSIDE_AND_OUTSIDE", [1,0], volumeNodeformasking, outputVolume, maskExtent) 
        extent = maskExtent 
          
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


        # remove temporary output volume node if compactness is measured
        if segmentID == areaSegmentID and areaSegmentID != segmentNode:
          slicer.mrmlScene.RemoveNode(outputVolume)
        
        if volumeNode == None:
          slicer.mrmlScene.RemoveNode(volumeNodeformasking)


        # volumeExtents so first and last number of images in XYZ directions. Starts with 0 not 1	
        volumeExtents = tempSegmentLabelmapVolumeNode.GetImageData().GetExtent()
        numSlices = volumeExtents[axisIndex*2+1] - volumeExtents[axisIndex*2] + 1
        
        # determine how many and which slices to calculate statistics for
        if interval > 0:
          resample = np.arange(interval, stop = 101, step = interval)
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
          
        # determine centroid of the first and last slice. Identical if only one slice
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

        if segmentID == segmentNode:
          if interval > 0:
            for i in range(len(sampleSlices)):
              sliceNumberArray.InsertNextValue(sampleSlices[i]) # adds slice number to the array
              SegmentNameArray.InsertNextValue(segName)
              percentLengthArray.InsertNextValue(percentLength[i])
              
          else:
            for i in range(numSlices):
              sliceNumberArray.InsertNextValue(sampleSlices[i]) # adds slice number to the array
              SegmentNameArray.InsertNextValue(segName)
              percentLengthArray.InsertNextValue(percentLength[i])


        ###### DO CALCULATIONS ######
        spacing = tempSegmentLabelmapVolumeNode.GetSpacing()
        narray = slicer.util.arrayFromVolume(tempSegmentLabelmapVolumeNode)
        #if spacing[0] != spacing[1] or spacing[0] != spacing[2] or spacing[1] != spacing[2]:
        #  raise ValueError("Voxels are anisotropic! Resample the volume")            
  
        if axisIndex == 0:
          PixelDepthMm = spacing[0] # get mm for length
          PixelHeightMm = spacing[2]
          PixelWidthMm = spacing[1]
          areaOfPixelMm2 = PixelHeightMm * PixelWidthMm
          unitOfPixelMm4 = PixelHeightMm**2 * PixelWidthMm**2
        elif axisIndex == 1:
          PixelDepthMm = spacing[1] # get mm for length
          PixelHeightMm = spacing[2]
          PixelWidthMm = spacing[0]
          areaOfPixelMm2 = PixelHeightMm * PixelWidthMm
          unitOfPixelMm4 = PixelHeightMm**2 * PixelWidthMm**2
        elif axisIndex == 2:
          PixelDepthMm = spacing[2] # get mm for length
          PixelHeightMm = spacing[1]
          PixelWidthMm = spacing[0]
          areaOfPixelMm2 = PixelHeightMm * PixelWidthMm
          unitOfPixelMm4 = PixelHeightMm**2 * PixelWidthMm**2

        for i in sampleSlices:
          if axisIndex == 0:
            slicetemp = narray[:, :, i] # get the ijk coordinates for all voxels in the label map
            CSA = np.count_nonzero(narray[:,:,i])
            if volumeNode != None and IntensitycheckBox == True:
              meanIntensity = np.mean(voxelArray[:,:,i][np.where(voxelArray[:,:,i])]) 
          elif axisIndex == 1:
            slicetemp = narray[:, i, :] # get the ijk coordinates for all voxels in the label map     
            CSA = np.count_nonzero(narray[:, i, :])
            if volumeNode != None and IntensitycheckBox == True:
              meanIntensity = np.mean(voxelArray[:,i,:][np.where(voxelArray[:,i,:])]) 
          elif axisIndex == 2:
            slicetemp = narray[i, :, :] # get the ijk coordinates for all voxels in the label map
            CSA = np.count_nonzero(narray[i, :, :])
            if volumeNode != None and IntensitycheckBox == True:
              meanIntensity = np.mean(voxelArray[i,:,:][np.where(voxelArray[i, :, :])]) 

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

          if np.count_nonzero(slicetemp) == 0:
            PerimArray.InsertNextValue(0)
            CircularityArray.InsertNextValue(0)
           
          # calculate perimeter
          elif segmentID == segmentNode:
            startx = min(coords_Ijk[0])  
            starty = max(coords_Ijk[1][coords_Ijk[0] == startx])
            perimx = startx
            perimy = starty
            prevx = startx
            prevy = starty
            dire = "N"
          
            while True:
            
              if dire == "N":
                quad = "Q1"
              elif dire == "NE" or dire == "E":
                quad = "Q2"
              elif dire == "SE" or dire == "S":
                quad = "Q3"
              elif dire == "SW":
                quad = "Q4"
              elif dire == "W" or dire == "NW":
                quad = "Q5"
              
              right = coords_Ijk[1][coords_Ijk[0]==prevx+1]        
              vert = coords_Ijk[1][coords_Ijk[0]==prevx] 
              left = coords_Ijk[1][coords_Ijk[0]==prevx-1]   
                        
              if quad == "Q1":
                if any(left == prevy):
                  dire = "W"
                  perimx = np.append(perimx,prevx-1)
                  perimy = np.append(perimy,prevy)
                  prevx = prevx-1
                  prevy = prevy               
                elif any(left == prevy+1):
                  dire = "NW"
                  perimx = np.append(perimx,prevx-1)
                  perimy = np.append(perimy,prevy+1)
                  prevx = prevx-1
                  prevy = prevy+1   
                elif any(vert == prevy+1):
                  dire = "N"
                  perimx = np.append(perimx,prevx)
                  perimy = np.append(perimy,prevy+1)
                  prevx = prevx
                  prevy = prevy+1 
                elif any(right == prevy+1):
                  dire = "NE"
                  perimx = np.append(perimx,prevx+1)
                  perimy = np.append(perimy,prevy+1)
                  prevx = prevx+1
                  prevy = prevy+1  
                elif any(right == prevy):
                  dire = "E"
                  perimx = np.append(perimx,prevx+1)
                  perimy = np.append(perimy,prevy)
                  prevx = prevx+1
                  prevy = prevy 
                elif any(right == prevy-1):
                  dire = "SE"
                  perimx = np.append(perimx,prevx+1)
                  perimy = np.append(perimy,prevy-1)
                  prevx = prevx+1
                  prevy = prevy-1 
                elif any(vert == prevy-1):
                  dire = "S"
                  perimx = np.append(perimx,prevx)
                  perimy = np.append(perimy,prevy-1)
                  prevx = prevx
                  prevy = prevy-1 
                elif any(left == prevy -1):
                  dire = "SW"
                  perimx = np.append(perimx,prevx-1)
                  perimy = np.append(perimy,prevy-1)
                  prevx = prevx-1
                  prevy = prevy-1 

              if quad == "Q2":
                if any(left == prevy+1):
                  dire = "NW"
                  perimx = np.append(perimx,prevx-1)
                  perimy = np.append(perimy,prevy+1)
                  prevx = prevx-1
                  prevy = prevy+1   
                elif any(vert == prevy+1):
                  dire = "N"
                  perimx = np.append(perimx,prevx)
                  perimy = np.append(perimy,prevy+1)
                  prevx = prevx
                  prevy = prevy+1 
                elif any(right == prevy+1):
                  dire = "NE"
                  perimx = np.append(perimx,prevx+1)
                  perimy = np.append(perimy,prevy+1)
                  prevx = prevx+1
                  prevy = prevy+1  
                elif any(right == prevy):
                  dire = "E"
                  perimx = np.append(perimx,prevx+1)
                  perimy = np.append(perimy,prevy)
                  prevx = prevx+1
                  prevy = prevy 
                elif any(right == prevy-1):
                  dire = "SE"
                  perimx = np.append(perimx,prevx+1)
                  perimy = np.append(perimy,prevy-1)
                  prevx = prevx+1
                  prevy = prevy-1 
                elif any(vert == prevy-1):
                  dire = "S"
                  perimx = np.append(perimx,prevx)
                  perimy = np.append(perimy,prevy-1)
                  prevx = prevx
                  prevy = prevy-1 
                elif any(left == prevy -1):
                  dire = "SW"
                  perimx = np.append(perimx,prevx-1)
                  perimy = np.append(perimy,prevy-1)
                  prevx = prevx-1
                  prevy = prevy-1 
                elif any(left == prevy):
                  dire = "W"
                  perimx = np.append(perimx,prevx-1)
                  perimy = np.append(perimy,prevy)
                  prevx = prevx-1
                  prevy = prevy 
                
                
              if quad == "Q3":
                if any(right == prevy+1):
                  dire = "NE"
                  perimx = np.append(perimx,prevx+1)
                  perimy = np.append(perimy,prevy+1)
                  prevx = prevx+1
                  prevy = prevy+1  
                elif any(right == prevy):
                  dire = "E"
                  perimx = np.append(perimx,prevx+1)
                  perimy = np.append(perimy,prevy)
                  prevx = prevx+1
                  prevy = prevy 
                elif any(right == prevy-1):
                  dire = "SE"
                  perimx = np.append(perimx,prevx+1)
                  perimy = np.append(perimy,prevy-1)
                  prevx = prevx+1
                  prevy = prevy-1 
                elif any(vert == prevy-1):
                  dire = "S"
                  perimx = np.append(perimx,prevx)
                  perimy = np.append(perimy,prevy-1)
                  prevx = prevx
                  prevy = prevy-1 
                elif any(left == prevy -1):
                  dire = "SW"
                  perimx = np.append(perimx,prevx-1)
                  perimy = np.append(perimy,prevy-1)
                  prevx = prevx-1
                  prevy = prevy-1 
                elif any(left == prevy):
                  dire = "W"
                  perimx = np.append(perimx,prevx-1)
                  perimy = np.append(perimy,prevy)
                  prevx = prevx-1
                  prevy = prevy              
                elif any(left == prevy +1):
                  dire = "NW"
                  perimx = np.append(perimx,prevx-1)
                  perimy = np.append(perimy,prevy+1)
                  prevx = prevx-1
                  prevy = prevy+1   
                elif any(vert == prevy+1):
                  dire = "N"
                  perimx = np.append(perimx,prevx)
                  perimy = np.append(perimy,prevy+1)
                  prevx = prevx
                  prevy = prevy+1 

              if quad == "Q4":
                if any(right == prevy-1):
                  dire = "SE"
                  perimx = np.append(perimx,prevx+1)
                  perimy = np.append(perimy,prevy-1)
                  prevx = prevx+1
                  prevy = prevy-1 
                elif any(vert == prevy-1):
                  dire = "S"
                  perimx = np.append(perimx,prevx)
                  perimy = np.append(perimy,prevy-1)
                  prevx = prevx
                  prevy = prevy-1 
                elif any(left == prevy -1):
                  dire = "SW"
                  perimx = np.append(perimx,prevx-1)
                  perimy = np.append(perimy,prevy-1)
                  prevx = prevx-1
                  prevy = prevy-1 
                elif any(left == prevy):
                  dire = "W"
                  perimx = np.append(perimx,prevx-1)
                  perimy = np.append(perimy,prevy)
                  prevx = prevx-1
                  prevy = prevy               
                elif any(left == prevy +1):
                  dire = "NW"
                  perimx = np.append(perimx,prevx-1)
                  perimy = np.append(perimy,prevy+1)
                  prevx = prevx-1
                  prevy = prevy+1   
                elif any(vert == prevy+1):
                  dire = "N"
                  perimx = np.append(perimx,prevx)
                  perimy = np.append(perimy,prevy+1)
                  prevx = prevx
                  prevy = prevy+1 
                elif any(right == prevy+1):
                  dire = "NE"
                  perimx = np.append(perimx,prevx+1)
                  perimy = np.append(perimy,prevy+1)
                  prevx = prevx+1
                  prevy = prevy+1  
                elif any(right == prevy):
                  dire = "E"
                  perimx = np.append(perimx,prevx+1)
                  perimy = np.append(perimy,prevy)
                  prevx = prevx+1
                  prevy = prevy 

              if quad == "Q5":
                if any(left == prevy -1):
                  dire = "SW"
                  perimx = np.append(perimx,prevx-1)
                  perimy = np.append(perimy,prevy-1)
                  prevx = prevx-1
                  prevy = prevy-1 
                elif any(left == prevy):
                  dire = "W"
                  perimx = np.append(perimx,prevx-1)
                  perimy = np.append(perimy,prevy)
                  prevx = prevx-1
                  prevy = prevy               
                elif any(left == prevy +1):
                  dire = "NW"
                  perimx = np.append(perimx,prevx-1)
                  perimy = np.append(perimy,prevy+1)
                  prevx = prevx-1
                  prevy = prevy+1   
                elif any(vert == prevy+1):
                  dire = "N"
                  perimx = np.append(perimx,prevx)
                  perimy = np.append(perimy,prevy+1)
                  prevx = prevx
                  prevy = prevy+1              
                elif any(right == prevy+1):
                  dire = "NE"
                  perimx = np.append(perimx,prevx+1)
                  perimy = np.append(perimy,prevy+1)
                  prevx = prevx+1
                  prevy = prevy+1  
                elif any(right == prevy):
                  dire = "E"
                  perimx = np.append(perimx,prevx+1)
                  perimy = np.append(perimy,prevy)
                  prevx = prevx+1
                  prevy = prevy 
                elif any(right == prevy-1):
                  dire = "SE"
                  perimx = np.append(perimx,prevx+1)
                  perimy = np.append(perimy,prevy-1)
                  prevx = prevx+1
                  prevy = prevy-1 
                elif any(vert == prevy-1):
                  dire = "S"
                  perimx = np.append(perimx,prevx)
                  perimy = np.append(perimy,prevy-1)
                  prevx = prevx
                  prevy = prevy-1 
                
              if prevx == startx and prevy == starty:
                break
               
            perimeter = 0
            if isinstance(perimx,np.int64):
              perimeter = 4
            else:
              for p in range(len(perimx)-1):
                perimeter = perimeter +  np.sqrt((perimx[p+1]-perimx[p])**2+(perimy[p+1]-perimy[p])**2)
              perimeter = perimeter + np.sqrt((perimx[0]-perimx[len(perimx)-1])**2+(perimy[0]-perimy[len(perimy)-1])**2)
            PerimArray.InsertNextValue(perimeter * PixelWidthMm)
            Circularity = 4*np.pi*CSA*areaOfPixelMm2/(perimeter*PixelWidthMm)**2
            CircularityArray.InsertNextValue(Circularity)
          
          # calculate maximum diameter manually using all points
          # TODO: calculate convex hull without python packages
          #if segmentID == segmentNode:
          #  Fdiam = 0
          #  if np.count_nonzero(slicetemp) == 0:
          #    Fdiam = 0
          #  elif isinstance(coords_Ijk[0],np.int64):
          #    Fdiam = 1
          #  elif len(coords_Ijk[0]) == 2:
          #    Fdiam = 2
          #  elif len(coords_Ijk[0]) >= 3: 
          #    for h in range(len(coords_Ijk[0])):
          #      x1 = coords_Ijk[0][h]
          #      y1 = coords_Ijk[1][h]
          #      for j in range(len(coords_Ijk[0])):
          #        x2 = coords_Ijk[0][j]
          #        y2 = coords_Ijk[1][j]
          #        Fdiam = max(Fdiam, np.sqrt((x2-x1)**2 +(y2-y1)**2) * PixelWidthMm)
          
          # calculate maximum diameter from convex hull
          if segmentID == segmentNode:
            from scipy.spatial.qhull import ConvexHull
            from scipy.spatial.distance import euclidean
            Fdiam = 0
            if np.count_nonzero(slicetemp) == 0:
              Fdiam = 0
            elif isinstance(coords_Ijk[0],np.int64):
              Fdiam = 1
            elif len(coords_Ijk[0]) == 2:
              Fdiam = 2
            elif len(coords_Ijk[0]) >= 3 and len(set(coords_Ijk[0])) > 1  and len(set(coords_Ijk[1])) > 1: 
              points = np.concatenate((coords_Ijk[0][:,None],coords_Ijk[1][:,None]),axis = 1)
              hull = ConvexHull(points)
              Fdiam = 0
              for h in hull.vertices:
                pt1 = points[h]
                for j in hull.vertices:
                  pt2 = points[j]
                  Fdiam = max(Fdiam, np.sqrt((pt2[0]-pt1[0])**2 +(pt2[1]-pt1[1])**2)* PixelWidthMm)
            elif len(coords_Ijk[0]) >= 3 and len(set(coords_Ijk[0])) == 1:  
              Fdiam = max(coords_Ijk[1]) - min(coords_Ijk[1])
            elif len(coords_Ijk[1]) >= 3 and len(set(coords_Ijk[1])) == 1:  
              Fdiam = max(coords_Ijk[0]) - min(coords_Ijk[0])
            FeretArray.InsertNextValue(Fdiam)
            # find smallest, largest diameter to calculate aspect ratio
            sampleMin = int(max(sampleSlices)*.05)
            sampleMax = int(max(sampleSlices)*.95)
            if i >= sampleMin and i <= sampleMax:
              if FdiamMin == None and Fdiam > 0:
                FdiamMin = (numSlices * PixelDepthMm)
              if FdiamMin != None and Fdiam > 0:
                FdiamMin = min(FdiamMin,Fdiam)
                AR = (numSlices * PixelDepthMm)/FdiamMin
                if AR > 10:
                  eulerflag = 0     
                            
          # set up variables for calculations
          Sn = np.count_nonzero(slicetemp)
          Sx = sum(coords_Ijk[0])
          Sy = sum(coords_Ijk[1])
          
          if Sn == 0:
            if segmentID == segmentNode:
              CxArray.InsertNextValue(0)
              CyArray.InsertNextValue(0)
              JzArray.InsertNextValue(0)
              ZpolArray.InsertNextValue(0)
                            
              ThetaMinArray.InsertNextValue(0)       
              ThetaMaxArray.InsertNextValue(0)       
              ImajorArray.InsertNextValue(0)
              IminorArray.InsertNextValue(0)
              RmajorArray.InsertNextValue(0)
              RminorArray.InsertNextValue(0)
              RmaxArray.InsertNextValue(0)
              ZmajorArray.InsertNextValue(0)
              ZminorArray.InsertNextValue(0)
              if SummerscheckBox == True:
                ImajorArray_Summers.InsertNextValue(0)
                IminorArray_Summers.InsertNextValue(0)
                ZmajorArray_Summers.InsertNextValue(0)
                ZminorArray_Summers.InsertNextValue(0)
                JzArray_Summers.InsertNextValue(0)
                ZpolArray_Summers.InsertNextValue(0)
              if DoubecheckBox == True:
                ImajorArray_Doube.InsertNextValue(0)
                IminorArray_Doube.InsertNextValue(0)
                ZmajorArray_Doube.InsertNextValue(0)
                ZminorArray_Doube.InsertNextValue(0)
                JzArray_Doube.InsertNextValue(0)
                ZpolArray_Doube.InsertNextValue(0)
              if OrientationcheckBox == True: 
                IlaArray.InsertNextValue(0)
                InaArray.InsertNextValue(0)
                ZnaArray.InsertNextValue(0)
                ZlaArray.InsertNextValue(0)
                RnaArray.InsertNextValue(0)
                RlaArray.InsertNextValue(0)
                if DoubecheckBox == True:
                  InaArray_Doube.InsertNextValue(0)
                  IlaArray_Doube.InsertNextValue(0)
                  ZnaArray_Doube.InsertNextValue(0)
                  ZlaArray_Doube.InsertNextValue(0)
                if SummerscheckBox == True:
                  InaArray_Summers.InsertNextValue(0)
                  IlaArray_Summers.InsertNextValue(0)
                  ZnaArray_Summers.InsertNextValue(0)
                  ZlaArray_Summers.InsertNextValue(0)

          elif Sn > 0:
            # calculate centroid coordinates
            Cx = Sx / Sn
            Cy = Sy / Sn 
            if segmentID == segmentNode:
            # add values to calculations                       
              CxArray.InsertNextValue((Cx))
              CyArray.InsertNextValue((Cy))
            
            # calculate second moment of area along horizontal and vertical axes
            Ix = 0
            for  s in range(Sn):
              Ix = Ix + 1/12 + (Cy - coords_Ijk[1][s])**2
               
            Iy = 0
            for  s in range(Sn):
              Iy = Iy + 1/12 + (Cx - coords_Ijk[0][s])**2
              
            # calculated polar moment of inertia
            Jz = 0
            for s in range(Sn):
              Jz = Jz + ((Cx - coords_Ijk[0][s])**2 + (Cy - coords_Ijk[1][s])**2)

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
              Imajor = Imajor+ (rad + 1/12)
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
              Iminor = Iminor + (rad + 1/12)
              Rminor = max(Rminor,np.sqrt(rad))
            if Rminor == 0:
              Zminor = Iminor
            else:    
              Zminor = Iminor/Rminor 
              
            Zpol = 0
            Maxrad = 0
            for s in range(Sn):
              Maxrad = max(Maxrad, np.sqrt((coords_Ijk[0][s]-Cx)**2 + (coords_Ijk[1][s]-Cy)**2))
            Zpol = Jz/Maxrad     
                                  
            if segmentID == segmentNode:
            # add values to calculations                       
              ThetaMinArray.InsertNextValue((Theta + np.pi/2)*180/np.pi)       
              ThetaMaxArray.InsertNextValue(Theta*180/np.pi)
              JzArray.InsertNextValue(Jz * unitOfPixelMm4)   
              ImajorArray.InsertNextValue(Imajor * unitOfPixelMm4)
              IminorArray.InsertNextValue(Iminor * unitOfPixelMm4)
              RmajorArray.InsertNextValue(Rmajor * PixelWidthMm)
              RminorArray.InsertNextValue(Rminor * PixelWidthMm)
              ZmajorArray.InsertNextValue(Zmajor * unitOfPixelMm4 / PixelWidthMm)
              ZminorArray.InsertNextValue(Zminor * unitOfPixelMm4 / PixelWidthMm)
              ZpolArray.InsertNextValue(Zpol * unitOfPixelMm4 / PixelWidthMm)
              RmaxArray.InsertNextValue(Maxrad * PixelWidthMm)
            
              # do material normalization          
              if SummerscheckBox == True:
                ImajorArray_Summers.InsertNextValue(Imajor/((np.pi * (np.sqrt(CSA/np.pi))**4) / 4))
                IminorArray_Summers.InsertNextValue(Iminor/((np.pi * (np.sqrt(CSA/np.pi))**4) / 4))
                ZmajorArray_Summers.InsertNextValue(Zmajor/((np.pi * (np.sqrt(CSA/np.pi))**3) / 4))
                ZminorArray_Summers.InsertNextValue(Zminor/((np.pi * (np.sqrt(CSA/np.pi))**3) / 4))
                JzArray_Summers.InsertNextValue(Jz/((2*np.sqrt(CSA/np.pi))**4 * np.pi / 32))
                ZpolArray_Doube.InsertNextValue(Jz/np.sqrt(CSA/np.pi))
              
              # do size correction
              if DoubecheckBox == True:
                ImajorArray_Doube.InsertNextValue(Imajor**(1/4) / numSlices)
                IminorArray_Doube.InsertNextValue(Iminor**(1/4) / numSlices)
                ZmajorArray_Doube.InsertNextValue(Zmajor**(1/3) / numSlices)
                ZminorArray_Doube.InsertNextValue(Zminor**(1/3) / numSlices)
                JzArray_Doube.InsertNextValue(Jz**(1/4) / numSlices)
                ZpolArray_Doube.InsertNextValue(Zpol**(1/4) / numSlices)
           
              # use custom neutral axis  
              if OrientationcheckBox == True: 
                Theta = angle * np.pi/180  

                #neutral axis
                Ina = 0
                Rna = 0
                for s in range(Sn): 
                  rad = ((coords_Ijk[1][s]-Cy)*np.cos(Theta) - (coords_Ijk[0][s]-Cx)*np.sin(Theta))**2
                  Ina = Ina +(rad + 1/12)
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
                  Ila = Ila+ (rad + 1/12)
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
         compactness = float(areaArray.GetTuple(s)[0])/float(TotalAreaArray.GetTuple(s)[0])
         if compactness > 1:
           CompactnessArray.InsertNextValue(float(1))
         else:
           CompactnessArray.InsertNextValue(float(areaArray.GetTuple(s)[0])/float(TotalAreaArray.GetTuple(s)[0]))

      
      try:
        if SMAcheckBox_1 == True or MODcheckBox_1 == True:
          if eulerflag == 0:
            ResultsText.setText("{} aspect ratio: {}.".format(segmentationNode.GetSegmentation().GetSegment(segmentNode).GetName(),round(AR,2)))   
            ResultsText.setStyleSheet("background: transparent; border: transparent")
          if eulerflag == 1:
            ResultsText.setText("Warning! {} aspect ratio ({}) is less than 10. The no-shear assumption may be violated.".format(segmentationNode.GetSegmentation().GetSegment(segmentNode).GetName(),round(AR,2)))
            ResultsText.setStyleSheet("color: red; background: transparent; border: transparent")
        elif OrientationcheckBox == True and SMAcheckBox_1 == True or MODcheckBox_1 == True: 
          if eulerflag == 0:
            ResultsText.setText("{} aspect ratio: {}.".format(segmentationNode.GetSegmentation().GetSegment(segmentNode).GetName(),round(AR,2)))   
            ResultsText.setStyleSheet("background: transparent; border: transparent")
          if eulerflag == 1:
            ResultsText.setText("Warning! {} aspect ratio ({}) is less than 10. The no-shear assumption may be violated.".format(segmentationNode.GetSegmentation().GetSegment(segmentNode).GetName(),round(AR,2)))
            ResultsText.setStyleSheet("color: red; background: transparent; border: transparent")
        else: ResultsText.clear()
      except AttributeError:
        pass
        
      # adds table column for various arrays
      tableNode.AddColumn(SegmentNameArray)
      tableNode.SetColumnDescription(SegmentNameArray.GetName(), "Segment name")  
      
      tableNode.AddColumn(sliceNumberArray)
      tableNode.SetColumnDescription(sliceNumberArray.GetName(), "Corresponding slice index on the resampled volume")
      
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
      
      if PerimcheckBox == True:
        tableNode.AddColumn(PerimArray)
        tableNode.SetColumnUnitLabel(PerimArray.GetName(), "mm")  # TODO: use length unit
        tableNode.SetColumnDescription(PerimArray.GetName(), "Perimeter of the section")  

      if volumeNode != None and IntensitycheckBox == True:
        tableNode.AddColumn(meanIntensityArray)
        tableNode.SetColumnDescription(LengthArray.GetName(), "Mean pixel brightness") 

      if CSAcheckBox == True:    
        tableNode.AddColumn(areaArray)
        tableNode.SetColumnUnitLabel(areaArray.GetName(), "mm^2")  # TODO: use length unit
        tableNode.SetColumnDescription(areaArray.GetName(), "Cross-sectional area")  

      if CompactnesscheckBox == True:    
        tableNode.AddColumn(CompactnessArray)
        tableNode.SetColumnDescription(CompactnessArray.GetName(), "Compactness calculated as CSA/TCSA")    

      if CentroidcheckBox == True:    
        tableNode.AddColumn(CxArray)
        tableNode.SetColumnUnitLabel(CxArray.GetName(), "none")  # TODO: use length unit
        tableNode.SetColumnDescription(CxArray.GetName(), "x-coordinate of the centroid in IJK format on the resampled volume")  
        
        tableNode.AddColumn(CyArray)
        tableNode.SetColumnUnitLabel(CyArray.GetName(), "none")  # TODO: use length unit
        tableNode.SetColumnDescription(CyArray.GetName(), "y-coordinate of the centroid in IJK format on the resampled volume")         
                
      if ThetacheckBox == True:    
        tableNode.AddColumn(ThetaMinArray)
        tableNode.SetColumnUnitLabel(ThetaMinArray.GetName(), "degrees")  # TODO: use length unit
        tableNode.SetColumnDescription(ThetaMinArray.GetName(), "Angle between the minor principal axis and the horizontal (right side), in a clockwise direction")  
        
        #tableNode.AddColumn(ThetaMaxArray)
        #tableNode.SetColumnUnitLabel(ThetaMaxArray.GetName(), "degrees")  # TODO: use length unit
        #tableNode.SetColumnDescription(ThetaMaxArray.GetName(), "Angle of the major principal axis")  
      
      if SMAcheckBox_1 == True:  
        tableNode.AddColumn(IminorArray)
        tableNode.SetColumnUnitLabel(IminorArray.GetName(), "mm^4")  # TODO: use length unit
        tableNode.SetColumnDescription(IminorArray.GetName(), "Second moment of area around the minor principal axis (larger I)")
       
        tableNode.AddColumn(ImajorArray)
        tableNode.SetColumnUnitLabel(ImajorArray.GetName(), "mm^4")  # TODO: use length unit
        tableNode.SetColumnDescription(ImajorArray.GetName(), "Second moment of area around the major principal axis (smaller I)")

      if MODcheckBox_1 == True:
        tableNode.AddColumn(ZminorArray)
        tableNode.SetColumnUnitLabel(ZminorArray.GetName(), "mm^3")  # TODO: use length unit
        tableNode.SetColumnDescription(ZminorArray.GetName(), "Section modulus around the minor principal axis (larger Z)")
      
        tableNode.AddColumn(ZmajorArray)
        tableNode.SetColumnUnitLabel(ZmajorArray.GetName(), "mm^3")  # TODO: use length unit
        tableNode.SetColumnDescription(ZmajorArray.GetName(), "Section modulus around the major principal axis (smaller Z)")

      if RcheckBox == True:  
        tableNode.AddColumn(RminorArray)
        tableNode.SetColumnUnitLabel(RminorArray.GetName(), "mm")  # TODO: use length unit
        tableNode.SetColumnDescription(RminorArray.GetName(), "Max distance from the minor principal axis") 
         
        tableNode.AddColumn(RmajorArray)
        tableNode.SetColumnUnitLabel(RmajorArray.GetName(), "mm")  # TODO: use length unit
        tableNode.SetColumnDescription(RmajorArray.GetName(), "Max distance from the major principal axis") 

      if JzcheckBox == True:
        tableNode.AddColumn(JzArray)
        tableNode.SetColumnUnitLabel(JzArray.GetName(), "mm^4")  # TODO: use length unit
        tableNode.SetColumnDescription(JzArray.GetName(), "Polar moment of inertia")

      if ZpolcheckBox == True:
        tableNode.AddColumn(ZpolArray)
        tableNode.SetColumnUnitLabel(ZpolArray.GetName(), "mm^3")  # TODO: use length unit
        tableNode.SetColumnDescription(ZpolArray.GetName(), "Polar section modulus")

      if RcheckBox == True and ZpolcheckBox == True:  
        tableNode.AddColumn(RmaxArray)
        tableNode.SetColumnUnitLabel(RmaxArray.GetName(), "mm")  # TODO: use length unit
        tableNode.SetColumnDescription(RmaxArray.GetName(), "Max radius from the centroid") 

      if OrientationcheckBox == True and SMAcheckBox_1 == True:  
        tableNode.AddColumn(InaArray)
        tableNode.SetColumnUnitLabel(InaArray.GetName(), "mm^4")  # TODO: use length unit
        tableNode.SetColumnDescription(InaArray.GetName(), "Second moment of area around the neutral axis")
        
        tableNode.AddColumn(IlaArray)
        tableNode.SetColumnUnitLabel(IlaArray.GetName(), "mm^4")  # TODO: use length unit
        tableNode.SetColumnDescription(IlaArray.GetName(), "Second moment of area around the loading axis")
              
      if OrientationcheckBox == True and MODcheckBox_1 == True:
        tableNode.AddColumn(ZnaArray)
        tableNode.SetColumnUnitLabel(ZnaArray.GetName(), "mm^3")  # TODO: use length unit
        tableNode.SetColumnDescription(ZnaArray.GetName(), "Section modulus around the neutral axis")
        
        tableNode.AddColumn(ZlaArray)
        tableNode.SetColumnUnitLabel(ZlaArray.GetName(), "mm^3")  # TODO: use length unit
        tableNode.SetColumnDescription(ZlaArray.GetName(), "Section modulus around the loading axis")
        
      if RcheckBox == True and OrientationcheckBox == True:
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
      
      if DoubecheckBox == True and SMAcheckBox_1 == True and OrientationcheckBox == True:
        tableNode.AddColumn(InaArray_Doube)
        tableNode.SetColumnUnitLabel(InaArray_Doube.GetName(), "none")  # TODO: use length unit
        tableNode.SetColumnDescription(InaArray_Doube.GetName(), "Ina^(1/4)/Length")
        
        tableNode.AddColumn(IlaArray_Doube)
        tableNode.SetColumnUnitLabel(IlaArray_Doube.GetName(), "none")  # TODO: use length unit
        tableNode.SetColumnDescription(IlaArray_Doube.GetName(), "Ila^(1/4)/Length")

      if DoubecheckBox == True and MODcheckBox_1 == True and OrientationcheckBox == True:
        tableNode.AddColumn(ZlaArray_Doube)
        tableNode.SetColumnUnitLabel(ZlaArray_Doube.GetName(), "none")  # TODO: use length unit
        tableNode.SetColumnDescription(ZlaArray_Doube.GetName(), "Zla^(1/3)/Length")  
        
        tableNode.AddColumn(ZnaArray_Doube)
        tableNode.SetColumnUnitLabel(ZnaArray_Doube.GetName(), "none")  # TODO: use length unit
        tableNode.SetColumnDescription(ZnaArray_Doube.GetName(), "Zna^(1/3)/Length")

      if DoubecheckBox == True and JzcheckBox == True:
        tableNode.AddColumn(JzArray_Doube)
        tableNode.SetColumnUnitLabel(JzArray_Doube.GetName(), "none")  # TODO: use length unit
        tableNode.SetColumnDescription(JzArray_Doube.GetName(), "Jz^(1/4)/Length")
   
      if DoubecheckBox == True and ZpolcheckBox == True:
        tableNode.AddColumn(ZpolArray_Doube)
        tableNode.SetColumnUnitLabel(ZpolArray_Doube.GetName(), "none")  # TODO: use length unit
        tableNode.SetColumnDescription(ZpolArray_Doube.GetName(), "Zpol^(1/3)/Length")  

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

      if SummerscheckBox == True and JzcheckBox == True:
        tableNode.AddColumn(JzArray_Summers)
        tableNode.SetColumnUnitLabel(JzArray_Summers.GetName(), "none")  # TODO: use length unit
        tableNode.SetColumnDescription(JzArray_Summers.GetName(), "Jz divided by the polar moment of inertia of a solid circle with the same cross-sectional area") 

      if SummerscheckBox == True and ZpolcheckBox == True:
        tableNode.AddColumn(ZpolArray_Summers)
        tableNode.SetColumnUnitLabel(ZpolArray_Summers.GetName(), "none")  # TODO: use length unit
        tableNode.SetColumnDescription(ZpolArray_Summers.GetName(), "Zpol divided by the polar section modulus of a solid circle with the same cross-sectional area")    
        
      if SummerscheckBox == True and SMAcheckBox_1 == True and OrientationcheckBox == True:
        tableNode.AddColumn(InaArray_Summers)
        tableNode.SetColumnUnitLabel(InaArray_Summers.GetName(), "none")  # TODO: use length unit
        tableNode.SetColumnDescription(InaArray_Summers.GetName(), "Ina divided by the second moment of area of a solid circle with the same cross-sectional area")
        
        tableNode.AddColumn(IlaArray_Summers)
        tableNode.SetColumnUnitLabel(IlaArray_Summers.GetName(), "none")  # TODO: use length unit
        tableNode.SetColumnDescription(IlaArray_Summers.GetName(), "Ila divided by the second moment of area of a solid circle with the same cross-sectional area") 
        
      if SummerscheckBox == True and MODcheckBox_1 == True and OrientationcheckBox == True:
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
      if OrientationcheckBox == True and SMAcheckBox_1 == True: 
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
          plotSeriesNode3 = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotSeriesNode", segName + " CSA (mm^2)")
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
      slicer.mrmlScene.RemoveNode(slicer.mrmlScene.GetFirstNodeByName("TempAnnotationROI"))

      # move segment back to where it was originally
      if trans != None:
        trans_new = slicer.mrmlScene.GetNodeByID(segmentationNode.GetTransformNodeID())
        trans_new.SetMatrixTransformToParent(og_matrix) 
      # Change layout to include plot and table      
      customLayout = """
      <layout type=\"vertical\" split=\"true\" >
       <item splitSize=\"500\">
        <layout type=\"horizontal\">
         <item>
          <view class=\"vtkMRMLViewNode\" singletontag=\"1\">
           <property name=\"viewlabel\" action=\"default\">1</property>
          </view>
         </item>
         <item>
          <view class=\"vtkMRMLPlotViewNode\" singletontag=\"PlotView1\">
           <property name=\"viewlabel\" action=\"default\">P</property>
          </view>
         </item>
        </layout>
       </item>
       <item splitSize=\"500\">
        <layout type=\"horizontal\">
         <item>
          <view class=\"vtkMRMLSliceNode\" singletontag=\"Red\">
           <property name=\"orientation\" action=\"default\">Axial</property>
           <property name=\"viewlabel\" action=\"default\">R</property>
           <property name=\"viewcolor\" action=\"default\">#F34A33</property>
          </view>
         </item>   
         <item>
          <view class=\"vtkMRMLSliceNode\" singletontag=\"Yellow\">
           <property name=\"orientation\" action=\"default\">Axial</property>
           <property name=\"viewlabel\" action=\"default\">Y</property>
           <property name=\"viewcolor\" action=\"default\">#EDD54C</property>
          </view>
         </item>    
         <item>
          <view class=\"vtkMRMLSliceNode\" singletontag=\"Green\">
           <property name=\"orientation\" action=\"default\">Axial</property>
           <property name=\"viewlabel\" action=\"default\">G</property>
           <property name=\"viewcolor\" action=\"default\">#6EB04B</property>
          </view>
         </item>  
        </layout>
       </item>
       <item splitSize=\"500\">
        <view class=\"vtkMRMLTableViewNode\" singletontag=\"TableView1\">
         <property name=\"viewlabel\" action=\"default\">T</property>
        </view>
       </item>
      </layout>
      """
      
      customLayoutId=666

      layoutManager = slicer.app.layoutManager()
      layoutManager.layoutLogic().GetLayoutNode().AddLayoutDescription(customLayoutId, customLayout)

      # Switch to the new custom layout
      layoutManager.setLayout(customLayoutId)
      plotWidget = layoutManager.plotWidget(0)
      plotViewNode = plotWidget.mrmlPlotViewNode()
      plotViewNode.SetPlotChartNodeID(plotChartNode.GetID())      
      tableWidget = layoutManager.tableWidget(0)
      tableWidget.tableView().setMRMLTableNode(tableNode)
      
      
    logging.info('Processing completed')
    end = time.time()
    TotalTime = np.round(end - start,2)
    print("Total time elapsed:", TotalTime, "seconds")


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
    masterVolumeNode = sampleDataLogic.downloadMRBrainTumor1()
    #sampleDataLogic.downloadDentalSurgery()
    #masterVolumeNode = slicer.util.getFirstNodeByName("PreDentalSurgery")

    # Create segmentation
    segmentationNode = slicer.vtkMRMLSegmentationNode()
    slicer.mrmlScene.AddNode(segmentationNode)
    segmentationNode.CreateDefaultDisplayNodes()  # only needed for display
    segmentationNode.SetReferenceImageGeometryParameterFromVolumeNode(masterVolumeNode)

    # Create a sphere shaped segment
    radius = 30
    tumorSeed = vtk.vtkSphereSource()
    tumorSeed.SetCenter(-6, 30, 28)
    #tumorSeed.SetCenter(-90, -90, 80)
    tumorSeed.SetRadius(radius)
    tumorSeed.SetPhiResolution(120)
    tumorSeed.SetThetaResolution(120)
    tumorSeed.Update()
    segmentId = segmentationNode.AddSegmentFromClosedSurfaceRepresentation(tumorSeed.GetOutput(), "Tumor",
                                                                           [1.0, 0.0, 0.0])
    segmentId2 = segmentationNode.AddSegmentFromClosedSurfaceRepresentation(tumorSeed.GetOutput(), "Tumor",
                                                                           [1.0, 0.0, 0.0])
    segmentNode = segmentationNode.GetSegmentation().GetSegment(segmentId)                                                                       

    tableNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTableNode", "SegmentGeometry test table")
    plotChartNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotChartNode", "SegmentGeometry test plot")
    
    
    logic = SegmentGeometryLogic()
    logic.run(segmentationNode, segmentId, masterVolumeNode, "S (Red)", 0, tableNode, plotChartNode, True, True, True, False, True, True,
    True, True, 0, True, True, True, True, True, segmentationNode, segmentId, True, True, True)
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
    self.assertTrue(errorPercent < 2.0)
    self.assertTrue(errorPercent2 < 2.0)
    self.assertTrue(errorPercent3 < 2.0)

    self.delayDisplay('Test passed')
