
from typing import List

from logging import Logger
from logging import getLogger

import matplotlib.pyplot as plt

from networkx import DiGraph
from networkx import Graph
from networkx import parse_gml

from org.pyut.ui.UmlFrame import UmlFrame

from org.pyut.ogl.OglClass import OglClass

from org.pyut.plugins.orthogonal.GMLExporter import GMLExporter

from org.pyut.plugins.PyutToPlugin import PyutToPlugin

from org.pyut.plugins.orthogonal.alternate.TSM import Compaction
from org.pyut.plugins.orthogonal.alternate.TSM import Planarization
from org.pyut.plugins.orthogonal.alternate.TSM import Orthogonalization


class ToOrthogonalLayoutAlternate(PyutToPlugin):
    """
    Alternate Orthogonal Layout plugin using homegrown engine
    """
    def __init__(self, umlObjects: List[OglClass], umlFrame: UmlFrame):
        """

        Args:
            umlObjects:  list of ogl objects
            umlFrame:    A Pyut UML Frame
        """
        super().__init__(umlObjects, umlFrame)

        self.logger: Logger = getLogger(__name__)

    def getName(self):
        """
        Returns: the name of the plugin.
        """
        return "Orthogonal Layout-2"

    def getAuthor(self):
        """
        Returns: The author's name
        """
        return "Humberto A. Sanchez II"

    def getVersion(self):
        """
        Returns: The plugin version string
        """
        return "2.0"

    def getMenuTitle(self):
        """
        Returns:  The menu title for this plugin
        """
        return "Orthogonal Layout-2"

    def setOptions(self):
        """
        Prepare the import.
        This can be used to ask the user some questions

        Returns: if False, the import will be cancelled.
        """
        return True

    def doAction(self, umlObjects: List[OglClass], selectedObjects: List[OglClass], umlFrame: UmlFrame):
        """
        Do the tool's action

        Args:
            umlObjects:         list of the uml objects of the diagram
            selectedObjects:    list of the selected objects
            umlFrame:           The diagram frame
        """
        if umlFrame is None:
            self.displayNoUmlFrame()
            return
        if len(umlObjects) == 0:
            self.displayNoUmlObjects()
            return

        self.logger.info(f'Begin Orthogonal algorithm')

        gmlExporter: GMLExporter = GMLExporter()

        gmlExporter.prettyPrint = True
        gmlExporter.translate(umlObjects=umlObjects)
        gml: str = gmlExporter.gml

        self.logger.info(f'Generated GML:\n{gml}')
        gmlExporter.write('generated.gml')

        spicy: DiGraph = parse_gml(gml)
        nxGraph: Graph = Graph(spicy)

        nodes = nxGraph.nodes
        # compact: Compaction = self._generate(nxGraph, {node: eval(node) for node in nxGraph})
        nodePositions = {}
        for nodeName in nxGraph:
            nodeDict = nxGraph.nodes[nodeName]
            x = nodeDict['graphics']['x']
            y = nodeDict['graphics']['y']
            nodePositions[nodeName] = (x, y)
            self.logger.info(f'{nodeName}')

        compact: Compaction = self._generate(nxGraph, nodePositions)

        compact.draw(with_labels=True)
        plt.savefig(f'generated.png')
        for flowKey in compact.flow_dict.keys():
            flowValues = compact.flow_dict[flowKey]
            self.logger.info(f'flowKey: `{flowKey}` - flowValues: {flowValues}')
            for flowValueKey in flowValues.keys():
                xyzDict = flowValues[flowValueKey]
                self.logger.info(f'\tflowValueKey: {flowValueKey} - {xyzDict}')
                for xyzKeys in xyzDict:
                    self.logger.info(f'\t\txyzKeys: {xyzKeys}')

        self.logger.info(f'pos: {compact.pos}')

    def _generate(self, G, pos=None) -> Compaction:

        planar:     Planarization     = Planarization(G, pos)
        orthogonal: Orthogonalization = Orthogonalization(planar)
        compact:    Compaction        = Compaction(orthogonal)

        return compact


