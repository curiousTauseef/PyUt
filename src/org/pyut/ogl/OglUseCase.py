
from wx import DC

from org.pyut.ogl.OglObject import OglObject
from org.pyut.model.PyutUseCase import PyutUseCase
from org.pyut.general.LineSplitter import LineSplitter


class OglUseCase(OglObject):
    """
    OGL object that represent an UML use case in use case diagrams.
    This class defines OGL objects that represents a use case for Use
    Cases diagram. You can just instanciate an OGLUseCase and add it to
    the diagram, links, resizing, ... are managed by parent class
    `OglObject`.

    For more instructions about how to create an OGL object, please refer
    to the `OglObject` class.

    :version: $Revision: 1.8 $
    :author: Philippe Waelti
    :contact: pwaelti@eivd.ch
    """
    def __init__(self, pyutUseCase=None, w: float = 100.0, h: float = 60.0):
        """
        Constructor.
        @param  w : Width of the shape
        @param  h : Height of the shape

        @since 1.0
        @author Philippe Waelti <pwaelti@eivd.ch>
        """
        # Init associated PyutObject
        if pyutUseCase is None:
            pyutObject = PyutUseCase()
        else:
            pyutObject = pyutUseCase

        super().__init__(pyutObject, w, h)

        # Should not draw border
        self._drawFrame = False

    def Draw(self, dc: DC, withChildren=False):
        """
        Draw the actor.
        @param dc : Device context
        @param withChildren

        @since 1.0
        @author Philippe Waelti <pwaelti@eivd.ch>
        """
        OglObject.Draw(self, dc, withChildren)
        dc.SetFont(self._defaultFont)

        # Gets the minimum bounding box for the shape
        width, height = self.GetSize()

        # Calculate the top left of the shape
        x, y = self.GetPosition()

        # Draw ellipse
        dc.DrawEllipse(x + 1.0, y + 1.0, width - 2.0, height - 2.0)

        # Draw text
        x += 0.25 * width
        y += 0.25 * height
        textWidth = 0.6 * width             # Text aera width
        space = 1.1 * dc.GetCharHeight()    # Space between lines

        # Drawing is restricted in the specified region of the device
        dc.SetClippingRegion(x, y, textWidth, 0.6 * height)

        # Split lines
        lines = LineSplitter().split(self.getPyutObject().getName(), dc, textWidth)

        # Draw text
        for line in lines:
            dc.DrawText(line, x, y)
            y += space

        dc.DestroyClippingRegion()
