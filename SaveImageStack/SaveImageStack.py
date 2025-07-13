import logging
import os
import qt
from typing import Annotated, Optional

import vtk

import slicer
from slicer.i18n import tr as _
from slicer.i18n import translate
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
from slicer.parameterNodeWrapper import (
    parameterNodeWrapper,
    WithinRange,
)

from slicer import vtkMRMLScalarVolumeNode


#
# SaveImageStack
#


class SaveImageStack(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = _("Save ImageStack")  # TODO: make this more human readable by adding spaces
        # TODO: set categories (folders where the module shows up in the module selector)
        self.parent.categories = ["SlicerBiomech.Utilities"]
        self.parent.dependencies = []  # TODO: add here list of module names that this module requires
        self.parent.contributors = ["Jonathan M. Huie"]  # TODO: replace with "Firstname Lastname (Organization)"
        # TODO: update with short description of the module and a link to online module documentation
        # _() function marks text as translatable to other languages
        self.parent.helpText = _("""
This module allows you export a volume node as a stack of images.
""")
        # TODO: replace with organization, grant and thanks
        self.parent.acknowledgementText = _("""This module was developed by Jonathan M. Huie, who was supported by an NSF Graduate Research Fellowship (DGE-1746914).
""")

        # Additional initialization step after application startup is complete
        #slicer.app.connect("startupCompleted()", registerSampleData)


#
# SaveImageStackParameterNode
#


@parameterNodeWrapper
class SaveImageStackParameterNode:
    """
    The parameters needed by module.

    inputVolume - The volume to threshold.
    """

    inputVolume: vtkMRMLScalarVolumeNode
    #exportPath:
    #filename:
    #extension:


#
# SaveImageStackWidget
#


class SaveImageStackWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent=None) -> None:
        """Called when the user opens the module the first time and the widget is initialized."""
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)  # needed for parameter node observation
        self.logic = None
        self._parameterNode = None
        self._parameterNodeGuiTag = None
        self.loadingIsInProgress = False
        self.cancelRequested = False

    def setup(self) -> None:
        """Called when the user opens the module the first time and the widget is initialized."""
        ScriptedLoadableModuleWidget.setup(self)

        # Load widget from .ui file (created by Qt Designer).
        # Additional widgets can be instantiated manually and added to self.layout.
        uiWidget = slicer.util.loadUI(self.resourcePath("UI/SaveImageStack.ui"))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)

        # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
        # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
        # "setMRMLScene(vtkMRMLScene*)" slot.
        uiWidget.setMRMLScene(slicer.mrmlScene)

        # Create logic class. Logic implements all computations that should be possible to run
        # in batch mode, without a graphical user interface.
        self.logic = SaveImageStackLogic()

        # Connections

        # These connections ensure that we update parameter node when scene is closed
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)
        
        # Check GUI to update the Apply Button
        self.ui.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self._checkCanApply)
        self.ui.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.BitChanger)
        self.ui.ExportPathEdit.connect('currentPathChanged(QString)', self._checkCanApply)
        self.ui.FilenameBox.connect('textEdited(QString)', self._checkCanApply)
        self.ui.FormatcomboBox.connect('currentTextChanged(QString)', self._checkCanApply)
        
        self.ui.progressBar.hide()
        
        # Buttons
        self.ui.applyButton.connect("clicked(bool)", self.onApplyButton)

        # Make sure parameter node is initialized (needed for module reload)
        self.initializeParameterNode()

    def cleanup(self) -> None:
        """Called when the application closes and the module widget is destroyed."""
        self.removeObservers()

    def enter(self) -> None:
        """Called each time the user opens this module."""
        # Make sure parameter node exists and observed
        self.initializeParameterNode()

    def exit(self) -> None:
        """Called each time the user opens a different module."""
        # Do not react to parameter node changes (GUI will be updated when the user enters into the module)
        if self._parameterNode:
            self._parameterNode.disconnectGui(self._parameterNodeGuiTag)
            self._parameterNodeGuiTag = None
            self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self._checkCanApply)

    def onSceneStartClose(self, caller, event) -> None:
        """Called just before the scene is closed."""
        # Parameter node will be reset, do not use it anymore
        self.setParameterNode(None)

    def onSceneEndClose(self, caller, event) -> None:
        """Called just after the scene is closed."""
        # If this module is shown while the scene is closed then recreate a new parameter node immediately
        if self.parent.isEntered:
            self.initializeParameterNode()

    def initializeParameterNode(self) -> None:
        """Ensure parameter node exists and observed."""
        # Parameter node stores all user choices in parameter values, node selections, etc.
        # so that when the scene is saved and reloaded, these settings are restored.

        self.setParameterNode(self.logic.getParameterNode())

        # Select default input nodes if nothing is selected yet to save a few clicks for the user
        if not self._parameterNode.inputVolume:
            firstVolumeNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLScalarVolumeNode")
            if firstVolumeNode:
                self._parameterNode.inputVolume = firstVolumeNode

    def setParameterNode(self, inputParameterNode: Optional[SaveImageStackParameterNode]) -> None:
        """
        Set and observe parameter node.
        Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
        """

        if self._parameterNode:
            self._parameterNode.disconnectGui(self._parameterNodeGuiTag)
            self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self._checkCanApply)
        self._parameterNode = inputParameterNode
        if self._parameterNode:
            # Note: in the .ui file, a Qt dynamic property called "SlicerParameterName" is set on each
            # ui element that needs connection.
            self._parameterNodeGuiTag = self._parameterNode.connectGui(self.ui)
            self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self._checkCanApply)
            self._checkCanApply()

    def BitChanger(self, caller=None, event=None) -> None:
      inputVolume = self.ui.inputSelector.currentNode()
      VolumeArray = slicer.util.arrayFromVolume(inputVolume)
      if VolumeArray.dtype == "uint8":
        self.ui.FormatcomboBox.clear()
        #self.ui.FormatcomboBox.addItem('bmp')
        self.ui.FormatcomboBox.addItem('jpg')
        self.ui.FormatcomboBox.addItem('png')
        self.ui.FormatcomboBox.addItem('tiff')
        self.ui.FormatcomboBox.setCurrentIndex(3)
      if VolumeArray.dtype == "uint16":
        self.ui.FormatcomboBox.clear()
        self.ui.FormatcomboBox.addItem('png')
        self.ui.FormatcomboBox.addItem('tiff')
        self.ui.FormatcomboBox.setCurrentIndex(1)

    def _checkCanApply(self, caller=None, event=None) -> None:
        if self._parameterNode and self._parameterNode.inputVolume and self.ui.ExportPathEdit.currentPath != '' and self.ui.FilenameBox.text != '':
            self.ui.applyButton.toolTip = _("Save image stack")
            self.ui.applyButton.enabled = True
        else:
            self.ui.applyButton.toolTip = _("Select input volume node and export parameters")
            self.ui.applyButton.enabled = False


    def onApplyButton(self) -> None:
        """Run processing when user clicks "Apply" button."""
        
        if self.loadingIsInProgress:
            self.cancelRequested = True
            return

        self.loadingIsInProgress = True
        self.ui.progressBar.value = 0
        self.ui.progressBar.show()
        self.ui.applyButton.text = "Cancel saving"

        qt.QApplication.setOverrideCursor(qt.Qt.WaitCursor)
        try:
            slicer.app.pauseRender()
            outputNode = self.logic.process(self.ui.inputSelector.currentNode(), self.ui.axisSelectorBox.currentText, self.ui.ExportPathEdit.currentPath,
                               self.ui.FilenameBox.text, self.ui.FormatcomboBox.currentText, 
                               progressCallback=self.onProgress)
            #self.setCurrentNode(outputNode)
            qt.QApplication.restoreOverrideCursor()
        except Exception as e:
            qt.QApplication.restoreOverrideCursor()
            message, _, details = str(e).partition('\nDetails:\n')
            slicer.util.errorDisplay("Saving failed: " + message, detailedText=details)
            import traceback
            traceback.print_exc()

        slicer.app.resumeRender()
        self.cancelRequested = False
        self.loadingIsInProgress = False
        self.ui.progressBar.hide()
        self.ui.applyButton.text = "Save files"
        
    def onProgress(self, percentComplete):
        self.ui.progressBar.value = int(self.ui.progressBar.maximum * percentComplete)
        slicer.app.processEvents()
        return not self.cancelRequested

#
# SaveImageStackLogic
#


class SaveImageStackLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self) -> None:
        """Called when the logic class is instantiated. Can be used for initializing member variables."""
        ScriptedLoadableModuleLogic.__init__(self)

    def getParameterNode(self):
        return SaveImageStackParameterNode(super().getParameterNode())

    def process(self,
                inputVolume,
                axisIndex,
                exportPath,
                filename,
                fileformat,
                progressCallback = None):
        """
        Run the processing algorithm.
        Can be used without GUI widget.
        :param inputVolume: volume to be thresholded
        :param imageThreshold: values above/below this threshold will be set to 0
        :param invert: if True then values above the threshold will be set to 0, otherwise values below are set to 0
        """

        if not inputVolume:
            raise ValueError("Input volume is not selected")
            
        if exportPath == '':
            raise ValueError("Export path not valid")
            
        if filename == '':
            raise ValueError("Filename not valid")
            
        import time

        startTime = time.time()
        logging.info("Processing started")

        
        # establish volume metadata
        VolumeArray = slicer.util.arrayFromVolume(inputVolume)

        try:
          import imageio
        except ModuleNotFoundError:
          slicer.util.pip_install("imageio")
          import imageio
        
        dim = inputVolume.GetImageData().GetExtent()  
        if axisIndex == "Red (RS)":
          nslice = dim[5]+1 
        if axisIndex == "Green (PA)":
          nslice = dim[3]+1 
        if axisIndex == "Yellow (RL)":
          nslice = dim[1]+1 

        
        # save log file     
        import datetime
        spacing = inputVolume.GetSpacing()
        rounded_spacing = tuple(round(s, 9) for s in spacing)

        # Get the current time and date
        current_time = datetime.datetime.now()

        # Specify the file path where you want to save the file
        file_path = f"{exportPath}/{filename}_stack"
        if not os.path.exists(file_path):
        	os.makedirs(file_path)
        meta_path = f"{exportPath}/{filename}_log.txt"  # Replace with your desired path

        # Open the file at the specified path in write mode
        with open(meta_path, "w") as file:
            file.write(f"Exported from 3D Slicer with Save ImageStack module\n\n")
            # Write the current time and date as the first line
            file.write(f"Date: {current_time}\n\n")
    
            # Write the remaining lines
            file.write(f"Filename Prefix: {filename}\n")
            file.write(f"File Format: {fileformat}\n")
            file.write(f"Number of Images: {nslice}\n")
            
            if VolumeArray.dtype == "uint8":
              file.write(f"Bit Type: 8-bit\n")
            if VolumeArray.dtype == "uint16":
              file.write(f"Bit Type: 16-bit\n")
            file.write(f"\n")
           
            if axisIndex == "Red (RS)":
              file.write(f"Image Spacing X: {rounded_spacing[0]}\n")
              file.write(f"Image Spacing Y: {rounded_spacing[1]}\n")
              file.write(f"Image Spacing Z: {rounded_spacing[2]}\n")
            if axisIndex == "Green (PA)":
              file.write(f"Image Spacing X: {rounded_spacing[0]}\n")
              file.write(f"Image Spacing Y: {rounded_spacing[2]}\n")
              file.write(f"Image Spacing Z: {rounded_spacing[1]}\n")
            if axisIndex == "Yellow (RL)":
              file.write(f"Image Spacing X: {rounded_spacing[1]}\n")
              file.write(f"Image Spacing Y: {rounded_spacing[2]}\n")
              file.write(f"Image Spacing Z: {rounded_spacing[0]}\n")
            file.write(f"Image Spacing Units: mm")

        # Save images
        for i in range(nslice):
          if progressCallback:
            toContinue = progressCallback(i/nslice)
          if not toContinue:
            raise ValueError("User requested cancel")       
          n = i + 1
          if axisIndex == "Red (RS)":
            imageio.imwrite(f"{exportPath}/{filename}_{n:04}.{fileformat}", VolumeArray[i,:,:])
          if axisIndex == "Green (PA)":
            imageio.imwrite(f"{exportPath}/{filename}_{n:04}.{fileformat}", VolumeArray[:,i,:])
          if axisIndex == "Yellow (RL)":
            imageio.imwrite(f"{exportPath}/{filename}_{n:04}.{fileformat}", VolumeArray[:,:,i])

        stopTime = time.time()
        logging.info(f"Processing completed in {stopTime-startTime:.2f} seconds")
        

#
# SaveImageStackTest
#


class SaveImageStackTest(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
        """Do whatever is needed to reset the state - typically a scene clear will be enough."""
        slicer.mrmlScene.Clear()

    def runTest(self):
        """Run as few or as many tests as needed here."""
        self.setUp()
        self.test_SaveImageStack1()

    def test_SaveImageStack1(self):
        """Ideally you should have several levels of tests.  At the lowest level
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

        registerSampleData()
        inputVolume = SampleData.downloadSample("SaveImageStack1")
        self.delayDisplay("Loaded test data set")

        inputScalarRange = inputVolume.GetImageData().GetScalarRange()
        self.assertEqual(inputScalarRange[0], 0)
        self.assertEqual(inputScalarRange[1], 695)

        outputVolume = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode")
        threshold = 100

        # Test the module logic

        logic = SaveImageStackLogic()

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

        self.delayDisplay("Test passed")
