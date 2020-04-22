
from typing import cast

from logging import Logger
from logging import getLogger

from wx import DEFAULT_FRAME_STYLE
from wx import ID_ANY
from wx import OK

from wx import App
from wx import Frame

from org.pyut.MiniOgl.DiagramFrame import DiagramFrame

from org.pyut.dialogs.DlgPyutDebug import DlgPyutDebug

from tests.TestBase import TestBase


class TestADialog(App):

    FRAME_ID: int = 0xDeadBeef

    def OnInit(self):

        TestBase.setUpLogging()
        self.logger: Logger = getLogger(__name__)
        frameTop: Frame = Frame(parent=None, id=TestADialog.FRAME_ID, title="Test A Dialog", size=(600, 400), style=DEFAULT_FRAME_STYLE)
        frameTop.Show(True)

        diagramFrame: DiagramFrame = DiagramFrame(frameTop)
        diagramFrame.SetSize((1200, 1200))
        diagramFrame.SetScrollbars(10, 10, 100, 100)

        diagramFrame.Show(True)

        self.SetTopWindow(diagramFrame)

        self._diagramFrame: DiagramFrame = diagramFrame

        self.initTest()
        return True

    def initTest(self):
        with DlgPyutDebug(self._diagramFrame, ID_ANY) as dlg:
            dlg: DlgPyutDebug = cast(DlgPyutDebug, dlg)
            if dlg.ShowModal() == OK:
                self.logger.warning(f'Retrieved data')
            else:
                self.logger.warning(f'Cancelled')

        self.logger.info(f"After dialog show")


testApp: App = TestADialog(redirect=False)

testApp.MainLoop()
