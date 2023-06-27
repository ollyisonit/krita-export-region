# type: ignore
from krita import *
from PyQt5.QtWidgets import QWidget, QAction
from pprint import pprint


# If part of the document is selected, export the selection.
# If nothing is selected, export everything in the current layer's bounding box.
def export_region():
    clear_at_end = False

    if not Krita.instance().activeDocument().selection():
        Krita.instance().action("selectopaque").trigger()
        clear_at_end = True
    Krita.instance().action("copy_merged").trigger()

    orig_document = Krita.instance().activeDocument()

    Krita.instance().action("paste_new").trigger()

    new_document = Krita.instance().activeDocument()
    Krita.instance().action("file_export_file").trigger()
    new_document.close()

    Krita.instance().setActiveDocument(orig_document)
    if clear_at_end:
        Krita.instance().action("deselect").trigger()


export_region_action = QAction("dninosores_export_region")
export_region_action.setStatusTip(
    "Export selected part of document, or part of document bounded by current layer if"
    " nothing is selected."
)
export_region_action.setText("Export Region...")
export_region_action.triggered.connect(export_region)

menubar = Krita.instance().activeWindow().qwindow().menuBar()

file_menu = [
    menu_item for menu_item in menubar.actions() if menu_item.objectName() == "file"
]

if file_menu:
    file_menu = file_menu[0].menu()
    file_menu_items = file_menu.actions()
    pprint(file_menu_items)
    export_action = None
    for i in range(len(file_menu_items)):
        action = file_menu_items[i]
        if action.objectName() == "file_export_advanced":
            export_action = action
    if export_action:
        file_menu.insertAction(export_action, export_region_action)

pprint(file_menu)
