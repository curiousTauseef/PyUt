

from org.pyut.plugins.PyutToPlugin import PyutToPlugin
from org.pyut.ogl.OglClass import OglClass


class ToAscii(PyutToPlugin):
    """
    Python code generation/reverse engineering
    """
    def __init__(self, umlObjects, umlFrame):
        """

        Args:
            umlObjects:  list of ogl objects
            umlFrame:    the umlframe of pyut
        """
        PyutToPlugin.__init__(self, umlObjects, umlFrame)
        self._umlFrame = umlFrame

    def getName(self) -> str:
        """

        Returns: the name of the plugin.
        """
        return "ASCII Class export"

    def getAuthor(self) -> str:
        """

        Returns: The author's name

        """
        return "Philippe Waelti <pwaelti@eivd.ch>"

    def getVersion(self) -> str:
        """
        Returns: The plugin version string
        """
        return "1.0"

    def getMenuTitle(self) -> str:
        """
        Returns:  The menu title for this plugin
        """
        return "ASCII Class Export"

    def setOptions(self) -> bool:
        """
        Prepare the import.
        This can be used to ask some questions to the user.

        Returns: if False, the import will be cancelled.
        """
        return True

    def write(self, oglObjects):
        """
        Write the data to a file
        Args:
            oglObjects:   The objects to export
        """
        import math
        import os.path

        for oglObject in oglObjects:

            if not isinstance(oglObject, OglClass):
                continue

            o = oglObject.getPyutObject()

            suffix = 2
            filename = o.getName()

            while os.path.exists(filename + ".acl"):
                print("File exists")
                filename += str(suffix)
                suffix += 1

            file = open(filename + ".acl", "w")

            # base = []
            base = [o.getName()]
            if o.getStereotype() is not None:
                base.append(str(o.getStereotype()))

            fields = [str(x) for x in o.getFields()]
            methods = [str(x) for x in o.getMethods()]

            lnlgth = max([len(x) for x in base + fields + methods]) + 4

            file.write(lnlgth * "-" + "\n")

            for line in base:
                spaces = lnlgth - 4 - len(line)
                file.write("| " + int(math.floor(spaces / 2.0)) * " " + line + int(math.ceil(spaces / 2.0)) * " " + " |\n")

            file.write("|" + (lnlgth - 2) * "-" + "|\n")

            for line in fields:
                file.write("| " + line + (lnlgth - len(line) - 4) * " " + " |\n")

            file.write("|" + (lnlgth - 2) * "-" + "|\n")

            for line in methods:
                file.write("| " + line + (lnlgth - len(line) - 4) * " " + " |\n")

            file.write(lnlgth * "-" + "\n\n")

            file.write(o.getDescription())

            file.close()

    def doAction(self, umlObjects, selectedObjects, umlFrame):
        """

        Args:
            umlObjects:         list of the uml objects of the diagram
            selectedObjects:    list of the selected objects
            umlFrame:           The diagram frame
        """
        if len(selectedObjects) < 1:
            print("Please select class(es)")
            return
        self.write(selectedObjects)
