
from typing import cast

from logging import Logger
from logging import getLogger

from wx import ALIGN_CENTER
from wx import ALIGN_CENTER_HORIZONTAL
from wx import ALIGN_RIGHT
from wx import ALL
from wx import EVT_BUTTON
from wx import EVT_LISTBOX
from wx import EVT_LISTBOX_DCLICK
from wx import EXPAND
from wx import HORIZONTAL
from wx import ICON_ERROR
from wx import ID_ANY
from wx import OK
from wx import VERTICAL
from wx import LB_SINGLE

from wx import Dialog
from wx import ListBox
from wx import MessageDialog
from wx import TextCtrl
from wx import Button
from wx import BoxSizer
from wx import CheckBox
from wx import StaticText
from wx import CommandEvent


from org.pyut.model.PyutClass import PyutClass
from org.pyut.model.PyutField import PyutField

from org.pyut.model.PyutParam import PyutParam
from org.pyut.model.PyutStereotype import getPyutStereotype

from org.pyut.dialogs.DlgEditClassCommon import DlgEditClassCommon
from org.pyut.dialogs.DlgEditField import DlgEditField

from org.pyut.general.Globals import _
from org.pyut.PyutUtils import PyutUtils

# Assign constants
[
    ID_TXT_STEREO_TYPE,
    ID_BTN_FIELD_ADD, ID_BTN_FIELD_EDIT, ID_BTN_FIELD_REMOVE,
    ID_BTN_FIELD_UP, ID_BTN_FIELD_DOWN, ID_LST_FIELD_LIST,
   ] = PyutUtils.assignID(7)


class DlgEditClass(DlgEditClassCommon):
    """
    Dialog for the class edits.

    Creating a DlgEditClass object will automatically open a dialog for class
    editing. The PyutClass given in the constructor parameters will be used to fill the
    fields of the dialog, and will be updated when the OK button is clicked.

    Dialogs for methods and fields editing are implemented in different classes and
    created when invoking the _callDlgEditMethod and _callDlgEditField methods.

    Because dialog works on a copy of the PyutClass object, if you cancel the
    dialog any modifications are lost.

    Examples of `DlgEditClass` use are in  `Mediator.py`
    """
    def __init__(self, parent, windowId, pyutClass: PyutClass):
        """

        Args:
            parent:         dialog parent
            windowId:       dialog identity
            pyutClass:      Class modified by dialog
        """
        super().__init__(parent=parent, windowId=windowId, dlgTitle=_("Class Edit"), pyutModel=pyutClass)

        self.logger:         Logger = getLogger(__name__)
        lblStereotype:       StaticText = StaticText (self, -1, _("Stereotype"))
        self._txtStereotype: TextCtrl = TextCtrl(self, ID_TXT_STEREO_TYPE, "", size=(125, -1))

        self._szrNameStereotype.Add(lblStereotype, 0, ALL, 5)
        self._szrNameStereotype.Add(self._txtStereotype, 1, ALIGN_CENTER)

        # Label Fields
        lblField = StaticText (self, -1, _("Fields :"))

        # ListBox List
        self._lstFieldList = ListBox(self, ID_LST_FIELD_LIST, choices=[], style=LB_SINGLE)
        self.Bind(EVT_LISTBOX, self._evtFieldList, id=ID_LST_FIELD_LIST)
        self.Bind(EVT_LISTBOX_DCLICK, self._evtFieldListDClick, id=ID_LST_FIELD_LIST)

        # Button Add
        self._btnFieldAdd = Button(self, ID_BTN_FIELD_ADD, _("&Add"))
        self.Bind(EVT_BUTTON, self._onFieldAdd, id=ID_BTN_FIELD_ADD)

        # Button Edit
        self._btnFieldEdit = Button(self, ID_BTN_FIELD_EDIT, _("&Edit"))
        self.Bind(EVT_BUTTON, self._onFieldEdit, id=ID_BTN_FIELD_EDIT)

        # Button Remove
        self._btnFieldRemove = Button(self, ID_BTN_FIELD_REMOVE, _("&Remove"))
        self.Bind(EVT_BUTTON, self._onFieldRemove, id=ID_BTN_FIELD_REMOVE)

        # Button Up
        self._btnFieldUp = Button(self, ID_BTN_FIELD_UP, _("&Up"))
        self.Bind(EVT_BUTTON, self._onFieldUp, id=ID_BTN_FIELD_UP)

        # Button Down
        self._btnFieldDown = Button(self, ID_BTN_FIELD_DOWN, _("&Down"))
        self.Bind(EVT_BUTTON, self._onFieldDown, id=ID_BTN_FIELD_DOWN)

        # Sizer for Fields buttons
        szrFieldButtons = BoxSizer (HORIZONTAL)
        szrFieldButtons.Add(self._btnFieldAdd, 0, ALL, 5)
        szrFieldButtons.Add(self._btnFieldEdit, 0, ALL, 5)
        szrFieldButtons.Add(self._btnFieldRemove, 0, ALL, 5)
        szrFieldButtons.Add(self._btnFieldUp, 0, ALL, 5)
        szrFieldButtons.Add(self._btnFieldDown, 0, ALL, 5)

        szrMethodButtons: BoxSizer = self._createMethodsUIArtifacts()
        # Show stereotype checkbox
        self._chkShowStereotype = CheckBox(self, -1, _("Show stereotype"))

        # Show fields checkbox
        self._chkShowFields = CheckBox(self, -1, _("Show fields"))

        # Show methods checkbox
        self._chkShowMethods = CheckBox(self, -1, _("Show methods"))

        # Sizer for display properties
        szrDisplayProperties = BoxSizer (VERTICAL)
        szrDisplayProperties.Add(self._chkShowStereotype, 0, ALL, 5)
        szrDisplayProperties.Add(self._chkShowFields,    0, ALL, 5)
        szrDisplayProperties.Add(self._chkShowMethods,   0, ALL, 5)

        self._szrMain.Add(lblField, 0, ALL, 5)
        self._szrMain.Add(self._lstFieldList, 1, ALL | EXPAND, 5)
        self._szrMain.Add(szrFieldButtons, 0, ALL | ALIGN_CENTER_HORIZONTAL, 5)

        self._szrMain.Add(self._lblMethod, 0, ALL, 5)
        self._szrMain.Add(self._lstMethodList, 1, ALL | EXPAND, 5)
        self._szrMain.Add(szrMethodButtons, 0, ALL | ALIGN_CENTER_HORIZONTAL, 5)

        self._szrMain.Add(szrDisplayProperties, 0, ALL | ALIGN_CENTER_HORIZONTAL, 5)
        self._szrMain.Add(self._szrButtons, 0, ALL | ALIGN_RIGHT, 5)     # wxPython 4.1.0 Vertical alignment flags are ignored in vertical sizers

        # Fill the txt control with class data
        self._fillAllControls()

        # Fix buttons (enable or not)
        self._fixBtnFields()
        self._fixBtnMethod()

        # Set the focus and selection
        self._txtName.SetFocus()
        self._txtName.SetSelection(0, len(self._txtName.GetValue()))

        # Help Pycharm
        self._dlgMethod = cast(Dialog, None)
        self._szrMain.Fit(self)     # subclasses need to do this

        self.Centre()
        self.ShowModal()

    def _callDlgEditField(self, field: PyutField) -> int:
        """
                Dialog for Field editing

        Args:
            field:  Field to be edited

        Returns: return code from dialog
        """
        self._dlgField = DlgEditField(theParent=self, theWindowId=ID_ANY, fieldToEdit=field, theMediator=self._mediator)
        return self._dlgField.ShowModal()

    def _dupParams(self, params):
        """
        Duplicate a list of params, all params are duplicated too.

        @since 1.9
        @author N. Dubois <n_dub@altavista.com>
        """
        dupParams = []
        for i in params:
            param: PyutParam = PyutParam(name=i.getName(), theParameterType=i.getType(), defaultValue=i.getDefaultValue())
            dupParams.append(param)
        return dupParams

    def _fillAllControls(self):
        """
        Fill all controls with _pyutModelCopy data.

        """
        # Fill Class name
        self._txtName.SetValue(self._pyutModelCopy.getName())

        # Fill Stereotype
        stereotype = self._pyutModelCopy.getStereotype()
        if stereotype is None:
            strStereotype = ""
        else:
            strStereotype = stereotype.getName()
        self._txtStereotype.SetValue(strStereotype)

        # Fill the list controls
        try:
            for el in self._pyutModelCopy.fields:
                self.logger.debug(f'field: {el}')
                self._lstFieldList.Append(str(el))

            self._fillMethodList()
        except (ValueError, Exception) as e:

            eMsg: str = _(f"Error: {e}")
            dlg = MessageDialog(self, eMsg, OK | ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

        # Fill display properties
        self._chkShowFields.SetValue(self._pyutModelCopy.showFields)
        self._chkShowMethods.SetValue(self._pyutModelCopy.showMethods)
        self._chkShowStereotype.SetValue(self._pyutModelCopy.getShowStereotype())

    def _fixBtnFields(self):
        """
        Fix buttons of fields list (enable or not).
        """
        selection = self._lstFieldList.GetSelection()
        # Button Edit and Remove
        ans = selection != -1
        self._btnFieldEdit.Enable(ans)
        self._btnFieldRemove.Enable(ans)
        self._btnFieldUp.Enable(selection > 0)
        self._btnFieldDown.Enable(ans and selection < self._lstFieldList.GetCount() - 1)

    # noinspection PyUnusedLocal
    def _onFieldAdd(self, event: CommandEvent):
        """
        Add a new field in the list.

        Args:
            event:
        """
        field = PyutField()
        ret = self._callDlgEditField(field)
        if ret == OK:
            self._pyutModelCopy.fields.append(field)
            # Add fields in dialog list
            self._lstFieldList.Append(str(field))

            # Tell window that its data has been modified
            fileHandling = self._mediator.getFileHandling()
            project = fileHandling.getCurrentProject()
            if project is not None:
                project.setModified()

    # noinspection PyUnusedLocal
    def _onFieldEdit(self, event: CommandEvent):
        """
        Edit a field.
        """
        selection = self._lstFieldList.GetSelection()
        field = self._pyutModelCopy.fields[selection]
        ret = self._callDlgEditField(field)
        if ret == OK:
            # Modify field in dialog list
            self._lstFieldList.SetString(selection, str(field))
            # Tell window that its data has been modified
            fileHandling = self._mediator.getFileHandling()
            project = fileHandling.getCurrentProject()
            if project is not None:
                project.setModified()

    # noinspection PyUnusedLocal
    def _onFieldRemove(self, event: CommandEvent):
        """
        Remove a field from the list.
        """
        # Remove from list control
        selection = self._lstFieldList.GetSelection()
        self._lstFieldList.Delete(selection)

        # Select next
        if self._lstFieldList.GetCount() > 0:
            index = min(selection, self._lstFieldList.GetCount()-1)
            self._lstFieldList.SetSelection(index)

        # Remove from _pyutModelCopy
        fields = self._pyutModelCopy.fields
        fields.pop(selection)

        # Fix buttons of fields list (enable or not)
        self._fixBtnFields()

        # Tell window that its data has been modified
        fileHandling = self._mediator.getFileHandling()
        project = fileHandling.getCurrentProject()
        if project is not None:
            project.setModified()

    # noinspection PyUnusedLocal
    def _onFieldUp(self, event: CommandEvent):
        """
        Move up a field in the list.
        """
        # Move up the field in _pyutModelCopy
        selection = self._lstFieldList.GetSelection()
        fields = self._pyutModelCopy.fields
        field = fields[selection]
        fields.pop(selection)
        fields.insert(selection - 1, field)

        # Move up the field in dialog list
        self._lstFieldList.SetString(selection, str(fields[selection]))
        self._lstFieldList.SetString(selection - 1, str(fields[selection - 1]))
        self._lstFieldList.SetSelection(selection - 1)

        # Fix buttons (enable or not)
        self._fixBtnFields()

        # Tell window that its data has been modified
        fileHandling = self._mediator.getFileHandling()
        project = fileHandling.getCurrentProject()
        if project is not None:
            project.setModified()

    # noinspection PyUnusedLocal
    def _onFieldDown(self, event: CommandEvent):
        """
        Move down a field in the list.
        """
        selection = self._lstFieldList.GetSelection()
        fields = self._pyutModelCopy.fields
        field = fields[selection]
        fields.pop(selection)
        fields.insert(selection + 1, field)

        # Move down the field in dialog list
        self._lstFieldList.SetString(selection, str(fields[selection]))
        self._lstFieldList.SetString(selection + 1, str(fields[selection + 1]))
        self._lstFieldList.SetSelection(selection + 1)

        # Fix buttons (enable or not)
        self._fixBtnFields()

        # Tell window that its data has been modified
        fileHandling = self._mediator.getFileHandling()
        project = fileHandling.getCurrentProject()
        if project is not None:
            project.setModified()

    # noinspection PyUnusedLocal
    def _evtFieldList(self, event):
        """
        Called when click on Fields list.
        """
        self._fixBtnFields()

    def _evtFieldListDClick(self, event: CommandEvent):
        """
        Called when there is a double-click on Fields list.
        """
        self._onFieldEdit(event)

    def _convertNone(self, theString):
        """
        Return the same string, if string = None, return an empty string.

        Args:
            theString:  The string

        Returns:  The input string or 'None' if it was empty
        """
        if theString is None:
            theString = ""
        return theString

    # noinspection PyUnusedLocal
    def _onOk(self, event: CommandEvent):
        """
        Activated when button OK is clicked.
        """
        strStereotype = self._txtStereotype.GetValue()
        if strStereotype == "":
            self._pyutModel.setStereotype(None)
        else:
            self._pyutModel.setStereotype(getPyutStereotype(strStereotype))
        # Adds all fields in a list
        self._pyutModel.fields = self._pyutModelCopy.fields

        # Update display properties
        self._pyutModel.showFields  = self._chkShowFields.GetValue()
        self._pyutModel.showMethods = self._chkShowMethods.GetValue()
        self._pyutModel.setShowStereotype(self._chkShowStereotype.GetValue())

        from org.pyut.PyutPreferences import PyutPreferences
        prefs = PyutPreferences()
        try:
            if prefs["AUTO_RESIZE"]:
                oglClass = self._mediator.getOglClass(self._pyutModel)
                oglClass.autoResize()
        except (ValueError, Exception) as e:
            self.logger.warning(f'{e}')

        fileHandling = self._mediator.getFileHandling()
        project = fileHandling.getCurrentProject()
        if project is not None:
            project.setModified()

        super()._onOk(event)
