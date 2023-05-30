# Sample addin that demonstrates creating a button in the ui
# This is the simplest forma of transitioning a script to have a command in the ui
# No Dialog is created, it simply executes a single function called command_execute()
import os
import traceback

import adsk.core
import adsk.fusion
import adsk.cam

# Local list of event handlers used to maintain a reference.
create_handlers = []
cmd_handlers = []

# Specify the command identity information.
CMD_ID = f'BLOCK_SIMPLE_ADDIN_DONE'
CMD_NAME = 'Make a Block'
CMD_Description = 'A Fusion 360 Add-in Command to make a block'

# Use ui.workspaces to see available workspaces, like: CAMEnvironment
WORKSPACE_ID = 'FusionSolidEnvironment'

# Use workspace.toolbarPanels to see available panels for a given workspace
PANEL_ID = 'SolidScriptsAddinsPanel'

# Specify if the command will be promoted in the panel.
IS_PROMOTED = True

# Resource location for command icons, here we assume a sub folder in this directory named "resources".
ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', '')

app = adsk.core.Application.get()
ui = app.userInterface


# This function is called when the user clicks your button in the Fusion UI
def command_execute(args: adsk.core.CommandEventArgs):

    # ******************************** Your code here ********************************
    inputs = args.command.commandInputs
    length_input = adsk.core.ValueCommandInput.cast(inputs.itemById('length_input'))
    width_input = adsk.core.ValueCommandInput.cast(inputs.itemById('width_input'))
    height_input = adsk.core.ValueCommandInput.cast(inputs.itemById('height_input'))

    length = length_input.value
    width = width_input.value
    height = height_input.value

    #  Get the active Document
    document = adsk.core.Document.cast(app.activeDocument)

    #  Get the design
    #  The "cast" is to enable type hints to work better
    design = adsk.fusion.Design.cast(document.products.itemByProductType('DesignProductType'))

    # Get reference to the root component
    root_comp = design.rootComponent

    # Get reference to the sketches and plane
    sketches = root_comp.sketches
    xy_plane = root_comp.xYConstructionPlane

    # Create a new sketch and get lines reference
    sketch = sketches.add(xy_plane)
    lines = sketch.sketchCurves.sketchLines

    # Use autodesk methods to create input geometry
    point0 = adsk.core.Point3D.create(0, 0, 0)
    point1 = adsk.core.Point3D.create(length, 0, 0)
    point2 = adsk.core.Point3D.create(length, width, 0)
    point3 = adsk.core.Point3D.create(0, width, 0)

    # Create lines
    lines.addByTwoPoints(point0, point1)
    lines.addByTwoPoints(point1, point2)
    lines.addByTwoPoints(point2, point3)
    lines.addByTwoPoints(point3, point0)

    # Get the profile defined by the circle
    profile = sketch.profiles.item(0)

    # Get the extrude features Collection for the root component
    extrudes = root_comp.features.extrudeFeatures

    # Create an extrusion input
    extrude_input = extrudes.createInput(profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

    # Define that the extent is a distance extent of 1 cm
    distance = adsk.core.ValueInput.createByReal(height)

    # Define the direction for the extrude feature to be in the positive direction
    direction = adsk.fusion.ExtentDirections.PositiveExtentDirection

    # Create a distance extent object
    distance_extent_definition = adsk.fusion.DistanceExtentDefinition.create(distance)

    # Set the extrude feature to be single direction
    extrude_input.setOneSideExtent(distance_extent_definition, direction)

    # Create the extrusion
    extrudes.add(extrude_input)


# This function is called when the user clicks your button in the Fusion UI and is used to create the input dialog
def command_created(args: adsk.core.CommandEventArgs):
    inputs = args.command.commandInputs

    # Create a value input field and set the default using 1 unit of the default length unit.
    default_length_units = app.activeProduct.unitsManager.defaultLengthUnits
    default_value = adsk.core.ValueInput.createByString('1')

    # Define three value inputs to capture length, width and height
    inputs.addValueInput('length_input', 'Length', default_length_units, default_value)
    inputs.addValueInput('width_input', 'Width', default_length_units, default_value)
    inputs.addValueInput('height_input', 'Height', default_length_units, default_value)


# ************************** Below is standard code and should not need modification **************************

# Runs once when the add-in is initially started
def run(context):
    try:
        # Cleanup if we had a previous error that left the ui in a bad state
        old_definition = ui.commandDefinitions.itemById(CMD_ID)
        if old_definition is not None:
            old_definition.deleteMe()

        # Create a command Definition.
        cmd_def = ui.commandDefinitions.addButtonDefinition(CMD_ID, CMD_NAME, CMD_Description, ICON_FOLDER)

        # Define an event handler for the command created event.
        on_command_created = MyCommandCreatedHandler()
        cmd_def.commandCreated.add(on_command_created)
        create_handlers.append(on_command_created)

        # Get the specified workspace and end if it is not found
        workspace = ui.workspaces.itemById(WORKSPACE_ID)
        if workspace is None:
            ui.messageBox(f'Invalid Workspace ID: {WORKSPACE_ID}')
            adsk.terminate()
            return

        # Get the specified panel and end if it is not found
        panel = workspace.toolbarPanels.itemById(PANEL_ID)
        if panel is None:
            ui.messageBox(f'Invalid Panel ID: {PANEL_ID}')
            adsk.terminate()
            return

        # Cleanup if we had a previous error that left the ui in a bad state
        old_control = panel.controls.itemById(CMD_ID)
        if old_control is not None:
            old_control.deleteMe()

        # Add a control for our button command into the UI so the user can run the command.
        control = panel.controls.addCommand(cmd_def)
        control.isPromoted = IS_PROMOTED

    except:
        ui.messageBox('Failed to run addin:\n{}'.format(traceback.format_exc()))


# Runs when the add-in is stopped either: manually from the Scripts dialog or via adsk.terminate()
def stop(context):
    global create_handlers
    global cmd_handlers
    try:
        # Remove all the event handlers your app has created
        create_handlers = []
        cmd_handlers = []

        # Get the command control and definition
        workspace = ui.workspaces.itemById(WORKSPACE_ID)
        if workspace:
            panel = workspace.toolbarPanels.itemById(PANEL_ID)
            if panel:
                command_control = panel.controls.itemById(CMD_ID)
                command_definition = ui.commandDefinitions.itemById(CMD_ID)

                # Delete the command control and definition
                if command_control:
                    command_control.deleteMe()
                if command_definition:
                    command_definition.deleteMe()

    except:
        ui.messageBox('Failed to stop addin:\n{}'.format(traceback.format_exc()))


# Event handler that reacts when the button is pressed and creates the command instance
class MyCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            # Get the command that was created.
            cmd = adsk.core.Command.cast(args.command)

            # You could create a command dialog here
            command_created(args)

            # Connect to the command destroy event.
            on_destroy = MyCommandDestroyHandler()
            cmd.destroy.add(on_destroy)
            cmd_handlers.append(on_destroy)

            # Connect to the command execute event.
            on_execute = MyCommandExecuteHandler()
            cmd.execute.add(on_execute)
            cmd_handlers.append(on_execute)

        except:
            ui.messageBox('Failed to create command:\n{}'.format(traceback.format_exc()))


# Event handler that is automatically notified since we have not defined a dialog
class MyCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            command_execute(args)

        except:
            ui.messageBox('Failed to execute command:\n{}'.format(traceback.format_exc()))


# Event handler that is notified when each instance of the command completes
class MyCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        global cmd_handlers
        try:
            cmd_handlers = []

        except:
            ui.messageBox('Failed to destroy command:\n{}'.format(traceback.format_exc()))
