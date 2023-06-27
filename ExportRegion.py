# type: ignore
from krita import *

# If part of the document is selected, export the selection.
# If nothing is selected, export everything in the current layer's bounding box.

orig_layer = Krita.instance().activeDocument().activeNode()

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
