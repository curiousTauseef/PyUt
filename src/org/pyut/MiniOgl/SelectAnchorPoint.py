
from wx import MouseEvent
from wx import RED_PEN

from org.pyut.MiniOgl.AnchorPoint import AnchorPoint
from org.pyut.MiniOgl.Shape import Shape
from org.pyut.MiniOgl.ShapeEventHandler import ShapeEventHandler
from org.pyut.enums.AttachmentPoint import AttachmentPoint


class SelectAnchorPoint(AnchorPoint, ShapeEventHandler):

    """
    This is a point attached to a shape to indicate where to click;  Presumably, to indicate where
    to attach something

    """
    def __init__(self, x: float, y: float, attachmentPoint: AttachmentPoint, parent: Shape = None):
        """

        Args:
            x: x position of the point
            y: y position of the point
            parent:
        """
        super().__init__(x, y, parent)
        self._attachmentPoint: AttachmentPoint = attachmentPoint

    @property
    def attachmentPoint(self) -> AttachmentPoint:
        return self._attachmentPoint

    @attachmentPoint.setter
    def attachmentPoint(self, newValue: AttachmentPoint):
        self._attachmentPoint = newValue

    def Draw(self, dc, withChildren=True):

        dc.SetPen(RED_PEN)
        super().Draw(dc, withChildren)

    def OnLeftDown(self, event: MouseEvent):
        """
        Callback for left clicks.

        Args:
            event: The mouse event
        """

        from org.pyut.general.Mediator import getMediator   # avoid circular import

        print(f'SelectAnchorPoint: {self._attachmentPoint}')

        getMediator().createLollipopInterface(implementor=self.GetParent(), attachmentAnchor=self)
