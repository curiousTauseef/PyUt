
from typing import cast
from typing import List
from typing import NewType

from logging import Logger
from logging import getLogger

from org.pyut.PyutPreferences import PyutPreferences

from org.pyut.model.PyutModifier import PyutModifier
from org.pyut.model.PyutVisibilityEnum import PyutVisibilityEnum
from org.pyut.model.PyutType import PyutType

from org.pyut.model.PyutObject import PyutObject


[WITH_PARAMS, WITHOUT_PARAMS] = range(2)

PyutModifiers    = NewType('PyutModifiers',    List[PyutModifier])


class PyutMethod(PyutObject):
    """
    A method representation.

    A PyutMethod represents a method of a UML class in Pyut. It manages its:
        - visibility (`PyutVisibility`)
        - modifiers (`PyutModifier`)
        - parameters (`PyutParameter`)
        - return type (`PyutType`)

    It has a string mode that influence the way `__str__` works. The two modes
    are:
        - `WITHOUT_PARAMS` (default) : uml string description without params
        - `WITH_PARAMS` : uml string description with params

    You can change it with the `setStringMode` class method. This means the
    change will be done for each `PyutMethod` instance.
    """

    # define class flag to avoid PyCharm warning in get/set string mode
    __selectedStringMode = None

    def __init__(self, name="", visibility=PyutVisibilityEnum.PUBLIC, returns=""):
        """
        Constructor.

        @param string name : init the method name
        @since 1.0
        @author Laurent Burgbacher <lb@alawa.ch>
        """
        super().__init__(name)

        self.logger: Logger = getLogger(__name__)

        self._visibility: PyutVisibilityEnum = visibility
        self._modifiers:  PyutModifiers      = cast(PyutModifiers, [])

        self._params     = []
        self._returns    = PyutType(returns)

        prefs = PyutPreferences()
        if prefs["SHOW_PARAMS"] == "1":
            PyutMethod.setStringMode(WITH_PARAMS)
        else:
            PyutMethod.setStringMode(WITHOUT_PARAMS)

    def getString(self):
        """
        Return the string with params in all cases.

        @since 1.9
        @author Laurent Burgbacher <lb@alawa.ch>
        """
        return self.__stringWithParams()

    @classmethod
    def setStringMode(cls, mode):
        """
        Set the mode for __str__.
        """
        if mode == WITH_PARAMS:
            cls.__selectedStringMode = cls.__stringWithParams
        elif mode == WITHOUT_PARAMS:
            cls.__selectedStringMode = cls.__stringWithoutParams

    @classmethod
    def getStringMode(cls):
        """
        Get the mode for __str__.
        """
        if cls.__selectedStringMode is cls.__stringWithParams:
            return WITH_PARAMS
        else:
            return WITHOUT_PARAMS

    def getVisibility(self) -> PyutVisibilityEnum:
        """
        Return the visibility of the method.

        @return PyutVisibility
        """
        return self._visibility

    def setVisibility(self, visibility: PyutVisibilityEnum):
        """
        Set the visibility of the method.
        """
        self._visibility = visibility

    def getModifiers(self) -> PyutModifiers:
        """
        Return a list of the modifiers.
        This is not a copy, but the original one. Any change made to it is
        directly made on the class.

        @since 1.0
        @author Laurent Burgbacher <lb@alawa.ch>
        """
        return self._modifiers

    def setModifiers(self, modifiers: PyutModifiers):
        """
        Replace the actual modifiers by those given in the list.
        The methods passed are not copied, but used directly.

        @since 1.0
        @author Laurent Burgbacher <lb@alawa.ch>
        """
        self._modifiers = modifiers

    def addModifier(self, newModifier: PyutModifier):
        """
        Adds new modifier to current list

        Args:
            newModifier:
                modifier to add to current list
        """
        self._modifiers.append(newModifier)

    def getParams(self):
        """
        Return a list of the params.
        This is not a copy, but the original one. Any change made to it is
        directly made on the class.

        @since 1.0
        @author Laurent Burgbacher <lb@alawa.ch>
        """
        return self._params

    def addParam(self, param):
        """
        Add a param.

        @param PyutParam param : param to add
        @since 1.6
        @author Laurent Burgbacher <lb@alawa.ch>
        """
        self._params.append(param)

    def setParams(self, params):
        """
        Replace the actual params by those given in the list.
        The methods passed are not copied, but used directly.

        @since 1.0
        @author Laurent Burgbacher <lb@alawa.ch>
        """
        self._params = params

    def getReturns(self):
        """
        Return the return type.

        @return PyutType
        @since 1.0
        @author Laurent Burgbacher <lb@alawa.ch>
        """
        return self._returns

    def setReturns(self, returnType: str):
        """
        Set the return type of the method.

        Args:
            returnType:  A string

        """
        if type(returnType) is str:
            pyutType: PyutType = PyutType(returnType)
        else:
            pyutType: PyutType = PyutType('unknown')
        self._returns = pyutType

    def __stringWithoutParams(self):
        """
        String representation without params.

        @since 1.7
        @author Laurent Burgbacher <lb@alawa.ch>
        """
        string = str(self._visibility) + self._name + "()"
        # add the params
        if str(self._returns) != "":
            string += " : " + str(self._returns)
        return string

    def __stringWithParams(self):
        """
        String representation with params.

        @since 1.7
        @author Laurent Burgbacher <lb@alawa.ch>
        """
        string = str(self._visibility) + self._name + "("
        # add the params
        # if self._params == []:
        if not self._params:
            string += "  "  # to compensate the removing [:-2]
        for param in self._params:
            string += str(param) + ", "
        string = string[:-2] + ")"      # remove the last "," and add a )
        if str(self._returns) != "":
            string += " : " + str(self._returns)
        return string

    def __str__(self):
        """
        String representation.
        Select the wanted representation with setStringMode().

        @since 1.0
        @author Laurent Burgbacher <lb@alawa.ch>
        """
        try:
            return self.__selectedStringMode()
        except (ValueError, Exception) as e:
            self.logger.error(f'{e}')
            return ""