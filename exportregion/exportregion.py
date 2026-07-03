# type: ignore
from krita import *
import os
from .qtpy.qtpy.QtCore import QTimer
from pprint import pprint
from functools import partial


class ExportRegionExtension(Extension):
    def __init__(self, parent):
        super().__init__(parent)

    # If part of the document is selected, export the selection.
    # If nothing is selected, export everything in the current layer's bounding box and mask to that layer
    def export_region(self):
        crop_to_layer_mode = False

        doc = Krita.instance().activeDocument()

        if not doc:
            return

        filename = "untitled"
        path = doc.fileName()
        if path:
            filename = os.path.basename(path).split('.')[0]

        if not doc.selection():
            Krita.instance().action("selectopaque").trigger()
            crop_to_layer_mode = True
        doc.waitForDone()

        selection = doc.selection()

        # crop selection to document
        full_selection = Selection()
        full_selection.select(0, 0, doc.width(), doc.height(), 255)
        selection.intersect(full_selection)

        # Setup doc
        export_doc = Krita.instance().createDocument(selection.width(),
                                                     selection.height(),
                                                     filename,
                                                     doc.colorModel(),
                                                     doc.colorDepth(),
                                                     doc.colorProfile(),
                                                     doc.resolution())
        # Give the export document a suggested file path so the Export dialog
        # autopopulates the filename field even on the first export of a session.
        export_doc.setFileName(filename)

        Krita.instance().activeWindow().addView(export_doc)
        Krita.instance().setActiveDocument(export_doc)

        # Remove existing nodes
        for layer in export_doc.topLevelNodes():
            layer.remove()

        # Copy data (thanks to Destiny Hailstorm (djgaven588) for pixelData logic)
        newNode = export_doc.createNode("Copy", "paintlayer")
        ba = doc.pixelData(selection.x(), selection.y(), selection.width(),
                           selection.height())
        newNode.setPixelData(ba, 0, 0, selection.width(), selection.height())

        export_doc.rootNode().addChildNode(newNode, None)

        # Finish
        export_doc.refreshProjection()
        export_doc.waitForDone()

        # Mask to selection
        selection_pixeldata = bytearray(
            selection.pixelData(selection.x(), selection.y(),
                                selection.width(), selection.height()))
        export_doc_selection = Selection()
        export_doc_selection.setPixelData(selection_pixeldata, 0, 0,
                                          selection.width(),
                                          selection.height())

        export_doc.setSelection(export_doc_selection)
        export_doc.setActiveNode(newNode)
        Krita.instance().action("invert_selection").trigger()
        Krita.instance().action("clear").trigger()

        export_doc.refreshProjection()
        export_doc.waitForDone()

        # Export
        Krita.instance().action("file_export_file").trigger()
        export_doc.setModified(False)
        Krita.instance().setActiveDocument(doc)
        export_doc.close()

        if crop_to_layer_mode:
            Krita.instance().action("deselect").trigger()

    def setup(self):
        pass

    def createActions(self, window):
        export_region_action = window.createAction("dninosores_export_region",
                                                   "Export Region...", "file")
        export_region_action.triggered.connect(self.export_region)
        QTimer.singleShot(
            0, partial(self.moveAction, export_region_action,
                       window.qwindow()))

    # Take the existing export_region action and move it to be after file_export in the file menu
    def moveAction(self, action, qwindow):
        menu_bar = qwindow.menuBar()
        file_menu_action = next(
            (a for a in menu_bar.actions() if a.objectName() == "file"), None)
        if file_menu_action:
            file_menu = file_menu_action.menu()
            for file_action in file_menu.actions():
                if file_action.objectName() == "file_export_advanced":
                    file_menu.removeAction(action)
                    file_menu.insertAction(file_action, action)


Krita.instance().addExtension(ExportRegionExtension(Krita.instance()))
