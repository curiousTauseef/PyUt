
from typing import List
from typing import cast

from logging import Logger
from logging import getLogger

from datetime import datetime

from org.pyut.general.PyutVersion import PyutVersion
from org.pyut.model.PyutClass import PyutClass
from org.pyut.model.PyutMethod import PyutMethod

from org.pyut.model.PyutVisibilityEnum import PyutVisibilityEnum


class PyutToPython:

    MAX_WIDTH: int = 80

    """
    Reads the Pyut data model in order to generated syntactically correct Python code
    """
    def __init__(self):

        self.logger: Logger = getLogger(__name__)

    def generateTopCode(self) -> List[str]:

        now = datetime.now()

        dateTimeStr: str = now.strftime("%Y-%m-%d %H:%M:%S")
        topCode: List[str] = [
            f'# \n',
            f'# Generated by Pyut Version {PyutVersion.getPyUtVersion()}\n',
            f'# -- La Vida Buena, LLC\n',
            f'# {dateTimeStr}\n',
            f'# \n'
            ]

        return topCode

    def generateClassStanza(self, pyutClass: PyutClass) -> str:
        """
        Generates something like this

        ```python
            class Car:
        ```
        or with inheritance

        ```python
            class ElectricCar(BaseVehicle, Car):
        ```
`
        Args:
            pyutClass:   The data model class

        Returns:
            The Python class start stanza
        """

        generatedCode:     str             = f'class {pyutClass.getName()}'
        parentPyutClasses: List[PyutClass] = cast(List[PyutClass], pyutClass.getParents())

        if len(parentPyutClasses) > 0:  # Add parents
            generatedCode = f'{generatedCode}('
            for i in range(len(parentPyutClasses)):
                generatedCode = f'{generatedCode}{parentPyutClasses[i].getName()}'
                if i < len(parentPyutClasses) - 1:
                    generatedCode = f'{generatedCode},'
            generatedCode = f'{generatedCode})'
        generatedCode = f'{generatedCode}:\n'

        return generatedCode

    def generateVisibilityPrefix(self, visibility: PyutVisibilityEnum) -> str:
        """
        Return the python code for the given enumeration value

        Args:
            visibility:

        Returns:
            The Python code that by convention depicts `method` or `field` visibility
        """
        code: str = ''
        if visibility == PyutVisibilityEnum.PUBLIC:
            code = ''
        elif visibility == PyutVisibilityEnum.PROTECTED:
            code = '_'
        elif visibility == PyutVisibilityEnum.PRIVATE:
            code = '__'
        else:
            self.logger.error(f"PyutToPython: Field code not supported : {visibility}")
        self.logger.debug(f"Python code: {code}, for {visibility}")
        return code

    def getOneMethodCode(self, pyutMethod: PyutMethod, writePass: bool = True) -> List[str]:
        """
        Generate the Python code for the input method

        Args:
            pyutMethod:    The PyutMethod for which we will generate code
            writePass:  If `True` write `pass` in the code

        Returns:
            A list that is the generated code
        """
        methodCode:  List[str] = []
        currentCode: str = "def "

        # Add visibility
        currentCode += self.generateVisibilityPrefix(pyutMethod.getVisibility())
        # Add name
        currentCode += str(pyutMethod.getName()) + "(self"

        # Add parameters (parameter, parameter, parameter, ...)
        # TODO : add default value ?
        params = pyutMethod.getParams()
        if len(params) > 0:
            currentCode += ", "
        for i in range(len(params)):
            # Add param code
            paramCode = ""
            paramCode += params[i].getName()
            if params[i].getDefaultValue() is not None:
                paramCode += "=" + params[i].getDefaultValue()
            if i < len(pyutMethod.getParams())-1:
                paramCode += ", "
            if (len(currentCode) % 80) + len(paramCode) > PyutToPython.MAX_WIDTH:  # Width limit
                currentCode += "\n" + self.indentStr(self.indentStr(paramCode))
            else:
                currentCode += paramCode

        # End first(s) line(s)
        currentCode += "):\n"

        # Add to the method code
        methodCode.append(currentCode)
        # currentCode = ""

        # Add comments
        methodCode.append(self.indentStr('"""\n'))
        methodCode.append(self.indentStr('(TODO : add description)\n\n'))

        # Add parameters
        params = pyutMethod.getParams()
        # if len(params)>0: currentCode+=", "
        for i in range(len(params)):
            methodCode.append(self.indentStr('@param ' + str(params[i].getType()) + ' ' + params[i].getName() + '\n'))

        # Add others
        if pyutMethod.getReturns() is not None and len(str(pyutMethod.getReturns())) > 0:
            methodCode.append(self.indentStr('@return ' + str(pyutMethod.getReturns()) + '\n'))
        methodCode.append(self.indentStr('@since 1.0' + '\n'))
        methodCode.append(self.indentStr('@author ' + '\n'))
        methodCode.append(self.indentStr('"""\n'))
        if writePass:
            methodCode.append(self.indentStr('pass\n'))

        # Return the field code
        return methodCode

    def indentStr(self, stringToIndent) -> str:
        """
        Indent one string by one unit

        Args:
            stringToIndent:  string to indent

        Returns:
            Indented string
        """
        return f'    {stringToIndent}'