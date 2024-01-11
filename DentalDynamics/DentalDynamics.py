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
    self.ui.SimpleMarkupsWidget.connect("markupsNodeChanged()", self.updateParameterNodeFromGUI)
    self.ui.SimpleMarkupsWidget.connect("markupsNodeChanged()", self.onMarkupNodeChanged)
    self.ui.MusclecheckBox1.connect("stateChanged(int)", self.updateParameterNodeFromGUI)
    self.ui.ForceInputBox1.connect("valueChanged(double)", self.updateParameterNodeFromGUI)
    self.ui.AngleInputBox1.connect("valueChanged(double)", self.updateParameterNodeFromGUI)
    self.ui.MusclecheckBox2.connect("stateChanged(int)", self.updateParameterNodeFromGUI)
    self.ui.ForceInputBox2.connect("valueChanged(double)", self.updateParameterNodeFromGUI)
    self.ui.AngleInputBox2.connect("valueChanged(double)", self.updateParameterNodeFromGUI)
    self.ui.MusclecheckBox3.connect("stateChanged(int)", self.updateParameterNodeFromGUI)
    self.ui.ForceInputBox3.connect("valueChanged(double)", self.updateParameterNodeFromGUI)
    self.ui.AngleInputBox3.connect("valueChanged(double)", self.updateParameterNodeFromGUI)
    self.ui.tableSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    #self.ui.OutVisButton.connect('clicked(bool)', self.updateParameterNodeFromGUI)
    #self.ui.PosVisButton.connect('clicked(bool)', self.updateParameterNodeFromGUI)
    self.ui.FlipSegmentSelectorWidget.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)

    # Buttons
    self.ui.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.ui.ResetpushButton.connect('clicked(bool)', self.onResetButton)
    self.ui.TemplatepushButton.connect('clicked(bool)', self.onTemplate)
    self.ui.FlipButton.connect('clicked(bool)', self.onFlipResults)
    self.ui.FlipSomeButton.connect('clicked(bool)', self.onFlipSomeResults)
    self.ui.OutVisButton.connect('clicked(bool)', self.onOutleverVis)
    self.ui.PosVisButton.connect('clicked(bool)', self.onPositionVis)


    # Make sure parameter node is initialized (needed for module reload)
    self.initializeParameterNode()
    
    if self._parameterNode.GetParameter("OutLevers") == "True":
      self.onOutleverVis()
    if self._parameterNode.GetParameter("ToothPos") == "True":
      self.onPositionVis()
    if not self._parameterNode.GetNodeReference("JawPoints"):  
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
      jawPoints = slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Jaw Points")
      if jawPoints:
        self._parameterNode.SetNodeReferenceID("JawPoints", jawPoints.GetID())  
      
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
    self.ui.SimpleMarkupsWidget.setCurrentNode(self._parameterNode.GetNodeReference("JawPoints"))
    self.ui.MusclecheckBox1.checked = (self._parameterNode.GetParameter("Muscle") == "True")
    self.ui.ForceInputBox1.value = float(self._parameterNode.GetParameter("Force"))
    self.ui.AngleInputBox1.value = float(self._parameterNode.GetParameter("Angle"))
    self.ui.MusclecheckBox2.checked = (self._parameterNode.GetParameter("Muscle2") == "True")
    self.ui.ForceInputBox2.value = float(self._parameterNode.GetParameter("Force2"))
    self.ui.AngleInputBox2.value = float(self._parameterNode.GetParameter("Angle2"))  
    self.ui.MusclecheckBox3.checked = (self._parameterNode.GetParameter("Muscle3") == "True")
    self.ui.ForceInputBox3.value = float(self._parameterNode.GetParameter("Force3"))
    self.ui.AngleInputBox3.value = float(self._parameterNode.GetParameter("Angle3"))    
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
      if self.ui.SimpleMarkupsWidget.currentNode().GetNthControlPointPosition(2) != (0, 0, 0):
        self.ui.MusclecheckBox1.enabled = True
      else: 
        self.ui.MusclecheckBox1.enabled = False
      if self.ui.SimpleMarkupsWidget.currentNode().GetNthControlPointPosition(3) != (0, 0, 0):
        self.ui.MusclecheckBox2.enabled = True
      else: 
        self.ui.MusclecheckBox2.enabled = False    
      if self.ui.SimpleMarkupsWidget.currentNode().GetNthControlPointPosition(4) != (0, 0, 0):
        self.ui.MusclecheckBox3.enabled = True
      else: 
        self.ui.MusclecheckBox3.enabled = False  
    else:
      self.ui.MusclecheckBox1.enabled = False
      self.ui.MusclecheckBox2.enabled = False 
      self.ui.MusclecheckBox3.enabled = False 
    
    if self._parameterNode.GetParameter("Muscle") == "True" and self.ui.MusclecheckBox1.enabled == True:
      self.ui.ForceInputBox1.enabled = True
      self.ui.AngleInputBox1.enabled = True
    else:
      self.ui.ForceInputBox1.enabled = False
      self.ui.AngleInputBox1.enabled = False       
        
    if self._parameterNode.GetParameter("Muscle2") == "True" and self.ui.MusclecheckBox2.enabled == True:
      self.ui.ForceInputBox2.enabled = True
      self.ui.AngleInputBox2.enabled = True
    else:
      self.ui.ForceInputBox2.enabled = False
      self.ui.AngleInputBox2.enabled = False

    if self._parameterNode.GetParameter("Muscle3") == "True" and self.ui.MusclecheckBox3.enabled == True:
      self.ui.ForceInputBox3.enabled = True
      self.ui.AngleInputBox3.enabled = True
    else:
      self.ui.ForceInputBox3.enabled = False
      self.ui.AngleInputBox3.enabled = False
      
            
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
    if self.ui.SimpleMarkupsWidget.currentNode() != None: 
      self._parameterNode.SetNodeReferenceID("JawPoints", self.ui.SimpleMarkupsWidget.currentNode().GetID())
    else: 
      self._parameterNode.SetNodeReferenceID("JawPoints", None)
    self._parameterNode.SetParameter("Muscle", str(self.ui.MusclecheckBox1.checked))      
    self._parameterNode.SetParameter("Force", str(self.ui.ForceInputBox1.value))
    self._parameterNode.SetParameter("Angle", str(self.ui.AngleInputBox1.value))
    self._parameterNode.SetParameter("Muscle2", str(self.ui.MusclecheckBox2.checked))      
    self._parameterNode.SetParameter("Force2", str(self.ui.ForceInputBox2.value))
    self._parameterNode.SetParameter("Angle2", str(self.ui.AngleInputBox2.value))  
    self._parameterNode.SetParameter("Muscle3", str(self.ui.MusclecheckBox3.checked))      
    self._parameterNode.SetParameter("Force3", str(self.ui.ForceInputBox3.value))
    self._parameterNode.SetParameter("Angle3", str(self.ui.AngleInputBox3.value))    
    self._parameterNode.SetParameter("FlipSegments", str(self.ui.FlipSegmentSelectorWidget.selectedSegmentIDs()))
    self._parameterNode.SetNodeReferenceID("ResultsTable", self.ui.tableSelector.currentNodeID)

    self._parameterNode.EndModify(wasModified)

  def updateSelectedSegments(self):
    """
    Automatically select all segments when changing the segmentation node
    """
    Allsegments = self.ui.SegmentSelectorWidget.segmentIDs()
    self.ui.SegmentSelectorWidget.setSelectedSegmentIDs(Allsegments)
    
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
    pointListNode.AddControlPoint([0,0,0],"Closing Muscle 2 Insertion")
    pointListNode.AddControlPoint([0,0,0],"Closing Muscle 3 Insertion")
    pointListNode.UnsetNthControlPointPosition(0)
    pointListNode.UnsetNthControlPointPosition(1)
    pointListNode.UnsetNthControlPointPosition(2)
    pointListNode.UnsetNthControlPointPosition(3)  
    pointListNode.UnsetNthControlPointPosition(4)      
    pointListNode.GetDisplayNode().SetPropertiesLabelVisibility(True)
    pointListNode.GetDisplayNode().SetTextScale(3)
    self.ui.SimpleMarkupsWidget.setCurrentNode(pointListNode)
    self.ui.ActionFixedNumberOfControlPoints.trigger()
  
  def onMarkupNodeChanged(self):
    """
    Run processing when user changes the point list.
    """    
    pointListNode = self.ui.SimpleMarkupsWidget.currentNode()
    def watchTemplate(unusedArg1 = None, unusedArg2 = None):
      self.updateGUIFromParameterNode()
    if pointListNode is not None:
      TemplateObserver = pointListNode.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent, watchTemplate)
      pointListNode.RemoveObserver(TemplateObserver)
    if pointListNode is not None:  
      TemplateObserver = pointListNode.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent, watchTemplate)

  def onOutleverVis(self):
    """
    Run processing when user clicks "Outlever Vis" button.
    """  
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    outFolder = shNode.GetItemByName("Out Levers")
    pluginHandler = slicer.qSlicerSubjectHierarchyPluginHandler().instance()
    folderPlugin = pluginHandler.pluginByName("Folder")
    
    def outjointMarkupChanged(unusedArg1=None, unusedArg2=None):
      #if slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Jaw Points") != None:
      if self.ui.SimpleMarkupsWidget.currentNode() != None:
        #JawPoints = slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Jaw Points")
        JawPoints = self.ui.SimpleMarkupsWidget.currentNode()
        jointRAS = [0,]*3
        JawPoints.GetNthControlPointPosition(0,jointRAS)
        children = vtk.vtkIdList()
        shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
        outFolder = shNode.GetItemByName("Out Levers")
        pluginHandler = slicer.qSlicerSubjectHierarchyPluginHandler().instance()
        folderPlugin = pluginHandler.pluginByName("Folder")        
        if outFolder > 0:
          shNode.GetItemChildren(outFolder, children)
          if children.GetNumberOfIds() > 0:
            lineNames = [shNode.GetItemDataNode(children.GetId(0)).GetName()]
            for i in range(1,children.GetNumberOfIds()):
              lineNames.append(shNode.GetItemDataNode(children.GetId(i)).GetName())
            for i in lineNames:
              ToothOutlineNode = slicer.mrmlScene.GetFirstNodeByName(i)
              ToothOutlineNode.SetNthControlPointPosition(0, jointRAS)     

    def outtoothMarkupChanged(unusedArg1=None, unusedArg2=None):
      if slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Out Lever Points") != None:
        ToothOutPoints = slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Out Lever Points")
        children = vtk.vtkIdList()
        shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
        outFolder = shNode.GetItemByName("Out Levers")
        pluginHandler = slicer.qSlicerSubjectHierarchyPluginHandler().instance()
        folderPlugin = pluginHandler.pluginByName("Folder")        
        if outFolder > 0:
          shNode.GetItemChildren(outFolder, children)
          if children.GetNumberOfIds() > 0:
            lineNames = [shNode.GetItemDataNode(children.GetId(0)).GetName()]
            for i in range(1,children.GetNumberOfIds()):
              lineNames.append(shNode.GetItemDataNode(children.GetId(i)).GetName())
            lineNames = [sub.replace(' Out Lever', '') for sub in lineNames]
            for i in lineNames:
              ToothOutlineNode = slicer.mrmlScene.GetFirstNodeByName(i + " Out Lever")
              toothoutRAS = [0,]*3
              ptindex = ToothOutPoints.GetControlPointIndexByLabel(i)
              ToothOutPoints.GetNthControlPointPosition(ptindex,toothoutRAS)
              ToothOutlineNode.SetNthControlPointPosition(1, toothoutRAS)     

        
    if slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Out Lever Points") != None:
      ToothOutPoints = slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Out Lever Points")
      #if slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Jaw Points") != None:
      if self.ui.SimpleMarkupsWidget.currentNode() != None:
        #JawPoints = slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Jaw Points")
        JawPoints = self.ui.SimpleMarkupsWidget.currentNode()
        jointRAS = [0,]*3
        JawPoints.GetNthControlPointPosition(0,jointRAS)
        posjointMarkupsNodeObserver = JawPoints.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent, outjointMarkupChanged)
      outtoothMarkupsNodeObserver = ToothOutPoints.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent, outtoothMarkupChanged)
      for i in range(ToothOutPoints.GetNumberOfControlPoints()):
        toothoutRAS = [0,]*3
        ToothOutPoints.GetNthControlPointPosition(i,toothoutRAS)
        segname = ToothOutPoints.GetNthControlPointLabel(i)
        if slicer.mrmlScene.GetFirstNodeByName(segname + " Out Lever") == None:
          ToothOutlineNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", segname + " Out Lever")
          ToothOutlineNode.GetDisplayNode().SetPropertiesLabelVisibility(False)
          ToothOutlineNode.SetSaveWithScene(0)
          ToothOutlineNode.AddControlPoint(jointRAS)
          ToothOutlineNode.AddControlPoint(toothoutRAS)
          ToothOutlineNode.SetNthControlPointLocked(0,1)
          ToothOutlineNode.SetNthControlPointLocked(1,1)
          ToothOutlineNode.GetDisplayNode().SetGlyphType(7)
          ToothOutlineNode.SetLocked(1)
          shNode.SetItemParent(shNode.GetItemByDataNode(ToothOutlineNode), outFolder)
        else: 
          ToothOutlineNode = slicer.mrmlScene.GetFirstNodeByName(segname + " Out Lever")
          if ToothOutlineNode.GetDisplayNode().GetVisibility() == 1:
            ToothOutlineNode.GetDisplayNode().SetVisibility(0)
          else:
            ToothOutlineNode.GetDisplayNode().SetVisibility(1)
      toothoutRAS = [0,]*3
      ToothOutPoints.GetNthControlPointPosition(0,toothoutRAS)
      segname = ToothOutPoints.GetNthControlPointLabel(0)
      ToothOutlineNode = slicer.mrmlScene.GetFirstNodeByName(segname + " Out Lever")
      if ToothOutlineNode.GetDisplayNode().GetVisibility() == 1:
        self._parameterNode.SetParameter("OutLevers","True")
      else:
        self._parameterNode.SetParameter("OutLevers","False")

  def onPositionVis(self):
    """
    Run processing when user clicks "Outlever Vis" button.
    """
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    posFolder = shNode.GetItemByName("Tooth Positions")
    pluginHandler = slicer.qSlicerSubjectHierarchyPluginHandler().instance()
    folderPlugin = pluginHandler.pluginByName("Folder")
    
    def posjointMarkupChanged(unusedArg1=None, unusedArg2=None):
      #if slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Jaw Points") != None:
      if self.ui.SimpleMarkupsWidget.currentNode() != None:
        #JawPoints = slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Jaw Points")
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
      if slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Position Points") != None:
        ToothPosPoints = slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Position Points")
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
            lineNames = [sub.replace(' Position', '') for sub in lineNames]
            for i in lineNames:
              ToothPoslineNode = slicer.mrmlScene.GetFirstNodeByName(i + " Position")
              toothposRAS = [0,]*3
              ptindex = ToothPosPoints.GetControlPointIndexByLabel(i)
              ToothPosPoints.GetNthControlPointPosition(ptindex,toothposRAS)
              ToothPoslineNode.SetNthControlPointPosition(1, toothposRAS)     

        
    if slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Position Points") != None:
      ToothPosPoints = slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Position Points")
      #if slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Jaw Points") != None:
      if self.ui.SimpleMarkupsWidget.currentNode() != None:
        #JawPoints = slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Jaw Points")
        JawPoints = self.ui.SimpleMarkupsWidget.currentNode()
        jointRAS = [0,]*3
        JawPoints.GetNthControlPointPosition(0,jointRAS)
        posjointMarkupsNodeObserver = JawPoints.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent, posjointMarkupChanged)
      postoothMarkupsNodeObserver = ToothPosPoints.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent, postoothMarkupChanged)
      for i in range(ToothPosPoints.GetNumberOfControlPoints()):
        toothposRAS = [0,]*3
        ToothPosPoints.GetNthControlPointPosition(i,toothposRAS)
        segname = ToothPosPoints.GetNthControlPointLabel(i)
        if slicer.mrmlScene.GetFirstNodeByName(segname + " Position") == None:
          ToothPoslineNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", segname + " Position")
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
          ToothPoslineNode = slicer.mrmlScene.GetFirstNodeByName(segname + " Position")
          if ToothPoslineNode.GetDisplayNode().GetVisibility() == 1:
            ToothPoslineNode.GetDisplayNode().SetVisibility(0)
          else:
            ToothPoslineNode.GetDisplayNode().SetVisibility(1)
      toothposRAS = [0,]*3
      ToothPosPoints.GetNthControlPointPosition(0,toothposRAS)
      segname = ToothPosPoints.GetNthControlPointLabel(0)
      ToothPoslineNode = slicer.mrmlScene.GetFirstNodeByName(segname + " Position")
      if ToothPoslineNode.GetDisplayNode().GetVisibility() == 1:
        self._parameterNode.SetParameter("ToothPos","True")
      else:
        self._parameterNode.SetParameter("ToothPos","False")


  def onFlipResults(self):
    """
    Run processing when user clicks "Flip" button.
    """
    if slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Position Points") != None and slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Out Lever Points") != None:
      ToothPosPoints = slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Position Points")
      ToothOutPoints = slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Out Lever Points")
      for i in range(ToothPosPoints.GetNumberOfControlPoints()):
        posPos =  [0,]*3
        ToothPosPoints.GetNthControlPointPosition(i,posPos)
        outPos =  [0,]*3
        ToothOutPoints.GetNthControlPointPosition(i, outPos)
        
        ToothPosPoints.SetNthControlPointPosition(i, outPos)
        ToothOutPoints.SetNthControlPointPosition(i, posPos)

  def onFlipSomeResults(self):
    """
    Run processing when user clicks "Flip" button.
    """
    if self.ui.FlipSegmentSelectorWidget.currentNode() != None:
      segmentationNode = self.ui.SegmentSelectorWidget.currentNode()
      segmentList = self.ui.FlipSegmentSelectorWidget.selectedSegmentIDs()
      if len(segmentList) > 0:
        segmentNames = [segmentationNode.GetSegmentation().GetSegment(segmentList[0]).GetName()]
        for i in range(1,len(segmentList)):
          segmentNames.append(segmentationNode.GetSegmentation().GetSegment(segmentList[i]).GetName())
        if slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Position Points") != None and slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Out Lever Points") != None:
          ToothPosPoints = slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Position Points")
          ToothOutPoints = slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Out Lever Points")
      
        for i in segmentNames:
          ptindex = ToothPosPoints.GetControlPointIndexByLabel(i)
          if ptindex > -1:
            posPos =  [0,]*3
            ToothPosPoints.GetNthControlPointPosition(ptindex,posPos)
            outPos =  [0,]*3
            ToothOutPoints.GetNthControlPointPosition(ptindex, outPos)
        
            ToothPosPoints.SetNthControlPointPosition(ptindex, outPos)
            ToothOutPoints.SetNthControlPointPosition(ptindex, posPos)

    
  def onResetButton(self):
    """
    Run processing when user clicks "Reset" button.
    """
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    shFolderItemId = shNode.GetItemByName("Dental Dynamics Misc")
    if shFolderItemId != 0:
      shNode.RemoveItem(shFolderItemId)
    slicer.mrmlScene.RemoveNode(self.ui.tableSelector.currentNode())

    outFolder = shNode.GetItemByName("Out Levers")
    pluginHandler = slicer.qSlicerSubjectHierarchyPluginHandler().instance()
    folderPlugin = pluginHandler.pluginByName("Folder")
    
    def outjointMarkupChanged(unusedArg1=None, unusedArg2=None):
      if slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Jaw Points") != None:
      #if self.ui.SimpleMarkupsWidget.currentNode() != None:
        JawPoints = slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Jaw Points")
        jointRAS = [0,]*3
        JawPoints.GetNthControlPointPosition(0,jointRAS)
        children = vtk.vtkIdList()
        shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
        outFolder = shNode.GetItemByName("Out Levers")
        pluginHandler = slicer.qSlicerSubjectHierarchyPluginHandler().instance()
        folderPlugin = pluginHandler.pluginByName("Folder")        
        if outFolder > 0:
          shNode.GetItemChildren(outFolder, children)
          if children.GetNumberOfIds() > 0:
            lineNames = [shNode.GetItemDataNode(children.GetId(0)).GetName()]
            for i in range(1,children.GetNumberOfIds()):
              lineNames.append(shNode.GetItemDataNode(children.GetId(i)).GetName())
            for i in lineNames:
              ToothOutlineNode = slicer.mrmlScene.GetFirstNodeByName(i)
              ToothOutlineNode.SetNthControlPointPosition(0, jointRAS)           
    
    def outtoothMarkupChanged(unusedArg1=None, unusedArg2=None):
      if slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Out Lever Points") != None:
        ToothOutPoints = slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Out Lever Points")
        children = vtk.vtkIdList()
        shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
        outFolder = shNode.GetItemByName("Out Levers")
        pluginHandler = slicer.qSlicerSubjectHierarchyPluginHandler().instance()
        folderPlugin = pluginHandler.pluginByName("Folder")        
        if outFolder > 0:
          shNode.GetItemChildren(outFolder, children)
          if children.GetNumberOfIds() > 0:
            lineNames = [shNode.GetItemDataNode(children.GetId(0)).GetName()]
            for i in range(1,children.GetNumberOfIds()):
              lineNames.append(shNode.GetItemDataNode(children.GetId(i)).GetName())
            lineNames = [sub.replace(' Out Lever', '') for sub in lineNames]
            for i in lineNames:
              ToothOutlineNode = slicer.mrmlScene.GetFirstNodeByName(i + " Out Lever")
              toothoutRAS = [0,]*3
              ptindex = ToothOutPoints.GetControlPointIndexByLabel(i)
              ToothOutPoints.GetNthControlPointPosition(ptindex,toothoutRAS)
              ToothOutlineNode.SetNthControlPointPosition(1, toothoutRAS)     
 
    def posjointMarkupChanged(unusedArg1=None, unusedArg2=None):
      if slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Jaw Points") != None:
      #if self.ui.SimpleMarkupsWidget.currentNode() != None:
        JawPoints = slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Jaw Points")
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
      if slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Position Points") != None:
        ToothPosPoints = slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Position Points")
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
            lineNames = [sub.replace(' Position', '') for sub in lineNames]
            for i in lineNames:
              ToothPoslineNode = slicer.mrmlScene.GetFirstNodeByName(i + " Position")
              toothposRAS = [0,]*3
              ptindex = ToothPosPoints.GetControlPointIndexByLabel(i)
              ToothPosPoints.GetNthControlPointPosition(ptindex,toothposRAS)
              ToothPoslineNode.SetNthControlPointPosition(1, toothposRAS)  

    if slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Jaw Points") != None:
      JawPoints = slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Jaw Points")
      outjointMarkupsNodeObserver = JawPoints.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent, outjointMarkupChanged)
      JawPoints.RemoveObserver(outjointMarkupsNodeObserver)
      posjointMarkupsNodeObserver = JawPoints.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent, posjointMarkupChanged)
      JawPoints.RemoveObserver(posjointMarkupsNodeObserver)

    if slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Out Lever Points") != None:
      ToothOutPoints = slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Out Lever Points")
      outtoothMarkupsNodeObserver = ToothOutPoints.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent, outtoothMarkupChanged)
      ToothOutPoints.RemoveObserver(outtoothMarkupsNodeObserver)
    if slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Position Points") != None:
      ToothPosPoints = slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Position Points")      
      postoothMarkupsNodeObserver = ToothPosPoints.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent, postoothMarkupChanged)
      ToothPosPoints.RemoveObserver(postoothMarkupsNodeObserver)
    
    
    self._parameterNode.SetParameter("OutLevers", "False")
    self._parameterNode.SetParameter("ToothPos", "False")

    
    layoutManager = slicer.app.layoutManager()
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
      self.ui.SegmentSelectorWidget.currentNode(), self.ui.SegmentSelectorWidget.selectedSegmentIDs(), 
      self.ui.SimpleMarkupsWidget.currentNode(), 
      self.ui.MusclecheckBox1.checked, self.ui.ForceInputBox1.value, self.ui.AngleInputBox1.value, 
      self.ui.MusclecheckBox2.checked, self.ui.ForceInputBox2.value, self.ui.AngleInputBox2.value, 
      self.ui.MusclecheckBox3.checked, self.ui.ForceInputBox3.value, self.ui.AngleInputBox3.value,       
      tableNode)
            
      if len(self.ui.FlipSegmentSelectorWidget.selectedSegmentIDs()) != 0:
        self.ui.FlipSegmentSelectorWidget.multiSelection = False
        self.ui.FlipSegmentSelectorWidget.multiSelection = True
        
      if self._parameterNode.GetParameter("OutLevers") == "False":
        self.onOutleverVis()
         
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
      parameterNode.SetParameter("SpeciesName", "Enter species name")    
    if not parameterNode.GetParameter("Segments"):
      parameterNode.SetParameter("Segments", "()")   
    if not parameterNode.GetParameter("Muscle"):
     parameterNode.SetParameter("Muscle", "True")    
    if not parameterNode.GetParameter("Force"):
     parameterNode.SetParameter("Force", "1.0")
    if not parameterNode.GetParameter("Angle"):
     parameterNode.SetParameter("Angle", "90.0")
    if not parameterNode.GetParameter("Muscle2"):
     parameterNode.SetParameter("Muscle2", "False")    
    if not parameterNode.GetParameter("Force2"):
     parameterNode.SetParameter("Force2", "1.0")
    if not parameterNode.GetParameter("Angle2"):
     parameterNode.SetParameter("Angle2", "90.0")
    if not parameterNode.GetParameter("Muscle3"):
     parameterNode.SetParameter("Muscle3", "False")     
    if not parameterNode.GetParameter("Force3"):
     parameterNode.SetParameter("Force3", "1.0")
    if not parameterNode.GetParameter("Angle3"):
     parameterNode.SetParameter("Angle3", "90.0")
    if not parameterNode.GetParameter("FlipSegments"):
      parameterNode.SetParameter("FlipSegments", "()") 
    if not parameterNode.GetParameter("OutLevers"):
      parameterNode.SetParameter("OutLevers", "False")
    if not parameterNode.GetParameter("ToothPos"):
      parameterNode.SetParameter("ToothPos", "False")

            
  def run(self, species, LowerradioButton, UpperradioButton, LeftradioButton, RightradioButton,
  segmentationNode, segmentList, pointNode, MusclecheckBox1, force1, angle1, MusclecheckBox2, force2, angle2, MusclecheckBox3, force3, angle3, tableNode):
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
    if species == "Enter species name" or species == "": 
      species = "NA" 
    jawID = "NA"
    if LowerradioButton == True:
      jawID = "Lower Jaw"
    if UpperradioButton == True:
      jawID = "Upper Jaw"
    side = "NA"
    if LeftradioButton == True:
      side = "Left"
    if RightradioButton == True:
      side = "Right"
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    newFolder = shNode.GetItemByName("Dental Dynamics Misc")
    outFolder = shNode.GetItemByName("Out Levers")
    posFolder = shNode.GetItemByName("Tooth Positions")
    if slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Out Lever Points") == None:
      ToothOutPoints = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode", "Dental Dynamics Out Lever Points")
    else:
      ToothOutPoints = slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Out Lever Points") 
    if slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Position Points") == None:
      ToothPosPoints = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode", "Dental Dynamics Position Points")
      ToothPosPoints.GetDisplayNode().SetSelectedColor((0, 0.72, 0.92))
      ToothPosPoints.GetDisplayNode().SetActiveColor((1, 0.65, 0.0))
      ToothPosPoints.GetDisplayNode().SetPointLabelsVisibility(False)
    else:
      ToothPosPoints = slicer.mrmlScene.GetFirstNodeByName("Dental Dynamics Position Points") 
    if newFolder == 0:
      newFolder = shNode.CreateFolderItem(shNode.GetSceneItemID(), "Dental Dynamics Misc")      
      outFolder = shNode.CreateFolderItem(shNode.GetSceneItemID(), "Out Levers")      
      posFolder = shNode.CreateFolderItem(shNode.GetSceneItemID(), "Tooth Positions")
      pluginHandler = slicer.qSlicerSubjectHierarchyPluginHandler().instance()
      folderPlugin = pluginHandler.pluginByName("Folder")
      shNode.SetItemParent(shNode.GetItemByDataNode(ToothOutPoints), newFolder)
      shNode.SetItemParent(shNode.GetItemByDataNode(ToothPosPoints), newFolder)
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
    slicer.mrmlScene.RemoveNode(lengthLine)
    
    # measure in-lever
    if MusclecheckBox1 == False and MusclecheckBox2 == False and MusclecheckBox3 == False:
      raise ValueError("No input muscles selected")
    if MusclecheckBox1 == True:
      inleverRAS = [0,]*3
      pointNode.GetNthControlPointPosition(2,inleverRAS)
      if inleverRAS == [0, 0, 0]:
        raise ValueError("Muscle 1 Insertion not defined")
      leverLine = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", "InLever1")
      leverLine.GetDisplayNode().SetPropertiesLabelVisibility(False)
      leverLine.AddControlPoint(jointRAS)
      leverLine.AddControlPoint(inleverRAS)
      InLever1 = leverLine.GetMeasurement('length').GetValue()
      slicer.mrmlScene.RemoveNode(leverLine)

    if MusclecheckBox2 == True:
      inleverRAS = [0,]*3
      pointNode.GetNthControlPointPosition(3,inleverRAS)
      if inleverRAS == [0, 0, 0]:
        raise ValueError("Muscle 2 Insertion not defined")
      leverLine = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", "InLever2")
      leverLine.GetDisplayNode().SetPropertiesLabelVisibility(False)
      leverLine.AddControlPoint(jointRAS)
      leverLine.AddControlPoint(inleverRAS)
      InLever2 = leverLine.GetMeasurement('length').GetValue()
      slicer.mrmlScene.RemoveNode(leverLine) 
      
    if MusclecheckBox3 == True:
      inleverRAS = [0,]*3
      pointNode.GetNthControlPointPosition(4,inleverRAS)
      if inleverRAS == [0, 0, 0]:
        raise ValueError("Muscle 3 Insertion not defined")
      leverLine = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", "InLever3")
      leverLine.GetDisplayNode().SetPropertiesLabelVisibility(False)
      leverLine.AddControlPoint(jointRAS)
      leverLine.AddControlPoint(inleverRAS)
      InLever3 = leverLine.GetMeasurement('length').GetValue()
      slicer.mrmlScene.RemoveNode(leverLine) 
      
      
    # remove any control points that should no longer be included
    segmentNames = [segmentationNode.GetSegmentation().GetSegment(segmentList[0]).GetName()]
    for i in range(1,len(segmentList)):
      segmentNames.append(segmentationNode.GetSegmentation().GetSegment(segmentList[i]).GetName())
    pointlabels =  vtk.vtkStringArray()
    ToothOutPoints.GetControlPointLabels(pointlabels)
    if pointlabels.GetNumberOfValues() > 0:
      labelNames = [pointlabels.GetValue(0)]
      for i in range(1,pointlabels.GetSize()):
        labelNames.append(pointlabels.GetValue(i))
      extralabels = set(labelNames) - set(segmentNames)
      extralabels = list(extralabels)
      for i in extralabels:
        pointindex = ToothOutPoints.GetControlPointIndexByLabel(i)
        ToothOutPoints.RemoveNthControlPoint(pointindex)   
        ToothPosPoints.RemoveNthControlPoint(pointindex)
        
    # remove any lines that should no longer exist
    pointlabels =  vtk.vtkStringArray()
    ToothOutPoints.GetControlPointLabels(pointlabels)
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
        lineNames = [sub.replace(' Out Lever', '') for sub in lineNames]
        extralines = set(lineNames) - set(labelNames)
        extralines = list(extralines)
        for i in extralines:
          extraline = slicer.mrmlScene.GetFirstNodeByName(i + " Out Lever")
          slicer.mrmlScene.RemoveNode(extraline)       
          extraline = slicer.mrmlScene.GetFirstNodeByName(i + " Position")
          slicer.mrmlScene.RemoveNode(extraline)       
      
    #segmentList = stats["SegmentIDs"]
    for segmentId in segmentList:
     
     SpeciesArray.InsertNextValue(species)  
     JawIDArray.InsertNextValue(jawID)
     SideArray.InsertNextValue(side)
     
     segment = segmentationNode.GetSegmentation().GetSegment(segmentId)
     SegmentNameArray.InsertNextValue(segment.GetName())
     InputForceArray.InsertNextValue(force1)
     InputAngleArray.InsertNextValue(angle1)
     
     JawLengthArray.InsertNextValue(JawLength)
     
     # measure surface area
     Area = stats[segmentId,"LabelmapSegmentStatisticsPlugin.surface_area_mm2"]/2
     SurfaceAreaArray.InsertNextValue(Area)
     
     # try to get tooth position at the base of the tooth
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
     toothposRAS = closestPointOnSurface_World # draw to the base of the tooth

     
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
       
     # add pos and out points to a list
     if ToothOutPoints.GetControlPointIndexByLabel(segment.GetName()) == -1:
       ToothOutPoints.AddControlPoint(toothoutRAS, segment.GetName())
     if ToothPosPoints.GetControlPointIndexByLabel(segment.GetName()) == -1:
       ToothPosPoints.AddControlPoint(toothposRAS, segment.GetName())
     
     # measure distance between jaw joint and the base of the tooth
     ToothPoslineNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", segment.GetName())
     shNode.SetItemParent(shNode.GetItemByDataNode(ToothPoslineNode), posFolder)
     ToothPoslineNode.GetDisplayNode().SetPropertiesLabelVisibility(False)
     ToothPoslineNode.GetDisplayNode().SetSelectedColor((0, 0.72, 0.92))
     ToothPoslineNode.GetDisplayNode().SetActiveColor((1, 0.65, 0.0))
     ToothPoslineNode.AddControlPoint(jointRAS)
     toothposRAS = [0,]*3
     ToothPosPoints.GetNthControlPointPosition(ToothPosPoints.GetControlPointIndexByLabel(segment.GetName()),toothposRAS)
     ToothPoslineNode.AddControlPoint(toothposRAS)
     ToothPos = ToothPoslineNode.GetMeasurement('length').GetValue()
     PositionArray.InsertNextValue(ToothPos)
     slicer.mrmlScene.RemoveNode(ToothPoslineNode)

     # measure distance between jaw joint and tip of the tooth
     ToothOutlineNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", segment.GetName())
     shNode.SetItemParent(shNode.GetItemByDataNode(ToothOutlineNode), outFolder)
     ToothOutlineNode.GetDisplayNode().SetPropertiesLabelVisibility(False)
     ToothOutlineNode.AddControlPoint(jointRAS)
     toothoutRAS = [0,]*3
     ToothOutPoints.GetNthControlPointPosition(ToothOutPoints.GetControlPointIndexByLabel(segment.GetName()),toothoutRAS)
     ToothOutlineNode.AddControlPoint(toothoutRAS)
     OutLever = ToothOutlineNode.GetMeasurement('length').GetValue()
     slicer.mrmlScene.RemoveNode(ToothOutlineNode)
     
     # get relative tooth position
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
     ftooth_total = 0
     if MusclecheckBox1 == True:
       MA1 = InLever1/OutLever
       ftooth_1 = force1 * math.sin(math.radians(angle1)) * MA1
       ftooth_total = ftooth_total + ftooth_1
       MechAdvArray.InsertNextValue(MA1)
     if MusclecheckBox2 == True:
       MA2 = InLever2/OutLever
       ftooth_2 = force2 * math.sin(math.radians(angle2)) * MA2
       ftooth_total = ftooth_total + ftooth_2
       #MechAdvArray.InsertNextValue(MA2)
     if MusclecheckBox3 == True:
       MA3 = InLever3/OutLever
       ftooth_3 = force3 * math.sin(math.radians(angle3)) * MA3
       ftooth_total = ftooth_total + ftooth_3
       #MechAdvArray.InsertNextValue(MA3)

     FToothArray.InsertNextValue(ftooth_total)
     
     # calculate tooth stress
     stress = ftooth_total/(Area * 1e-6)
     StressArray.InsertNextValue(stress)

    
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