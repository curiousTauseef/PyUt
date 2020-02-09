
from typing import cast
from typing import Dict
from typing import List
from typing import Union
from typing import NewType

from logging import Logger
from logging import getLogger

from xml.dom.minidom import Element
from xml.dom.minidom import NodeList

from org.pyut.MiniOgl.ControlPoint import ControlPoint
from org.pyut.MiniOgl.TextShape import TextShape

from org.pyut.PyutClass import PyutClass
from org.pyut.PyutField import PyutField
from org.pyut.PyutLink import PyutLink
from org.pyut.PyutMethod import PyutMethod
from org.pyut.PyutNote import PyutNote
from org.pyut.PyutParam import PyutParam
from org.pyut.PyutUtils import PyutUtils
from org.pyut.PyutVisibilityEnum import PyutVisibilityEnum

from org.pyut.enums.OglLinkType import OglLinkType

from org.pyut.ogl.OglClass import OglClass
from org.pyut.ogl.OglAssociation import OglAssociation
from org.pyut.ogl.OglAssociation import CENTER
from org.pyut.ogl.OglAssociation import DEST_CARD
from org.pyut.ogl.OglAssociation import SRC_CARD
from org.pyut.ogl.OglLink import OglLink
from org.pyut.ogl.OglNote import OglNote
from org.pyut.ogl.OglObject import OglObject

from org.pyut.ogl.sd.OglSDInstance import OglSDInstance

from org.pyut.PyutStereotype import getPyutStereotype
from org.pyut.ogl.OglLinkFactory import getOglLinkFactory

OglObjects    = NewType('OglObjects',    Dict[int, OglObject])
OglClasses    = NewType('OglClasses',    Dict[int, OglClass])
OglNotes      = NewType('OglNotes',      Dict[int, OglNote])
PyutMethods   = NewType('PyutMethods',   List[PyutMethod])
PyutFields    = NewType('PyutFields',    List[PyutField])
ControlPoints = NewType('ControlPoints', List[ControlPoint])
Links         = NewType('Links',         Union[OglLink, OglSDInstance])
OglLinks      = NewType('OglLinks',      List[Links])


class ToOgl:
    """
    The refactored version of this does NO UI related actions;  It is up to the
    caller to actually place the visual OGL object on the diagram frame

    """
    def __init__(self):

        self.logger: Logger = getLogger(__name__)

    def getOglClasses(self, xmlOglClasses: NodeList) -> OglClasses:
        """
        Loads to OGL objects
        Parse the XML elements given and build data model for the Pyut classes.

        Args:
            xmlOglClasses:   XML 'GraphicClass' elements

        Returns:
                The built dictionary uses an ID for the key and an OglClass for the value
        """
        oglObjects: OglClasses = cast(OglClasses, {})

        for xmlOglClass in xmlOglClasses:

            xmlOglClass: Element   = cast(Element, xmlOglClass)
            pyutClass:   PyutClass = PyutClass()

            height: float      = float(xmlOglClass.getAttribute('height'))
            width:  float      = float(xmlOglClass.getAttribute('width'))
            oglClass: OglClass = OglClass(pyutClass, width, height)

            xmlClass: Element = xmlOglClass.getElementsByTagName('Class')[0]

            pyutClass.setId(int(xmlClass.getAttribute('id')))
            pyutClass.setName(xmlClass.getAttribute('name'))
            pyutClass.setDescription(xmlClass.getAttribute('description'))
            if xmlClass.hasAttribute('stereotype'):
                pyutClass.setStereotype(getPyutStereotype(xmlClass.getAttribute('stereotype')))

            # adding display properties (cd)
            value = PyutUtils.secureBoolean(xmlClass.getAttribute('showStereotype'))
            pyutClass.setShowStereotype(value)
            value = PyutUtils.secureBoolean(xmlClass.getAttribute('showMethods'))
            pyutClass.setShowMethods(value)
            value = PyutUtils.secureBoolean(xmlClass.getAttribute('showFields'))
            pyutClass.setShowFields(value)

            pyutClass.setFilename(xmlClass.getAttribute('filename'))

            pyutClass.setMethods(self._getMethods(xmlClass))
            pyutClass.setFields(self._getFields(xmlClass))

            # Adding properties necessary to place shape on a diagram frame
            x = float(xmlOglClass.getAttribute('x'))
            y = float(xmlOglClass.getAttribute('y'))

            oglClass.SetPosition(x, y)

            oglObjects[pyutClass.getId()] = oglClass

        return oglObjects

    def getOglLinks(self, xmlOglLinks: NodeList, oglClasses: OglObjects) -> OglLinks:
        """
        Extract the link for the OglClasses

        Args:
            xmlOglLinks:    A DOM node list of links
            oglClasses:  The OglClasses

        Returns:
            The OglLinks list
        """
        oglLinks: OglLinks = cast(OglLinks, [])

        for xmlLink in xmlOglLinks:
            # src and dst anchor position
            xmlLink: Element = cast(Element, xmlLink)

            sx = PyutUtils.secureFloat(xmlLink.getAttribute("srcX"))
            sy = PyutUtils.secureFloat(xmlLink.getAttribute("srcY"))
            dx = PyutUtils.secureFloat(xmlLink.getAttribute("dstX"))
            dy = PyutUtils.secureFloat(xmlLink.getAttribute("dstY"))

            spline = PyutUtils.secureSplineInt(xmlLink.getAttribute("spline"))

            # get the associated PyutLink
            srcId, dstId, assocPyutLink = self._getPyutLink(xmlLink)

            src: OglClass         = oglClasses[srcId]
            dst: OglClass         = oglClasses[dstId]
            linkType: OglLinkType = assocPyutLink.getType()
            pyutLink: PyutLink = PyutLink(name=assocPyutLink.getName(),
                                          linkType=linkType,
                                          cardSrc=assocPyutLink.sourceCardinality,
                                          cardDest=assocPyutLink.destinationCardinality,
                                          source=src.getPyutObject(), destination=dst.getPyutObject())

            oglLinkFactory = getOglLinkFactory()
            oglLink = oglLinkFactory.getOglLink(src, pyutLink, dst, linkType)
            src.addLink(oglLink)
            dst.addLink(oglLink)
            # umlFrame.GetDiagram().AddShape(oglLink, withModelUpdate=False)
            oglLinks.append(oglLink)

            oglLink.SetSpline(spline)

            # put the anchors at the right position
            srcAnchor = oglLink.GetSource()
            dstAnchor = oglLink.GetDestination()
            srcAnchor.SetPosition(sx, sy)
            dstAnchor.SetPosition(dx, dy)

            # add the control points to the line
            line = srcAnchor.GetLines()[0]  # only 1 line per anchor in pyut
            parent = line.GetSource().GetParent()
            selfLink = parent is line.GetDestination().GetParent()

            ctrlpts: ControlPoints = self._generateControlPoints(xmlLink)
            for ctrl in ctrlpts:
                line.AddControl(ctrl)
                if selfLink:
                    x, y = ctrl.GetPosition()
                    ctrl.SetParent(parent)
                    ctrl.SetPosition(x, y)

            if isinstance(oglLink, OglAssociation):
                self.__furtherCustomizeAssociationLink(xmlLink, oglLink)

        return oglLinks

    def getOglNotes(self, xmlOglNotes, umlFrame) -> OglNotes:
        """
        Parse the XML elements given and build data layer for PyUt notes.

        Args:
            xmlOglNotes:        XML 'GraphicNote' elements
            umlFrame:           Where to draw

        Returns:
            The returned dictionary uses a generated ID for the key
        """
        oglNotes: OglNotes = cast(OglNotes, {})
        for xmlOglNote in xmlOglNotes:

            pyutNote: PyutNote = PyutNote()

            # Building OGL Note
            height: float = float(xmlOglNote.getAttribute('height'))
            width:  float = float(xmlOglNote.getAttribute('width'))
            oglNote = OglNote(pyutNote, width, height)

            xmlNote: Element = xmlOglNote.getElementsByTagName('Note')[0]

            pyutNote.setId(int(xmlNote.getAttribute('id')))

            name = xmlNote.getAttribute('name')
            name = name.replace("\\\\\\\\", "\n")

            pyutNote.setName(name)

            pyutNote.setFilename(xmlNote.getAttribute('filename'))

            # Adding properties necessary to place shape on a diagram frame
            x: float = float(xmlOglNote.getAttribute('x'))
            y: float = float(xmlOglNote.getAttribute('y'))

            oglNote.SetPosition(x, y)
            # Update the dictionary
            oglNotes[pyutNote.getId()] = oglNote

        return oglNotes

    def _getMethods(self, xmlClass: Element) -> PyutMethods:
        """
        Converts XML methods to `PyutMethod`s
        Args:
            xmlClass:  A DOM element that is a UML Class

        Returns:
            A list of `PyutMethod`s associated with the class
        """
        allMethods: PyutMethods = cast(PyutMethods, [])
        for xmlMethod in xmlClass.getElementsByTagName("Method"):

            pyutMethod: PyutMethod = PyutMethod(xmlMethod.getAttribute('name'))

            strVis: str = xmlMethod.getAttribute('visibility')
            vis: PyutVisibilityEnum = PyutVisibilityEnum(strVis)
            pyutMethod.setVisibility(visibility=vis)

            returnElt: Element = xmlMethod.getElementsByTagName("Return")[0]
            pyutMethod.setReturns(returnElt.getAttribute('type'))

            methodParameters = []
            for xmlParam in xmlMethod.getElementsByTagName("Param"):
                methodParameters.append(self._getParam(xmlParam))

            pyutMethod.setParams(methodParameters)

            allMethods.append(pyutMethod)

        return allMethods

    def _getParam(self, domElement: Element) -> PyutParam:
        """

        Args:
            domElement:  The xml element tht is a paremeter

        Returns:
            A parameter model object
        """
        pyutParam: PyutParam = PyutParam(name=domElement.getAttribute('name'), theParameterType=domElement.getAttribute('type'))

        if domElement.hasAttribute('defaultValue'):
            pyutParam.setDefaultValue(domElement.getAttribute('defaultValue'))

        return pyutParam

    def _getFields(self, xmlClass: Element) -> PyutFields:
        """
        Extracts fields from a DOM element that represents a UML class

        Args:
            xmlClass:
                The DOM version of a UML class

        Returns:
            PyutFields
        """
        pyutFields: PyutFields = cast(PyutFields, [])

        for xmlField in xmlClass.getElementsByTagName("Field"):

            xmlField:   Element  = cast(Element, xmlField)
            pyutField: PyutField = PyutField()

            pyutField.setVisibility(xmlField.getAttribute('visibility'))
            xmlParam: Element = xmlField.getElementsByTagName("Param")[0]

            if xmlParam.hasAttribute('defaultValue'):
                pyutField.setDefaultValue(xmlParam.getAttribute('defaultValue'))
            pyutField.setName(xmlParam.getAttribute('name'))
            pyutField.setType(xmlParam.getAttribute('type'))

            pyutFields.append(pyutField)

        return pyutFields

    def _generateControlPoints(self, link: Element) -> ControlPoints:

        ctrlpts: ControlPoints = cast(ControlPoints, [])

        for ctrlpt in link.getElementsByTagName("ControlPoint"):
            x = PyutUtils.secureFloat(ctrlpt.getAttribute("x"))
            y = PyutUtils.secureFloat(ctrlpt.getAttribute("y"))
            ctrlpts.append(ControlPoint(x, y))

        return ctrlpts

    def _getPyutLink(self, obj: Element):
        """

        Args:
            obj:  The GraphicLink DOM element

        Returns:
            A tuple of a source ID, destination ID, and a PyutLink object
        """
        link: Element = obj.getElementsByTagName("Link")[0]

        pyutLink: PyutLink = PyutLink()

        pyutLink.setBidir(bool(link.getAttribute('bidir')))

        pyutLink.destinationCardinality = link.getAttribute('cardDestination')
        pyutLink.sourceCardinality      = link.getAttribute('cardSrc')

        pyutLink.setName(link.getAttribute('name'))

        strLinkType: str         = link.getAttribute('type')
        linkType:    OglLinkType = OglLinkType[strLinkType]
        pyutLink.setType(linkType)

        # source and destination will be reconstructed by _getOglLinks
        sourceId = int(link.getAttribute('sourceId'))
        destId   = int(link.getAttribute('destId'))

        return sourceId, destId, pyutLink

    def __furtherCustomizeAssociationLink(self, xmlLink: Element, oglLink: OglAssociation):
        """
        Customize the visual aspects of an Association link
        Args:
            xmlLink:
            oglLink:
        """
        center: TextShape = oglLink.getLabels()[CENTER]
        src:    TextShape = oglLink.getLabels()[SRC_CARD]
        dst:    TextShape = oglLink.getLabels()[DEST_CARD]

        self.__setAssociationLabelPosition(xmlLink, 'LabelCenter', center)
        self.__setAssociationLabelPosition(xmlLink, 'LabelSrc',    src)
        self.__setAssociationLabelPosition(xmlLink, 'LabelDst',    dst)

    def __setAssociationLabelPosition(self, xmlLink: Element, tagName: str, textShape: TextShape):
        """

        Args:
            xmlLink:
            tagName:
            textShape:
        """
        label:  Element   = xmlLink.getElementsByTagName(tagName)[0]
        x = float(label.getAttribute("x"))
        y = float(label.getAttribute("y"))

        self.logger.debug(f'tagName: {tagName} textShape.text: `{textShape.GetText()}`  pos: ({x:.2f},{y:.2f})')

        textShape.SetPosition(x, y)
