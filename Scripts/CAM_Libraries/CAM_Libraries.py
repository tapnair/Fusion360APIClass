import adsk.cam
import adsk.core
import adsk.fusion
import traceback


app = adsk.core.Application.get()
ui = app.userInterface


def run(context):
    try:
        get_tool()

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
            # for tool in toolLib:
            #     if tool.parameters.itemByName('tool_description').value.value == '1/16" Ball Endmill':
                    # return tool
            # return None

    return None
