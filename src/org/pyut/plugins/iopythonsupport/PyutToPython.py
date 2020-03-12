from typing import Dict
from typing import List
from typing import cast
from typing import NewType

from logging import Logger
from logging import getLogger

from datetime import datetime

from org.pyut.general.PyutVersion import PyutVersion
from org.pyut.model.PyutClass import PyutClass
from org.pyut.model.PyutField import PyutField
from org.pyut.model.PyutMethod import PyutMethod
from org.pyut.model.PyutParam import PyutParam
from org.pyut.model.PyutType import PyutType

from org.pyut.model.PyutVisibilityEnum import PyutVisibilityEnum


class PyutToPython:

    MethodsCodeType = NewType('MethodsCodeType', Dict[str, List[str]])

    MAX_WIDTH:            int = 120
    CLASS_COMMENTS_START: str = '"""'
    CLASS_COMMENTS_END:   str = '"""'
    SINGLE_TAB:           str = '    '

    SPECIAL_PYTHON_CONSTRUCTOR: str = '__init__'

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
        generatedCode = f'{generatedCode}{self.__indentStr(PyutToPython.CLASS_COMMENTS_START)}\n'
        generatedCode = f'{generatedCode}{self.__indentStr(pyutClass.getDescription())}\n'   # TODO need to split lines according to MAX_WIDTH
        generatedCode = f'{generatedCode}{self.__indentStr(PyutToPython.CLASS_COMMENTS_END)}\n'

        return generatedCode

    def generateMethodsCode(self, pyutClass: PyutClass) -> MethodsCodeType:
        """
        Return a dictionary of method code for a given class

        Args:
            pyutClass:  The data model class for which we have to generate a bunch fo code for

        Returns:
            A bunch of code that is the code for this class; The map key is the method name the
            value is a list of the method code
        """
        clsMethods = cast(PyutToPython.MethodsCodeType, {})
        for pyutMethod in pyutClass.getMethods():
            # Separation
            txt = ""
            lstCodeMethod = [txt]

            # Get code
            subCode:       List[str] = self.generateASingleMethodsCode(pyutMethod)
            lstCodeMethod += self.indent(subCode)

            clsMethods[pyutMethod.getName()] = lstCodeMethod

        # Add fields
        if len(pyutClass.getFields()) > 0:
            # Create method __init__ if it does not exist
            if PyutToPython.SPECIAL_PYTHON_CONSTRUCTOR not in clsMethods:
                # Separation
                lstCodeMethod = []

                subCode = self.generateASingleMethodsCode(PyutMethod(PyutToPython.SPECIAL_PYTHON_CONSTRUCTOR), False)

                for el in self.indent(subCode):
                    lstCodeMethod.append(str(el))

                clsMethods[PyutToPython.SPECIAL_PYTHON_CONSTRUCTOR] = lstCodeMethod

            clsInit = clsMethods[PyutToPython.SPECIAL_PYTHON_CONSTRUCTOR]
            for pyutField in pyutClass.getFields():
                clsInit.append(self.__indentStr(self.__indentStr(self.generateFieldPythonCode(pyutField))))
            clsInit.append('\n')

        return clsMethods

    def generateASingleMethodsCode(self, pyutMethod: PyutMethod, writePass: bool = True) -> List[str]:
        """
        Generate the Python code for the input method

        Args:
            pyutMethod:    The PyutMethod for which we will generate code
            writePass:  If `True` write `pass` in the code

        Returns:
            A list that is the generated code
        """
        methodCode:  List[str] = []

        currentCode: str = self._generateMethodDefinitionStanza(pyutMethod)
        # Add parameters (parameter, parameter, parameter, ...)
        params = pyutMethod.getParams()
        currentCode = self._generateParametersCode(currentCode, params)
        currentCode = f'{currentCode})'

        returnType: PyutType = pyutMethod.getReturns()
        if returnType is not None and returnType.value != '':
            currentCode = f'{currentCode} -> {returnType.value}'

        currentCode = f'{currentCode}:\n'

        # Add to the method code
        methodCode.append(currentCode)

        # Add comments
        methodCode.append(self.__indentStr('"""\n'))
        methodCode = self._generateMethodComments(methodCode, pyutMethod)
        methodCode.append(self.__indentStr('"""\n'))

        if writePass:
            methodCode.append(self.__indentStr('pass\n'))

        methodCode.append('\n')
        return methodCode

    def generateFieldPythonCode(self, pyutField: PyutField):
        """
        Generate the Python code for a given field

        Args:
            pyutField:   The PyutField that is the source of our code generation

        Returns:
            Python Code !!
        """
        fieldCode: str = "self."

        fieldCode = f'{fieldCode}{self.generateVisibilityPrefix(pyutField.getVisibility())}'
        fieldCode = f'{fieldCode}{pyutField.getName()}: {pyutField.getType()}'

        value = pyutField.getDefaultValue()
        if value == '':
            fieldCode = f'{fieldCode} = None'
        else:
            fieldCode = f'{fieldCode} = {value}'

        fieldCode = f'{fieldCode}\n'
        return fieldCode

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

    def _generateMethodDefinitionStanza(self, pyutMethod: PyutMethod):
        """
        Follow Python conventions for method visibility

        Something like:
        ```python
            def publicMethod(self
            def _protectedMethod(self
            def __privateMethod(self
        ```
        Args:
            pyutMethod: The method whose code we are generating

        Returns:
            The method start stanza
        """
        currentCode: str = "def "
        currentCode = f'{currentCode}{self.generateVisibilityPrefix(pyutMethod.getVisibility())}'
        currentCode = f'{currentCode}{pyutMethod.getName()}(self'

        return currentCode

    def _generateParametersCode(self, currentCode: str, params: List[PyutParam]):

        if len(params) > 0:
            currentCode = f'{currentCode}, '
        # Add parameter code
        for i in range(len(params)):
            pyutParam: PyutParam = params[i]
            numParams: int = len(params)
            paramCode: str = self.__generateParameter(currentParamNumber=i, numberOfParameters=numParams, pyutParam=pyutParam)

            currentCode = self.__addParamToMethodSignature(currentCode, paramCode)
        return currentCode

    def __generateParameter(self, currentParamNumber: int, numberOfParameters: int, pyutParam: PyutParam) -> str:
        """

        Args:
            currentParamNumber: The current parameter #
            numberOfParameters: The number of parameters the method has
            pyutParam:          What we are generating code from

        Returns:
            Python code for a single parameter
        """

        paramCode: str = ""

        paramCode = f'{paramCode}{pyutParam.getName()}'

        paramType: PyutType = pyutParam.getType()
        if paramType is not None and paramType.value != '':
            paramCode = f'{paramCode}: {paramType.value}'
        if pyutParam.getDefaultValue() is not None:
            paramCode = f'{paramCode} = {pyutParam.getDefaultValue()}'
        if currentParamNumber < numberOfParameters - 1:
            paramCode = f'{paramCode}, '

        return paramCode

    def _generateMethodComments(self, methodCode, pyutMethod):

        methodCode.append(self.__indentStr('(TODO : add description)\n\n'))

        params: List[PyutParam] = pyutMethod.getParams()

        if len(params) > 0:
            methodCode.append(self.__indentStr(f'Args:\n'))

        for i in range(len(params)):
            param: PyutParam = params[i]
            methodCode.append(self.__indentStr(f'{param.getName()}:\n', 2))
        # Add others
        if pyutMethod.getReturns() is not None and len(str(pyutMethod.getReturns())) > 0:
            methodCode.append(self.__indentStr('Returns:\n'))
            methodCode.append(self.__indentStr(f'{pyutMethod.getReturns()}\n', 2))

        return methodCode

    def __addParamToMethodSignature(self, currentCode, paramCode):
        """
        Is smart enough to know if the parameters list is so long it must be indented

        Args:
            currentCode:    Generated 'so far` code
            paramCode:      Generated code for current parameter

        Returns:
            Updated code
        """
        if (len(currentCode) % PyutToPython.MAX_WIDTH) + len(paramCode) > PyutToPython.MAX_WIDTH:  # Width limit
            currentCode += "\n" + self.__indentStr(self.__indentStr(paramCode))
        else:
            currentCode = f'{currentCode}{paramCode}'
        return currentCode

    def __indentStr(self, stringToIndent: str, numTabs: int = 1) -> str:
        """
        Indent one string by one unit

        Args:
            stringToIndent:  string to indent
            numTabs:         number of tabs to insert

        Returns:
            Indented string
        """
        insertedTabs: str = ''
        for x in range(numTabs):
            insertedTabs = f'{insertedTabs}{PyutToPython.SINGLE_TAB}'

        return f'{insertedTabs}{stringToIndent}'

    def indent(self, listIn: List[str]) -> List[str]:
        """
        Indent every line in listIn by one unit

        Args:
            listIn: Many strings

        Returns:
            A new list with indented strings
        """
        listOut: List[str] = []
        for el in listIn:
            listOut.append(self.__indentStr(str(el)))
        return listOut
