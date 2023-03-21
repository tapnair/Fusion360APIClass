# Author-Patrick Rainsberry
# Description-Basic Script to create a block

import adsk.cam
import adsk.core
import adsk.fusion
import traceback


app = adsk.core.Application.get()
ui = app.userInterface


def run(context):
    try:
        #  Get the design
        #  The "cast" is to enable type hints to work better
        design = adsk.fusion.Design.cast(app.activeProduct)

        # Get reference to the root component
        root_comp = design.rootComponent

        # Get reference to the sketches and plane
        sketches = root_comp.sketches
        xy_plane = root_comp.xYConstructionPlane

        # Create a new sketch and get lines reference
        sketch = sketches.add(xy_plane)
        lines = sketch.sketchCurves.sketchLines
        
        length = 4
        depth = 2
        height = 3
        
        # Use autodesk methods to create input geometry        
        point0 = adsk.core.Point3D.create(0, 0, 0)
        point1 = adsk.core.Point3D.create(0, length, 0)
        point2 = adsk.core.Point3D.create(depth, length, 0)
        point3 = adsk.core.Point3D.create(depth, 0, 0)
        
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
        
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
