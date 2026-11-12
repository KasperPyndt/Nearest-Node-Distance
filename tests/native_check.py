"""Run in an isolated Glyphs CLI process; never touches an open user font."""
import builtins
import math
import os
import runpy
import sys
import traceback
from pathlib import Path

from AppKit import NSImage
from Foundation import NSPoint
from GlyphsApp import GSLayer, GSPath, GSNode, LINE, OFFCURVE, DRAWFOREGROUND
from GlyphsApp import callbackOperationTargets


def main():
    source = Path(__file__).resolve().parents[1] / "Nearest Node Distance.glyphsReporter/Contents/Resources/at_nearest_node_distance.py"
    script = runpy.run_path(str(source), run_name="nearest_node_test")
    measure = script["nearest_distances"]
    format_distance = script["format_distance"]

    def layer_with_paths(*contours):
        layer = GSLayer()
        for coordinates in contours:
            path = GSPath()
            for x, y, kind in coordinates:
                path.nodes.append(GSNode(NSPoint(x, y), kind))
            path.closed = False
            layer.shapes.append(path)
        return layer

    layer = layer_with_paths(
        [(0, 0, LINE), (3, 4, LINE), (100, 100, LINE)],
        [(1, 0, LINE), (200, 200, LINE)],
    )
    source_node = layer.paths[0].nodes[0]
    layer.selection = [source_node]
    before = str(layer.shapes)
    result = measure(layer)
    assert len(result) == 1 and result[0][1] == layer.paths[1].nodes[0]
    assert result[0][2] == 1.0
    # Geometry changes must be reflected immediately without rebuilding a cache.
    layer.paths[1].nodes[0].position = NSPoint(50, 0)
    assert measure(layer)[0][2] == 5.0
    layer.paths[1].nodes[0].position = NSPoint(0, 0)
    assert measure(layer)[0][2] == 0.0
    layer.paths[1].nodes[0].position = NSPoint(1, 0)
    assert str(layer.shapes) == before
    print("PASS: nearest across contours, live movement, coincident nodes")

    layer = layer_with_paths([(0, 0, LINE), (1, 0, OFFCURVE), (3, 4, LINE)])
    layer.selection = [layer.paths[0].nodes[0]]
    assert measure(layer)[0][2] == 5.0
    assert measure(layer, True)[0][2] == 1.0
    layer.selection = [layer.paths[0].nodes[1]]
    assert measure(layer) == [] and measure(layer, True)[0][2] == 1.0
    layer.selection = [layer.paths[0].nodes[0], layer.paths[0].nodes[2]]
    assert len(measure(layer)) == 2
    layer.selection = []
    assert measure(layer) == []
    singleton = layer_with_paths([(0, 0, LINE)])
    singleton.selection = [singleton.paths[0].nodes[0]]
    assert measure(singleton) == []
    assert [format_distance(d) for d in (0, 5, 10, math.sqrt(2))] == ["0", "5", "10", "1.4"]
    print("PASS: handles, multiselection, no selection, isolated node, formatting")

    layer.selection = [layer.paths[0].nodes[0]]
    before = str(layer.shapes)
    controller = script["NearestNodeDistance"]()
    for scale in (0.25, 0.5, 1.0, 2.0, 4.0):
        image = NSImage.alloc().initWithSize_((250, 250))
        image.lockFocus()
        try:
            controller.draw(layer, {"Scale": scale})
        finally:
            image.unlockFocus()
        assert not controller.reported_error
    assert str(layer.shapes) == before
    print("PASS: AppKit rendering at five zooms without geometry edits")

    callbacks_before = len(callbackOperationTargets.get(DRAWFOREGROUND, {}))
    for _ in range(3):
        script["toggle"]()
        assert getattr(builtins, script["_STATE_KEY"], None) is not None
        assert len(callbackOperationTargets[DRAWFOREGROUND]) == callbacks_before + 1
        # Running through a fresh namespace reproduces Script menu execution.
        fresh = runpy.run_path(str(source), run_name="nearest_node_test_again")
        fresh["toggle"]()
        assert getattr(builtins, script["_STATE_KEY"], None) is None
        assert len(callbackOperationTargets[DRAWFOREGROUND]) == callbacks_before
    print("PASS: repeated enable/disable across fresh script namespaces")


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
