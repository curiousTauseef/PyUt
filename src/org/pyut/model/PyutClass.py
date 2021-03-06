
from typing import List
from typing import cast

from org.pyut.model.PyutClassCommon import PyutClassCommon
from org.pyut.model.PyutInterface import PyutInterface
from org.pyut.model.PyutLinkedObject import PyutLinkedObject
from org.pyut.model.PyutStereotype import PyutStereotype
from org.pyut.model.PyutStereotype import getPyutStereotype


class PyutClass(PyutClassCommon, PyutLinkedObject):
    """
    A standard class representation.

    A PyutClass represents a UML class in Pyut. It manages its:
        - object data fields (`PyutField`)
        - methods (`PyutMethod`)
        - parents (`PyutClass`)(classes from which this one inherits)
        - stereotype (`PyutStereotype`)
        - a description (`string`)

    Example::
        myClass = PyutClass("Foo") # this will create a `Foo` class
        myClass.description = "Example class"

        fields = myClass.fields # this is the original fields []
        fields.append(PyutField("bar", "int"))

    """

    def __init__(self, name=""):
        """

        Args:
            name: class name
        """
        PyutLinkedObject.__init__(self, name)
        PyutClassCommon.__init__(self)

        self._stereotype: PyutStereotype = cast (PyutStereotype, None)

        # Display properties
        self._showStereotype: bool = True
        self._showMethods:    bool = True
        self._showFields:     bool = True
        self._interfaces:     List[PyutInterface] = []

    @property
    def interfaces(self) -> List[PyutInterface]:
        return self._interfaces

    @interfaces.setter
    def interfaces(self, theNewInterfaces: List[PyutInterface]):
        self._interfaces = theNewInterfaces

    def addInterface(self, pyutInterface: PyutInterface):
        self._interfaces.append(pyutInterface)

    def getStereotype(self):
        """
        Return the stereotype used, or None if there's no stereotype.

        @since 1.0
        @author Laurent Burgbacher <lb@alawa.ch>
        """
        return self._stereotype

    def setStereotype(self, stereotype):
        """
        Replace the actual stereotype by the one given.

        @param stereotype  String or Unicode or PyutStereotype
        @since 1.0
        @author Laurent Burgbacher <lb@alawa.ch>
        """
        # Python 3 update
        # if type(stereotype) == StringType or type(stereotype) == UnicodeType:
        if type(stereotype) is str:
            stereotype = getPyutStereotype(stereotype)
        self._stereotype = stereotype

    def getShowStereotype(self):
        """
        Return True if we must display the stereotype

        @return boolean indicating if we must display the stereotype
        @since 1.1.1.2
        @author C.Dutoit <dutoitc@hotmail.com>
        """
        return self._showStereotype

    def setShowStereotype(self, theNewValue: bool):
        """
        Define the showStereotype property

        @param theNewValue : boolean indicating if we must display the stereotype
        @since 1.1.1.2
        @author C.Dutoit <dutoitc@hotmail.com>
        """
        self._showStereotype = theNewValue

    def __getstate__(self):
        """
        For deepcopy operations, tells which fields to avoid copying.
        Deepcopy must not copy the links to other classes, or it would result
        in copying all the diagram.

        @since 1.5
        @author Laurent Burgbacher <lb@alawa.ch>
        """
        aDict = self.__dict__.copy()
        aDict["_fathers"]    = []
        return aDict

    def __str__(self):
        """
        String representation.

        @since 1.0
        @author Laurent Burgbacher <lb@alawa.ch>
        """
        return f"Class : {self.getName()}"
