import os
import traceback

import adsk.cam
import adsk.core
import adsk.fusion


def run(context):
    ui = None
    try:

        #################### initialisation #####################
        app = adsk.core.Application.get()
        ui = app.userInterface

        # use existing document, load 2D Strategies model from the Fusion CAM Samples folder
        doc = app.activeDocument

        # switch to manufacturing space
        camWS = ui.workspaces.itemById('CAMEnvironment')
        camWS.activate()

        # get the CAM product
        products = doc.products

        #################### Find tools in sample tool library ####################
        # get the tool libraries from the library manager
        camManager = adsk.cam.CAMManager.get()
        libraryManager = camManager.libraryManager
        toolLibraries = libraryManager.toolLibraries

        # we can use a library URl directly if we know its address (here we use Fusion's Metric sample library)
        url = adsk.core.URL.create('systemlibraryroot://Samples/Milling Tools (Metric).json')

        # load tool library
        toolLibrary = toolLibraries.toolLibraryAtURL(url)

        # create some variables for the milling tools which will be used in the operations
        faceTool = None
        adaptiveTool = None

        # searching the face mill and the bull nose using a loop for the roughing operations
        for tool in toolLibrary:
            # read the tool type
            toolType = tool.parameters.itemByName('tool_type').value.value

            # select the first face tool found
            if toolType == 'face mill' and not faceTool:
                faceTool = tool

                # search the roughing tool
            elif toolType == 'bull nose end mill' and not adaptiveTool:
                # we look for a bull nose end mill tool larger or equal to 10mm but less than 14mm
                diameter = tool.parameters.itemByName('tool_diameter').value.value
                if diameter >= 1.0 and diameter < 1.4:
                    adaptiveTool = tool

            # exit when the 2 tools are found
            if faceTool and adaptiveTool:
                break

        #################### create setup ####################
        cam = adsk.cam.CAM.cast(products.itemByProductType("CAMProductType"))
        setups = cam.setups
        setupInput = setups.createInput(adsk.cam.OperationTypes.MillingOperation)
        # create a list for the models to add to the setup Input
        models = []
        part = cam.designRootOccurrence.bRepBodies.item(0)
        # add the part to the model list
        models.append(part)
        # pass the model list to the setup input
        setupInput.models = models
        # create the setup
        setup = setups.add(setupInput)
        # change some properties of the setup
        setup.name = 'CAM Basic Script Sample'
        setup.stockMode = adsk.cam.SetupStockModes.RelativeBoxStock
        # set offset mode
        setup.parameters.itemByName('job_stockOffsetMode').expression = "'simple'"
        # set offset stock side
        setup.parameters.itemByName('job_stockOffsetSides').expression = '0 mm'
        # set offset stock top
        setup.parameters.itemByName('job_stockOffsetTop').expression = '2 mm'
        # set setup origin
        setup.parameters.itemByName('wcs_origin_boxPoint').value.value = 'top 1'

        #################### face operation ####################
        # create a face operation input
        input = setup.operations.createInput('face')
        input.tool = faceTool
        input.displayName = 'Face Operation'
        input.parameters.itemByName('tolerance').expression = '0.01 mm'
        input.parameters.itemByName('stepover').expression = '0.75 * tool_diameter'
        input.parameters.itemByName('direction').expression = "'climb'"

        # add the operation to the setup
        faceOp = setup.operations.add(input)

        #################### adaptive operation ####################
        input = setup.operations.createInput('adaptive')
        input.tool = adaptiveTool
        input.displayName = 'Adaptive Roughing'
        input.parameters.itemByName('tolerance').expression = '0.1 mm'
        input.parameters.itemByName('maximumStepdown').expression = '5 mm'
        input.parameters.itemByName('fineStepdown').expression = '0.25 * maximumStepdown'
        input.parameters.itemByName('flatAreaMachining').expression = 'false'

        # add the operation to the setup
        adaptiveOp = setup.operations.add(input)

        ##################### generate operations ####################
        cam.generateToolpath(faceOp)
        cam.generateToolpath(adaptiveOp)

        #################### ncProgram and post-processing ####################
        # get the post library from library manager
        postLibrary = libraryManager.postLibrary

        # query post library to get postprocessor list
        postQuery = postLibrary.createQuery(adsk.cam.LibraryLocations.Fusion360LibraryLocation)
        postQuery.vendor = "Autodesk"
        postQuery.capability = adsk.cam.PostCapabilities.Milling
        postConfigs = postQuery.query()

        # find the "XYZ" post in the post library and import it to local library
        for config in postConfigs:
            if config.description == 'XYZ':
                url = adsk.core.URL.create("user://")
                importedURL = postLibrary.importPostConfiguration(config, url, "NCProgramSamplePost.cps")

        # get the imported local post config
        postConfig = postLibrary.postConfigurationAtURL(importedURL)

        # create NCProgramInput object
        ncInput = cam.ncPrograms.createInput()
        ncInput.displayName = 'NC Program Sample'

        # change some nc program parameters...
        ncParameters = ncInput.parameters
        ncParameters.itemByName('nc_program_filename').value.value = 'NCProgramSample'
        ncParameters.itemByName('nc_program_openInEditor').value.value = True

        # set user desktop as output directory (Windows and Mac)
        # make the path valid for Fusion360 by replacing \\ to / in the path
        desktopDirectory = os.path.expanduser("~/Desktop").replace('\\', '/')
        ncParameters.itemByName('nc_program_output_folder').value.value = desktopDirectory

        # select the operations to generate (we skip steep_and_shallow here)
        ncInput.operations = [faceOp, adaptiveOp]

        # add a new ncprogram from the ncprogram input
        newProgram = cam.ncPrograms.add(ncInput)

        # set post processor
        newProgram.postConfiguration = postConfig

        # change some post parameter
        postParameters = newProgram.postParameters
        postParameters.itemByName(
            'builtin_tolerance').value.value = 0.01  # NcProgram parameters is pass as it is to the postprocessor (it has no units)
        postParameters.itemByName(
            'builtin_minimumChordLength').value.value = 0.33  # NcProgram parameters is pass as it is to the postprocessor (it has no units)

        # update/apply post parameters
        newProgram.updatePostParameters(postParameters)

        # post-process
        # uncomment next line to automatically postprocess operations (requires them to be calculated!)
        # newProgram.postProcess()

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
