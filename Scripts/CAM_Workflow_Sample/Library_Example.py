import adsk.cam
import adsk.core
import adsk.fusion
import traceback

def get_tool():
    # Get a reference to the CAMManager object. 
    camMgr = adsk.cam.CAMManager.get() 
    
    # Get the ToolLibraries object. 
    toolLibs = camMgr.libraryManager.toolLibraries 
    
    # Get the URL for the local libraries. 
    localLibLocationURL = toolLibs.urlByLocation(adsk.cam.LibraryLocations.LocalLibraryLocation) 
    
    # Get the URL of the folder, which will be for the "CustomTools" folder. 
    f360FolderURLs = toolLibs.childFolderURLs(localLibLocationURL) 
    customToolsFolderURL = f360FolderURLs[0] 

    # Get the "CustomMilling" library. 
    f360LibraryURLs = toolLibs.childAssetURLs(customToolsFolderURL)
     
    toolLib = None 
    for libURL in f360LibraryURLs: 
        if 'CustomMilling' in libURL.leafName: 
            toolLib = toolLibs.toolLibraryAtURL(libURL) 
            
            # Find a specific tool. 
            for tool in toolLib: 
                if tool.parameters.itemByName('tool_description').value.value == '1/16" Ball Endmill': 
                    return tool 
                return 
        return None