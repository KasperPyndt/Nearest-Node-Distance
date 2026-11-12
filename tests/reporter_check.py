"""Isolated Glyphs CLI checks of the packaged reporter and native drawing."""
import os
import sys
import traceback
from pathlib import Path

from AppKit import NSBitmapImageRep, NSColor, NSImage
from Foundation import NSClassFromString, NSPoint
from GlyphsApp import Glyphs, GSLayer, GSNode, GSPath, LINE


def main():
    cls = NSClassFromString("ATNearestNodeDistanceReporter")
    assert cls is not None, "Reporter bundle was not loaded"
    reporter = cls.alloc().init()
    assert reporter.title() == "Nearest Node Distance"
    assert reporter.interfaceVersion() == 1
    print("PASS: packaged reporter loaded by Glyphs 4")

    # The isolated CLI has no View menu / reporter registry. Native on/off
    # controls are supplied by ReporterPlugin after installation in the GUI.
    print("LIMIT: View/Reporters panel toggling requires the Glyphs GUI")

    layer = GSLayer()
    path = GSPath()
    path.closed = False
    for point in [(30, 30), (130, 30)]:
        path.nodes.append(GSNode(NSPoint(*point), LINE))
    layer.shapes.append(path)
    layer.selection = [path.nodes[0]]
    before = str(layer.shapes)
    for scale in (0.25, 0.5, 1.0, 2.0, 4.0):
        image = NSImage.alloc().initWithSize_((200, 200))
        image.lockFocus()
        try:
            reporter.drawForegroundForLayer_options_(layer, {"Scale": scale, "Black": False})
        finally:
            image.unlockFocus()
        assert not reporter._overlay.reported_error
        if scale == 1.0:
            bitmap = NSBitmapImageRep.imageRepWithData_(image.TIFFRepresentation())
            # Bitmap Y direction differs from the drawing context. Inspect
            # both candidate rows and allow antialiasing around the stroke.
            samples = [bitmap.colorAtX_y_(80, y) for y in (29, 30, 169, 170)]
            assert any(0.15 < color.alphaComponent() < 0.65 for color in samples)
            print("PASS: green measuring line renders with partial transparency")
    assert str(layer.shapes) == before
    print("PASS: reporter foreground at five zooms without outline changes")




code = 0
try:
    main()
except BaseException:
    traceback.print_exc()
    code = 1
finally:
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(code)
