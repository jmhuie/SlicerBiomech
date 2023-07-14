import os
import unittest
import logging
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin

#
# DentalDynamics
#

class DentalDynamics(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Dental Dynamics"  
    self.parent.categories = ["Quantification"] 
    self.parent.dependencies = []  # TODO: add here list of module names that this module requires
    self.parent.contributors = ["Jonathan M. Huie"]  
    self.parent.helpText = """This module uses lever mechanics to calculate tooth stress from segmented teeth and jaws.
    For more information please see the <a href="https://github.com/jmhuie/Slicer-SegmentGeometry">online documentation</a>."""
    self.parent.acknowledgementText = """This module was developed by Jonathan M. Huie. JMH was supported by an NSF Graduate Research Fellowship (DGE-1746914)."""


    # Additional initialization step after application startup is complete
    #slicer.app.connect("startupCompleted()", registerSampleData)

#
# Register sample data sets in Sample Data module
#


#
# DentalDynamicsWidget
#

class DentalDynamicsWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
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
    self._updatingGUIFromParameterNode = False

  def setup(self):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.setup(self)

    # Load widget from .ui file (created by Qt Designer).
    # Additional widgets can be instantiated manually and added to self.layout.
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/DentalDynamics.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
    # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
    # "setMRMLScene(vtkMRMLScene*)" slot.
    uiWidget.setMRMLScene(slicer.mrmlScene)

    # Create logic class. Logic implements all computations that should be possible to run
    # in batch mode, without a graphical user interface.
    self.logic = DentalDynamicsLogic()
        
    # Connections

    # These connections ensure that we update parameter node when scene is closed
    self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
    self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

    # These connections ensure that whenever user changes some settings on the GUI, that is saved in the MRML scene
    # (in the selected parameter node).
    self.ui.segmentationSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.SimpleMarkupsWidget.connect("markupsNodeChanged()", self.updateParameterNodeFromGUI)
    self.ui.SimpleMarkupsWidget.connect("markupsNodeChanged()", self.updateGUIFromParameterNode)
    self.ui.ForceInputSlider.connect("valueChanged(double)", self.updateParameterNodeFromGUI)
    self.ui.AngleInputSlider.connect("valueChanged(double)", self.updateParameterNodeFromGUI)
    self.ui.tableSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.SpecieslineEdit.connect('stateChanged(int)', self.updateParameterNodeFromGUI)
    self.ui.SegmentSelectorWidget.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.SkipSegCheckBox.connect('stateChanged(int)', self.updateParameterNodeFromGUI)

    # Buttons
    self.ui.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.ui.ResetpushButton.connect('clicked(bool)', self.onResetButton)
    self.ui.TemplatepushButton.connect('clicked(bool)', self.onTemplate)
    self.ui.FlipButton.connect('clicked(bool)', self.onFlipResults)
    self.ui.FlipButton.connect('clicked(bool)', self.onApplyButton)
    self.ui.FlipSomeButton.connect('clicked(bool)', self.onFlipSomeResults)
    self.ui.FlipSomeButton.connect('clicked(bool)', self.onApplyButton)
    self.ui.PosVisButton.connect('clicked(bool)', self.onPositionVis)
    self.ui.OutVisButton.connect('clicked(bool)', self.onOutleverVis)
    self.ui.segmentationSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onResetButton)



    # Make sure parameter node is initialized (needed for module reload)
    self.initializeParameterNode()

  def cleanup(self):
    """
    Called when the application closes and the module widget is destroyed.
    """
    self.removeObservers()

  def enter(self):
    """
    Called each time the user opens this module.
    """
    # Make sure parameter node exists and observed
    self.initializeParameterNode()

  def exit(self):
    """
    Called each time the user opens a different module.
    """
    # Do not react to parameter node changes (GUI wlil be updated when the user enters into the module)
    self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

  def onSceneStartClose(self, caller, event):
    """
    Called just before the scene is closed.
    """
    # Parameter node will be reset, do not use it anymore
    self.setParameterNode(None)

  def onSceneEndClose(self, caller, event):
    """
    Called just after the scene is closed.
    """
    # If this module is shown while the scene is closed then recreate a new parameter node immediately
    if self.parent.isEntered:
      self.initializeParameterNode()

  def initializeParameterNode(self):
    """
    Ensure parameter node exists and observed.
    """
    # Parameter node stores all user choices in parameter values, node selections, etc.
    # so that when the scene is saved and reloaded, these settings are restored.

    self.setParameterNode(self.logic.getParameterNode())

    # Select default input nodes if nothing is selected yet to save a few clicks for the user
    #if not self._parameterNode.GetNodeReference("InputVolume"):
    #  firstVolumeNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLScalarVolumeNode")
    #  if firstVolumeNode:
    #    self._parameterNode.SetNodeReferenceID("InputVolume", firstVolumeNode.GetID())

  def setParameterNode(self, inputParameterNode):
    """
    Set and observe parameter node.
    Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
    """

    if inputParameterNode:
      self.logic.setDefaultParameters(inputParameterNode)

    # Unobserve previously selected parameter node and add an observer to the newly selected.
    # Changes of parameter node are observed so that whenever parameters are changed by a script or any other module
    # those are reflected immediately in the GUI.
    if self._parameterNode is not None:
      self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
    self._parameterNode = inputParameterNode
    if self._parameterNode is not None:
      self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

    # Initial GUI update
    self.updateGUIFromParameterNode()

  def updateGUIFromParameterNode(self, caller=None, event=None):
    """
    This method is called whenever parameter node is changed.
    The module GUI is updated to show the current state of the parameter node.
    """

    if self._parameterNode is None or self._updatingGUIFromParameterNode:
      return

    # Make sure GUI changes do not call updateParameterNodeFromGUI (it could cause infinite loop)
    self._updatingGUIFromParameterNode = True

    # Update node selectors and sliders
    wasBlocked = self.ui.segmentationSelector.blockSignals(True)
    self.ui.segmentationSelector.setCurrentNode(self._parameterNode.GetNodeReference("Segmentation"))
    self.ui.segmentationSelector.blockSignals(wasBlocked)

    wasBlocked = self.ui.SegmentSelectorWidget.blockSignals(True)
    self.ui.SegmentSelectorWidget.setCurrentNode(self._parameterNode.GetNodeReference("Segmentation"))
    self.ui.SegmentSelectorWidget.blockSignals(wasBlocked)

    #self.ui.SimpleMarkupsWidget.setCurrentNode(self._parameterNode.GetNodeReference("RefPoints"))
    
    wasBlocked = self.ui.tableSelector.blockSignals(True)
    self.ui.tableSelector.setCurrentNode(self._parameterNode.GetNodeReference("ResultsTable"))
    self.ui.tableSelector.blockSignals(wasBlocked)

    # Update buttons states and tooltips
    if self._parameterNode.GetNodeReference("Segmentation") and self.ui.SimpleMarkupsWidget.currentNode() is not None:
      self.ui.applyButton.toolTip = "Compute tooth stress"
      self.ui.applyButton.enabled = True
    else:
      self.ui.applyButton.toolTip = "Select input and output parameters"
      self.ui.applyButton.enabled = False
      
    if self._parameterNode.GetNodeReference("ResultsTable"):
      self.ui.tableSelector.toolTip = "Edit output table"
    else:
      self.ui.tableSelector.toolTip = "Select output table"
      
    # All the GUI updates are done
    self._updatingGUIFromParameterNode = False

  def updateParameterNodeFromGUI(self, caller=None, event=None):
    """
    This method is called when the user makes any change in the GUI.
    The changes are saved into the parameter node (so that they are restored when the scene is saved and loaded).
    """

    if self._parameterNode is None or self._updatingGUIFromParameterNode:
      return

    wasModified = self._parameterNode.StartModify()  # Modify all properties in a single batch
    self._parameterNode.SetNodeReferenceID("Segmentation", self.ui.segmentationSelector.currentNodeID)
    #self._parameterNode.SetNodeReferenceID("RefPoints", self.ui.SimpleMarkupsWidget.currentNode)
    self._parameterNode.SetParameter("Force", str(self.ui.ForceInputSlider.value))
    self._parameterNode.SetParameter("Angle", str(self.ui.AngleInputSlider.value))
    self._parameterNode.SetNodeReferenceID("ResultsTable", self.ui.tableSelector.currentNodeID)
    

    self._parameterNode.EndModify(wasModified)
    
  def onTemplate(self):
    """
    Run processing when user clicks "Create new reference point list" button.
    """
    pointListNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode", "Dental Dynamics Point List")
    pointListNode.AddControlPoint([0,0,0],"Jaw Joint")
    pointListNode.AddControlPoint([0,0,0],"Tip of Jaw")
    pointListNode.AddControlPoint([0,0,0],"Muscle Insertion Site")
    pointListNode.UnsetNthControlPointPosition(0)
    pointListNode.UnsetNthControlPointPosition(1)
    pointListNode.UnsetNthControlPointPosition(2)
    pointListNode.GetDisplayNode().SetPropertiesLabelVisibility(True)
    pointListNode.GetDisplayNode().SetTextScale(3)
    slicer.modules.segmentgeometry.widgetRepresentation()
    slicer.modules.DentalDynamicsWidget.ui.SimpleMarkupsWidget.setCurrentNode(pointListNode)
    slicer.modules.DentalDynamicsWidget.ui.ActionFixedNumberOfControlPoints.trigger()
    
  def onFlipResults(self):
    """
    Run processing when user clicks "Flip" button.
    """
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    pluginHandler = slicer.qSlicerSubjectHierarchyPluginHandler().instance()
    folderPlugin = pluginHandler.pluginByName("Folder")
    outvis = folderPlugin.getDisplayVisibility(shNode.GetItemByName("Out Levers"))
    posvis = folderPlugin.getDisplayVisibility(shNode.GetItemByName("Tooth Positions"))
    folderPlugin.setDisplayVisibility(shNode.GetItemByName("Out Levers"), 0)
    folderPlugin.setDisplayVisibility(shNode.GetItemByName("Tooth Positions"), 0)
    
    
    OutItemID = shNode.GetItemByName("Out Levers")
    Outchildren = vtk.vtkIdList()
    shNode.GetItemChildren(OutItemID, Outchildren)
    PosItemID = shNode.GetItemByName("Tooth Positions")
    Poschildren = vtk.vtkIdList()
    shNode.GetItemChildren(PosItemID, Poschildren)

    for i in range(Outchildren.GetNumberOfIds()):
      child = Outchildren.GetId(i)
      shNode.SetItemParent(child, PosItemID)
      childNode = shNode.GetItemDataNode(child)
      childNode.GetDisplayNode().SetSelectedColor((0, 0.72, 0.92))
      childNode.GetDisplayNode().SetActiveColor((1, 0.65, 0.0))


    for i in range(Poschildren.GetNumberOfIds()):
      child = Poschildren.GetId(i)
      shNode.SetItemParent(child, OutItemID)
      childNode = shNode.GetItemDataNode(child)
      childNode.GetDisplayNode().SetSelectedColor((1.0, 0.5000076295109483, 0.5000076295109483))
      childNode.GetDisplayNode().SetActiveColor((0.4, 1.0, 0.0))
      
    pluginHandler = slicer.qSlicerSubjectHierarchyPluginHandler().instance()
    folderPlugin = pluginHandler.pluginByName("Folder")
    folderPlugin.setDisplayVisibility(shNode.GetItemByName("Out Levers"), outvis)
    folderPlugin.setDisplayVisibility(shNode.GetItemByName("Tooth Positions"), posvis)

  def onFlipSomeResults(self):
    """
    Run processing when user clicks "Flip" button.
    """
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    pluginHandler = slicer.qSlicerSubjectHierarchyPluginHandler().instance()
    folderPlugin = pluginHandler.pluginByName("Folder")
    outvis = folderPlugin.getDisplayVisibility(shNode.GetItemByName("Out Levers"))
    posvis = folderPlugin.getDisplayVisibility(shNode.GetItemByName("Tooth Positions"))
    folderPlugin.setDisplayVisibility(shNode.GetItemByName("Out Levers"), 0)
    folderPlugin.setDisplayVisibility(shNode.GetItemByName("Tooth Positions"), 0)
    
    segmentation = self.ui.SegmentSelectorWidget.currentNode()
    segments = self.ui.SegmentSelectorWidget.selectedSegmentIDs()
    OutItemID = shNode.GetItemByName("Out Levers")
    PosItemID = shNode.GetItemByName("Tooth Positions")
    Outchildren = []
    Poschildren = []

    for i in segments:
      segname = segmentation.GetSegmentation().GetSegment(i).GetName()
      Outchildren.append(shNode.GetItemChildWithName(OutItemID, segname))
      Poschildren.append(shNode.GetItemChildWithName(PosItemID, segname))

    for i in Outchildren:
      child = i
      shNode.SetItemParent(child, PosItemID)
      childNode = shNode.GetItemDataNode(child)
      childNode.GetDisplayNode().SetSelectedColor((0, 0.72, 0.92))
      childNode.GetDisplayNode().SetActiveColor((1, 0.65, 0.0))

    for i in Poschildren:
      child = i
      shNode.SetItemParent(child, OutItemID)
      childNode = shNode.GetItemDataNode(child)
      childNode.GetDisplayNode().SetSelectedColor((1.0, 0.5000076295109483, 0.5000076295109483))
      childNode.GetDisplayNode().SetActiveColor((0.4, 1.0, 0.0))
      
    pluginHandler = slicer.qSlicerSubjectHierarchyPluginHandler().instance()
    folderPlugin = pluginHandler.pluginByName("Folder")
    folderPlugin.setDisplayVisibility(shNode.GetItemByName("Out Levers"), outvis)
    folderPlugin.setDisplayVisibility(shNode.GetItemByName("Tooth Positions"), posvis)

  def onOutleverVis(self):
    """
    Run processing when user clicks "Outlever Vis" button.
    """    
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    folderItemID = shNode.GetItemByName("Out Levers")
    pluginHandler = slicer.qSlicerSubjectHierarchyPluginHandler().instance()
    folderPlugin = pluginHandler.pluginByName("Folder")

    if shNode.GetItemDisplayVisibility(folderItemID) == 0:
      folderPlugin.setDisplayVisibility(folderItemID, 1)
    
    else:
      folderPlugin.setDisplayVisibility(folderItemID, 0)
      
  def onPositionVis(self):
    """
    Run processing when user clicks "Outlever Vis" button.
    """
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    folderItemID = shNode.GetItemByName("Tooth Positions")
    pluginHandler = slicer.qSlicerSubjectHierarchyPluginHandler().instance()
    folderPlugin = pluginHandler.pluginByName("Folder")

    if shNode.GetItemDisplayVisibility(folderItemID) == 0:
      folderPlugin.setDisplayVisibility(folderItemID, 1)
    
    else:
      folderPlugin.setDisplayVisibility(folderItemID, 0)

  def onResetButton(self):
    """
    Run processing when user clicks "Reset" button.
    """
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    shFolderItemId = shNode.GetItemByName("Dental Dynamics Misc")
    shNode.RemoveItem(shFolderItemId)
    slicer.mrmlScene.RemoveNode(self.ui.tableSelector.currentNode())
    layoutManager = slicer.app.layoutManager()

    tableWidget = layoutManager.tableWidget(0)
    
    self.ui.OutVisButton.enabled = False
    self.ui.PosVisButton.enabled = False
    self.ui.FlipButton.enabled = False
    self.ui.FlipSomeButton.enabled = False
    self.ui.FlipSomeButton.enabled = False
    self.ui.SegmentSelectorWidget.enabled = False
    #self.ui.ResetpushButton.enabled = False
    

  def onApplyButton(self):
    """
    Run processing when user clicks "Apply" button.
    """
    try:
      # Create nodes for results      
      tableNode = self.ui.tableSelector.currentNode()
      expTable = "Dental Dynamics Table"
      if not tableNode:
        tableNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTableNode", expTable)
        self.ui.tableSelector.setCurrentNode(tableNode)
      if tableNode.GetName() != expTable and slicer.mrmlScene.GetFirstNodeByName(expTable) != None:
        tableNode = slicer.mrmlScene.GetFirstNodeByName(expTable)
        self.ui.tableSelector.setCurrentNode(tableNode)
      if tableNode.GetName() != expTable and slicer.mrmlScene.GetFirstNodeByName(expTable) == None:
        tableNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTableNode", expTable)
        self.ui.tableSelector.setCurrentNode(tableNode)

      # Compute output
      self.logic.run(self.ui.segmentationSelector.currentNode(), self.ui.SkipSegCheckBox.checked, self.ui.SimpleMarkupsWidget.currentNode(), 
      self.ui.ForceInputSlider.value, self.ui.AngleInputSlider.value, tableNode, self.ui.SpecieslineEdit.text, self.ui.LowerradioButton.checked, self.ui.UpperradioButton.checked,
      self.ui.LeftradioButton.checked, self.ui.RightradioButton.checked)
      

      self.ui.OutVisButton.enabled = True
      self.ui.PosVisButton.enabled = True
      self.ui.FlipButton.enabled = True
      self.ui.FlipSomeButton.enabled = True
      self.ui.SegmentSelectorWidget.enabled = True
      self.ui.ResetpushButton.enabled = True  
      
      
      if len(self.ui.SegmentSelectorWidget.selectedSegmentIDs()) != 0:
        self.ui.SegmentSelectorWidget.multiSelection = False
        self.ui.SegmentSelectorWidget.multiSelection = True
 
    except Exception as e:
      slicer.util.errorDisplay("Failed to compute results: "+str(e))
      import traceback
      traceback.print_exc()
#
# DentalDynamicsLogic
#

class DentalDynamicsLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self):
    """
    Called when the logic class is instantiated. Can be used for initializing member variables.
    """
    ScriptedLoadableModuleLogic.__init__(self)

  def setDefaultParameters(self, parameterNode):
    """
    Initialize parameter node with default settings.
    """
    if not parameterNode.GetParameter("Force"):
     parameterNode.SetParameter("Force", "1.0")


  def run(self, segmentationNode, skipBox, pointNode, force, angle, tableNode, species, LowerradioButton, UpperradioButton, LeftradioButton, RightradioButton):
    """
    Run the processing algorithm.
    Can be used without GUI widget.
    :param segmentation: segmentation file with all of the segmented teeth
    :param skipBox: skip the first segment in calculations
    :param jawlength: markups line node measuring jaw length
    :param jawjoint: markups fiducial placed where the jaw joint is
    :param inlever: markups fiducial placed where the muscle insertion is on the jaw
    :param force: amount of force exerted by the muscles acting on the jaw
    :param angle: insertion angle of the muscle acting on the jaw
    :param tableNode: table to show results
    """

    import numpy as np
    import time

    start = time.time()
    logging.info('Processing started')

    if not segmentationNode:
      raise ValueError("Segmentation node is invalid")
    
    # Get visible segment ID list.
    # Get segment ID list
    visibleSegmentIds = vtk.vtkStringArray()
    segmentationNode.GetDisplayNode().GetVisibleSegmentIDs(visibleSegmentIds)
    if visibleSegmentIds.GetNumberOfValues() == 0:
      raise ValueError("Dental Dyanamics will not return any results: there are no visible segments")
    
              
    # Make a table and set the first column as the slice number. 
    tableNode.RemoveAllColumns()
    table = tableNode.GetTable()
    
    SpeciesArray = vtk.vtkStringArray()
    SpeciesArray.SetName("Species")
    
    JawIDArray = vtk.vtkStringArray()
    JawIDArray.SetName("Jaw ID")
    
    SideArray = vtk.vtkStringArray()
    SideArray.SetName("Side of Face")
    
    SegmentNameArray = vtk.vtkStringArray()
    SegmentNameArray.SetName("Tooth ID")
    
    JawLengthArray = vtk.vtkFloatArray()
    JawLengthArray.SetName("Jaw Length (mm)")  
   
    RelPosArray = vtk.vtkFloatArray()
    RelPosArray.SetName("Rel Position")   
   
    PositionArray = vtk.vtkFloatArray()
    PositionArray.SetName("Position (mm)")
    
    ToothHeightArray = vtk.vtkFloatArray()
    ToothHeightArray.SetName("Tooth Height (mm)")
    
    ToothWidthArray = vtk.vtkFloatArray()
    ToothWidthArray.SetName("Tooth Width (mm)")
    
    AspectRatioArray = vtk.vtkFloatArray()
    AspectRatioArray.SetName("Aspect Ratio")    

    SurfaceAreaArray = vtk.vtkFloatArray()
    SurfaceAreaArray.SetName("Surface Area (mm^2)")
    
    InputForceArray = vtk.vtkFloatArray()
    InputForceArray.SetName("Input Force (N)")
    
    InputAngleArray = vtk.vtkFloatArray()
    InputAngleArray.SetName("Insert Angle (deg)")
    
    MechAdvArray = vtk.vtkFloatArray()
    MechAdvArray.SetName("Mechanical Advantage")  
    
    FToothArray = vtk.vtkFloatArray()
    FToothArray.SetName("F-Tooth (N)")    

    StressArray = vtk.vtkFloatArray()
    StressArray.SetName("Stress (N/m^2)")
    
    # create misc folder
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    newFolder = shNode.GetItemByName("Dental Dynamics Misc")
    outFolder = shNode.GetItemByName("Out Levers")
    posFolder = shNode.GetItemByName("Tooth Positions")
    if newFolder == 0:
      newFolder = shNode.CreateFolderItem(shNode.GetSceneItemID(), "Dental Dynamics Misc")      
      outFolder = shNode.CreateFolderItem(shNode.GetSceneItemID(), "Out Levers")      
      posFolder = shNode.CreateFolderItem(shNode.GetSceneItemID(), "Tooth Positions")
      pluginHandler = slicer.qSlicerSubjectHierarchyPluginHandler().instance()
      folderPlugin = pluginHandler.pluginByName("Folder")
      folderPlugin.setDisplayVisibility(posFolder, 0)
      shNode.SetItemParent(outFolder, newFolder)
      shNode.SetItemParent(posFolder, newFolder)
    shNode.SetItemExpanded(newFolder,0)   
    shNode.SetItemExpanded(outFolder,0) 
    shNode.SetItemExpanded(posFolder,0) 
    # create models of the teeth
    exportFolderItemId = shNode.CreateFolderItem(shNode.GetSceneItemID(), "Tooth Segments")
    slicer.modules.segmentations.logic().ExportAllSegmentsToModels(segmentationNode, exportFolderItemId) 
    #boxFolderItemId = shNode.CreateFolderItem(shNode.GetSceneItemID(), "Tooth Boxes")
    #shNode.SetItemParent(boxFolderItemId, newFolder)
    #shNode.SetItemExpanded(boxFolderItemId,0)

    # calculate the centroid and surface area of each segment
    import SegmentStatistics
    segStatLogic = SegmentStatistics.SegmentStatisticsLogic()
    segStatLogic.getParameterNode().SetParameter("Segmentation", segmentationNode.GetID())
    segStatLogic.getParameterNode().SetParameter("LabelmapSegmentStatisticsPlugin.enabled", str(True))
    segStatLogic.getParameterNode().SetParameter("LabelmapSegmentStatisticsPlugin.surface_area_mm2.enabled", str(True))
    segStatLogic.getParameterNode().SetParameter("LabelmapSegmentStatisticsPlugin.centroid_ras.enabled", str(True))
    segStatLogic.getParameterNode().SetParameter("LabelmapSegmentStatisticsPlugin.obb_origin_ras.enabled",str(True))
    segStatLogic.getParameterNode().SetParameter("LabelmapSegmentStatisticsPlugin.obb_diameter_mm.enabled",str(True))
    segStatLogic.getParameterNode().SetParameter("LabelmapSegmentStatisticsPlugin.obb_direction_ras_x.enabled",str(True))
    segStatLogic.getParameterNode().SetParameter("LabelmapSegmentStatisticsPlugin.obb_direction_ras_y.enabled",str(True))
    segStatLogic.getParameterNode().SetParameter("LabelmapSegmentStatisticsPlugin.obb_direction_ras_z.enabled",str(True))
    segStatLogic.computeStatistics()
    stats = segStatLogic.getStatistics()

    jointRAS = [0,]*3
    pointNode.GetNthControlPointPosition(0,jointRAS)
	# draw line representing jaw length
    jawtipRAS = [0,]*3
    pointNode.GetNthControlPointPosition(1,jawtipRAS)
    lengthLine = slicer.util.getFirstNodeByClassByName("vtkMRMLMarkupsLineNode", "JawLength")
    if lengthLine == None:
      lengthLine = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", "JawLength")
      lengthLine.GetDisplayNode().SetPropertiesLabelVisibility(False)
      lengthLine.AddControlPoint(jointRAS)
      lengthLine.AddControlPoint(jawtipRAS)
      shNode.SetItemParent(shNode.GetItemByDataNode(lengthLine), newFolder)
    else: 
      lengthLine.SetNthControlPointPosition(0,jointRAS) 
      lengthLine.SetNthControlPointPosition(1,jawtipRAS) 
    lengthLine.SetDisplayVisibility(0)

	
	# draw line representing in-lever
    inleverRAS = [0,]*3
    pointNode.GetNthControlPointPosition(2,inleverRAS)
    leverLine = slicer.util.getFirstNodeByClassByName("vtkMRMLMarkupsLineNode", "InLever")
    if leverLine == None:
      leverLine = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", "InLever")
      leverLine.GetDisplayNode().SetPropertiesLabelVisibility(False)
      leverLine.AddControlPoint(jointRAS)
      leverLine.AddControlPoint(inleverRAS)
      shNode.SetItemParent(shNode.GetItemByDataNode(leverLine), newFolder)
    else: 
      leverLine.SetNthControlPointPosition(0,jointRAS)
      leverLine.SetNthControlPointPosition(1,inleverRAS) 
    leverLine.SetDisplayVisibility(0)
    
    # perform computations for each tooth 
    segmentList = stats["SegmentIDs"]
    if skipBox == True:
      segmentList = stats["SegmentIDs"][1:len(stats["SegmentIDs"])]
      slicer.util.getFirstNodeByClassByName("vtkMRMLMarkupsLineNode", "InLever")
      firstsegmentName = segmentationNode.GetSegmentation().GetSegment(stats["SegmentIDs"][0]).GetName()
      ToothPoslineNode = shNode.GetItemDataNode(shNode.GetItemChildWithName(posFolder, firstsegmentName))
      slicer.mrmlScene.RemoveNode(ToothPoslineNode)
      ToothOutlineNode = shNode.GetItemDataNode(shNode.GetItemChildWithName(outFolder, firstsegmentName))
      slicer.mrmlScene.RemoveNode(ToothOutlineNode)
    for segmentId in segmentList:
     
     if species != "Enter species name" and species != "":
       SpeciesArray.InsertNextValue(species)  
     if species == "Enter species name" or species == "": 
       species = "NA" 
       SpeciesArray.InsertNextValue(species)  
     jawID = "NA"
     if LowerradioButton == True:
       jawID = "Lower Jaw"
     if UpperradioButton == True:
       jawID = "Upper Jaw"
     if jawID != "":
       JawIDArray.InsertNextValue(jawID)
     side = "NA"
     if LeftradioButton == True:
       side = "Left"
     if RightradioButton == True:
       side = "Right"
     if side != "":
       SideArray.InsertNextValue(side)
     
     segment = segmentationNode.GetSegmentation().GetSegment(segmentId)
     SegmentNameArray.InsertNextValue(segment.GetName())
     InputForceArray.InsertNextValue(force)
     InputAngleArray.InsertNextValue(angle)
     
     
     JawLength = lengthLine.GetMeasurement('length').GetValue()
     JawLengthArray.InsertNextValue(JawLength)
     
     # measure surface area
     Area = stats[segmentId,"LabelmapSegmentStatisticsPlugin.surface_area_mm2"]/2
     SurfaceAreaArray.InsertNextValue(Area)
     
     # get tooth position at the base of the tooth
     obb_origin_ras = np.array(stats[segmentId,"LabelmapSegmentStatisticsPlugin.obb_origin_ras"])
     obb_diameter_mm = np.array(stats[segmentId,"LabelmapSegmentStatisticsPlugin.obb_diameter_mm"])
     obb_direction_ras_x = np.array(stats[segmentId,"LabelmapSegmentStatisticsPlugin.obb_direction_ras_x"])
     obb_direction_ras_y = np.array(stats[segmentId,"LabelmapSegmentStatisticsPlugin.obb_direction_ras_y"])
     obb_direction_ras_z = np.array(stats[segmentId,"LabelmapSegmentStatisticsPlugin.obb_direction_ras_z"])
     if LowerradioButton == True:
       obb_center_ras = obb_origin_ras+0.5*(obb_diameter_mm[0] * obb_direction_ras_x + obb_diameter_mm[1] * obb_direction_ras_y + obb_diameter_mm[2]*-2.2 * obb_direction_ras_z)
       if (obb_direction_ras_z[0] > 0 and obb_direction_ras_z[1] > 0 and obb_direction_ras_z[2] < 0):
         obb_center_ras = obb_origin_ras+0.5*(obb_diameter_mm[0] * obb_direction_ras_x + obb_diameter_mm[1] * obb_direction_ras_y + obb_diameter_mm[2]*2.2 * obb_direction_ras_z)
       if (obb_direction_ras_z[1] < 0):
         obb_center_ras = obb_origin_ras+0.5*(obb_diameter_mm[0] * obb_direction_ras_x + obb_diameter_mm[1] * obb_direction_ras_y + obb_diameter_mm[2]*2.2 * obb_direction_ras_z)
       if (obb_direction_ras_z[0] < 0 and obb_direction_ras_z[1] < 0):
         obb_center_ras = obb_origin_ras+0.5*(obb_diameter_mm[0] * obb_direction_ras_x + obb_diameter_mm[1] * obb_direction_ras_y + obb_diameter_mm[2]*-2.2 * obb_direction_ras_z)
       if all(obb_direction_ras_z < 0):
         obb_center_ras = obb_origin_ras+0.5*(obb_diameter_mm[0] * obb_direction_ras_x + obb_diameter_mm[1] * obb_direction_ras_y + obb_diameter_mm[2]*2.2 * obb_direction_ras_z)
     if UpperradioButton == True:
       obb_center_ras = obb_origin_ras+0.5*(obb_diameter_mm[0] * obb_direction_ras_x + obb_diameter_mm[1] * obb_direction_ras_y + obb_diameter_mm[2]*2.2 * obb_direction_ras_z)
       if (obb_direction_ras_z[0] > 0 and obb_direction_ras_z[1] > 0 and obb_direction_ras_z[2] < 0):
         obb_center_ras = obb_origin_ras+0.5*(obb_diameter_mm[0] * obb_direction_ras_x + obb_diameter_mm[1] * obb_direction_ras_y + obb_diameter_mm[2]*-2.2 * obb_direction_ras_z)
       if (obb_direction_ras_z[1] < 0):
         obb_center_ras = obb_origin_ras+0.5*(obb_diameter_mm[0] * obb_direction_ras_x + obb_diameter_mm[1] * obb_direction_ras_y + obb_diameter_mm[2]*-2.2 * obb_direction_ras_z)
       if (obb_direction_ras_z[0] < 0 and obb_direction_ras_z[1] < 0):
         obb_center_ras = obb_origin_ras+0.5*(obb_diameter_mm[0] * obb_direction_ras_x + obb_diameter_mm[1] * obb_direction_ras_y + obb_diameter_mm[2]*2.2 * obb_direction_ras_z)
       if all(obb_direction_ras_z < 0):
         obb_center_ras = obb_origin_ras+0.5*(obb_diameter_mm[0] * obb_direction_ras_x + obb_diameter_mm[1] * obb_direction_ras_y + obb_diameter_mm[2]*-2.2 * obb_direction_ras_z)
     modelNode = slicer.util.getFirstNodeByClassByName("vtkMRMLModelNode", segment.GetName())

     if modelNode.GetParentTransformNode():
       transformModelToWorld = vtk.vtkGeneralTransform()
       slicer.vtkMRMLTransformNode.GetTransformBetweenNodes(modelNode.GetParentTransformNode(), None, transformModelToWorld)
       polyTransformToWorld = vtk.vtkTransformPolyDataFilter()
       polyTransformToWorld.SetTransform(transformModelToWorld)
       polyTransformToWorld.SetInputData(modelNode.GetPolyData())
       polyTransformToWorld.Update()
       surface_World = polyTransformToWorld.GetOutput()
     else:
       surface_World = modelNode.GetPolyData()
     distanceFilter = vtk.vtkImplicitPolyDataDistance()
     distanceFilter.SetInput(surface_World)
     closestPointOnSurface_World = [0,0,0]
     distanceFilter.EvaluateFunctionAndGetClosestPoint(obb_center_ras, closestPointOnSurface_World)
     #slicer.mrmlScene.RemoveNode(modelNode)
     #toothposRAS = stats[segmentId,"LabelmapSegmentStatisticsPlugin.centroid_ras"] # draw to the center of tooth
     toothposRAS = closestPointOnSurface_World # draw to the tip of the tooth

     
     # try to find the tip of the tooth
     #obb_origin_ras = np.array(stats[segmentId,"LabelmapSegmentStatisticsPlugin.obb_origin_ras"])
     #obb_diameter_mm = np.array(stats[segmentId,"LabelmapSegmentStatisticsPlugin.obb_diameter_mm"])
     #obb_direction_ras_x = np.array(stats[segmentId,"LabelmapSegmentStatisticsPlugin.obb_direction_ras_x"])
     #obb_direction_ras_y = np.array(stats[segmentId,"LabelmapSegmentStatisticsPlugin.obb_direction_ras_y"])
     #obb_direction_ras_z = np.array(stats[segmentId,"LabelmapSegmentStatisticsPlugin.obb_direction_ras_z"])
     if LowerradioButton == True:
       obb_center_ras = obb_origin_ras+0.5*(obb_diameter_mm[0] * obb_direction_ras_x + obb_diameter_mm[1] * obb_direction_ras_y + obb_diameter_mm[2]*2.2 * obb_direction_ras_z)
       if (obb_direction_ras_z[0] > 0 and obb_direction_ras_z[1] > 0 and obb_direction_ras_z[2] < 0):
         obb_center_ras = obb_origin_ras+0.5*(obb_diameter_mm[0] * obb_direction_ras_x + obb_diameter_mm[1] * obb_direction_ras_y + obb_diameter_mm[2]*-2.2 * obb_direction_ras_z)
       if (obb_direction_ras_z[1] < 0):
         obb_center_ras = obb_origin_ras+0.5*(obb_diameter_mm[0] * obb_direction_ras_x + obb_diameter_mm[1] * obb_direction_ras_y + obb_diameter_mm[2]*-2.2 * obb_direction_ras_z)
       if (obb_direction_ras_z[0] < 0 and obb_direction_ras_z[1] < 0):
         obb_center_ras = obb_origin_ras+0.5*(obb_diameter_mm[0] * obb_direction_ras_x + obb_diameter_mm[1] * obb_direction_ras_y + obb_diameter_mm[2]*2.2 * obb_direction_ras_z)
       if all(obb_direction_ras_z < 0):
         obb_center_ras = obb_origin_ras+0.5*(obb_diameter_mm[0] * obb_direction_ras_x + obb_diameter_mm[1] * obb_direction_ras_y + obb_diameter_mm[2]*-2.2 * obb_direction_ras_z)
     if UpperradioButton == True:
       obb_center_ras = obb_origin_ras+0.5*(obb_diameter_mm[0] * obb_direction_ras_x + obb_diameter_mm[1] * obb_direction_ras_y + obb_diameter_mm[2]*-2.2 * obb_direction_ras_z)
       if (obb_direction_ras_z[0] > 0 and obb_direction_ras_z[1] > 0 and obb_direction_ras_z[2] < 0):
         obb_center_ras = obb_origin_ras+0.5*(obb_diameter_mm[0] * obb_direction_ras_x + obb_diameter_mm[1] * obb_direction_ras_y + obb_diameter_mm[2]*2.2 * obb_direction_ras_z)
       if (obb_direction_ras_z[1] < 0):
         obb_center_ras = obb_origin_ras+0.5*(obb_diameter_mm[0] * obb_direction_ras_x + obb_diameter_mm[1] * obb_direction_ras_y + obb_diameter_mm[2]*2.2 * obb_direction_ras_z)
       if (obb_direction_ras_z[0] < 0 and obb_direction_ras_z[1] < 0):
         obb_center_ras = obb_origin_ras+0.5*(obb_diameter_mm[0] * obb_direction_ras_x + obb_diameter_mm[1] * obb_direction_ras_y + obb_diameter_mm[2]*-2.2 * obb_direction_ras_z)
       if all(obb_direction_ras_z < 0):
         obb_center_ras = obb_origin_ras+0.5*(obb_diameter_mm[0] * obb_direction_ras_x + obb_diameter_mm[1] * obb_direction_ras_y + obb_diameter_mm[2]*2.2 * obb_direction_ras_z)
     modelNode = slicer.util.getFirstNodeByClassByName("vtkMRMLModelNode", segment.GetName())

     if modelNode.GetParentTransformNode():
       transformModelToWorld = vtk.vtkGeneralTransform()
       slicer.vtkMRMLTransformNode.GetTransformBetweenNodes(modelNode.GetParentTransformNode(), None, transformModelToWorld)
       polyTransformToWorld = vtk.vtkTransformPolyDataFilter()
       polyTransformToWorld.SetTransform(transformModelToWorld)
       polyTransformToWorld.SetInputData(modelNode.GetPolyData())
       polyTransformToWorld.Update()
       surface_World = polyTransformToWorld.GetOutput()
     else:
       surface_World = modelNode.GetPolyData()
     distanceFilter = vtk.vtkImplicitPolyDataDistance()
     distanceFilter.SetInput(surface_World)
     closestPointOnSurface_World = [0,0,0]
     distanceFilter.EvaluateFunctionAndGetClosestPoint(obb_center_ras, closestPointOnSurface_World)
     slicer.mrmlScene.RemoveNode(modelNode)
     #toothoutRAS = stats[segmentId,"LabelmapSegmentStatisticsPlugin.centroid_ras"] # draw to the center of tooth
     toothoutRAS = closestPointOnSurface_World # draw to the tip of the tooth
     
     jawvec = jointRAS[0]-jawtipRAS[0],jointRAS[1]-jawtipRAS[1],jointRAS[2]-jawtipRAS[2]
     jawvec = np.array(jawvec)
     posvec = toothposRAS[0]-jointRAS[0],toothposRAS[1]-jointRAS[1],toothposRAS[2]-jointRAS[2]
     posvec = np.array(posvec)
     t = np.dot(jawvec,posvec)/jawvec**2
     jawvecpoint = jointRAS + t*jawvec
     ToothPos = np.linalg.norm(np.array(toothposRAS)-np.array(jawvecpoint))
     OutLever = np.linalg.norm(np.array(toothoutRAS)-np.array(jawvecpoint))
     if (ToothPos > OutLever and jawID == "Lower Jaw"):
       tmp1 = toothoutRAS
       tmp2 = toothposRAS
       toothoutRAS = tmp2
       toothposRAS = tmp1
     posvec = toothposRAS[0]-inleverRAS[0],toothposRAS[1]-inleverRAS[1],toothposRAS[2]-inleverRAS[2]
     posvec = np.array(posvec)
     t = np.dot(jawvec,posvec)/jawvec**2
     jawvecpoint = inleverRAS + t*jawvec
     ToothPos = np.linalg.norm(np.array(toothposRAS)-np.array(jawvecpoint))
     OutLever = np.linalg.norm(np.array(toothoutRAS)-np.array(jawvecpoint))
     if (ToothPos < OutLever and jawID == "Upper Jaw"):
       tmp1 = toothoutRAS
       tmp2 = toothposRAS
       toothoutRAS = tmp2
       toothposRAS = tmp1       
     
     # draw line between jaw joint and the base of the tooth
     ToothPoslineNode = shNode.GetItemDataNode(shNode.GetItemChildWithName(posFolder, segment.GetName()))
     if ToothPoslineNode == None:
       ToothPoslineNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", segment.GetName())
       ToothPoslineNode.GetDisplayNode().SetPropertiesLabelVisibility(False)
       ToothPoslineNode.GetDisplayNode().SetSelectedColor((0, 0.72, 0.92))
       ToothPoslineNode.GetDisplayNode().SetActiveColor((1, 0.65, 0.0))
       ToothPoslineNode.AddControlPoint(jointRAS)
       ToothPoslineNode.AddControlPoint(toothposRAS)
       shNode.SetItemParent(shNode.GetItemByDataNode(ToothPoslineNode), posFolder)
     ToothPos = ToothPoslineNode.GetMeasurement('length').GetValue()
     PositionArray.InsertNextValue(ToothPos)
     # auto hide the positions folder
     shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
     pluginHandler = slicer.qSlicerSubjectHierarchyPluginHandler().instance()
     folderPlugin = pluginHandler.pluginByName("Folder")
     if folderPlugin.getDisplayVisibility(posFolder) == 0:
       folderPlugin.setDisplayVisibility(posFolder, 1)
       folderPlugin.setDisplayVisibility(posFolder, 0)
     
     # draw line between jaw joint and tooth
     ToothOutlineNode = shNode.GetItemDataNode(shNode.GetItemChildWithName(outFolder, segment.GetName()))
     if ToothOutlineNode == None:
       ToothOutlineNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", segment.GetName())
       ToothOutlineNode.GetDisplayNode().SetPropertiesLabelVisibility(False)
       ToothOutlineNode.AddControlPoint(jointRAS)
       ToothOutlineNode.AddControlPoint(toothoutRAS)
       shNode.SetItemParent(shNode.GetItemByDataNode(ToothOutlineNode), outFolder)
     else: 
       ToothOutlineNode.SetNthControlPointPosition(0,jointRAS)     
     OutLever = ToothOutlineNode.GetMeasurement('length').GetValue()
     # auto show the outlever folder
     shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
     pluginHandler = slicer.qSlicerSubjectHierarchyPluginHandler().instance()
     folderPlugin = pluginHandler.pluginByName("Folder")
     if folderPlugin.getDisplayVisibility(outFolder) == 0:
       folderPlugin.setDisplayVisibility(outFolder, 1)
       folderPlugin.setDisplayVisibility(outFolder, 0)
              
     
     RelPosArray.InsertNextValue(ToothPos/JawLength)
     
     # calculate tooth aspect ratio
     heightNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", segment.GetName())
     heightNode.GetDisplayNode().SetPropertiesLabelVisibility(False)
     heightNode.AddControlPoint(ToothPoslineNode.GetNthControlPointPosition(1))
     heightNode.AddControlPoint(ToothOutlineNode.GetNthControlPointPosition(1))
     ToothHeight = heightNode.GetMeasurement('length').GetValue()
     slicer.mrmlScene.RemoveNode(heightNode)
     #ToothHeight = obb_diameter_mm[2]
     ToothHeightArray.InsertNextValue(ToothHeight)
     if obb_diameter_mm[0] > obb_diameter_mm[1]:
       ToothWidthArray.InsertNextValue(obb_diameter_mm[0])
       AspectRatioArray.InsertNextValue(ToothHeight/obb_diameter_mm[0])
     if obb_diameter_mm[0] < obb_diameter_mm[1]:
       ToothWidthArray.InsertNextValue(obb_diameter_mm[1])
       AspectRatioArray.InsertNextValue(ToothHeight/obb_diameter_mm[1])

     
     # calculate mechanical advantage and F-Tooth
     InLever = leverLine.GetMeasurement('length').GetValue()
     MA = InLever/OutLever
     MechAdvArray.InsertNextValue(MA)
     FToothArray.InsertNextValue(force * np.sin(angle) * MA)
     
     # calculate tooth stress
     StressArray.InsertNextValue((force * np.sin(angle) * MA)/ (Area * 1e-6))

    
    if species != "Enter species name" and species != "":
      tableNode.AddColumn(SpeciesArray)
      tableNode.SetColumnDescription(SpeciesArray.GetName(), "Species")

    tableNode.AddColumn(JawIDArray)
    tableNode.SetColumnDescription(JawIDArray.GetName(), "If upper or lower jaw")
   
    tableNode.AddColumn(SideArray)
    tableNode.SetColumnDescription(SideArray.GetName(), "Side of face that the jaw is on")  
        
    tableNode.AddColumn(JawLengthArray)
    tableNode.SetColumnDescription(JawLengthArray.GetName(), "Jaw Length")
    tableNode.SetColumnUnitLabel(JawLengthArray.GetName(), "mm")  # TODO: use length unit
    
    tableNode.AddColumn(SegmentNameArray)
    tableNode.SetColumnDescription(SegmentNameArray.GetName(), "Tooth segment name")
    
    tableNode.AddColumn(PositionArray)
    tableNode.SetColumnDescription(PositionArray.GetName(), "Distance between the base of the tooth and the jaw joint")
    tableNode.SetColumnUnitLabel(PositionArray.GetName(), "mm")  # TODO: use length unit
    
    #tableNode.AddColumn(RelPosArray)
    #tableNode.SetColumnDescription(RelPosArray.GetName(), "Relative position of the tooth")
    #tableNode.SetColumnUnitLabel(RelPosArray.GetName(), "%")  # TODO: use length unit

    tableNode.AddColumn(ToothHeightArray)
    tableNode.SetColumnDescription(ToothHeightArray.GetName(), "Tooth Height")
    tableNode.SetColumnUnitLabel(ToothHeightArray.GetName(), "mm")  # TODO: use length unit

    tableNode.AddColumn(ToothWidthArray)
    tableNode.SetColumnDescription(ToothWidthArray.GetName(), "Tooth Width")
    tableNode.SetColumnUnitLabel(ToothWidthArray.GetName(), "mm")  # TODO: use length unit

    tableNode.AddColumn(AspectRatioArray)
    tableNode.SetColumnDescription(AspectRatioArray.GetName(), "Tooth Aspect Ratio")
    tableNode.SetColumnUnitLabel(AspectRatioArray.GetName(), "mm")  # TODO: use length unit

    tableNode.AddColumn(SurfaceAreaArray)
    tableNode.SetColumnDescription(SurfaceAreaArray.GetName(), "Tooth Surface Area")
    tableNode.SetColumnUnitLabel(SurfaceAreaArray.GetName(), "mm^2")  # TODO: use length unit
    
    tableNode.AddColumn(InputForceArray)
    tableNode.SetColumnDescription(InputForceArray.GetName(), "Muscle Input Force")
    tableNode.SetColumnUnitLabel(InputForceArray.GetName(), "N")  # TODO: use length unit
    
    tableNode.AddColumn(InputAngleArray)
    tableNode.SetColumnDescription(InputAngleArray.GetName(), "Muscle Insertion Angle")
    tableNode.SetColumnUnitLabel(InputAngleArray.GetName(), "deg")  # TODO: use length unit
    
    tableNode.AddColumn(MechAdvArray)
    tableNode.SetColumnDescription(MechAdvArray.GetName(), "Tooth mechanical advantage")

    tableNode.AddColumn(FToothArray)
    tableNode.SetColumnDescription(FToothArray.GetName(), "The force acting on a tooth (input force * insert angle * mechanical advantage)")
    tableNode.SetColumnUnitLabel(FToothArray.GetName(), "N")  # TODO: use length unit

    tableNode.AddColumn(StressArray)
    tableNode.SetColumnDescription(StressArray.GetName(), "Tooth stress (tooth force / surface area)")

    shNode.RemoveItem(exportFolderItemId)

    customLayout = """
      <layout type=\"vertical\" split=\"true\" >
       <item splitSize=\"600\">
        <view class=\"vtkMRMLViewNode\" singletontag=\"1\">
         <property name=\"viewlabel\" action=\"default\">1</property>
        </view>
       </item>
       <item splitSize=\"400\">
        <view class=\"vtkMRMLTableViewNode\" singletontag=\"TableView1\">
         <property name=\"viewlabel\" action=\"default\">T</property>
        </view>
       </item>
      </layout>
      """
    customLayoutId=999

    layoutManager = slicer.app.layoutManager()
    layoutManager.layoutLogic().GetLayoutNode().AddLayoutDescription(customLayoutId, customLayout)

    # Switch to the new custom layout
    layoutManager.setLayout(customLayoutId)
    tableWidget = layoutManager.tableWidget(0)
    tableWidget.tableView().setMRMLTableNode(tableNode)    

    # Change layout to include plot and table      
#    slicer.app.layoutManager().setLayout(customLayoutId)
#    slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID(tableNode.GetID())
#    slicer.app.applicationLogic().PropagateTableSelection()

    logging.info('Processing completed')
    end = time.time()
    TotalTime = np.round(end - start,2)
    print("Total time elapsed:", TotalTime, "seconds")

    

#
# DentalDynamicsTest
#

class DentalDynamicsTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear()

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_DentalDynamics1()

  def test_DentalDynamics1(self):
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

    # Get/create input data

    import SampleData
    #inputVolume = SampleData.downloadSample('DentalDynamics1')
    self.delayDisplay('Loaded test data set')

    inputScalarRange = inputVolume.GetImageData().GetScalarRange()
    self.assertEqual(inputScalarRange[0], 0)
    self.assertEqual(inputScalarRange[1], 695)

    outputVolume = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode")
    threshold = 100

    # Test the module logic

    logic = DentalDynamicsLogic()

    # Test algorithm with non-inverted threshold
    logic.process(inputVolume, outputVolume, threshold, True)
    outputScalarRange = outputVolume.GetImageData().GetScalarRange()
    self.assertEqual(outputScalarRange[0], inputScalarRange[0])
    self.assertEqual(outputScalarRange[1], threshold)

    # Test algorithm with inverted threshold
    logic.process(inputVolume, outputVolume, threshold, False)
    outputScalarRange = outputVolume.GetImageData().GetScalarRange()
    self.assertEqual(outputScalarRange[0], inputScalarRange[0])
    self.assertEqual(outputScalarRange[1], inputScalarRange[1])

    self.delayDisplay('Test passed')
