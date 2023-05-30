# Author-Patrick Rainsberry
# Description-Basic Script to post process A CAM setup
import os
from time import sleep, time

import adsk.core
import adsk.fusion
import adsk.cam
import traceback

app = adsk.core.Application.get()
ui = app.userInterface

POST_PROCESS_WAIT_INTERVAL = 1  # sec
OUTPUT_FOLDER = os.path.join(os.path.expanduser('~'), 'Fusion360APIClass', 'cam')
POST_CONFIG_NAME = 'fanuc.cps'
PROGRAM_NAME = '1001'


def run(context):
    try:
        #  Get the active Document
        document = adsk.core.Document.cast(app.activeDocument)

        #  Get the CAM Product (the equivalent of the "design" product in the Design Workspace)
        #  The "cast" is to enable type hints to work better
        cam_product = document.products.itemByProductType('CAMProductType')
        if cam_product:
            cam_product = adsk.cam.CAM.cast(cam_product)

            # Make sure there is at least 1 setup and get the first one
            if cam_product.setups.count > 0:
                setup = cam_product.setups.item(0)

                # Check if tool-paths have been generated
                is_valid = cam_product.checkToolpath(setup)
                if not is_valid:

                    # If they are out of date re-generate them
                    future = cam_product.generateToolpath(setup)

                    # Potentially interesting to time generation
                    start_time = time()

                    # Wait for process to complete
                    while not future.isGenerationCompleted:
                        adsk.doEvents()
                        sleep(POST_PROCESS_WAIT_INTERVAL)

                        # Log elapsed time
                        elapsed_time = time() - start_time
                        app.log(f'Waiting for CAM to finish: {elapsed_time:.3f} secs')

                # Options for post processor
                post_folder = cam_product.genericPostFolder
                post_config = os.path.join(post_folder, POST_CONFIG_NAME)
                units = adsk.cam.PostOutputUnitOptions.DocumentUnitsOutput

                # Create Post Processor Input Object
                post_input = adsk.cam.PostProcessInput.create(PROGRAM_NAME, post_config, OUTPUT_FOLDER, units)
                post_input.isOpenInEditor = False

                # Execute the post process command
                result = cam_product.postProcess(setup, post_input)

                # If successful, log results and open output folder
                if result:
                    app.log(f'{setup.name} was post processed to {OUTPUT_FOLDER}/{PROGRAM_NAME}.nc')

                    # Open the output folder in Finder on Mac or in Explorer on Windows
                    if os.name == 'posix':
                        os.system(f'open "{OUTPUT_FOLDER}"')
                    elif os.name == 'nt':
                        os.startfile(OUTPUT_FOLDER)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
