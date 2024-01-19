import logging
import unittest
import os

import numpy as np
from scipy.stats import linregress

import vtk, ctk, qt

import slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin


#
# FractalDimension
#

class FractalDimension(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "FractalDimension"  # TODO: make this more human readable by adding spaces
        self.parent.categories = ["Examples"]  # TODO: set categories (folders where the module shows up in the module selector)
        self.parent.dependencies = []  # TODO: add here list of module names that this module requires
        self.parent.contributors = ["John Doe (AnyWare Corp.)"]  # TODO: replace with "Firstname Lastname (Organization)"
        # TODO: update with short description of the module and a link to online module documentation
        self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
See more information in <a href="https://github.com/organization/projectname#FractalDimension">module documentation</a>.
"""
        # TODO: replace with organization, grant and thanks
        self.parent.acknowledgementText = """
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc., Andras Lasso, PerkLab,
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
"""

        # Additional initialization step after application startup is complete
        slicer.app.connect("startupCompleted()", registerSampleData)


#
# Register sample data sets in Sample Data module
#

#def registerSampleData():
    """
    Add data sets to Sample Data module.
    """
    # It is always recommended to provide sample data for users to make it easy to try the module,
    # but if no sample data is available then this method (and associated startupCompeted signal connection) can be removed.

    #import SampleData
    #iconsPath = os.path.join(os.path.dirname(__file__), 'Resources/Icons')

    # To ensure that the source code repository remains small (can be downloaded and installed quickly)
    # it is recommended to store data sets that are larger than a few MB in a Github release.

    # FractalDimension1
    #SampleData.SampleDataLogic.registerCustomSampleDataSource(
    #    # Category and sample name displayed in Sample Data module
    #    category='FractalDimension',
    #    sampleName='FractalDimension1',
    #    # Thumbnail should have size of approximately 260x280 pixels and stored in Resources/Icons folder.
    #    # It can be created by Screen Capture module, "Capture all views" option enabled, "Number of images" set to "Single".
    #    thumbnailFileName=os.path.join(iconsPath, 'FractalDimension1.png'),
    #    # Download URL and target file name
    #    uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95",
    #    fileNames='FractalDimension1.nrrd',
    #    # Checksum to ensure file integrity. Can be computed by this command:
    #    #  import hashlib; print(hashlib.sha256(open(filename, "rb").read()).hexdigest())
    #    checksums='SHA256:998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95',
    #    # This node name will be used when the data set is loaded
    #    nodeNames='FractalDimension1'
    #)

    # FractalDimension2
    #SampleData.SampleDataLogic.registerCustomSampleDataSource(
    #    # Category and sample name displayed in Sample Data module
    #    category='FractalDimension',
    #    sampleName='FractalDimension2',
    #    thumbnailFileName=os.path.join(iconsPath, 'FractalDimension2.png'),
    #    # Download URL and target file name
    #    uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97",
    #    fileNames='FractalDimension2.nrrd',
    #    checksums='SHA256:1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97',
    #    # This node name will be used when the data set is loaded
    #    nodeNames='FractalDimension2'
    #)


#
# FractalDimensionWidget
#

class FractalDimensionWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
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
        uiWidget = slicer.util.loadUI(self.resourcePath('UI/FractalDimension.ui'))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)

        # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
        # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
        # "setMRMLScene(vtkMRMLScene*)" slot.
        uiWidget.setMRMLScene(slicer.mrmlScene)

        # Create logic class. Logic implements all computations that should be possible to run
        # in batch mode, without a graphical user interface.
        self.logic = FractalDimensionLogic()

        # Connections

        # These connections ensure that we update parameter node when scene is closed
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

        # These connections ensure that whenever user changes some settings on the GUI, that is saved in the MRML scene

        self.ui.Volume.connect("clicked(bool)", self.onFD)
        self.ui.segmentationSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
        #self.ui.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)

        # Buttons
        #self.ui.applyButton.connect('clicked(bool)', self.onApplyButton)

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
        
        # Make segmentation when initially opened
        if self.segmentationSelector.currentNode() is None:
            segmentationNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLSegmentationNode")
            self.segmentationSelector.setCurrentNode(segmentationNode)

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
        if not self._parameterNode.GetNodeReference("InputVolume"):
            firstVolumeNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLScalarVolumeNode")
            if firstVolumeNode:
                self._parameterNode.SetNodeReferenceID("InputVolume", firstVolumeNode.GetID())

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
        #self.ui.outputSelector.setCurrentNode(self._parameterNode.GetNodeReference("OutputVolume"))
        self.ui.segmentationSelector.setCurrentNode(self._parameterNode.GetNodeReference("Segmentation"))

        

        # Update buttons states and tooltips
#        if self._parameterNode.GetNodeReference("InputVolume") and self._parameterNode.GetNodeReference("OutputVolume"):
#            self.ui.applyButton.toolTip = "Compute output volume"
#            self.ui.applyButton.enabled = True
#        else:
#            #self.ui.applyButton.toolTip = "Select input and output volume nodes"
#            self.ui.applyButton.enabled = False

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

        #self._parameterNode.SetNodeReferenceID("OutputVolume", self.ui.outputSelector.currentNodeID)
        self._parameterNode.SetNodeReferenceID("Segmentation", self.ui.segmentationSelector.currentNodeID)
        #self._parameterNode.SetNodeReferenceID("ResultsTable", self.ui.outputSelector.currentNodeID)

        self._parameterNode.EndModify(wasModified)


#


    
    
    def onFD(self):
        # Arrays to store our table data
        indexCol = vtk.vtkIntArray()
        indexCol.SetName("Index")
        occupiedCol = vtk.vtkIntArray()
        occupiedCol.SetName("Cubes Occupied")
        occupiedColCube = vtk.vtkIntArray()
        occupiedColCube.SetName("Cubes Occupied (Cube FD)")
        cubeCol = vtk.vtkDoubleArray()
        cubeCol.SetName("Num Cubes")
        fractalCol = vtk.vtkDoubleArray()
        fractalCol.SetName("Fractal Dimension Divided")
        fractalColCube = vtk.vtkDoubleArray()
        fractalColCube.SetName("Fractal Dimension Cubes")
        
        # Column for indexing
        for i in range(1,21):
            indexCol.InsertNextValue(i)
            
        # The total amount of boxes
       # for i in range(1,21):
        #    cubeCol.InsertNextValue(i**3.0)

#       # Set segmentation node and Id
        segmentationNode = self.ui.segmentationSelector.currentNode()
        Name = segmentationNode.GetName()
#        segmentationNode = slicer.util.getNode("Segmentation")
#        segmentId = segmentationNode.GetSegmentation().GetSegmentIdBySegmentName('segmentation_1')
        segmentId = segmentationNode.GetSegmentation().GetSegmentIdBySegmentName(Name)
        
        # Create the labelmap volume node and export
        labelmapVolumeNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLabelMapVolumeNode")
        slicer.modules.segmentations.logic().ExportAllSegmentsToLabelmapNode(segmentationNode, labelmapVolumeNode, slicer.vtkSegmentation.EXTENT_REFERENCE_GEOMETRY)
        
        # Create another node to import labelmap to segmentation node, then get segment by Id
        seg = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode")
        slicer.modules.segmentations.logic().ImportLabelmapToSegmentationNode(labelmapVolumeNode, seg)
        segName = segmentationNode.GetSegmentation().GetSegment(segmentId)

        # Get the array from the labelmap Volume node
        labelArray = slicer.util.arrayFromVolume(labelmapVolumeNode)
        #spacing = labelArray.GetSpacing()
        print(labelArray)

        segmentData = labelArray
        print("segmentData Dimension", segmentData.shape)
        print("Sample SubMatrix", segmentData[300:310, 300:310, 100:110])


        # Fractal dimension with cubes
        print("Original Dims: ", segmentData.shape)
        
        def padArray(A, divideNum):

            if (A.shape[0] % divideNum) != 0:
                addNum = divideNum - (A.shape[0] % divideNum)
                zerosD1 = np.zeros([addNum,A.shape[1],A.shape[2]])
                A = np.vstack((A,zerosD1))

            if (A.shape[1] % divideNum) != 0:
                addNum = divideNum - (A.shape[1] % divideNum)
                zerosD2 = np.zeros([A.shape[0],addNum,A.shape[2]])
                A = np.hstack((A,zerosD2))

            if (A.shape[2] % divideNum) != 0:
                addNum = divideNum - (A.shape[2] % divideNum)
                zerosD3 = np.zeros([A.shape[0],A.shape[1],addNum])
                A = np.dstack((A,zerosD3))

            return(A)
            
            
        d1 = segmentData.shape[0]
        d2 = segmentData.shape[1]
        d3 = segmentData.shape[2]
        start_subdiv = 1
        end_subdiv = 21

        # To get equal dimension cubes, the `i` variable needs to scaled in each dimension

        # Try make it a true Cube
        # min_d = np.min(segmentData.shape)
        # segmentData = segmentData[:min_d, :min_d, :min_d]

        totalCubes = []
        containingCubes = []
        lineLength = []
        cubeCount = 0
        for i in range(start_subdiv, end_subdiv):
            # grid size is the shortest dimension divided by the number
            # of subdivisions, i
            d_min = np.min([d1, d2, d3])
            grid_size = int(d_min/i)
            

            # Get the total cube count, which is the number of
            # subdivisions along each dimension
            # lineLength.append(d_min/i)
            lineLength = np.append(lineLength, d_min/i)
            
            contCount = 0
            paddedArray = padArray(segmentData, grid_size)
            # Find the number of subdivisions along each dimension
            # such that the grid is uniform
            s1 = int(paddedArray.shape[0]/grid_size)
            s2 = int(paddedArray.shape[1]/grid_size)
            s3 = int(paddedArray.shape[2]/grid_size)
            cNum = s1*s2*s3
            totalCubes.append(cNum)
            
            print(paddedArray.shape)
            D1 = np.dsplit(paddedArray, s3)
            for j in D1:
                D2 = np.hsplit(j, s2)
                for k in D2:
                    D3 = np.vsplit(k, s1)
                    for C in D3:
                        # print(C.shape)
                        cubeCount += 1
                        if np.any(C) == True:
                            contCount +=1
            occupiedColCube.InsertNextValue(contCount)
            containingCubes = np.append(containingCubes, contCount)
            
            cubeCol.InsertNextValue(cubeCount)
            
            
        def fractDim(lineLength, numBoxes):
            #fit a line to these data to get the slope
            lineStats = linregress(np.log(1/lineLength),np.log(numBoxes))
            #print(lineStats)
            return(lineStats)
        
        lineLength = np.array(lineLength)
        containingCubes = np.array(containingCubes)
        FD = fractDim(lineLength, containingCubes)
        FractalDimension = np.around(FD[0],2)
            
        fractalColCube.InsertNextValue(FractalDimension)
        

        # ORIGINALLY DONE
        # Calculations
        def padArray(A, divideNum):

            if (A.shape[0] % divideNum) != 0:
                addNum = divideNum - (A.shape[0] % divideNum)
                zerosD1 = np.zeros([addNum,A.shape[1],A.shape[2]])
                A = np.vstack((A,zerosD1))

            if (A.shape[1] % divideNum) != 0:
                addNum = divideNum - (A.shape[1] % divideNum)
                zerosD2 = np.zeros([A.shape[0],addNum,A.shape[2]])
                A = np.hstack((A,zerosD2))

            if (A.shape[2] % divideNum) != 0:
                addNum = divideNum - (A.shape[2] % divideNum)
                zerosD3 = np.zeros([A.shape[0],A.shape[1],addNum])
                A = np.dstack((A,zerosD3))

            return(A)

        d1 = segmentData.shape[0]
        d2 = segmentData.shape[1]
        d3 = segmentData.shape[2]

        totalCubes = []
        containingCubes = []
        lineLength = []
        for i in range(1,21):
            lineLength.append(d3/i)
            cNum = i**3
            totalCubes.append(cNum)
            contCount = 0
            paddedArray = padArray(segmentData, i)
            #print(i)
            print(paddedArray.shape)
            D1 = np.dsplit(paddedArray, i)
            for j in D1:
                D2 = np.hsplit(j,i)
                for k in D2:
                    D3 = np.vsplit(k,i)
                    for C in D3:
                        #print(C.shape)
                        if np.any(C) == True:
                            contCount +=1
            occupiedCol.InsertNextValue(contCount)
            containingCubes.append(contCount)

        def fractDim(lineLength, numBoxes):
            #fit a line to these data to get the slope
            lineStats = linregress(np.log(1/lineLength),np.log(numBoxes))
            return(lineStats)

        lineLength = np.array(lineLength)
        containingCubes = np.array(containingCubes)
        FD = fractDim(lineLength, containingCubes)
        FractalDimension = np.around(FD[0],2)
        print(FractalDimension)

        # Column to print the fractal dimension
        fractalCol.InsertNextValue(FractalDimension)
        
        # DONE WITH SPLITTING INTO CUBES
        
        
        
        
        
#        minX = min(np.log(1/lineLength))
#        maxY = max(np.log(containingCubes))
#
#        histogram = np.histogram(slicer.util.arrayFromVolume(labelmapVolumeNode), bins=50)
#
#        tableNode=slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTableNode")
#        updateTableFromArray(tableNode, histogram)
#        tableNode.GetTable().GetColumn(0).SetName("Log 1/Line Length")
#        tableNode.GetTable().GetColumn(1).SetName("Log containingCubes")

#        plotSeriesNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotSeriesNode", labelmapVolumeNode.GetName() + " histogram")
#        plotSeriesNode.SetXColumnName("Log 1/Line Length")
#        plotSeriesNode.SetYColumnName("Log containingCubes")
        
        # Create table from column arrays
        resultTableNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTableNode", "Points from surface distance")
        resultTableNode.AddColumn(indexCol)
        resultTableNode.AddColumn(cubeCol)
        resultTableNode.AddColumn(occupiedCol)
        resultTableNode.AddColumn(occupiedColCube)
        resultTableNode.AddColumn(fractalCol)
        resultTableNode.AddColumn(fractalColCube)
        
        
        # Showing the table in view layout
        slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpTableView)
        slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID(resultTableNode.GetID())
        slicer.app.applicationLogic().PropagateTableSelection()
        
        
#
# FractalDimensionLogic
#

class FractalDimensionLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
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
        if not parameterNode.GetParameter("Threshold"):
            parameterNode.SetParameter("Threshold", "100.0")
        if not parameterNode.GetParameter("Invert"):
            parameterNode.SetParameter("Invert", "false")

    def process(self, inputVolume, outputVolume, imageThreshold, invert=False, showResult=True):
        """
        Run the processing algorithm.
        Can be used without GUI widget.
        :param inputVolume: volume to be thresholded
        :param outputVolume: thresholding result
        :param imageThreshold: values above/below this threshold will be set to 0
        :param invert: if True then values above the threshold will be set to 0, otherwise values below are set to 0
        :param showResult: show output volume in slice viewers
        """

        if not inputVolume or not outputVolume:
            raise ValueError("Input or output volume is invalid")

        import time
        startTime = time.time()
        logging.info('Processing started')

        # Compute the thresholded output volume using the "Threshold Scalar Volume" CLI module
        cliParams = {
            'InputVolume': inputVolume.GetID(),
            'OutputVolume': outputVolume.GetID(),
            'ThresholdValue': imageThreshold,
            'ThresholdType': 'Above' if invert else 'Below'
        }
        cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True, update_display=showResult)
        # We don't need the CLI module node anymore, remove it to not clutter the scene with it
        slicer.mrmlScene.RemoveNode(cliNode)

        stopTime = time.time()
        logging.info(f'Processing completed in {stopTime-startTime:.2f} seconds')

    def run(self,tableNode):
    
        tableNode.RemoveAllColumns()
        table = tableNode.GetTable()
        
#
# FractalDimensionTest
#

class FractalDimensionTest(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
        """ Do whatever is needed to reset the state - typically a scene clear will be enough.
        """
        slicer.mrmlScene.Clear()

    def runTest(self):
        """Run as few or as many tests as needed here.
        """
        self.setUp()
        self.test_FractalDimension1()

    def test_FractalDimension1(self):
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
        registerSampleData()
        inputVolume = SampleData.downloadSample('FractalDimension1')
        self.delayDisplay('Loaded test data set')

        inputScalarRange = inputVolume.GetImageData().GetScalarRange()
        self.assertEqual(inputScalarRange[0], 0)
        self.assertEqual(inputScalarRange[1], 695)

        outputVolume = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode")
        threshold = 100

        # Test the module logic

        logic = FractalDimensionLogic()

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