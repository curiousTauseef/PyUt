
from typing import cast
from typing import List

from logging import Logger
from logging import getLogger

from os import open
from os import write

from os import sep as osSep
from os import O_WRONLY
from os import O_CREAT

from org.pyut.model.PyutClass import PyutClass
from org.pyut.model.PyutMethod import PyutMethod
from org.pyut.model.PyutParam import PyutParam
from org.pyut.model.PyutStereotype import PyutStereotype
from org.pyut.plugins.PyutIoPlugin import PyutIoPlugin

from org.pyut.ogl.OglClass import OglClass

from org.pyut.model.PyutLink import PyutLink

from org.pyut.enums.OglLinkType import OglLinkType
from org.pyut.ui.UmlFrame import UmlFrame


class IoJava(PyutIoPlugin):
    """
    Java code generation
    """
    def __init__(self, oglObjects, umlFrame: UmlFrame):

        super().__init__(oglObjects, umlFrame)
        self.logger: Logger = getLogger(__name__)

    def getName(self):
        """
        This method returns the name of the plugin.

        Returns:
            The name of the plugin
        """
        return "Java code generation"

    def getAuthor(self):
        """
        This method returns the author of the plugin.

        Returns:
            The name of the author

        """
        return "N. Dubois <nicdub@gmx.ch>"

    def getVersion(self):
        """
        This method returns the version of the plugin.

        Returns:
            The version number
        """
        return "1.0"

    def getOutputFormat(self):
        """
        Return a specification tuple.

        Returns:
            A specification tuple.
        """
        return "Java", "java", "Java file format"

    def setExportOptions(self) -> bool:
        return True

    def _writeParam(self, file: int, param: PyutParam):
        """
        Writing params to file.

        Args:
            file:   file descriptor
            param:  pyut parameter object to write
        """
        # file.write(str(param.getType()) + " " + param.getName())
        paramType: str = param.getType().__str__()
        paramName: str = param.getName()
        write(file, f'{paramType} {paramName}'.encode())

    def _writeMethod(self, file: int, method: PyutMethod):
        """
        Writing a method in file : name(param, param, ...).

        Args:
            file:       File descriptor
            method:     method object
        """
        name:       str = method.getName()
        visibility: str = self.__visibility[str(method.getVisibility())]
        returnType: str = str(method.getReturns())
        if returnType == "":
            returnType = "void"

        # file.write(self.__tab + visibility + " " + returnType + " " + name + "(")
        write(file, f'{self.__tab}{visibility} {returnType} {name}('.encode())

        # for all param
        nbParam = len(method.getParams())
        self.logger.info(f'# params: {nbParam}')
        for param in method.getParams():
            # writing param
            self._writeParam(file, param)

            # comma between param
            nbParam = nbParam - 1
            if nbParam > 0:
                # file.write(" , ")
                write(file, ' , '.encode())

        # file.write(") {\n" + self.__tab + "}\n\n")
        write(file, f') {{\n{self.__tab}}}\n\n'.encode())

    def _writeMethods(self, file: int, methods):
        """
        Writing methods in source (.java) file

        Args:
            file:       file descriptor
            methods:    list of all method of a class
        """
        # Write header
        if len(methods) > 0:
            # file.write("\n" + self.__tab + "// -------\n" + self.__tab + "// Methods\n" + self.__tab + "// -------\n\n")
            header: str = f'\n{self.__tab}// -------\n{self.__tab}// Methods\n{self.__tab}// -------\n\n'
            write(file, header.encode())

        # for all method in methods list
        for method in methods:
            method: PyutMethod = cast(PyutMethod, method)
            self.logger.info(f'method: {method}')
            self._writeMethodComment(file, method, self.__tab)
            self._writeMethod(file, method)

    def _writeFields(self, file: int, fields):
        """
        Write fields in file.

        @param file file:
        @param [PyutField, ...] fields : list of all fields of a class

        @author N. Dubois <nicdub@gmx.ch>
        @since 1.1
        """
        # Write fields header
        if len(fields) > 0:
            # file.write(self.__tab + "// ------\n" + self.__tab + "// Fields\n" + self.__tab + "// ------\n\n")
            write(file, f'{self.__tab}// ------\n{self.__tab}// Fields\n{self.__tab}// ------\n\n'.encode())
        # Write all fields in file
        for field in fields:
            # Visibility converted from "+" to "public", ...
            visibility = self.__visibility[str(field.getVisibility())]

            # Type
            fieldType: str = str(field.getType())
            self.logger.info(f'fieldType: {fieldType}')

            # Name
            name = field.getName()

            # Default value
            default = field.getDefaultValue()
            if default is not None and default != "":
                if fieldType.lower() == 'string':
                    default = f' = "{default}"'
                else:
                    default = f' = {default}'
            else:
                default = ""

            # Comments
            if fieldType == "":
                comments = " // Warning: no type"
            else:
                comments = ""

            # Write the comment before the field
            self._writeFieldComment(file, name, self.__tab)

            # Write the complete line in file
            # file.write(self.__tab + visibility + " " + fieldType + " " + name + default + ";" + comments + "\n")
            write(file, f'{self.__tab}{visibility} {fieldType} {name}{default};{comments}\n'.encode())

    def _writeLinks(self, file, links):
        """
        Write relation links in file.

        @param file file:
        @param [] links : list of relation links
        """
        # file.write("\n")
        write(file, "\n".encode())
        # Write all relation links in file
        for link in links:
            link = cast(PyutLink, link)
            # Get Class linked (type of variable)
            destinationLinkName = link.getDestination().getName()
            # Get name of aggregation
            name = link.getName()
            # Array or single variable
            # if link.getDestinationCardinality().find('n') != -1:
            if link.destinationCardinality.find('n') != -1:
                array = "[]"
            else:
                array = ""

            # Write data in file
            # file.write(self.__tab + "private " + destinationLinkName + " " + name + array + ";\n")
            write(file, f'{self.__tab}private {destinationLinkName} {name}{array};\n'.encode())

    def _writeParent(self, file: int, parents):
        """
        Writing parent for inheritance.  (Java only has single inheritance)

        Args:
            file:       file descriptor
            parents:    list of parents
        """
        nbr = len(parents)

        # If there is a parent:
        if nbr != 0:
            write(file, " extends ".encode())

            # Only one parent allowed
            parent: PyutClass = parents[0]
            name:   str       = parent.getName()
            write(file, name.encode())

    def _writeInterfaces(self, file: int, interfaces: List[PyutLink]):
        """
        Writing interfaces implemented by the class.

        Args:
            file:       file descriptor
            interfaces: list of implemented interfaces
        """
        nbr = len(interfaces)

        # If there is at least one interface:
        if nbr != 0:
            write(file, " implements ".encode())

            # Write the first interface
            interfaceName: str = interfaces[0].getDestination().getName()
            write(file, interfaceName.encode())

            # For all next interfaces, write the name separated by a ','
            for interface in interfaces[1:]:
                write(file, f', {interface.getDestination().getName()}'.encode())

    def _writeClassComment(self, file: int, className, classInterface):
        """
        Write class comment with doxygen organization.

        Args:
            file:       file descriptor
            className:
            classInterface:
        """
        # file.write("/**\n * " + classInterface + " " + className + "\n * More info here \n */\n")
        write(file, f'/**\n * {classInterface} {className}\n * Class information here \n */\n'.encode())

    def _writeMethodComment(self, file: int, method: PyutMethod, tab=""):
        """
        Write method comment with doxygen organization.

        Args:
            file:   file descriptor
            method: pyutMethod
            tab:    tab character(s) to use

        """
        # file.write(tab + "/**\n")
        # file.write(tab + " * method " + method.getName()+"\n")
        # file.write(tab + " * More info here.\n")
        write(file, f'{tab}/**\n'.encode())
        write(file, f'{tab} * method {method.getName()}\n'.encode())
        write(file, f'{tab} * More info here.\n'.encode())

        for param in method.getParams():
            # file.write(tab + " * @param " + param.getName() + " : " + str(param.getType()) + "\n")
            write(file, f' * @param {param.getName()} : {str(param.getType())}\n'.encode())

        if str(method.getReturns()) != '':
            # file.write(tab + " * @return " + str(method.getReturns()) + "\n")
            write(file, f'{tab} * @return {str(method.getReturns())}\n'.encode())

        # file.write(tab + " */\n")
        write(file, f'{tab} */\n'.encode())

    def _writeFieldComment(self, file: int, name: str, tab=""):
        """
        Write method comment using doxygen format.

        Args:
            file:   File descriptor
            name:   The field name
            tab:    `tab` character to use
        """
        # file.write(tab + "/**\n")
        # file.write(tab + " * field " + name+"\n")
        # file.write(tab + " * More info here.\n")
        #
        # file.write(tab + " */\n")

        write(file, f'{tab}/**\n'.encode())
        write(file, f'{tab} * field {name}\n'.encode())
        write(file, f'{tab} * More field information here.\n'.encode())

        write(file, f'{tab} */\n'.encode())

    def _separateLinks(self, allLinks, interfaces, links):
        """
        Separate the different types of links into lists.

        Args:
            allLinks:   list of links of the class
            interfaces: list of interfaces implemented by the class
            links:

        Returns:

        """
        for link in allLinks:
            linkType = link.getType()
            self.logger.info(f'Found linkType: `{linkType}`')
            if linkType == OglLinkType.OGL_INTERFACE:
                interfaces.append(link)
            elif linkType == OglLinkType.OGL_COMPOSITION or linkType == OglLinkType.OGL_AGGREGATION:
                links.append(link)

    def _writeClass(self, pyutClass: PyutClass):
        """
        Writing a class to a file.

        @param pyutClass : an object pyutClass
        """
        # Read class name
        className = pyutClass.getName()

        # Opening a file for each class
        fqn: str = f'{self._dir}{osSep}{className}.java'
        # javaFile = open(self._dir + osSep + className + '.java')
        flags:      int = O_WRONLY | O_CREAT
        javaFileFD: int = open(fqn, flags)

        # Extract the data from the class
        fields     = pyutClass.getFields()
        methods    = pyutClass.getMethods()
        parents    = pyutClass.getParents()
        allLinks   = pyutClass.getLinks()

        stereotype: PyutStereotype = pyutClass.getStereotype()

        # List of links
        interfaces = []     # List of interfaces implemented by the class
        links      = []     # Aggregation and compositions
        self._separateLinks(allLinks, interfaces, links)

        # Is this class an interface
        # ~ self._isInterface(pyutClass)

        # Is it an interface
        classInterface = "class"
        if stereotype is not None:
            stereotypeName: str = stereotype.getStereotype()
            if stereotypeName.lower() == "interface":
                classInterface = "interface"

        # Write data in file
        # Write class comment
        self._writeClassComment(javaFileFD, className, classInterface)
        # class name
        # javaFile.write("public " + classInterface + " " + className)
        write(javaFileFD, f'public {classInterface} {className}'.encode())

        self._writeParent(javaFileFD, parents)
        self._writeInterfaces(javaFileFD, interfaces)
        # javaFile.write(" {\n\n")
        write(javaFileFD, ' {\n\n'.encode())

        # Fields
        self._writeFields(javaFileFD, fields)

        # Aggregation and Composition
        self._writeLinks(javaFileFD, links)
        # Methods
        self._writeMethods(javaFileFD, methods)
        # end of class
        # javaFile.write("}\n")
        write(javaFileFD, '}\n'.encode())

    def _writeType(self, file, aParam):
        """
        This method undefined.  What is it supposed to do.   hasii 02/2020
        Args:
            file:
            aParam:

        """
        pass

    def write(self, oglObjects):
        """
        Data saving
        @param oglObjects : list of exported objects
        """
        # Directory for sources
        self._dir = self._askForDirectoryExport()

        # If no destination, abort
        if self._dir == "":
            return

        # defining constant
        self.__tab = "    "
        self.__visibility = {
            "+": "public",
            "-": "private",
            "#": "protected"
        }
        oglClasses = []
        for oglObject in oglObjects:
            self.logger.info(f'oglObject: {oglObject}')
            if isinstance(oglObject, OglClass):
                oglClasses.append(oglObject)

        # for el in [object for objects in oglObjects if isinstance(object, OglClass)]:
        for el in oglClasses:
            self._writeClass(el.getPyutObject())
