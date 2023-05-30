import adsk.cam
import adsk.core
import adsk.fusion
import traceback


app = adsk.core.Application.get()
ui = app.userInterface


def run(context):
    try:
        get_tool()

        app.log(f'Running Query, be patient...')
        adsk.doEvents()

        library_query()

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def get_tool():
    # Get a reference to the CAMManager object.
    camMgr = adsk.cam.CAMManager.get()

    # Get the ToolLibraries object.
    toolLibs = camMgr.libraryManager.toolLibraries

    # Get the URL for the local libraries.
    localLibLocationURL = toolLibs.urlByLocation(adsk.cam.LibraryLocations.LocalLibraryLocation)
    app.log(f'localLibLocationURL = {localLibLocationURL.toString()}')

    # Get the URL of the folder, which will be for the "CustomTools" folder.
    f360FolderURLs = toolLibs.childFolderURLs(localLibLocationURL)
    customToolsFolderURL = f360FolderURLs[0]
    app.log(f'customToolsFolderURL = {customToolsFolderURL.toString()}')

    # Get the "CustomMilling" library.
    f360LibraryURLs = toolLibs.childAssetURLs(customToolsFolderURL)

    i = 0
    for libURL in f360LibraryURLs:
        app.log(f'f360LibraryURLs[{i}] = {libURL.toString()}')
        i += 1

        if 'CustomMilling' in libURL.leafName:
            toolLib = toolLibs.toolLibraryAtURL(libURL)

            # Find a specific tool.
            for tool in toolLib:
                description = tool.parameters.itemByName('tool_description').value.value
                if description == '1/16" Ball Endmill':
                    return tool
            return None

    return None


def library_query():
    # Get a reference to the CAMManager object.
    camMgr = adsk.cam.CAMManager.get()

    # Get the ToolLibraries object.
    toolLibs = camMgr.libraryManager.toolLibraries

    # Create a query object to query the local library.
    query = toolLibs.createQuery(adsk.cam.LibraryLocations.Fusion360LibraryLocation)

    # Add the search criteria.
    query.criteria.add('tool_diameter', adsk.core.ValueInput.createByReal(0.25 * 2.54))
    query.criteria.add('tool_cornerRadius.min', adsk.core.ValueInput.createByReal(0.05 * 2.54))
    query.criteria.add('tool_cornerRadius.max', adsk.core.ValueInput.createByReal(0.125 * 2.54))

    # Do the query.
    queryResults = query.query()

    # Get the tool from the results. There can be multiple tools returned. This used the first one.
    tool = None
    if len(queryResults) > 0:

        for queryResult in queryResults:
            tool = queryResult.tool

            description = tool.parameters.itemByName('tool_description').value.value
            diameter = tool.parameters.itemByName('tool_diameter').value.value
            app.log(f'Query Result: {description} with diameter {str(diameter)}')
    
    return tool
