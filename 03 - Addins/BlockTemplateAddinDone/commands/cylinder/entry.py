import adsk.core
import adsk.fusion
import os
from ...lib import fusion360utils as futil
from ... import config
app = adsk.core.Application.get()
ui = app.userInterface


# TODO *** Specify the command identity information. ***
CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_cylinder_command'
CMD_NAME = 'Cylinder'
CMD_Description = 'A Fusion 360 Add-in Command to create a Cylinder'

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

# Local list of event handlers used to maintain a reference so
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
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Created Event')

    # https://help.autodesk.com/view/fusion360/ENU/?contextId=CommandInputs
    inputs = args.command.commandInputs

    # Create a value input field and set the default using 1 unit of the default length unit.
    default_length_units = app.activeProduct.unitsManager.defaultLengthUnits
    default_value = adsk.core.ValueInput.createByString('1')

    # Define three value inputs to capture length, width and height
    inputs.addValueInput('radius_input', 'Radius', default_length_units, default_value)
    inputs.addValueInput('height_input', 'Height', default_length_units, default_value)

    # Add relevant events
    futil.add_handler(args.command.execute, command_execute, local_handlers=local_handlers)
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
    make_cylinder(inputs)


# This event handler is called when the command needs to compute a new preview in the graphics window.
def command_preview(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Preview Event')
    inputs = args.command.commandInputs

    # Preview the block
    make_cylinder(inputs)

    # Optionally set the preview results as "valid"
    # This will bypass the redundant call in command_execute
    # args.isValidResult = True


# This event handler is called when the command terminates.
def command_destroy(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Destroy Event')

    global local_handlers
    local_handlers = []


def make_cylinder(inputs: adsk.core.CommandInputs):

    # Get the command inputs
    radius_input = adsk.core.ValueCommandInput.cast(inputs.itemById('radius_input'))
    height_input = adsk.core.ValueCommandInput.cast(inputs.itemById('height_input'))

    # Get the values from the command inputs
    radius = radius_input.value
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
    circles = sketch.sketchCurves.sketchCircles

    # Use autodesk methods to create input geometry
    point0 = adsk.core.Point3D.create(0, 0, 0)

    # Create lines
    circles.addByCenterRadius(point0, radius)

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
