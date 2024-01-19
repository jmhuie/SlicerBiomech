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
    self.parent.categories = ["SlicerBiomech"] 
    self.parent.dependencies = []  # TODO: add here list of module names that this module requires
    self.parent.contributors = ["Jonathan M. Huie"]  
    self.parent.helpText = """This module uses lever mechanics to calculate tooth stress from segmented teeth and jaws. For more information please see the <a href="https://github.com/jmhuie/SlicerBiomech">online documentation</a>."""
    self.parent.acknowledgementText = """This module was developed by Jonathan M. Huie, who was supported by an NSF Graduate Research Fellowship (DGE-1746914)."""

    # Additional initialization step after application startup is complete
    slicer.app.connect("startupCompleted()", addlayoutDescription)
    slicer.app.connect("startupCompleted()", registerSampleData)
           
#
# Add New Layout
#

def addlayoutDescription():
    """Add new layouts"""
    
    customLayout = """
      <layout type=\"vertical\" split=\"true\" >
       <item splitSize=\"600\">
         <layout type=\"horizontal\">
           <item>
            <view class=\"vtkMRMLViewNode\" singletontag=\"1\">
             <property name=\"viewlabel\" action=\"default\">1</property>
            </view>
           </item>
         </layout>
       </item>
       <item splitSize=\"400\">
        <layout type=\"horizontal\">
         <item>
          <view class=\"vtkMRMLTableViewNode\" singletontag=\"TableViewerWindow_1\">"
           <property name=\"viewlabel\" action=\"default\">T</property>"
          </view>"
         </item>"
        </layout>
       </item>
      </layout>
    """    
    layoutManager = slicer.app.layoutManager()
    layoutManager.layoutLogic().GetLayoutNode().AddLayoutDescription(166, customLayout)
    
#
# Register sample data sets in Sample Data module
#

def registerSampleData():
    """Add data sets to Sample Data module."""
    # It is always recommended to provide sample data for users to make it easy to try the module,
    # but if no sample data is available then this method (and associated startupCompeted signal connection) can be removed.

    import SampleData

    iconsPath = os.path.join(os.path.dirname(__file__), "Resources/Icons")

    # To ensure that the source code repository remains small (can be downloaded and installed quickly)
    # it is recommended to store data sets that are larger than a few MB in a Github release.

    # DentalDynamics1
    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category="SlicerBiomech",
        sampleName="Demo Skull",
        # Thumbnail should have size of approximately 260x280 pixels and stored in Resources/Icons folder.
        # It can be created by Screen Capture module, "Capture all views" option enabled, "Number of images" set to "Single".
        thumbnailFileName=os.path.join(iconsPath, "DentalDynamics1.png"),
        # Download URL and target file name
        uris="https://github.com/jmhuie/SlicerBiomech/releases/download/SampleData/USNM279384_Aneides_lugubris_skull.nrrd",
        fileNames="USNM279384_Aneides_lugubris_skull.nrrd",
        # Checksum to ensure file integrity. Can be computed by this command:
        #  import hashlib; print(hashlib.sha256(open(filename, "rb").read()).hexdigest())
        #checksums="SHA256:998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95",
        # This node name will be used when the data set is loaded
        nodeNames="Dental Dynamics Demo Skull",
        loadFileType='VolumeFile',
    )

    # DentalDynamics2
    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category="SlicerBiomech",
        sampleName="Demo Segment",
        thumbnailFileName=os.path.join(iconsPath, "DentalDynamics2.png"),
        # Download URL and target file name
        uris="https://github.com/jmhuie/SlicerBiomech/releases/download/SampleData/USNM279384_Aneides_lugubris_left_jaw.seg.nrrd",
        fileNames="USNM279384_Aneides_lugubris_left_jaw.seg.nrrd",
        #checksums="SHA256:1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97",
        # This node name will be used when the data set is loaded
        nodeNames="Dental Dynamics Jaw Segment",
        loadFileType='SegmentationFile',
    )
    
    # DentalDynamics3
    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category="SlicerBiomech",
        sampleName="Demo Jaw Points",
        thumbnailFileName=os.path.join(iconsPath, "DentalDynamics3.png"),
        # Download URL and target file name
        uris="https://github.com/jmhuie/SlicerBiomech/releases/download/SampleData/Dental.Dynamics.Jaw.Points.mrk.json",
        fileNames="Dental.Dynamics.Jaw.Points.mrk.json",
        #checksums="SHA256:1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97",
        # This node name will be used when the data set is loaded
        nodeNames="Dental Dynamics Jaw Points",
        loadFileType='MarkupsFile',
    )


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
    
    self.ui.SimpleMarkupsWidget.markupsSelectorComboBox().addEnabled = False
    slicer.modules.DentalDynamicsWidget.ui.label_Segment.text = "Select Teeth: "
    #self.ui.SegmentSelectorWidget.setCurrentNodeID('')
        
    # Connections

    # These connections ensure that we update parameter node when scene is closed
    self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
    self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

    # These connections ensure that whenever user changes some settings on the GUI, that is saved in the MRML scene
    # (in the selected parameter node).
    self.ui.SpecieslineEdit.connect('textEdited(QString)', self.updateParameterNodeFromGUI)
    self.ui.LowerradioButton.connect('toggled(bool)', self.updateParameterNodeFromGUI)
    self.ui.UpperradioButton.connect('toggled(bool)', self.updateParameterNodeFromGUI)
    self.ui.RightradioButton.connect('toggled(bool)', self.updateParameterNodeFromGUI)
    self.ui.LeftradioButton.connect('toggled(bool)', self.updateParameterNodeFromGUI)
    self.ui.SegmentSelectorWidget.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.SegmentSelectorWidget.connect("segmentSelectionChanged(QStringList)", self.updateParameterNodeFromGUI)
    self.ui.SegmentSelectorWidget.connect("currentNodeChanged(vtkMRMLNode*)", self.updateSelectedSegments)
    self.ui.FlipcheckBox.connect("stateChanged(int)", self.updateParameterNodeFromGUI)
    self.ui.SimpleMarkupsWidget.connect("markupsNodeChanged()", self.updateParameterNodeFromGUI)
    self.ui.SimpleMarkupsWidget.connect("markupsNodeChanged()", self.onMarkupNodeChanged)
    self.ui.SimpleMarkupsWidget.connect("currentMarkupsControlPointSelectionChanged(int)", self.onSelectedControlPointChanged)
    self.ui.SimradioButton.connect('toggled(bool)', self.updateParameterNodeFromGUI)
    self.ui.EmpradioButton.connect('toggled(bool)', self.updateParameterNodeFromGUI)
    self.ui.MusclecheckBox1.connect("stateChanged(int)", self.updateParameterNodeFromGUI)
    self.ui.ForceInputBox1.connect("valueChanged(double)", self.updateParameterNodeFromGUI)
    self.ui.AngleInputBox1.connect("valueChanged(double)", self.updateParameterNodeFromGUI)
    self.ui.VolumeInputBox1.connect("valueChanged(double)", self.updateParameterNodeFromGUI)
    self.ui.MusclecheckBox2.connect("stateChanged(int)", self.updateParameterNodeFromGUI)
    self.ui.ForceInputBox2.connect("valueChanged(double)", self.updateParameterNodeFromGUI)
    self.ui.AngleInputBox2.connect("valueChanged(double)", self.updateParameterNodeFromGUI)
    self.ui.VolumeInputBox2.connect("valueChanged(double)", self.updateParameterNodeFromGUI)
    self.ui.MusclecheckBox3.connect("stateChanged(int)", self.updateParameterNodeFromGUI)
    self.ui.ForceInputBox3.connect("valueChanged(double)", self.updateParameterNodeFromGUI)
    self.ui.AngleInputBox3.connect("valueChanged(double)", self.updateParameterNodeFromGUI)
    self.ui.VolumeInputBox3.connect("valueChanged(double)", self.updateParameterNodeFromGUI)
    self.ui.tableSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    #self.ui.OutVisButton.connect('clicked(bool)', self.updateParameterNodeFromGUI)
    #self.ui.PosVisButton.connect('clicked(bool)', self.updateParameterNodeFromGUI)
    self.ui.FlipSegmentSelectorWidget.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.FlipSegmentSelectorWidget.connect("segmentSelectionChanged(QStringList)", self.updateParameterNodeFromGUI)

    # Buttons
    self.ui.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.ui.ResetpushButton.connect('clicked(bool)', self.onResetButton)
    self.ui.TemplatepushButton.connect('clicked(bool)', self.onTemplate)
    self.ui.NoneFlipButton.connect('clicked(bool)', self.onSelectNoneFlip)
    self.ui.AllFlipButton.connect('clicked(bool)', self.onSelectAllFlip)
    self.ui.LabelVisButton.connect('clicked(bool)', self.onPointLabelVis)
    self.ui.OutVisButton.connect('clicked(bool)', self.onTipVis)
    self.ui.PosVisButton.connect('clicked(bool)', self.onPositionVis)
    self.ui.AllpushButton.connect('clicked(bool)', self.onSelectAll)
    self.ui.NonepushButton.connect('clicked(bool)', self.onSelectNone)
    
    # Make sure parameter node is initialized (needed for module reload)
    self.initializeParameterNode()
    
    if self._parameterNode.GetParameter("ToothTips") == "True":
      self.onTipVis()
    if self._parameterNode.GetParameter("ToothPos") == "True":
      self.onPositionVis()
    if not self._parameterNode.GetNodeReference("JawPoints") and self._parameterNode.GetNodeReference("Segmentation") is not None:  
      self.onTemplate()  
    

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
    if not self._parameterNode.GetNodeReference("Segmentation"):
      firstSegmentationNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLSegmentationNode")
      if firstSegmentationNode:
        self._parameterNode.SetNodeReferenceID("Segmentation", firstSegmentationNode.GetID())
        Allsegments = self.ui.SegmentSelectorWidget.segmentIDs()
        self.ui.SegmentSelectorWidget.setSelectedSegmentIDs(Allsegments)
        
    if not self._parameterNode.GetNodeReference("JawPoints"):
      jawPoints = slicer.mrmlScene.GetFirstNodeByName(f"Dental Dynamics Jaw Points")
      if jawPoints:
        self._parameterNode.SetNodeReferenceID("JawPoints", jawPoints.GetID())  
        
    if not self._parameterNode.GetNodeReference("JawPoints") and self._parameterNode.GetNodeReference("Segmentation") is not None:  
      self.onTemplate()  
            
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
    if self._parameterNode is not None and self.hasObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode):
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
    self.ui.SpecieslineEdit.text = self._parameterNode.GetParameter("SpeciesName")
    self.ui.LowerradioButton.checked = (self._parameterNode.GetParameter("LowerJaw") == "True")
    self.ui.UpperradioButton.checked = (self._parameterNode.GetParameter("UpperJaw") == "True")
    self.ui.LeftradioButton.checked = (self._parameterNode.GetParameter("LeftJaw") == "True")
    self.ui.RightradioButton.checked = (self._parameterNode.GetParameter("RightJaw") == "True")
    self.ui.SegmentSelectorWidget.setCurrentNode(self._parameterNode.GetNodeReference("Segmentation"))
    if self._parameterNode.GetNodeReference("Segmentation") is not None:
      self.ui.SegmentSelectorWidget.setSelectedSegmentIDs(eval(self._parameterNode.GetParameter("Segments")))
    self.ui.FlipcheckBox.checked = (self._parameterNode.GetParameter("Flip") == "True")
    self.ui.SimpleMarkupsWidget.setCurrentNode(self._parameterNode.GetNodeReference("JawPoints"))
    self.ui.SimradioButton.checked = (self._parameterNode.GetParameter("Simulate") == "True")
    self.ui.EmpradioButton.checked = (self._parameterNode.GetParameter("Empirical") == "True")   
    self.ui.MusclecheckBox1.checked = (self._parameterNode.GetParameter("Muscle1") == "True")
    self.ui.ForceInputBox1.value = float(self._parameterNode.GetParameter("Force1"))
    self.ui.AngleInputBox1.value = float(self._parameterNode.GetParameter("Angle1"))
    self.ui.VolumeInputBox1.value = float(self._parameterNode.GetParameter("Volume1"))
    self.ui.MusclecheckBox2.checked = (self._parameterNode.GetParameter("Muscle2") == "True")
    self.ui.ForceInputBox2.value = float(self._parameterNode.GetParameter("Force2"))
    self.ui.AngleInputBox2.value = float(self._parameterNode.GetParameter("Angle2"))  
    self.ui.VolumeInputBox2.value = float(self._parameterNode.GetParameter("Volume2"))
    self.ui.MusclecheckBox3.checked = (self._parameterNode.GetParameter("Muscle3") == "True")
    self.ui.ForceInputBox3.value = float(self._parameterNode.GetParameter("Force3"))
    self.ui.AngleInputBox3.value = float(self._parameterNode.GetParameter("Angle3")) 
    self.ui.VolumeInputBox3.value = float(self._parameterNode.GetParameter("Volume3"))   
    self.ui.FlipSegmentSelectorWidget.setCurrentNode(self._parameterNode.GetNodeReference("Segmentation"))
    if self._parameterNode.GetNodeReference("Segmentation") is not None:
      self.ui.FlipSegmentSelectorWidget.setSelectedSegmentIDs(eval(self._parameterNode.GetParameter("FlipSegments")))
    self.ui.tableSelector.setCurrentNode(self._parameterNode.GetNodeReference("ResultsTable"))

    # Update buttons states and tooltips
    if self._parameterNode.GetNodeReference("Segmentation") and self._parameterNode.GetNodeReference("JawPoints") is not None:
      self.ui.applyButton.toolTip = "Compute calculations"
      self.ui.applyButton.enabled = True
    else:
      self.ui.applyButton.toolTip = "Select input and output parameters"
      self.ui.applyButton.enabled = False
      
    if self._parameterNode.GetNodeReference("ResultsTable"):
      self.ui.tableSelector.toolTip = "Edit output table"
    else:
      self.ui.tableSelector.toolTip = "Select output table"

    if self.ui.SimpleMarkupsWidget.currentNode() != None:   
      if self.ui.SimpleMarkupsWidget.currentNode().GetNthControlPointPosition(2) != (0, 0, 0) and self.ui.SimpleMarkupsWidget.currentNode().GetNthControlPointPositionStatus(2) == 2:
        self.ui.MusclecheckBox1.enabled = True
      else: 
        self.ui.MusclecheckBox1.enabled = False
      if self.ui.SimpleMarkupsWidget.currentNode().GetNthControlPointPosition(4) != (0, 0, 0) and self.ui.SimpleMarkupsWidget.currentNode().GetNthControlPointPositionStatus(4) == 2:
        self.ui.MusclecheckBox2.enabled = True
      else: 
        self.ui.MusclecheckBox2.enabled = False    
      if self.ui.SimpleMarkupsWidget.currentNode().GetNthControlPointPosition(6) != (0, 0, 0) and self.ui.SimpleMarkupsWidget.currentNode().GetNthControlPointPositionStatus(6) == 2:
        self.ui.MusclecheckBox3.enabled = True
      else: 
        self.ui.MusclecheckBox3.enabled = False 
         
      if self.ui.SimpleMarkupsWidget.currentNode().GetNthControlPointPosition(3) != (0, 0, 0) and self.ui.SimpleMarkupsWidget.currentNode().GetNthControlPointPositionStatus(3) == 2:
        self.ui.EmpradioButton.enabled = True
        self.ui.EmpradioButton.checkable = True
      elif self.ui.SimpleMarkupsWidget.currentNode().GetNthControlPointPosition(5) != (0, 0, 0) and self.ui.SimpleMarkupsWidget.currentNode().GetNthControlPointPositionStatus(5) == 2: 
         self.ui.EmpradioButton.enabled = True
         self.ui.EmpradioButton.checkable = True
      elif self.ui.SimpleMarkupsWidget.currentNode().GetNthControlPointPosition(7) != (0, 0, 0) and self.ui.SimpleMarkupsWidget.currentNode().GetNthControlPointPositionStatus(7) == 2:
        self.ui.EmpradioButton.enabled = True
        self.ui.EmpradioButton.checkable = True
      else: 
        self.ui.EmpradioButton.enabled = False
        self.ui.EmpradioButton.checkable = False         
    else:
      self.ui.MusclecheckBox1.enabled = False
      self.ui.MusclecheckBox2.enabled = False 
      self.ui.MusclecheckBox3.enabled = False 
    
    if self._parameterNode.GetParameter("Muscle1") == "True" and self.ui.MusclecheckBox1.enabled == True and self._parameterNode.GetParameter("Simulate") == "True":
      self.ui.ForceInputBox1.enabled = True
      self.ui.AngleInputBox1.enabled = True
    else:
      self.ui.ForceInputBox1.enabled = False
      self.ui.AngleInputBox1.enabled = False       
        
    if self._parameterNode.GetParameter("Muscle2") == "True" and self.ui.MusclecheckBox2.enabled == True and self._parameterNode.GetParameter("Simulate") == "True":
      self.ui.ForceInputBox2.enabled = True
      self.ui.AngleInputBox2.enabled = True
    else:
      self.ui.ForceInputBox2.enabled = False
      self.ui.AngleInputBox2.enabled = False

    if self._parameterNode.GetParameter("Muscle3") == "True" and self.ui.MusclecheckBox3.enabled == True and self._parameterNode.GetParameter("Simulate") == "True":
      self.ui.ForceInputBox3.enabled = True
      self.ui.AngleInputBox3.enabled = True
    else:
      self.ui.ForceInputBox3.enabled = False
      self.ui.AngleInputBox3.enabled = False
      
    if self._parameterNode.GetParameter("Muscle1") == "True" and self.ui.MusclecheckBox1.enabled == True and self._parameterNode.GetParameter("Empirical") == "True":
      self.ui.VolumeInputBox1.enabled = True
    else:
      self.ui.VolumeInputBox1.enabled = False
        
    if self._parameterNode.GetParameter("Muscle2") == "True" and self.ui.MusclecheckBox2.enabled == True and self._parameterNode.GetParameter("Empirical") == "True":
      self.ui.VolumeInputBox2.enabled = True
    else:
      self.ui.VolumeInputBox2.enabled = False

    if self._parameterNode.GetParameter("Muscle3") == "True" and self.ui.MusclecheckBox3.enabled == True and self._parameterNode.GetParameter("Empirical") == "True":
      self.ui.VolumeInputBox3.enabled = True
    else:
      self.ui.VolumeInputBox3.enabled = False     
      
    if self.ui.SimpleMarkupsWidget.currentNode() != None:   
      pointListNode = self.ui.SimpleMarkupsWidget.currentNode()
      interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
      for i in range(pointListNode.GetNumberOfControlPoints()):
         if self.ui.SimpleMarkupsWidget.currentNode().GetNthControlPointPosition(i) == (0, 0, 0) and pointListNode.UnsetNthControlPointPosition(i) == 2: 
           pointListNode.UnsetNthControlPointPosition(i)
         if pointListNode.GetNthControlPointPositionStatus(i) == 0 and interactionNode.GetCurrentInteractionMode() == 2 and self.ui.SimpleMarkupsWidget.currentNode().GetNthControlPointPosition(i) != (0, 0, 0): 
           pointListNode.SetNthControlPointPosition(i, (0, 0, 0))
         
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
    
    self._parameterNode.SetParameter("SpeciesName", self.ui.SpecieslineEdit.text)
    self._parameterNode.SetParameter("LowerJaw", str(self.ui.LowerradioButton.checked))
    self._parameterNode.SetParameter("UpperJaw", str(self.ui.UpperradioButton.checked))
    self._parameterNode.SetParameter("LeftJaw", str(self.ui.LeftradioButton.checked))
    self._parameterNode.SetParameter("RightJaw", str(self.ui.RightradioButton.checked))
    self._parameterNode.SetNodeReferenceID("Segmentation", self.ui.SegmentSelectorWidget.currentNodeID())
    self._parameterNode.SetParameter("Segments", str(self.ui.SegmentSelectorWidget.selectedSegmentIDs()))
    self._parameterNode.SetParameter("Flip", str(self.ui.FlipcheckBox.checked))      
    if self.ui.SimpleMarkupsWidget.currentNode() != None: 
      self._parameterNode.SetNodeReferenceID("JawPoints", self.ui.SimpleMarkupsWidget.currentNode().GetID())
    else: 
      self._parameterNode.SetNodeReferenceID("JawPoints", None)
    self._parameterNode.SetParameter("Simulate", str(self.ui.SimradioButton.checked))
    self._parameterNode.SetParameter("Empirical", str(self.ui.EmpradioButton.checked))
    self._parameterNode.SetParameter("Muscle1", str(self.ui.MusclecheckBox1.checked))      
    self._parameterNode.SetParameter("Force1", str(self.ui.ForceInputBox1.value))
    self._parameterNode.SetParameter("Angle1", str(self.ui.AngleInputBox1.value))
    self._parameterNode.SetParameter("Volume1", str(self.ui.VolumeInputBox1.value))
    self._parameterNode.SetParameter("Muscle2", str(self.ui.MusclecheckBox2.checked))      
    self._parameterNode.SetParameter("Force2", str(self.ui.ForceInputBox2.value))
    self._parameterNode.SetParameter("Angle2", str(self.ui.AngleInputBox2.value))  
    self._parameterNode.SetParameter("Volume2", str(self.ui.VolumeInputBox2.value))
    self._parameterNode.SetParameter("Muscle3", str(self.ui.MusclecheckBox3.checked))      
    self._parameterNode.SetParameter("Force3", str(self.ui.ForceInputBox3.value))
    self._parameterNode.SetParameter("Angle3", str(self.ui.AngleInputBox3.value)) 
    self._parameterNode.SetParameter("Volume3", str(self.ui.VolumeInputBox3.value))   
    self._parameterNode.SetParameter("FlipSegments", str(self.ui.FlipSegmentSelectorWidget.selectedSegmentIDs()))
    self._parameterNode.SetNodeReferenceID("ResultsTable", self.ui.tableSelector.currentNodeID)

    self._parameterNode.EndModify(wasModified)

  def updateSelectedSegments(self):
    """
    Automatically select all segments when changing the segmentation node
    """
    Allsegments = self.ui.SegmentSelectorWidget.segmentIDs()
    self.ui.SegmentSelectorWidget.setSelectedSegmentIDs(Allsegments)

  def onSelectAll(self):
    if self.ui.SegmentSelectorWidget.currentNodeID() is not None:
      Allsegments = self.ui.SegmentSelectorWidget.segmentIDs()
      self.ui.SegmentSelectorWidget.setSelectedSegmentIDs(Allsegments)

  def onSelectNone(self):
    if self.ui.SegmentSelectorWidget.currentNodeID() is not None:
      self.ui.SegmentSelectorWidget.setSelectedSegmentIDs(())

  def onSelectAllFlip(self):
    if self.ui.SegmentSelectorWidget.currentNodeID() is not None:
      Allsegments = self.ui.FlipSegmentSelectorWidget.segmentIDs()
      self.ui.FlipSegmentSelectorWidget.setSelectedSegmentIDs(Allsegments)

  def onSelectNoneFlip(self):
    if self.ui.FlipSegmentSelectorWidget.currentNodeID() is not None:
      self.ui.FlipSegmentSelectorWidget.setSelectedSegmentIDs(())

  def onTemplate(self):
    """
    Run processing when user clicks "Create new reference point list" button.
    """
    pointListNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode", "Dental Dynamics Jaw Points")
    pointListNode.GetDisplayNode().SetSelectedColor((1,1,1))
    pointListNode.GetDisplayNode().SetActiveColor((0.87843, 0.87843, 0.87843))
    pointListNode.GetDisplayNode().SetGlyphScale(4)
    pointListNode.AddControlPoint([0,0,0],"Jaw Joint")
    pointListNode.AddControlPoint([0,0,0],"Tip of Jaw")
    pointListNode.AddControlPoint([0,0,0],"Closing Muscle 1 Insertion")
    pointListNode.AddControlPoint([0,0,0],"Closing Muscle 1 Origin")    
    pointListNode.AddControlPoint([0,0,0],"Closing Muscle 2 Insertion")
    pointListNode.AddControlPoint([0,0,0],"Closing Muscle 2 Origin")    
    pointListNode.AddControlPoint([0,0,0],"Closing Muscle 3 Insertion")
    pointListNode.AddControlPoint([0,0,0],"Closing Muscle 3 Origin")    
    pointListNode.UnsetNthControlPointPosition(0)
    pointListNode.UnsetNthControlPointPosition(1)
    pointListNode.UnsetNthControlPointPosition(2)
    pointListNode.UnsetNthControlPointPosition(3)  
    pointListNode.UnsetNthControlPointPosition(4)  
    pointListNode.UnsetNthControlPointPosition(5)
    pointListNode.UnsetNthControlPointPosition(6)  
    pointListNode.UnsetNthControlPointPosition(7)       
    pointListNode.GetDisplayNode().SetPropertiesLabelVisibility(True)
    pointListNode.GetDisplayNode().SetTextScale(3)
    self.ui.SimpleMarkupsWidget.setCurrentNode(pointListNode)
    self.ui.ActionFixedNumberOfControlPoints.trigger()
  
  def onMarkupNodeChanged(self):
    """
    Run process when user changes the point list.
    """    
    pointListNode = self.ui.SimpleMarkupsWidget.currentNode()
    def watchTemplate(unusedArg1 = None, unusedArg2 = None):
      self.updateGUIFromParameterNode()
    if pointListNode is not None:
      TemplateObserver = pointListNode.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent, watchTemplate)
      pointListNode.RemoveObserver(TemplateObserver)
    if pointListNode is not None:  
      TemplateObserver = pointListNode.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent, watchTemplate)
            
  def onSelectedControlPointChanged(self, controlPointIndex):
    """
    Run processing when user clicks on a different control point.
    """  
    if self.ui.SimpleMarkupsWidget.currentNode() is not None:
      pointListNode = self.ui.SimpleMarkupsWidget.currentNode()
      if pointListNode.GetNthControlPointPosition(controlPointIndex) == (0, 0, 0) or pointListNode.GetNthControlPointPositionStatus(controlPointIndex) == 0:
        pointListNode.SetControlPointPlacementStartIndex(controlPointIndex)
        slicer.modules.markups.logic().StartPlaceMode(0)
      else:
        self.ui.SimpleMarkupsWidget.placeActive(0)
    
  def onPointLabelVis(self):
    """
    Run process when user clicks "Tooth Label Vis" button.
    """  
    if slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Tooth Tip Points") != None:
      pointNode = slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Tooth Tip Points")
      if pointNode.GetDisplayNode().GetPointLabelsVisibility() == True:
        pointNode.GetDisplayNode().SetPointLabelsVisibility(0)
      elif pointNode.GetDisplayNode().GetPointLabelsVisibility() == False:
        pointNode.GetDisplayNode().SetPointLabelsVisibility(1)

  def onTipVis(self):
    """
    Run process when user clicks "Tooth Tip Vis" button.
    """  
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    outFolder = shNode.GetItemByName("Tooth Tips")
    pluginHandler = slicer.qSlicerSubjectHierarchyPluginHandler().instance()
    folderPlugin = pluginHandler.pluginByName("Folder")
    
    def outjointMarkupChanged(unusedArg1=None, unusedArg2=None):
      if self.ui.SimpleMarkupsWidget.currentNode() != None:
        JawPoints = self.ui.SimpleMarkupsWidget.currentNode()
        jointRAS = [0,]*3
        JawPoints.GetNthControlPointPosition(0,jointRAS)
        children = vtk.vtkIdList()
        shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
        outFolder = shNode.GetItemByName("Tooth Tips")
        pluginHandler = slicer.qSlicerSubjectHierarchyPluginHandler().instance()
        folderPlugin = pluginHandler.pluginByName("Folder")        
        if outFolder > 0:
          shNode.GetItemChildren(outFolder, children)
          if children.GetNumberOfIds() > 0:
            lineNames = [shNode.GetItemDataNode(children.GetId(0)).GetName()]
            for i in range(1,children.GetNumberOfIds()):
              lineNames.append(shNode.GetItemDataNode(children.GetId(i)).GetName())
            for i in lineNames:
              ToothTiplineNode = slicer.mrmlScene.GetFirstNodeByName(i)
              ToothTiplineNode.SetNthControlPointPosition(0, jointRAS)     

    def outtoothMarkupChanged(unusedArg1=None, unusedArg2=None):
      if slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Tooth Tip Points") != None:
        ToothTipPoints = slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Tooth Tip Points")
        children = vtk.vtkIdList()
        shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
        outFolder = shNode.GetItemByName("Tooth Tips")
        pluginHandler = slicer.qSlicerSubjectHierarchyPluginHandler().instance()
        folderPlugin = pluginHandler.pluginByName("Folder")        
        if outFolder > 0:
          shNode.GetItemChildren(outFolder, children)
          if children.GetNumberOfIds() > 0:
            lineNames = [shNode.GetItemDataNode(children.GetId(0)).GetName()]
            for i in range(1,children.GetNumberOfIds()):
              lineNames.append(shNode.GetItemDataNode(children.GetId(i)).GetName())
            lineNames = [sub.replace(' Tooth Tip', '') for sub in lineNames]
            for i in lineNames:
              ToothTiplineNode = slicer.mrmlScene.GetFirstNodeByName(i + " Tooth Tip")
              toothtipRAS = [0,]*3
              ptindex = ToothTipPoints.GetControlPointIndexByLabel(i)
              ToothTipPoints.GetNthControlPointPosition(ptindex,toothtipRAS)
              ToothTiplineNode.SetNthControlPointPosition(1, toothtipRAS)     

        
    if slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Tooth Tip Points") != None:
      ToothTipPoints = slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Tooth Tip Points")
      if self.ui.SimpleMarkupsWidget.currentNode() != None:
        JawPoints = self.ui.SimpleMarkupsWidget.currentNode()
        jointRAS = [0,]*3
        JawPoints.GetNthControlPointPosition(0,jointRAS)
        posjointMarkupsNodeObserver = JawPoints.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent, outjointMarkupChanged)
      outtoothMarkupsNodeObserver = ToothTipPoints.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent, outtoothMarkupChanged)
      for i in range(ToothTipPoints.GetNumberOfControlPoints()):
        toothtipRAS = [0,]*3
        ToothTipPoints.GetNthControlPointPosition(i,toothtipRAS)
        segname = ToothTipPoints.GetNthControlPointLabel(i)
        if slicer.mrmlScene.GetFirstNodeByName(segname + " Tooth Tip") == None:
          ToothTiplineNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", segname + " Tooth Tip")
          ToothTiplineNode.GetDisplayNode().SetPropertiesLabelVisibility(False)
          ToothTiplineNode.SetSaveWithScene(0)
          ToothTiplineNode.AddControlPoint(jointRAS)
          ToothTiplineNode.AddControlPoint(toothtipRAS)
          ToothTiplineNode.SetNthControlPointLocked(0,1)
          ToothTiplineNode.SetNthControlPointLocked(1,1)
          ToothTiplineNode.GetDisplayNode().SetGlyphType(7)
          ToothTiplineNode.SetLocked(1)
          shNode.SetItemParent(shNode.GetItemByDataNode(ToothTiplineNode), outFolder)
        else: 
          ToothTiplineNode = slicer.mrmlScene.GetFirstNodeByName(segname + " Tooth Tip")
          if ToothTiplineNode.GetDisplayNode().GetVisibility() == 1:
            ToothTiplineNode.GetDisplayNode().SetVisibility(0)
          else:
            ToothTiplineNode.GetDisplayNode().SetVisibility(1)
      toothtipRAS = [0,]*3
      ToothTipPoints.GetNthControlPointPosition(0,toothtipRAS)
      segname = ToothTipPoints.GetNthControlPointLabel(0)
      ToothTiplineNode = slicer.mrmlScene.GetFirstNodeByName(segname + " Tooth Tip")
      if ToothTiplineNode.GetDisplayNode().GetVisibility() == 1:
        self._parameterNode.SetParameter("ToothTips","True")
      else:
        self._parameterNode.SetParameter("ToothTips","False")

  def onPositionVis(self):
    """
    Run processing when user clicks "Tooth Position Vis" button.
    """
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    posFolder = shNode.GetItemByName("Tooth Positions")
    pluginHandler = slicer.qSlicerSubjectHierarchyPluginHandler().instance()
    folderPlugin = pluginHandler.pluginByName("Folder")
    
    def posjointMarkupChanged(unusedArg1=None, unusedArg2=None):
      if self.ui.SimpleMarkupsWidget.currentNode() != None:
        JawPoints = self.ui.SimpleMarkupsWidget.currentNode()
        jointRAS = [0,]*3
        JawPoints.GetNthControlPointPosition(0,jointRAS)
        children = vtk.vtkIdList()
        shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
        posFolder = shNode.GetItemByName("Tooth Positions")
        pluginHandler = slicer.qSlicerSubjectHierarchyPluginHandler().instance()
        folderPlugin = pluginHandler.pluginByName("Folder")        
        if posFolder > 0:
          shNode.GetItemChildren(posFolder, children)
          if children.GetNumberOfIds() > 0:
            lineNames = [shNode.GetItemDataNode(children.GetId(0)).GetName()]
            for i in range(1,children.GetNumberOfIds()):
              lineNames.append(shNode.GetItemDataNode(children.GetId(i)).GetName())
            for i in lineNames:
              ToothPoslineNode = slicer.mrmlScene.GetFirstNodeByName(i)
              ToothPoslineNode.SetNthControlPointPosition(0, jointRAS)     

    def postoothMarkupChanged(unusedArg1=None, unusedArg2=None):
      if slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Tooth Position Points") != None:
        ToothPosPoints = slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Tooth Position Points")
        children = vtk.vtkIdList()
        shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
        posFolder = shNode.GetItemByName("Tooth Positions")
        pluginHandler = slicer.qSlicerSubjectHierarchyPluginHandler().instance()
        folderPlugin = pluginHandler.pluginByName("Folder")        
        if posFolder > 0:
          shNode.GetItemChildren(posFolder, children)
          if children.GetNumberOfIds() > 0:
            lineNames = [shNode.GetItemDataNode(children.GetId(0)).GetName()]
            for i in range(1,children.GetNumberOfIds()):
              lineNames.append(shNode.GetItemDataNode(children.GetId(i)).GetName())
            lineNames = [sub.replace('Tooth Position', '') for sub in lineNames]
            for i in lineNames:
              ToothPoslineNode = slicer.mrmlScene.GetFirstNodeByName(i + "Tooth Position")
              toothposRAS = [0,]*3
              ptindex = ToothPosPoints.GetControlPointIndexByLabel(i)
              ToothPosPoints.GetNthControlPointPosition(ptindex,toothposRAS)
              ToothPoslineNode.SetNthControlPointPosition(1, toothposRAS)     

        
    if slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Tooth Position Points") != None:
      ToothPosPoints = slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Tooth Position Points")
      if self.ui.SimpleMarkupsWidget.currentNode() != None:
        JawPoints = self.ui.SimpleMarkupsWidget.currentNode()
        jointRAS = [0,]*3
        JawPoints.GetNthControlPointPosition(0,jointRAS)
        posjointMarkupsNodeObserver = JawPoints.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent, posjointMarkupChanged)
      postoothMarkupsNodeObserver = ToothPosPoints.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent, postoothMarkupChanged)
      for i in range(ToothPosPoints.GetNumberOfControlPoints()):
        toothposRAS = [0,]*3
        ToothPosPoints.GetNthControlPointPosition(i,toothposRAS)
        segname = ToothPosPoints.GetNthControlPointLabel(i)
        if slicer.mrmlScene.GetFirstNodeByName(segname + "Tooth Position") == None:
          ToothPoslineNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", segname + "Tooth Position")
          ToothPoslineNode.GetDisplayNode().SetPropertiesLabelVisibility(False)
          ToothPoslineNode.GetDisplayNode().SetSelectedColor((0, 0.72, 0.92))
          ToothPoslineNode.GetDisplayNode().SetActiveColor((1, 0.65, 0.0))
          ToothPoslineNode.SetSaveWithScene(0)
          ToothPoslineNode.AddControlPoint(jointRAS)
          ToothPoslineNode.AddControlPoint(toothposRAS)
          ToothPoslineNode.SetNthControlPointLocked(0,1)
          ToothPoslineNode.SetNthControlPointLocked(1,1)
          ToothPoslineNode.GetDisplayNode().SetGlyphType(7)
          ToothPoslineNode.SetLocked(1)
          shNode.SetItemParent(shNode.GetItemByDataNode(ToothPoslineNode), posFolder)
        else: 
          ToothPoslineNode = slicer.mrmlScene.GetFirstNodeByName(segname + "Tooth Position")
          if ToothPoslineNode.GetDisplayNode().GetVisibility() == 1:
            ToothPoslineNode.GetDisplayNode().SetVisibility(0)
          else:
            ToothPoslineNode.GetDisplayNode().SetVisibility(1)
      toothposRAS = [0,]*3
      ToothPosPoints.GetNthControlPointPosition(0,toothposRAS)
      segname = ToothPosPoints.GetNthControlPointLabel(0)
      ToothPoslineNode = slicer.mrmlScene.GetFirstNodeByName(segname + "Tooth Position")
      if ToothPoslineNode.GetDisplayNode().GetVisibility() == 1:
        self._parameterNode.SetParameter("ToothPos","True")
      else:
        self._parameterNode.SetParameter("ToothPos","False")

    
  def onResetButton(self):
    """
    Run processing when user clicks "Reset" button.
    """
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    shFolderItemId = shNode.GetItemByName("Dental Dynamics Misc")
    if shFolderItemId != 0:
      shNode.RemoveItem(shFolderItemId)
    slicer.mrmlScene.RemoveNode(self.ui.tableSelector.currentNode())

    outFolder = shNode.GetItemByName("Tooth Tips")
    pluginHandler = slicer.qSlicerSubjectHierarchyPluginHandler().instance()
    folderPlugin = pluginHandler.pluginByName("Folder")
    
    def outjointMarkupChanged(unusedArg1=None, unusedArg2=None):
      if self.ui.SimpleMarkupsWidget.currentNode() != None:
        JawPoints = self.ui.SimpleMarkupsWidget.currentNode()
        jointRAS = [0,]*3
        JawPoints.GetNthControlPointPosition(0,jointRAS)
        children = vtk.vtkIdList()
        shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
        outFolder = shNode.GetItemByName("Tooth Tips")
        pluginHandler = slicer.qSlicerSubjectHierarchyPluginHandler().instance()
        folderPlugin = pluginHandler.pluginByName("Folder")        
        if outFolder > 0:
          shNode.GetItemChildren(outFolder, children)
          if children.GetNumberOfIds() > 0:
            lineNames = [shNode.GetItemDataNode(children.GetId(0)).GetName()]
            for i in range(1,children.GetNumberOfIds()):
              lineNames.append(shNode.GetItemDataNode(children.GetId(i)).GetName())
            for i in lineNames:
              ToothTiplineNode = slicer.mrmlScene.GetFirstNodeByName(i)
              ToothTiplineNode.SetNthControlPointPosition(0, jointRAS)           
    
    def outtoothMarkupChanged(unusedArg1=None, unusedArg2=None):
      if slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Tooth Tip Points") != None:
        ToothTipPoints = slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Tooth Tip Points")
        children = vtk.vtkIdList()
        shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
        outFolder = shNode.GetItemByName("Tooth Tips")
        pluginHandler = slicer.qSlicerSubjectHierarchyPluginHandler().instance()
        folderPlugin = pluginHandler.pluginByName("Folder")        
        if outFolder > 0:
          shNode.GetItemChildren(outFolder, children)
          if children.GetNumberOfIds() > 0:
            lineNames = [shNode.GetItemDataNode(children.GetId(0)).GetName()]
            for i in range(1,children.GetNumberOfIds()):
              lineNames.append(shNode.GetItemDataNode(children.GetId(i)).GetName())
            lineNames = [sub.replace(' Tooth Tip', '') for sub in lineNames]
            for i in lineNames:
              ToothTiplineNode = slicer.mrmlScene.GetFirstNodeByName(i + " Tooth Tip")
              toothtipRAS = [0,]*3
              ptindex = ToothTipPoints.GetControlPointIndexByLabel(i)
              ToothTipPoints.GetNthControlPointPosition(ptindex,toothtipRAS)
              ToothTiplineNode.SetNthControlPointPosition(1, toothtipRAS)     
 
    def posjointMarkupChanged(unusedArg1=None, unusedArg2=None):
      if self.ui.SimpleMarkupsWidget.currentNode() != None:
        JawPoints = self.ui.SimpleMarkupsWidget.currentNode()
        jointRAS = [0,]*3
        JawPoints.GetNthControlPointPosition(0,jointRAS)
        children = vtk.vtkIdList()
        shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
        posFolder = shNode.GetItemByName("Tooth Positions")
        pluginHandler = slicer.qSlicerSubjectHierarchyPluginHandler().instance()
        folderPlugin = pluginHandler.pluginByName("Folder")        
        if posFolder > 0:
          shNode.GetItemChildren(posFolder, children)
          if children.GetNumberOfIds() > 0:
            lineNames = [shNode.GetItemDataNode(children.GetId(0)).GetName()]
            for i in range(1,children.GetNumberOfIds()):
              lineNames.append(shNode.GetItemDataNode(children.GetId(i)).GetName())
            for i in lineNames:
              ToothPoslineNode = slicer.mrmlScene.GetFirstNodeByName(i)
              ToothPoslineNode.SetNthControlPointPosition(0, jointRAS)     

    def postoothMarkupChanged(unusedArg1=None, unusedArg2=None):
      if slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Tooth Position Points") != None:
        ToothPosPoints = slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Tooth Position Points")
        children = vtk.vtkIdList()
        shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
        posFolder = shNode.GetItemByName("Tooth Positions")
        pluginHandler = slicer.qSlicerSubjectHierarchyPluginHandler().instance()
        folderPlugin = pluginHandler.pluginByName("Folder")        
        if posFolder > 0:
          shNode.GetItemChildren(posFolder, children)
          if children.GetNumberOfIds() > 0:
            lineNames = [shNode.GetItemDataNode(children.GetId(0)).GetName()]
            for i in range(1,children.GetNumberOfIds()):
              lineNames.append(shNode.GetItemDataNode(children.GetId(i)).GetName())
            lineNames = [sub.replace('Tooth Position', '') for sub in lineNames]
            for i in lineNames:
              ToothPoslineNode = slicer.mrmlScene.GetFirstNodeByName(i + "Tooth Position")
              toothposRAS = [0,]*3
              ptindex = ToothPosPoints.GetControlPointIndexByLabel(i)
              ToothPosPoints.GetNthControlPointPosition(ptindex,toothposRAS)
              ToothPoslineNode.SetNthControlPointPosition(1, toothposRAS)  

    if self.ui.SimpleMarkupsWidget.currentNode() != None:
      JawPoints = self.ui.SimpleMarkupsWidget.currentNode()
      outjointMarkupsNodeObserver = JawPoints.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent, outjointMarkupChanged)
      JawPoints.RemoveObserver(outjointMarkupsNodeObserver)
      posjointMarkupsNodeObserver = JawPoints.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent, posjointMarkupChanged)
      JawPoints.RemoveObserver(posjointMarkupsNodeObserver)

    if slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Tooth Tip Points") != None:
      ToothTipPoints = slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Tooth Tip Points")
      outtoothMarkupsNodeObserver = ToothTipPoints.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent, outtoothMarkupChanged)
      ToothTipPoints.RemoveObserver(outtoothMarkupsNodeObserver)
    if slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Tooth Position Points") != None:
      ToothPosPoints = slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Tooth Position Points")      
      postoothMarkupsNodeObserver = ToothPosPoints.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent, postoothMarkupChanged)
      ToothPosPoints.RemoveObserver(postoothMarkupsNodeObserver)
    
    
    self._parameterNode.SetParameter("ToothTips", "False")
    self._parameterNode.SetParameter("ToothPos", "False")

    
    layoutManager = slicer.app.layoutManager()
    if layoutManager.layout == 166:
      layoutManager.setLayout(4)          

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
      self.logic.run(self.ui.SpecieslineEdit.text, 
      self.ui.LowerradioButton.checked, self.ui.UpperradioButton.checked,
      self.ui.LeftradioButton.checked, self.ui.RightradioButton.checked,
      self.ui.SegmentSelectorWidget.currentNode(), self.ui.SegmentSelectorWidget.selectedSegmentIDs(), self.ui.FlipcheckBox.checked,
      self.ui.SimpleMarkupsWidget.currentNode(), self.ui.SimradioButton.checked,
      self.ui.MusclecheckBox1.checked, self.ui.ForceInputBox1.value, self.ui.AngleInputBox1.value, self.ui.VolumeInputBox1.value, 
      self.ui.MusclecheckBox2.checked, self.ui.ForceInputBox2.value, self.ui.AngleInputBox2.value, self.ui.VolumeInputBox2.value, 
      self.ui.MusclecheckBox3.checked, self.ui.ForceInputBox3.value, self.ui.AngleInputBox3.value, self.ui.VolumeInputBox3.value,       
      tableNode, self.ui.FlipSegmentSelectorWidget.selectedSegmentIDs())
            
      #if self.ui.FlipSegmentSelectorWidget.selectedSegmentIDs() != "()":
      #  self.ui.FlipSegmentSelectorWidget.setSelectedSegmentIDs("()")
        
      if self._parameterNode.GetParameter("ToothTips") == "False":
        self.onTipVis()
         
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
    if not parameterNode.GetParameter("SpeciesName"):
      parameterNode.SetParameter("SpeciesName", "Enter specimen name")    
    if not parameterNode.GetParameter("Segments"):
      parameterNode.SetParameter("Segments", "()")  
    if not parameterNode.GetParameter("Flip"):
      parameterNode.SetParameter("Flip", "False")    
    if not parameterNode.GetParameter("Muscle1"):
     parameterNode.SetParameter("Muscle1", "True")    
    if not parameterNode.GetParameter("Force1"):
     parameterNode.SetParameter("Force1", "1.0")
    if not parameterNode.GetParameter("Angle1"):
     parameterNode.SetParameter("Angle1", "90.0")
    if not parameterNode.GetParameter("Volume1"):
     parameterNode.SetParameter("Volume1", "1")    
    if not parameterNode.GetParameter("Muscle2"):
     parameterNode.SetParameter("Muscle2", "False")    
    if not parameterNode.GetParameter("Force2"):
     parameterNode.SetParameter("Force2", "1.0")
    if not parameterNode.GetParameter("Angle2"):
     parameterNode.SetParameter("Angle2", "90.0")
    if not parameterNode.GetParameter("Volume2"):
     parameterNode.SetParameter("Volume2", "1")  
    if not parameterNode.GetParameter("Muscle3"):
     parameterNode.SetParameter("Muscle3", "False")     
    if not parameterNode.GetParameter("Force3"):
     parameterNode.SetParameter("Force3", "1.0")
    if not parameterNode.GetParameter("Angle3"):
     parameterNode.SetParameter("Angle3", "90.0")
    if not parameterNode.GetParameter("Volume3"):
     parameterNode.SetParameter("Volume3", "1")       
    if not parameterNode.GetParameter("FlipSegments"):
      parameterNode.SetParameter("FlipSegments", "()") 
    if not parameterNode.GetParameter("ToothTips"):
      parameterNode.SetParameter("ToothTips", "False")
    if not parameterNode.GetParameter("ToothPos"):
      parameterNode.SetParameter("ToothPos", "False")

            
  def run(self, species, LowerJaw, UpperJaw, LeftJaw, RightJaw,
  segmentationNode, segmentList, flipcheckBox, pointNode, simulate, 
  muscle1, force1, angle1, volume1,
  muscle2, force2, angle2, volume2,
  muscle3, force3, angle3, volume3,
  tableNode, FlipsegmentList):
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
    import math
    import time

    start = time.time()
    logging.info('Processing started')

    if segmentationNode.GetSegmentation().GetConversionParameter("Conversion method") == "1":
      raise ValueError("Dental Dynamics is not compatible with the SurfaceNets method. Turn off to continue.")
    
    # Get visible segment ID list.
    # Get segment ID list
    visibleSegmentIds = vtk.vtkStringArray()
    segmentationNode.GetDisplayNode().GetVisibleSegmentIDs(visibleSegmentIds)
    segmentationNode.GetDisplayNode().SetAllSegmentsVisibility(False)
              
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
    RelPosArray.SetName("RelTooth Position")   
   
    ToothPositionArray = vtk.vtkFloatArray()
    ToothPositionArray.SetName("Position (mm)")
    
    ToothHeightArray = vtk.vtkFloatArray()
    ToothHeightArray.SetName("Tooth Height (mm)")
    
    ToothWidthArray = vtk.vtkFloatArray()
    ToothWidthArray.SetName("Tooth Width (mm)")
    
    AspectRatioArray = vtk.vtkFloatArray()
    AspectRatioArray.SetName("Aspect Ratio")    

    SurfaceAreaArray = vtk.vtkFloatArray()
    SurfaceAreaArray.SetName("Surface Area (mm^2)")
    
    if muscle1 == True:
      InputForceArray1 = vtk.vtkFloatArray()
      InputForceArray1.SetName("M1 In Force (N)")
    
      InputAngleArray1 = vtk.vtkFloatArray()
      InputAngleArray1.SetName("M1 Angle (deg)")
    
      MechAdvArray1 = vtk.vtkFloatArray()
      MechAdvArray1.SetName("M1 Mech Adv")  
    
      FToothArray1 = vtk.vtkFloatArray()
      FToothArray1.SetName("M1 F-tooth (N)")    
      
      if simulate == False: 
        FiberArray1 = vtk.vtkFloatArray()
        FiberArray1.SetName("M1 Fiber Length (mm)")  
      
        VolumeArray1 = vtk.vtkFloatArray()
        VolumeArray1.SetName("M1 Volume (mm^3)")  

      
    if muscle2 == True:
      InputForceArray2 = vtk.vtkFloatArray()
      InputForceArray2.SetName("M2 In Force (N)")
    
      InputAngleArray2 = vtk.vtkFloatArray()
      InputAngleArray2.SetName("M2 Angle (deg)")
    
      MechAdvArray2 = vtk.vtkFloatArray()
      MechAdvArray2.SetName("M2 Mech Adv")  
    
      FToothArray2 = vtk.vtkFloatArray()
      FToothArray2.SetName("M2 F-tooth (N)")  
      
      if simulate == False: 
        FiberArray2 = vtk.vtkFloatArray()
        FiberArray2.SetName("M2 Fiber Length (mm)")  

        VolumeArray2 = vtk.vtkFloatArray()
        VolumeArray2.SetName("M2 Volume (mm^3)")  

    if muscle3 == True:
      InputForceArray3 = vtk.vtkFloatArray()
      InputForceArray3.SetName("M3 In Force (N)")
    
      InputAngleArray3 = vtk.vtkFloatArray()
      InputAngleArray3.SetName("M3 Angle (deg)")
    
      MechAdvArray3 = vtk.vtkFloatArray()
      MechAdvArray3.SetName("M3 Mech Adv")  
    
      FToothArray3 = vtk.vtkFloatArray()
      FToothArray3.SetName("M3 F-tooth (N)")  
      
      if simulate == False: 
        FiberArray3 = vtk.vtkFloatArray()
        FiberArray3.SetName("M3 Fiber Length (mm)")  

        VolumeArray3 = vtk.vtkFloatArray()
        VolumeArray3.SetName("M3 Volume (mm^3)")  

          
    FToothTotalArray = vtk.vtkFloatArray()
    FToothTotalArray.SetName("Total F-tooth (N)")  
    StressArray = vtk.vtkFloatArray()
    StressArray.SetName("Stress (N/m^2)")
    
    # create misc folder  
    if species == "Enter specimen name" or species == "": 
      species = "NA" 
    jawID = "NA"
    if LowerJaw == True:
      jawID = "Lower Jaw"
    elif UpperJaw == True:
      jawID = "Upper Jaw"
    side = "NA"
    if LeftJaw == True:
      side = "Left"
    elif RightJaw == True:
      side = "Right"
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    newFolder = shNode.GetItemByName("Dental Dynamics Misc")
    outFolder = shNode.GetItemByName("Tooth Tips")
    posFolder = shNode.GetItemByName("Tooth Positions")
    if slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Tooth Tip Points") == None:
      ToothTipPoints = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode", "Dental Dynamics Tooth Tip Points")
      ToothTipPoints.GetDisplayNode().SetPointLabelsVisibility(False)
    else:
      ToothTipPoints = slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Tooth Tip Points") 
    if slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Tooth Position Points") == None:
      ToothPosPoints = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode", "Dental Dynamics Tooth Position Points")
      ToothPosPoints.GetDisplayNode().SetSelectedColor((0, 0.72, 0.92))
      ToothPosPoints.GetDisplayNode().SetActiveColor((1, 0.65, 0.0))
      ToothPosPoints.GetDisplayNode().SetPointLabelsVisibility(False)
    else:
      ToothPosPoints = slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Tooth Position Points") 
    if newFolder == 0:
      newFolder = shNode.CreateFolderItem(shNode.GetSceneItemID(), "Dental Dynamics Misc")      
      outFolder = shNode.CreateFolderItem(shNode.GetSceneItemID(), "Tooth Tips")      
      posFolder = shNode.CreateFolderItem(shNode.GetSceneItemID(), "Tooth Positions")
      pluginHandler = slicer.qSlicerSubjectHierarchyPluginHandler().instance()
      folderPlugin = pluginHandler.pluginByName("Folder")
      shNode.SetItemParent(shNode.GetItemByDataNode(ToothTipPoints), newFolder)
      shNode.SetItemParent(shNode.GetItemByDataNode(ToothPosPoints), newFolder)
      shNode.SetItemParent(outFolder, newFolder)
      shNode.SetItemParent(posFolder, newFolder)
    shNode.SetItemExpanded(newFolder,0)   
    shNode.SetItemExpanded(outFolder,0) 
    shNode.SetItemExpanded(posFolder,0) 
    # create models of the teeth
    exportFolderItemId = shNode.CreateFolderItem(shNode.GetSceneItemID(), "Tooth Segments")
    slicer.modules.segmentations.logic().ExportSegmentsToModels(segmentationNode, segmentList, exportFolderItemId)
    shNode.SetItemParent(exportFolderItemId, newFolder)
    boxFolderItemId = shNode.CreateFolderItem(shNode.GetSceneItemID(), "Tooth Boxes")
    shNode.SetItemParent(boxFolderItemId, newFolder)
    shNode.SetItemExpanded(boxFolderItemId,0)

    # calculate the centroid and surface area of each segment
    for i in segmentList:
      segmentationNode.GetDisplayNode().SetSegmentVisibility(i,True)

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
    segmentationNode.GetDisplayNode().SetAllSegmentsVisibility(False)

    # measure jaw length
    jointRAS = [0,]*3
    pointNode.GetNthControlPointPosition(0,jointRAS)
    jawtipRAS = [0,]*3
    pointNode.GetNthControlPointPosition(1,jawtipRAS)
    lengthLine = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", "JawLength")
    lengthLine.GetDisplayNode().SetPropertiesLabelVisibility(False)
    lengthLine.AddControlPoint(jointRAS)
    lengthLine.AddControlPoint(jawtipRAS)
    JawLength = lengthLine.GetMeasurement('length').GetValue()
    #slicer.mrmlScene.RemoveNode(lengthLine)
    
    # measure in-lever
    if muscle1 == False and muscle2 == False and muscle3 == False:
      raise ValueError("No input muscles selected")
    if muscle1 == True:
      insertRAS = [0,]*3
      pointNode.GetNthControlPointPosition(2,insertRAS)
      if insertRAS == [0, 0, 0]:
        raise ValueError("Muscle 1 Insertion not defined")
      leverLine = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", "InLever1")
      leverLine.GetDisplayNode().SetPropertiesLabelVisibility(False)
      leverLine.AddControlPoint(jointRAS)
      leverLine.AddControlPoint(insertRAS)
      InLever1 = leverLine.GetMeasurement('length').GetValue()
      slicer.mrmlScene.RemoveNode(leverLine)

    if muscle2 == True:
      insertRAS = [0,]*3
      pointNode.GetNthControlPointPosition(4,insertRAS)
      if insertRAS == [0, 0, 0]:
        raise ValueError("Muscle 2 Insertion not defined")
      leverLine = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", "InLever2")
      leverLine.GetDisplayNode().SetPropertiesLabelVisibility(False)
      leverLine.AddControlPoint(jointRAS)
      leverLine.AddControlPoint(insertRAS)
      InLever2 = leverLine.GetMeasurement('length').GetValue()
      slicer.mrmlScene.RemoveNode(leverLine) 
      
    if muscle3 == True:
      insertRAS = [0,]*3
      pointNode.GetNthControlPointPosition(6,insertRAS)
      if insertRAS == [0, 0, 0]:
        raise ValueError("Muscle 3 Insertion not defined")
      leverLine = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", "InLever3")
      leverLine.GetDisplayNode().SetPropertiesLabelVisibility(False)
      leverLine.AddControlPoint(jointRAS)
      leverLine.AddControlPoint(insertRAS)
      InLever3 = leverLine.GetMeasurement('length').GetValue()
      slicer.mrmlScene.RemoveNode(leverLine) 

    # measure fiber length and estimate force
    if muscle1 == False and muscle2 == False and muscle3 == False:
      raise ValueError("No input muscles selected")
    if muscle1 == True and simulate == False:
      insertRAS = [0,]*3
      pointNode.GetNthControlPointPosition(2,insertRAS)
      if insertRAS == [0, 0, 0]:
        raise ValueError("Muscle 1 Insertion not defined")
      originRAS = [0,]*3
      pointNode.GetNthControlPointPosition(3,originRAS)
      if originRAS == [0, 0, 0]:
        raise ValueError("Muscle 1 Origin not defined")
      fiberLine = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", "FiberLength1")
      fiberLine.GetDisplayNode().SetPropertiesLabelVisibility(False)
      fiberLine.AddControlPoint(insertRAS)
      fiberLine.AddControlPoint(originRAS)
      fiber1 = fiberLine.GetMeasurement('length').GetValue()
      slicer.mrmlScene.RemoveNode(fiberLine)
      force1 = volume1/fiber1 * 0.2 # use default of 200 kPA of 
      
    if muscle2 == True and simulate == False:
      insertRAS = [0,]*3
      pointNode.GetNthControlPointPosition(4,insertRAS)
      if insertRAS == [0, 0, 0]:
        raise ValueError("Muscle 2 Insertion not defined")
      originRAS = [0,]*3
      pointNode.GetNthControlPointPosition(5,originRAS)
      if originRAS == [0, 0, 0]:
        raise ValueError("Muscle 2 Origin not defined")
      fiberLine = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", "FiberLength2")
      fiberLine.GetDisplayNode().SetPropertiesLabelVisibility(False)
      fiberLine.AddControlPoint(insertRAS)
      fiberLine.AddControlPoint(originRAS)
      fiber2 = fiberLine.GetMeasurement('length').GetValue()
      slicer.mrmlScene.RemoveNode(fiberLine)
      force2 = volume2/fiber2 * 0.8

    if muscle3 == True and simulate == False:
      insertRAS = [0,]*3
      pointNode.GetNthControlPointPosition(6,insertRAS)
      if insertRAS == [0, 0, 0]:
        raise ValueError("Muscle 3 Insertion not defined")
      originRAS = [0,]*3
      pointNode.GetNthControlPointPosition(7,originRAS)
      if originRAS == [0, 0, 0]:
        raise ValueError("Muscle 3 Origin not defined")
      fiberLine = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", "FiberLength3")
      fiberLine.GetDisplayNode().SetPropertiesLabelVisibility(False)
      fiberLine.AddControlPoint(insertRAS)
      fiberLine.AddControlPoint(originRAS)
      fiber3 = fiberLine.GetMeasurement('length').GetValue()
      slicer.mrmlScene.RemoveNode(fiberLine)
      force3 = volume3/fiber3 * 0.8
      
    # measure muscle angle 
    if muscle1 == False and muscle2 == False and muscle3 == False:
      raise ValueError("No input muscles selected")
    if muscle1 == True and simulate == False:
      insertRAS = [0,]*3
      pointNode.GetNthControlPointPosition(2,insertRAS)
      if insertRAS == [0, 0, 0]:
        raise ValueError("Muscle 1 Insertion not defined")
      originRAS = [0,]*3
      pointNode.GetNthControlPointPosition(3,originRAS)
      if originRAS == [0, 0, 0]:
        raise ValueError("Muscle 1 Origin not defined")
      muscleAngle = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsAngleNode", "Angle1")
      muscleAngle.GetDisplayNode().SetPropertiesLabelVisibility(False)
      muscleAngle.AddControlPoint(jointRAS)
      muscleAngle.AddControlPoint(insertRAS)
      muscleAngle.AddControlPoint(originRAS)
      angle1 = muscleAngle.GetMeasurement('angle').GetValue()
      slicer.mrmlScene.RemoveNode(muscleAngle)
      
    if muscle2 == True and simulate == False:
      insertRAS = [0,]*3
      pointNode.GetNthControlPointPosition(4,insertRAS)
      if insertRAS == [0, 0, 0]:
        raise ValueError("Muscle 2 Insertion not defined")
      originRAS = [0,]*3
      pointNode.GetNthControlPointPosition(5,originRAS)
      if originRAS == [0, 0, 0]:
        raise ValueError("Muscle 2 Origin not defined")
      muscleAngle = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsAngleNode", "Angle2")
      muscleAngle.GetDisplayNode().SetPropertiesLabelVisibility(False)
      muscleAngle.AddControlPoint(jointRAS)
      muscleAngle.AddControlPoint(insertRAS)
      muscleAngle.AddControlPoint(originRAS)
      angle2 = muscleAngle.GetMeasurement('angle').GetValue()
      slicer.mrmlScene.RemoveNode(muscleAngle)

    if muscle3 == True and simulate == False:
      insertRAS = [0,]*3
      pointNode.GetNthControlPointPosition(6,insertRAS)
      if insertRAS == [0, 0, 0]:
        raise ValueError("Muscle 3 Insertion not defined")
      originRAS = [0,]*3
      pointNode.GetNthControlPointPosition(7,originRAS)
      if originRAS == [0, 0, 0]:
        raise ValueError("Muscle 3 Origin not defined")
      muscleAngle = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsAngleNode", "Angle3")
      muscleAngle.GetDisplayNode().SetPropertiesLabelVisibility(False)
      muscleAngle.AddControlPoint(jointRAS)
      muscleAngle.AddControlPoint(insertRAS)
      muscleAngle.AddControlPoint(originRAS)
      angle3 = muscleAngle.GetMeasurement('angle').GetValue()
      slicer.mrmlScene.RemoveNode(muscleAngle)

      
    # remove any control points that should no longer be included
    segmentNames = [segmentationNode.GetSegmentation().GetSegment(segmentList[0]).GetName()]
    for i in range(1,len(segmentList)):
      segmentNames.append(segmentationNode.GetSegmentation().GetSegment(segmentList[i]).GetName())
    pointlabels =  vtk.vtkStringArray()
    ToothTipPoints.GetControlPointLabels(pointlabels)
    if pointlabels.GetNumberOfValues() > 0:
      labelNames = [pointlabels.GetValue(0)]
      for i in range(1,pointlabels.GetSize()):
        labelNames.append(pointlabels.GetValue(i))
      extralabels = set(labelNames) - set(segmentNames)
      extralabels = list(extralabels)
      for i in extralabels:
        pointindex = ToothTipPoints.GetControlPointIndexByLabel(i)
        ToothTipPoints.RemoveNthControlPoint(pointindex)   
        ToothPosPoints.RemoveNthControlPoint(pointindex)
        
    # remove any lines that should no longer exist
    pointlabels =  vtk.vtkStringArray()
    ToothTipPoints.GetControlPointLabels(pointlabels)
    if pointlabels.GetNumberOfValues() > 0:
      labelNames = [pointlabels.GetValue(0)]
      for i in range(1,pointlabels.GetSize()):
        labelNames.append(pointlabels.GetValue(i))
      children = vtk.vtkIdList()
      shNode.GetItemChildren(outFolder, children)
      if children.GetNumberOfIds() > 0:
        lineNames = [shNode.GetItemDataNode(children.GetId(0)).GetName()]
        for i in range(1,children.GetNumberOfIds()):
          lineNames.append(shNode.GetItemDataNode(children.GetId(i)).GetName())
        lineNames = [sub.replace(' Tooth Tip', '') for sub in lineNames]
        extralines = set(lineNames) - set(labelNames)
        extralines = list(extralines)
        for i in extralines:
          extraline = slicer.mrmlScene.GetFirstNodeByName(i + " Tooth Tip")
          slicer.mrmlScene.RemoveNode(extraline)       
          extraline = slicer.mrmlScene.GetFirstNodeByName(i + "Tooth Position")
          slicer.mrmlScene.RemoveNode(extraline)       
     
      
    # do calculations for each segment
    for segmentId in segmentList:
     
     SpeciesArray.InsertNextValue(species)  
     JawIDArray.InsertNextValue(jawID)
     SideArray.InsertNextValue(side)
     
     segment = segmentationNode.GetSegmentation().GetSegment(segmentId)
     SegmentNameArray.InsertNextValue(segment.GetName())
     if muscle1 == True:
       InputForceArray1.InsertNextValue(force1)
       InputAngleArray1.InsertNextValue(angle1)
       if simulate == False:
         VolumeArray1.InsertNextValue(volume1)
         FiberArray1.InsertNextValue(fiber1)
     if muscle2 == True:
       InputForceArray2.InsertNextValue(force2)
       InputAngleArray2.InsertNextValue(angle2)
       if simulate == False:
         VolumeArray2.InsertNextValue(volume2)
         FiberArray2.InsertNextValue(fiber2)
     if muscle3 == True:
       InputForceArray3.InsertNextValue(force3)
       InputAngleArray3.InsertNextValue(angle3)
       if simulate == False:
         VolumeArray3.InsertNextValue(volume3)
         FiberArray3.InsertNextValue(fiber3)
         
     JawLengthArray.InsertNextValue(JawLength)
     
     # measure surface area
     Area = stats[segmentId,"LabelmapSegmentStatisticsPlugin.surface_area_mm2"]/2
     SurfaceAreaArray.InsertNextValue(Area)
     
     flipflag = False
     if segmentId in FlipsegmentList:
       flipflag = True
     
     if ToothTipPoints.GetControlPointIndexByLabel(segment.GetName()) == -1 or flipflag == True:
      # try to get tooth position at the base of the tooth
      obb_origin_ras = np.array(stats[segmentId,"LabelmapSegmentStatisticsPlugin.obb_origin_ras"])
      obb_diameter_mm = np.array(stats[segmentId,"LabelmapSegmentStatisticsPlugin.obb_diameter_mm"])
      obb_direction_ras_x = np.array(stats[segmentId,"LabelmapSegmentStatisticsPlugin.obb_direction_ras_x"])
      obb_direction_ras_y = np.array(stats[segmentId,"LabelmapSegmentStatisticsPlugin.obb_direction_ras_y"])
      obb_direction_ras_z = np.array(stats[segmentId,"LabelmapSegmentStatisticsPlugin.obb_direction_ras_z"])
      segment = segmentationNode.GetSegmentation().GetSegment(segmentId)
      roi=slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsROINode")
      roi.SetName(segment.GetName() + " OBB")
      roi.GetDisplayNode().SetHandlesInteractive(False)  # do not let the user resize the box
      roi.SetSize(obb_diameter_mm)
      #Tooth Position and orient ROI using a transform
      obb_center_ras = obb_origin_ras+0.5*(obb_diameter_mm[0] * obb_direction_ras_x + obb_diameter_mm[1] * obb_direction_ras_y + obb_diameter_mm[2] * obb_direction_ras_z)
      boundingBoxToRasTransform = np.row_stack((np.column_stack((obb_direction_ras_x, obb_direction_ras_y, obb_direction_ras_z, obb_center_ras)), (0, 0, 0, 1)))
      boundingBoxToRasTransformMatrix = slicer.util.vtkMatrixFromArray(boundingBoxToRasTransform)
      bounds = np.zeros(6)
      roi.GetBounds(bounds)
      toothtipRAS = np.array([[0],[0],[bounds[4]],[1]])
      toothposRAS = np.array([[0],[0],[bounds[5]],[1]])
      toothtipRAS_trans = np.dot(boundingBoxToRasTransform, toothtipRAS)
      toothposRAS_trans = np.dot(boundingBoxToRasTransform, toothposRAS)
      toothtipRAS = [float(toothtipRAS_trans[0]),float(toothtipRAS_trans[1]),float(toothtipRAS_trans[2])] 
      toothposRAS = [float(toothposRAS_trans[0]),float(toothposRAS_trans[1]),float(toothposRAS_trans[2])]   
      roi.SetAndObserveObjectToNodeMatrix(boundingBoxToRasTransformMatrix)
      shNode.SetItemParent(shNode.GetItemByDataNode(roi), boxFolderItemId)
      slicer.mrmlScene.RemoveNode(roi)
      
        
      # try to assess whether the tooth tip and position points need to be swapped
      # based on relative to distance to vector representing the lower jaw
      if LowerJaw == True:
        jawvec = jointRAS[0]-jawtipRAS[0],jointRAS[1]-jawtipRAS[1],jointRAS[2]-jawtipRAS[2]
        jawvec = np.array(jawvec)
        posvec = toothposRAS[0]-jointRAS[0],toothposRAS[1]-jointRAS[1],toothposRAS[2]-jointRAS[2]
        posvec = np.array(posvec)
        t = np.dot(jawvec,posvec)/jawvec**2
        jawvecpoint = jointRAS + t*jawvec # a point along jawvec that is closest to toothposRAS
        ToothPos = np.linalg.norm(np.array(toothposRAS)-np.array(jawvecpoint))
        ToothTip = np.linalg.norm(np.array(toothtipRAS)-np.array(jawvecpoint))
        # if the tooth tip is closer to jawvecpoint than the pos then tip and pos are probably swapped
        if flipcheckBox == False:
          if ToothPos > ToothTip:
            toothtipRAS = np.array([[0],[0],[bounds[5]*2.2],[1]])
            toothposRAS = np.array([[0],[0],[bounds[4]*2.2],[1]])
            toothtipRAS_trans = np.dot(boundingBoxToRasTransform, toothtipRAS)
            toothposRAS_trans = np.dot(boundingBoxToRasTransform, toothposRAS)
            toothtipRAS = [toothtipRAS_trans[0],toothtipRAS_trans[1],toothtipRAS_trans[2]]
            toothposRAS = [toothposRAS_trans[0],toothposRAS_trans[1],toothposRAS_trans[2]]
          else:
            toothtipRAS = np.array([[0],[0],[bounds[4]*2.2],[1]])
            toothposRAS = np.array([[0],[0],[bounds[5]*2.2],[1]])
            toothtipRAS_trans = np.dot(boundingBoxToRasTransform, toothtipRAS)
            toothposRAS_trans = np.dot(boundingBoxToRasTransform, toothposRAS)
            toothtipRAS = [toothtipRAS_trans[0],toothtipRAS_trans[1],toothtipRAS_trans[2]]
            toothposRAS = [toothposRAS_trans[0],toothposRAS_trans[1],toothposRAS_trans[2]]
        if flipcheckBox == True:
          if ToothPos < ToothTip:
            toothtipRAS = np.array([[0],[0],[bounds[5]*2.2],[1]])
            toothposRAS = np.array([[0],[0],[bounds[4]*2.2],[1]])
            toothtipRAS_trans = np.dot(boundingBoxToRasTransform, toothtipRAS)
            toothposRAS_trans = np.dot(boundingBoxToRasTransform, toothposRAS)
            toothtipRAS = [toothtipRAS_trans[0],toothtipRAS_trans[1],toothtipRAS_trans[2]]
            toothposRAS = [toothposRAS_trans[0],toothposRAS_trans[1],toothposRAS_trans[2]]
          else:
            toothtipRAS = np.array([[0],[0],[bounds[4]*2.2],[1]])
            toothposRAS = np.array([[0],[0],[bounds[5]*2.2],[1]])
            toothtipRAS_trans = np.dot(boundingBoxToRasTransform, toothtipRAS)
            toothposRAS_trans = np.dot(boundingBoxToRasTransform, toothposRAS)
            toothtipRAS = [toothtipRAS_trans[0],toothtipRAS_trans[1],toothtipRAS_trans[2]]
            toothposRAS = [toothposRAS_trans[0],toothposRAS_trans[1],toothposRAS_trans[2]]
        if flipflag == True: 
          tmp1 = toothtipRAS
          tmp2 = toothposRAS
          toothtipRAS = tmp2
          toothposRAS = tmp1

      if UpperJaw == True:
        insertRAS = [0,]*3
        pointNode.GetNthControlPointPosition(2,insertRAS)
        jawvec = jointRAS[0]-jawtipRAS[0],jointRAS[1]-jawtipRAS[1],jointRAS[2]-jawtipRAS[2]
        jawvec = np.array(jawvec)
        posvec = toothposRAS[0]-insertRAS[0],toothposRAS[1]-insertRAS[1],toothposRAS[2]-insertRAS[2]
        posvec = np.array(posvec)
        t = np.dot(jawvec,posvec)/jawvec**2
        jawvecpoint = insertRAS + t*jawvec
        ToothPos = np.linalg.norm(np.array(toothposRAS)-np.array(jawvecpoint))
        ToothTip = np.linalg.norm(np.array(toothtipRAS)-np.array(jawvecpoint))
        if flipcheckBox == False:
          if ToothPos < ToothTip:
            toothtipRAS = np.array([[0],[0],[bounds[5]*2.2],[1]])
            toothposRAS = np.array([[0],[0],[bounds[4]*2.2],[1]])
            toothtipRAS_trans = np.dot(boundingBoxToRasTransform, toothtipRAS)
            toothposRAS_trans = np.dot(boundingBoxToRasTransform, toothposRAS)
            toothtipRAS = [toothtipRAS_trans[0],toothtipRAS_trans[1],toothtipRAS_trans[2]]
            toothposRAS = [toothposRAS_trans[0],toothposRAS_trans[1],toothposRAS_trans[2]]
          else:
            toothtipRAS = np.array([[0],[0],[bounds[4]*2.2],[1]])
            toothposRAS = np.array([[0],[0],[bounds[5]*2.2],[1]])
            toothtipRAS_trans = np.dot(boundingBoxToRasTransform, toothtipRAS)
            toothposRAS_trans = np.dot(boundingBoxToRasTransform, toothposRAS)
            toothtipRAS = [toothtipRAS_trans[0],toothtipRAS_trans[1],toothtipRAS_trans[2]]
            toothposRAS = [toothposRAS_trans[0],toothposRAS_trans[1],toothposRAS_trans[2]]
        if flipcheckBox == True:
          if ToothPos > ToothTip:
            toothtipRAS = np.array([[0],[0],[bounds[5]*2.2],[1]])
            toothposRAS = np.array([[0],[0],[bounds[4]*2.2],[1]])
            toothtipRAS_trans = np.dot(boundingBoxToRasTransform, toothtipRAS)
            toothposRAS_trans = np.dot(boundingBoxToRasTransform, toothposRAS)
            toothtipRAS = [toothtipRAS_trans[0],toothtipRAS_trans[1],toothtipRAS_trans[2]]
            toothposRAS = [toothposRAS_trans[0],toothposRAS_trans[1],toothposRAS_trans[2]]
          else:
            toothtipRAS = np.array([[0],[0],[bounds[4]*2.2],[1]])
            toothposRAS = np.array([[0],[0],[bounds[5]*2.2],[1]])
            toothtipRAS_trans = np.dot(boundingBoxToRasTransform, toothtipRAS)
            toothposRAS_trans = np.dot(boundingBoxToRasTransform, toothposRAS)
            toothtipRAS = [toothtipRAS_trans[0],toothtipRAS_trans[1],toothtipRAS_trans[2]]
            toothposRAS = [toothposRAS_trans[0],toothposRAS_trans[1],toothposRAS_trans[2]]
        if flipflag == True: 
          tmp1 = toothtipRAS
          tmp2 = toothposRAS
          toothtipRAS = tmp2
          toothposRAS = tmp1
     
      # snap tooth tip points to the tooth  
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
      distanceFilter.EvaluateFunctionAndGetClosestPoint(toothtipRAS, closestPointOnSurface_World)
      #toothtipRAS = stats[segmentId,"LabelmapSegmentStatisticsPlugin.centroid_ras"] # draw to the center of tooth
      toothtipRAS = closestPointOnSurface_World # draw to the tip of the tooth
  
      # iteratively find the center base of the tooth
      curveNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsCurveNode")
      curveNode.AddControlPoint(toothposRAS)
      curveNode.AddControlPoint(obb_center_ras)
      curveNode.GetMeasurement("length").EnabledOn()
      length = curveNode.GetMeasurement("length").GetValue()
      curveNode.ResampleCurveWorld(length/20)
      distance = 1
      dist_index = 0
      # find a point close to the segment
      for i in range(curveNode.GetNumberOfControlPoints()):
        curveRAS = [0,]*3
        curveNode.GetNthControlPointPosition(i,curveRAS)
        distance = distanceFilter.EvaluateFunction(curveRAS)
        dist_index = i
        if distance <0:
          break
      curveRAS = [0,]*3
      curveNode.GetNthControlPointPosition(dist_index,curveRAS)         
      closestPointOnSurface_World = [0,0,0]
      distanceFilter.EvaluateFunctionAndGetClosestPoint(curveRAS, closestPointOnSurface_World)
      toothposRAS = closestPointOnSurface_World
     
      slicer.mrmlScene.RemoveNode(curveNode)
      slicer.mrmlScene.RemoveNode(modelNode)

        
      # add pos and out points to a list
      if ToothTipPoints.GetControlPointIndexByLabel(segment.GetName()) == -1:
        ToothTipPoints.AddControlPoint(toothtipRAS, segment.GetName())
      else: 
        ptindex = ToothTipPoints.GetControlPointIndexByLabel(segment.GetName())
        ToothTipPoints.SetNthControlPointPosition(ptindex,toothtipRAS)   
      if ToothPosPoints.GetControlPointIndexByLabel(segment.GetName()) == -1:
        ToothPosPoints.AddControlPoint(toothposRAS, segment.GetName())
      else:
        ptindex = ToothTipPoints.GetControlPointIndexByLabel(segment.GetName())
        ToothPosPoints.SetNthControlPointPosition(ptindex,toothposRAS)   
     
     
     ptindex = ToothTipPoints.GetControlPointIndexByLabel(segment.GetName())
     toothtipRAS = [0,]*3
     toothtipRAS = ToothTipPoints.GetNthControlPointPosition(ptindex)  
     ptindex = ToothPosPoints.GetControlPointIndexByLabel(segment.GetName())
     toothposRAS = [0,]*3   
     toothposRAS = ToothPosPoints.GetNthControlPointPosition(ptindex) 
 
     
     # measure distance between jaw joint and the base of the tooth
     ToothPoslineNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", segment.GetName())
     shNode.SetItemParent(shNode.GetItemByDataNode(ToothPoslineNode), posFolder)
     ToothPoslineNode.GetDisplayNode().SetPropertiesLabelVisibility(False)
     ToothPoslineNode.AddControlPoint(jointRAS)
     ToothPoslineNode.AddControlPoint(toothposRAS)
     ToothPos = ToothPoslineNode.GetMeasurement('length').GetValue()
     ToothPositionArray.InsertNextValue(ToothPos)
     slicer.mrmlScene.RemoveNode(ToothPoslineNode)

     # measure distance between jaw joint and tip of the tooth
     ToothTiplineNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", segment.GetName())
     shNode.SetItemParent(shNode.GetItemByDataNode(ToothTiplineNode), outFolder)
     ToothTiplineNode.GetDisplayNode().SetPropertiesLabelVisibility(False)
     ToothTiplineNode.AddControlPoint(jointRAS)
     ToothTiplineNode.AddControlPoint(toothtipRAS)
     OutLever = ToothTiplineNode.GetMeasurement('length').GetValue()
     slicer.mrmlScene.RemoveNode(ToothTiplineNode)
     
     # get relative tooth position
     RelPosArray.InsertNextValue(ToothPos/JawLength)
     
     # calculate tooth aspect ratio
     heightNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", segment.GetName())
     heightNode.GetDisplayNode().SetPropertiesLabelVisibility(False)
     heightNode.AddControlPoint(toothposRAS)
     heightNode.AddControlPoint(toothtipRAS)
     ToothHeight = heightNode.GetMeasurement('length').GetValue()
     slicer.mrmlScene.RemoveNode(heightNode)
     obb_diameter_mm = np.array(stats[segmentId,"LabelmapSegmentStatisticsPlugin.obb_diameter_mm"])
     ToothHeightArray.InsertNextValue(ToothHeight)
     if obb_diameter_mm[0] > obb_diameter_mm[1]:
       ToothWidthArray.InsertNextValue(obb_diameter_mm[0])
       AspectRatioArray.InsertNextValue(ToothHeight/obb_diameter_mm[0])
     if obb_diameter_mm[0] < obb_diameter_mm[1]:
       ToothWidthArray.InsertNextValue(obb_diameter_mm[1])
       AspectRatioArray.InsertNextValue(ToothHeight/obb_diameter_mm[1])

     
     # calculate mechanical advantage and F-Tooth
     ftooth_total = 0
     if muscle1 == True:
       MA1 = InLever1/OutLever
       ftooth_1 = force1 * math.sin(math.radians(angle1)) * MA1
       ftooth_total = ftooth_total + ftooth_1
       MechAdvArray1.InsertNextValue(MA1)
       FToothArray1.InsertNextValue(ftooth_1)
     if muscle2 == True:
       MA2 = InLever2/OutLever
       ftooth_2 = force2 * math.sin(math.radians(angle2)) * MA2
       ftooth_total = ftooth_total + ftooth_2
       MechAdvArray2.InsertNextValue(MA2)
       FToothArray2.InsertNextValue(ftooth_2)
     if muscle3 == True:
       MA3 = InLever3/OutLever
       ftooth_3 = force3 * math.sin(math.radians(angle3)) * MA3
       ftooth_total = ftooth_total + ftooth_3
       MechAdvArray3.InsertNextValue(MA3)
       FToothArray3.InsertNextValue(ftooth_3)

     FToothTotalArray.InsertNextValue(ftooth_total)
     
     # calculate tooth stress
     stress = ftooth_total/(Area * 1e-6)
     StressArray.InsertNextValue(stress)

    
    if species != "Enter specimen name" and species != "":
      tableNode.AddColumn(SpeciesArray)
      tableNode.SetColumnDescription(SpeciesArray.GetName(), "Specimen")

    tableNode.AddColumn(JawIDArray)
    tableNode.SetColumnDescription(JawIDArray.GetName(), "If upper or lower jaw")
   
    tableNode.AddColumn(SideArray)
    tableNode.SetColumnDescription(SideArray.GetName(), "Side of face that the jaw is on")  
        
    tableNode.AddColumn(JawLengthArray)
    tableNode.SetColumnDescription(JawLengthArray.GetName(), "Jaw Length")
    tableNode.SetColumnUnitLabel(JawLengthArray.GetName(), "mm")  # TODO: use length unit
    
    tableNode.AddColumn(SegmentNameArray)
    tableNode.SetColumnDescription(SegmentNameArray.GetName(), "Tooth segment name")
    
    tableNode.AddColumn(ToothPositionArray)
    tableNode.SetColumnDescription(ToothPositionArray.GetName(), "Distance between the base of the tooth and the jaw joint")
    tableNode.SetColumnUnitLabel(ToothPositionArray.GetName(), "mm")  # TODO: use length unit
    
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
    
    if muscle1 == True:
      if simulate == False:
        tableNode.AddColumn(FiberArray1)
        tableNode.SetColumnDescription(FiberArray1.GetName(), "Muscle 1 Fiber Length")
        tableNode.SetColumnUnitLabel(FiberArray1.GetName(), "mm")  # TODO: use length unit
    
        tableNode.AddColumn(VolumeArray1)
        tableNode.SetColumnDescription(VolumeArray1.GetName(), "Muscle 1 Volume")
        tableNode.SetColumnUnitLabel(VolumeArray1.GetName(), "mm^1")  # TODO: use length unit
      
      tableNode.AddColumn(InputAngleArray1)
      tableNode.SetColumnDescription(InputAngleArray1.GetName(), "Muscle 1 Insertion Angle")
      tableNode.SetColumnUnitLabel(InputAngleArray1.GetName(), "deg")  # TODO: use length unit
         
      tableNode.AddColumn(InputForceArray1)
      tableNode.SetColumnDescription(InputForceArray1.GetName(), "Muscle 1 Input Force")
      tableNode.SetColumnUnitLabel(InputForceArray1.GetName(), "N")  # TODO: use length unit
    
      tableNode.AddColumn(MechAdvArray1)
      tableNode.SetColumnDescription(MechAdvArray1.GetName(), "Muscle 1 Mechanical Advantage")

      tableNode.AddColumn(FToothArray1)
      tableNode.SetColumnDescription(FToothArray1.GetName(), "The muscle 1 force acting on a tooth (input force * insert angle * mechanical advantage)")
      tableNode.SetColumnUnitLabel(FToothArray1.GetName(), "N")  # TODO: use length unit

    if muscle2 == True:
      if simulate == False:
        tableNode.AddColumn(FiberArray2)
        tableNode.SetColumnDescription(FiberArray2.GetName(), "Muscle 2 Fiber Length")
        tableNode.SetColumnUnitLabel(FiberArray2.GetName(), "mm")  # TODO: use length unit
    
        tableNode.AddColumn(VolumeArray2)
        tableNode.SetColumnDescription(VolumeArray2.GetName(), "Muscle 2 Volume")
        tableNode.SetColumnUnitLabel(VolumeArray2.GetName(), "mm^2")  # TODO: use length unit
      
      tableNode.AddColumn(InputAngleArray2)
      tableNode.SetColumnDescription(InputAngleArray2.GetName(), "Muscle 2 Insertion Angle")
      tableNode.SetColumnUnitLabel(InputAngleArray2.GetName(), "deg")  # TODO: use length unit
         
      tableNode.AddColumn(InputForceArray2)
      tableNode.SetColumnDescription(InputForceArray2.GetName(), "Muscle 2 Input Force")
      tableNode.SetColumnUnitLabel(InputForceArray2.GetName(), "N")  # TODO: use length unit
    
      tableNode.AddColumn(MechAdvArray2)
      tableNode.SetColumnDescription(MechAdvArray2.GetName(), "Muscle 2 Mechanical Advantage")

      tableNode.AddColumn(FToothArray2)
      tableNode.SetColumnDescription(FToothArray2.GetName(), "The muscle 2 force acting on a tooth (input force * insert angle * mechanical advantage)")
      tableNode.SetColumnUnitLabel(FToothArray2.GetName(), "N")  # TODO: use length unit

    if muscle3 == True:
      if simulate == False:
        tableNode.AddColumn(FiberArray3)
        tableNode.SetColumnDescription(FiberArray3.GetName(), "Muscle 3 Fiber Length")
        tableNode.SetColumnUnitLabel(FiberArray3.GetName(), "mm")  # TODO: use length unit
    
        tableNode.AddColumn(VolumeArray3)
        tableNode.SetColumnDescription(VolumeArray3.GetName(), "Muscle 3 Volume")
        tableNode.SetColumnUnitLabel(VolumeArray3.GetName(), "mm^3")  # TODO: use length unit
      
      tableNode.AddColumn(InputAngleArray3)
      tableNode.SetColumnDescription(InputAngleArray3.GetName(), "Muscle 3 Insertion Angle")
      tableNode.SetColumnUnitLabel(InputAngleArray3.GetName(), "deg")  # TODO: use length unit
         
      tableNode.AddColumn(InputForceArray3)
      tableNode.SetColumnDescription(InputForceArray3.GetName(), "Muscle 3 Input Force")
      tableNode.SetColumnUnitLabel(InputForceArray3.GetName(), "N")  # TODO: use length unit
    
      tableNode.AddColumn(MechAdvArray3)
      tableNode.SetColumnDescription(MechAdvArray3.GetName(), "Muscle 3 Mechanical Advantage")

      tableNode.AddColumn(FToothArray3)
      tableNode.SetColumnDescription(FToothArray3.GetName(), "The muscle 3 force acting on a tooth (input force * insert angle * mechanical advantage)")
      tableNode.SetColumnUnitLabel(FToothArray3.GetName(), "N")  # TODO: use length unit

    muscles = np.array([muscle1,muscle2,muscle3])
    if len(muscles[muscles == True]) > 1:
      tableNode.AddColumn(FToothTotalArray)
      tableNode.SetColumnDescription(FToothTotalArray.GetName(), "The total closing force acting on a tooth (input force * insert angle * mechanical advantage)")
      tableNode.SetColumnUnitLabel(FToothTotalArray.GetName(), "N")  # TODO: use length unit

    tableNode.AddColumn(StressArray)
    tableNode.SetColumnDescription(StressArray.GetName(), "Tooth stress (tooth force / surface area)")

    shNode.RemoveItem(exportFolderItemId)
    shNode.RemoveItem(boxFolderItemId)
    slicer.mrmlScene.RemoveNode(lengthLine)
    
    for i in range(visibleSegmentIds.GetNumberOfValues()):
      visibleSegmentID = visibleSegmentIds.GetValue(i)
      segmentationNode.GetDisplayNode().SetSegmentVisibility(visibleSegmentID,True)
    for segment in segmentList:
      segmentationNode.GetDisplayNode().SetSegmentVisibility(segment,True)

    logging.info('Processing completed')
    end = time.time()
    TotalTime = np.round(end - start,2)
    print("Total time elapsed:", TotalTime, "seconds")

    # use custom layout
    customLayoutId=166
    layoutManager = slicer.app.layoutManager()

    # Change layout to include plot and table      
    slicer.app.layoutManager().setLayout(customLayoutId)
    slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID(tableNode.GetID())
    slicer.app.applicationLogic().PropagateTableSelection()
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