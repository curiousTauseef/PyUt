
from wx import EVT_TEXT
from wx import ID_ANY
from wx import TE_MULTILINE

from wx import CommandEvent
from wx import TextCtrl
from wx import StaticText
from wx import Window

from org.pyut.dialogs.BaseDlgEditText import BaseDlgEditText
from org.pyut.model.PyutNote import PyutNote
from org.pyut.PyutUtils import PyutUtils

from org.pyut.general.Globals import _
[
    TXT_NOTE
] = PyutUtils.assignID(1)


class DlgEditNote(BaseDlgEditText):
    """
    Defines a multi-line text control dialog for note editing.
    This dialog is used to ask the user to enter the text that will be
    displayed in a UML note.

    Sample use:
        dlg = DlgEditNote(self._uml, ID_ANY, pyutNote)
        dlg.Destroy()
    """
    def __init__(self, parent: Window, dialogIdentifier, pyutNote: PyutNote):
        """

        Args:
            parent:             parent window to center on
            dialogIdentifier:   An identifier for the dialog
            pyutNote:           Model object we are editing
        """
        super().__init__(parent, dialogIdentifier, _("Note Edit"))

        self._pyutNote:     PyutNote = pyutNote

        label = StaticText(self, ID_ANY, _("Note text"))

        self._txtCtrl = TextCtrl(self, TXT_NOTE, self._pyutNote.getName(), size=(400, 180), style=TE_MULTILINE)
        self._txtCtrl.SetFocus()

        self._setupMainDialogLayout(self._txtCtrl, label)

        self.Bind(EVT_TEXT, self._onTxtNoteChange, id=TXT_NOTE)

        self.Centre()
        self.ShowModal()

    def _onTxtNoteChange(self, event: CommandEvent):
        """
        Handle when the text in the widget identified by TXT_NOTE change.s

        Args:
            event:
        """
        self._pyutNote.setName(event.GetString())
