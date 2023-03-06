#Author-Patrick Rainsberry
#Description-Basic User Input for Block

import adsk.core, adsk.fusion, adsk.cam, traceback

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        design = app.activeProduct     
        
        # Get reference to the root component
        rootComp = design.rootComponent
        
        #Get reference to the sketchs and plane
        sketches = rootComp.sketches
        xyPlane = rootComp.xYConstructionPlane
        
        #Create a new sketch and get lines reference
        sketch = sketches.add(xyPlane)
        lines = sketch.sketchCurves.sketchLines
        
        # Prompt user for values (Note: zero error checking)
        length_input = ui.inputBox('Enter a length', 'Length', '3')
        depth_input = ui.inputBox('Enter a depth', 'Depth', '1')
        height_input = ui.inputBox('Enter a distance', 'Height', '2')
        
        # Convert string to number from returned value
        length = float(length_input[0])
        depth = float(depth_input[0])
        height = float(height_input[0])
        
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

        # Create an extrusion input
        extrudes = rootComp.features.extrudeFeatures
        ext_input = extrudes.createInput(profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        
        # Define that the extent is a distance extent of height
        distance = adsk.core.ValueInput.createByReal(height)
        
        # Set the distance extent to be single direction
        ext_input.setDistanceExtent(False, distance)
        
        # Set the extrude to be a solid one
        ext_input.isSolid = True

        # Create the extrusion
        extrudes.add(ext_input)
        
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
