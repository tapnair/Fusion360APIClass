import adsk.core
import adsk.fusion
import os
from ...lib import fusion360utils as futil
from ... import config
app = adsk.core.Application.get()
ui = app.userInterface


# TODO *** Specify the command identity information. ***
CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_block_command'
CMD_NAME = 'Block'
CMD_Description = 'A Fusion 360 Add-in Command to create a Block'

# Specify that the command will be promoted to the panel.
IS_PROMOTED = True

# TODO *** Define the location where the command button will be created. ***
# This is done by specifying the workspace, the tab, and the panel, and the 
# command it will be inserted beside. Not providing the command to position it
# will insert it at the end.
WORKSPACE_ID = 'FusionSolidEnvironment'
PANEL_ID = 'SolidScriptsAddinsPanel'
COMMAND_BESIDE_ID = 'ScriptsManagerCommand'

# Resource location for command icons, here we assume a sub folder in this directory named "resources".
ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', '')

# Local list of event handlers used to maintain a references
# they are not released and garbage collected.
local_handlers = []


# Executed when add-in is run.
def start():
    # Create a command Definition.
    cmd_def = ui.commandDefinitions.addButtonDefinition(CMD_ID, CMD_NAME, CMD_Description, ICON_FOLDER)

    # Define an event handler for the command created event. It will be called when the button is clicked.
    futil.add_handler(cmd_def.commandCreated, command_created)

    # ******** Add a button into the UI so the user can run the command. ********
    # Get the target workspace the button will be created in.
    workspace = ui.workspaces.itemById(WORKSPACE_ID)

    # Get the panel the button will be created in.
    panel = workspace.toolbarPanels.itemById(PANEL_ID)

    # Create the button command control in the UI after the specified existing command.
    control = panel.controls.addCommand(cmd_def, COMMAND_BESIDE_ID, False)

    # Specify if the command is promoted to the main toolbar. 
    control.isPromoted = IS_PROMOTED


# Executed when add-in is stopped.
def stop():
    # Get the various UI elements for this command
    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    panel = workspace.toolbarPanels.itemById(PANEL_ID)
    command_control = panel.controls.itemById(CMD_ID)
    command_definition = ui.commandDefinitions.itemById(CMD_ID)

    # Delete the button command control
    if command_control:
        command_control.deleteMe()

    # Delete the command definition
    if command_definition:
        command_definition.deleteMe()


# Function that is called when a user clicks the corresponding button in the UI.
# This defines the contents of the command dialog and connects to the command related events.
def command_created(args: adsk.core.CommandCreatedEventArgs):
    inputs = args.command.commandInputs

    # Additional input option to dynamically change the dialog behavior
    inputs.addBoolValueInput('is_cube_input', 'Is this a cube?', True, '', False)

    # Create a value input field and set the default using 1 unit of the default length unit.
    default_length_units = app.activeProduct.unitsManager.defaultLengthUnits
    default_value = adsk.core.ValueInput.createByString('1')

    # Define three value inputs to capture length, width and height
    inputs.addValueInput('length_input', 'Length', default_length_units, default_value)
    inputs.addValueInput('width_input', 'Width', default_length_units, default_value)
    inputs.addValueInput('height_input', 'Height', default_length_units, default_value)

    # Add relevant events
    futil.add_handler(args.command.execute, command_execute, local_handlers=local_handlers)
    futil.add_handler(args.command.inputChanged, command_input_changed, local_handlers=local_handlers)
    futil.add_handler(args.command.executePreview, command_preview, local_handlers=local_handlers)
    futil.add_handler(args.command.destroy, command_destroy, local_handlers=local_handlers)


# This event handler is called when the user clicks the OK button in the command dialog or 
# is immediately called after the created event not command inputs were created for the dialog.
def command_execute(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Execute Event')

    # Get a reference to your command's inputs.
    inputs = args.command.commandInputs

    # Make the block, this is redundant if you were to set the preview result to be valid.
    make_block(inputs)


# This event handler is called when the command needs to compute a new preview in the graphics window.
def command_preview(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Preview Event')
    inputs = args.command.commandInputs

    # Preview the block
    make_block(inputs)

    # Optionally set the preview results as "valid"
    # This will bypass the redundant call in command_execute
    # args.isValidResult = True


# This event handler is called when the user changes anything in the command dialog
# allowing you to modify values of other inputs based on that change.
def command_input_changed(args: adsk.core.InputChangedEventArgs):
    changed_input = args.input
    inputs = args.inputs

    # Get the command input objects
    # length_input = adsk.core.ValueCommandInput.cast(inputs.itemById('length_input'))
    width_input = adsk.core.ValueCommandInput.cast(inputs.itemById('width_input'))
    height_input = adsk.core.ValueCommandInput.cast(inputs.itemById('height_input'))
    is_cube_input = adsk.core.BoolValueCommandInput.cast(inputs.itemById('is_cube_input'))

    if changed_input.id == is_cube_input.id:
        if is_cube_input.value:
            width_input.isVisible = False
            height_input.isVisible = False
        else:
            width_input.isVisible = True
            height_input.isVisible = True

    # General logging for debug.
    futil.log(f'{CMD_NAME} Input Changed Event fired from a change to {changed_input.id}')
        

# This event handler is called when the command terminates.
def command_destroy(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Destroy Event')

    global local_handlers
    local_handlers = []


def make_block(inputs: adsk.core.CommandInputs):

    # Get the command inputs
    length_input = adsk.core.ValueCommandInput.cast(inputs.itemById('length_input'))
    width_input = adsk.core.ValueCommandInput.cast(inputs.itemById('width_input'))
    height_input = adsk.core.ValueCommandInput.cast(inputs.itemById('height_input'))
    is_cube_input = adsk.core.BoolValueCommandInput.cast(inputs.itemById('is_cube_input'))

    # Get the values from the command inputs
    length = length_input.value
    if is_cube_input.value:
        width = length_input.value
        height = length_input.value
    else:
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
