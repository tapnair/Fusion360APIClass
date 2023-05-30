# Author-Patrick Rainsberry
# Description-Basic Script to read info from CAM

import adsk.core
import adsk.fusion
import adsk.cam
import traceback

app = adsk.core.Application.get()
ui = app.userInterface


def run(context):
    try:
        # Get the active Document
        document = adsk.core.Document.cast(app.activeDocument)

        # Get the CAM Product (the equivalent of the "design" product in the Design Workspace)
        # The "cast" is to enable type hints to work better
        # This will fail if there is no CAM product in the current document
        cam_product = adsk.cam.CAM.cast(document.products.itemByProductType('CAMProductType'))

        # Variables for Machining Time calculation
        feed_scale = 1.0  # (%)
        rapid_feed = 100.0  # cm/sec
        tool_change_time = 0.0  # sec

        # Variables to track results
        total_time = 0.0
        final_message = ''

        # Generate all out-of-date tool paths
        cam_product.generateAllToolpaths(True)

        # Iterate over all Operations in the current document
        operation: adsk.cam.Operation
        for operation in cam_product.allOperations:

            # Compute machining time for this Operation
            machining_time = cam_product.getMachiningTime(operation, feed_scale, rapid_feed, tool_change_time)
            time = machining_time.machiningTime
            total_time += time

            # Get other properties for this Operation
            name = operation.name
            setup = operation.parentSetup
            setup_name = setup.name
            strategy = operation.strategy

            # Get the value of the feed rate parameter
            feed_rate_expression = ''
            feed_rate_value = 0.0
            feed_rate_parameter = operation.parameters.itemByName('tool_feedCutting')
            if feed_rate_parameter is not None:
                feed_rate_expression = feed_rate_parameter.expression
                feed_rate_parameter_value = adsk.cam.FloatParameterValue.cast(feed_rate_parameter.value)
                feed_rate_value = feed_rate_parameter_value.value

            # Get the value of the spindle speed parameter
            spindle_speed = ''
            spindle_speed_parameter = operation.parameters.itemByName('tool_spindleSpeed')
            if spindle_speed_parameter is not None:
                spindle_speed = spindle_speed_parameter.expression

            # Build message for this Operation
            msg = f"{name}\n"
            msg += f" - Type: {strategy}\n"
            msg += f" - Setup Name: {setup_name}\n"
            msg += f" - Feed Rate Expression: {feed_rate_expression}\n"
            msg += f" - Feed Rate Value: {feed_rate_value}\n"
            msg += f" - Spindle Speed: {spindle_speed}\n"
            msg += f" - Machining Time {time} secs\n"
            app.log(msg)
            final_message += msg

        # Add message for the total machining time
        total_time_msg = f"Total Machining Time: {total_time} secs"
        app.log(total_time_msg)
        final_message += total_time_msg

        # Display the final complete message in a message box
        button_type = adsk.core.MessageBoxButtonTypes.OKButtonType
        icon_type = adsk.core.MessageBoxIconTypes.NoIconIconType
        title = f'{document.name}: CAM Info'
        ui.messageBox(final_message, title, button_type, icon_type)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
