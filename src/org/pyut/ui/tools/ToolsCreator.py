
from typing import Callable
from typing import cast

from logging import Logger
from logging import getLogger

from wx import Bitmap
from wx import EVT_TOOL
from wx import ITEM_CHECK
from wx import ITEM_NORMAL
from wx import NO_BORDER
from wx import TB_FLAT
from wx import TB_HORIZONTAL
from wx import ToolBar
from wx import WindowIDRef
from wx import Frame


from org.pyut.resources.img import ImgToolboxActor
from org.pyut.resources.img import ImgToolboxArrow
from org.pyut.resources.img import ImgToolboxClass
from org.pyut.resources.img import ImgToolboxNewClassDiagram
from org.pyut.resources.img import ImgToolboxNewProject
from org.pyut.resources.img import ImgToolboxNewSequenceDiagram
from org.pyut.resources.img import ImgToolboxNewUseCaseDiagram
from org.pyut.resources.img import ImgToolboxNote
from org.pyut.resources.img import ImgToolboxOpenFile
from org.pyut.resources.img import ImgToolboxRedo
from org.pyut.resources.img import ImgToolboxRelationshipAggregation
from org.pyut.resources.img import ImgToolboxRelationshipAssociation
from org.pyut.resources.img import ImgToolboxRelationshipComposition
from org.pyut.resources.img import ImgToolboxRelationshipInheritance
from org.pyut.resources.img import ImgToolboxRelationshipNote
from org.pyut.resources.img import ImgToolboxRelationshipRealization
from org.pyut.resources.img import ImgToolboxSaveDiagram
from org.pyut.resources.img import ImgToolboxSequenceDiagramInstance
from org.pyut.resources.img import ImgToolboxSequenceDiagramMessage
from org.pyut.resources.img import ImgToolboxSystem
from org.pyut.resources.img import ImgToolboxUndo
from org.pyut.resources.img import ImgToolboxZoomIn
from org.pyut.resources.img import ImgToolboxZoomOut

from org.pyut.general.Mediator import Mediator

from org.pyut.ui.tools.ActionCallbackType import ActionCallbackType
from org.pyut.ui.tools.Tool import Tool
from org.pyut.ui.tools.SharedIdentifiers import SharedIdentifiers
from org.pyut.ui.tools.SharedTypes import SharedTypes

from org.pyut.general.Globals import _


class ToolsCreator:

    def __init__(self, frame: Frame,  callbackMap: SharedTypes.CallbackMap):

        self._containingFrame: Frame = frame
        self._callbackMap:     SharedTypes.CallbackMap = callbackMap

        self.logger: Logger   = getLogger(__name__)
        self._ctrl:  Mediator = Mediator()

    def initTools(self):
        """
        Init all PyUt tools for the toolbar and the toolbox
        """

        # Element tools
        toolArrow = Tool("pyut-arrow", ImgToolboxArrow.embeddedImage.GetBitmap(),
                         _("Arrow"),
                         _("Select tool"),
                         _("PyUt tools"),
                         self._callbackMap[ActionCallbackType.NEW_ACTION],
                         cast(Callable, None), wxID=SharedIdentifiers.ID_ARROW, isToggle=True)

        toolClass = Tool("pyut-class", ImgToolboxClass.embeddedImage.GetBitmap(),
                         _("Class"),
                         _("Create a new class"),
                         _("PyUt tools"),
                         self._callbackMap[ActionCallbackType.NEW_ACTION],
                         cast(Callable, None), wxID=SharedIdentifiers.ID_CLASS, isToggle=True)

        toolActor = Tool("pyut-actor", ImgToolboxActor.embeddedImage.GetBitmap(),
                         _("Actor"),
                         _("Create a new actor"),
                         _("PyUt tools"),
                         self._callbackMap[ActionCallbackType.NEW_ACTION],
                         cast(Callable, None), wxID=SharedIdentifiers.ID_ACTOR, isToggle=True)

        toolUseCase = Tool("pyut-system", ImgToolboxSystem.embeddedImage.GetBitmap(),
                           _("System"),
                           _("Create a new use case"),
                           _("PyUt tools"),
                           self._callbackMap[ActionCallbackType.NEW_ACTION],
                           cast(Callable, None), wxID=SharedIdentifiers.ID_USECASE, isToggle=True)

        toolNote = Tool("pyut-note", ImgToolboxNote.embeddedImage.GetBitmap(),
                        _("Note"),
                        _("Create a new note"),
                        _("PyUt tools"),
                        self._callbackMap[ActionCallbackType.NEW_ACTION],
                        cast(Callable, None), wxID=SharedIdentifiers.ID_NOTE, isToggle=True)

        toolZoomIn = Tool("pyut-zoomIn", ImgToolboxZoomIn.embeddedImage.GetBitmap(),
                          _("Zoom In"),
                          _("Zoom in on the selected area"),
                          _("PyUt tools"),
                          self._callbackMap[ActionCallbackType.NEW_ACTION],
                          cast(Callable, None), wxID=SharedIdentifiers.ID_ZOOM_IN, isToggle=True)

        toolZoomOut = Tool("pyut-zoomOut", ImgToolboxZoomOut.embeddedImage.GetBitmap(),
                           _("Zoom Out"),
                           _("Zoom out from the clicked point"),
                           _("PyUt tools"),
                           self._callbackMap[ActionCallbackType.NEW_ACTION],
                           cast(Callable, None), wxID=SharedIdentifiers.ID_ZOOM_OUT, isToggle=True)

        # Menu tools
        toolNewProject = Tool("pyut-new-project", ImgToolboxNewProject.embeddedImage.GetBitmap(),
                              _("New Project"),
                              _("Create a new project"),
                              _("PyUt menu"),
                              self._callbackMap[ActionCallbackType.NEW_PROJECT],
                              cast(Callable, None), wxID=SharedIdentifiers.ID_MNUFILENEWPROJECT)

        toolNewClassDiagram = Tool("pyut-new-class-diagram", ImgToolboxNewClassDiagram.embeddedImage.GetBitmap(),
                                   _("New Class Diagram"),
                                   _("Create a new class diagram"),
                                   _("PyUt menu"),
                                   self._callbackMap[ActionCallbackType.NEW_CLASS_DIAGRAM],
                                   cast(Callable, None), wxID=SharedIdentifiers.ID_MNU_FILE_NEW_CLASS_DIAGRAM)

        toolNewSequenceDiagram = Tool("pyut-new-sequence-diagram", ImgToolboxNewSequenceDiagram.embeddedImage.GetBitmap(),
                                      _("New Sequence Diagram"),
                                      _("Create a new sequence diagram"),
                                      _("PyUt menu"),
                                      self._callbackMap[ActionCallbackType.NEW_SEQUENCE_DIAGRAM],
                                      cast(Callable, None), wxID=SharedIdentifiers.ID_MNU_FILE_NEW_SEQUENCE_DIAGRAM)

        toolNewUseCaseDiagram = Tool("pyut-new-use-case-diagram", ImgToolboxNewUseCaseDiagram.embeddedImage.GetBitmap(),
                                     _("New Use-Case diagram"),
                                     _("Create a new use-case diagram"),
                                     _("PyUt menu"),
                                     self._callbackMap[ActionCallbackType.NEW_USE_CASE_DIAGRAM],
                                     cast(Callable, None), wxID=SharedIdentifiers.ID_MNU_FILE_NEW_USECASE_DIAGRAM)

        toolOpen = Tool("pyut-open", ImgToolboxOpenFile.embeddedImage.GetBitmap(),
                        _("Open"),
                        _("Open a file"),
                        _("PyUt menu"),
                        self._callbackMap[ActionCallbackType.FILE_OPEN],
                        cast(Callable, None), wxID=SharedIdentifiers.ID_MNU_FILE_OPEN)

        toolSave = Tool("pyut-save", ImgToolboxSaveDiagram.embeddedImage.GetBitmap(),
                        _("Save"),
                        _("Save current UML Diagram"),
                        _("PyUt menu"),
                        (lambda x: self._callbackMap[ActionCallbackType.FILE_SAVE]),
                        cast(Callable, None), wxID=SharedIdentifiers.ID_MNU_FILE_SAVE)

        toolUndo = Tool("pyut-undo", ImgToolboxUndo.embeddedImage.GetBitmap(),
                        _("undo"),
                        _("undo the last performed action"),
                        _("PyUt menu"),
                        self._callbackMap[ActionCallbackType.UNDO],
                        cast(Callable, None), wxID=SharedIdentifiers.ID_MNU_UNDO)

        toolRedo = Tool("pyut-redo", ImgToolboxRedo.embeddedImage.GetBitmap(),
                        _("redo"),
                        _("redo the last undone action"),
                        _("PyUt menu"),
                        self._callbackMap[ActionCallbackType.REDO],
                        cast(Callable, None), wxID=SharedIdentifiers.ID_MNU_REDO)

        # Relationship tools
        toolRelInheritance = Tool("pyut-rel-inheritance", ImgToolboxRelationshipInheritance.embeddedImage.GetBitmap(),
                                  _("New inheritance relation"),
                                  _("New inheritance relation"),
                                  _("PyUt tools"),
                                  self._callbackMap[ActionCallbackType.NEW_ACTION],
                                  cast(Callable, None), wxID=SharedIdentifiers.ID_REL_INHERITANCE, isToggle=True)

        toolRelRealisation = Tool("pyut-rel-realization", ImgToolboxRelationshipRealization.embeddedImage.GetBitmap(),
                                  _("New Realization relation"),
                                  _("New Realization relation"),
                                  _("PyUt tools"),
                                  self._callbackMap[ActionCallbackType.NEW_ACTION],
                                  cast(Callable, None), wxID=SharedIdentifiers.ID_REL_REALISATION, isToggle=True)

        toolRelComposition = Tool("pyut-rel-composition", ImgToolboxRelationshipComposition.embeddedImage.GetBitmap(),
                                  _("New composition relation"),
                                  _("New composition relation"),
                                  _("PyUt tools"),
                                  self._callbackMap[ActionCallbackType.NEW_ACTION],
                                  cast(Callable, None), wxID=SharedIdentifiers.ID_REL_COMPOSITION, isToggle=True)

        toolRelAggregation = Tool("pyut-rel-aggregation", ImgToolboxRelationshipAggregation.embeddedImage.GetBitmap(),
                                  _("New aggregation relation"),
                                  _("New aggregation relation"),
                                  _("PyUt tools"),
                                  self._callbackMap[ActionCallbackType.NEW_ACTION],
                                  cast(Callable, None), wxID=SharedIdentifiers.ID_REL_AGGREGATION, isToggle=True)

        toolRelAssociation = Tool("pyut-rel-association", ImgToolboxRelationshipAssociation.embeddedImage.GetBitmap(),
                                  _("New association relation"),
                                  _("New association relation"),
                                  _("PyUt tools"),
                                  self._callbackMap[ActionCallbackType.NEW_ACTION],
                                  cast(Callable, None), wxID=SharedIdentifiers.ID_REL_ASSOCIATION, isToggle=True)

        toolRelNote = Tool("pyut-rel-note", ImgToolboxRelationshipNote.embeddedImage.GetBitmap(),
                           _("New note relation"),
                           _("New note relation"),
                           _("PyUt tools"),
                           self._callbackMap[ActionCallbackType.NEW_ACTION],
                           cast(Callable, None), wxID=SharedIdentifiers.ID_REL_NOTE, isToggle=True)

        toolSDInstance = Tool("pyut-sd-instance", ImgToolboxSequenceDiagramInstance.embeddedImage.GetBitmap(),
                              _("New sequence diagram instance object"),
                              _("New sequence diagram instance object"),
                              _("PyUt tools"),
                              self._callbackMap[ActionCallbackType.NEW_ACTION],
                              cast(Callable, None), wxID=SharedIdentifiers.ID_SD_INSTANCE, isToggle=True)

        toolSDMessage = Tool("pyut-sd-message", ImgToolboxSequenceDiagramMessage.embeddedImage.GetBitmap(),
                             _("New sequence diagram message object"),
                             _("New sequence diagram message object"),
                             _("PyUt tools"),
                             self._callbackMap[ActionCallbackType.NEW_ACTION],
                             cast(Callable, None), wxID=SharedIdentifiers.ID_SD_MESSAGE, isToggle=True)

        self.logger.debug(f'toolSDMessage: {toolSDMessage}')

        # Create toolboxes
        for tool in [toolNewProject, toolNewClassDiagram, toolNewSequenceDiagram,
                     toolNewUseCaseDiagram, toolOpen, toolSave,
                     toolArrow, toolZoomIn, toolZoomOut, toolUndo, toolRedo,
                     toolClass, toolActor, toolUseCase, toolNote,
                     toolRelInheritance, toolRelRealisation, toolRelComposition,
                     toolRelAggregation, toolRelAssociation, toolRelNote,
                     toolSDInstance, toolSDMessage
                     ]:
            self._ctrl.registerTool(tool)

        # Create toolbar

        self._tb: ToolBar = self._containingFrame.CreateToolBar(TB_HORIZONTAL | NO_BORDER | TB_FLAT)
        self._containingFrame.SetToolBar(self._tb)

        for tool in [toolNewProject, toolNewClassDiagram, toolNewSequenceDiagram,
                     toolNewUseCaseDiagram, toolOpen, toolSave, None,
                     toolArrow, toolZoomIn, toolZoomOut, toolUndo, toolRedo, None,
                     toolClass, toolActor, toolUseCase, toolNote, None,
                     toolRelInheritance, toolRelRealisation, toolRelComposition,
                     toolRelAggregation, toolRelAssociation, toolRelNote, None,
                     toolSDInstance, toolSDMessage
                     ]:

            if tool is not None:
                toolId:    WindowIDRef = tool.wxID
                bitMap:    Bitmap      = tool.img
                caption:   str         = tool.caption
                isToggle:  bool        = tool.isToggle
                if isToggle is True:
                    itemKind = ITEM_CHECK
                else:
                    itemKind = ITEM_NORMAL
                """
                AddTool(toolId, label, bitmap, shortHelp=EmptyString, kind=ITEM_NORMAL) -> ToolBarToolBase
                """
                self._tb.AddTool(toolId, '', bitMap, caption, itemKind)     # TODO hasii -- do we need a label

                self._containingFrame.Bind(EVT_TOOL, tool.actionCallback, id=tool.wxID)
            else:
                self._tb.AddSeparator()

        self._tb.Realize()

        self._ctrl.registerToolBar(self._tb)
        self._ctrl.registerToolBarTools([
            SharedIdentifiers.ID_ARROW,
            SharedIdentifiers.ID_CLASS,
            SharedIdentifiers.ID_NOTE,
            SharedIdentifiers.ID_REL_INHERITANCE, SharedIdentifiers.ID_REL_REALISATION,
            SharedIdentifiers.ID_REL_COMPOSITION, SharedIdentifiers.ID_REL_AGGREGATION, SharedIdentifiers.ID_REL_ASSOCIATION,
            SharedIdentifiers.ID_REL_NOTE, SharedIdentifiers.ID_ACTOR,
            SharedIdentifiers.ID_USECASE,
            SharedIdentifiers.ID_SD_INSTANCE, SharedIdentifiers.ID_SD_MESSAGE,
            SharedIdentifiers.ID_ZOOM_IN, SharedIdentifiers.ID_ZOOM_OUT
        ])
