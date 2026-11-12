#MenuTitle: Show Nearest Node Distance
# -*- coding: utf-8 -*-
"""Toggle live distance labels and green measuring lines in Glyphs 4.

Run again to turn off. Distances are straight-line font units to the nearest
other on-curve node in the same layer, across all its editable paths. Handles,
anchors and component outlines are excluded by default. No font data is edited.
"""

import builtins
import math
import traceback
from objc import pyobjc_id

from AppKit import (
    NSAttributedString,
    NSBezierPath,
    NSColor,
    NSFont,
    NSFontAttributeName,
    NSForegroundColorAttributeName,
    NSGraphicsContext,
)
from Foundation import NSMakePoint, NSMakeRect
from GlyphsApp import DRAWFOREGROUND, GSNode, Glyphs, OFFCURVE


# Set True to count Bézier handles as nodes, including selected handles.
INCLUDE_HANDLES = False
FONT_SIZE = 13.0
LABEL_OFFSET = 9.0
LINE_WIDTH = 1.25
_STATE_KEY = "_approximateTypeNearestNodeDistance"


def nearest_distances(layer, include_handles=False):
    """Return (selected node, nearest node, Euclidean distance) tuples."""
    selected = [node for node in layer.selection if isinstance(node, GSNode)]
    if not selected:
        return []
    nodes = [
        node
        for path in layer.paths
        for node in path.nodes
        if include_handles or node.type != OFFCURVE
    ]
    results = []
    for source in selected:
        if not include_handles and source.type == OFFCURVE:
            continue
        # GSNode equality can match distinct nodes at identical coordinates.
        # Compare native identities so coincident nodes give a zero distance.
        source_id = pyobjc_id(source)
        if not any(source_id == pyobjc_id(node) for node in nodes):
            continue
        best = None
        best_distance = float("inf")
        origin = source.position
        for candidate in nodes:
            if pyobjc_id(candidate) == source_id:
                continue
            position = candidate.position
            distance = math.hypot(position.x - origin.x, position.y - origin.y)
            if distance < best_distance:
                best = candidate
                best_distance = distance
        if best is not None:
            results.append((source, best, best_distance))
    return results


def format_distance(distance):
    # Up to one decimal, with no unnecessary trailing .0.
    return "{:.1f}".format(distance).rstrip("0").rstrip(".")


class NearestNodeDistance:
    def __init__(self):
        self.include_handles = INCLUDE_HANDLES
        self.reported_error = False
        # Keep exactly the same bound callback for registration and removal.
        self.callback = self.draw

    def start(self):
        Glyphs.addCallback(self.callback, DRAWFOREGROUND)

    def stop(self):
        Glyphs.removeCallback(self.callback, DRAWFOREGROUND)
        Glyphs.redraw()

    def draw(self, layer, info):
        try:
            measurements = nearest_distances(layer, self.include_handles)
            if not measurements:
                return
            scale = float(info.get("Scale", 0.0))
            if not math.isfinite(scale) or scale <= 0.0:
                font = Glyphs.font
                tab = font.currentTab if font else None
                scale = float(tab.scale) if tab else 1.0
            scale = max(0.01, scale)
            attributes = {
                NSFontAttributeName: NSFont.systemFontOfSize_(FONT_SIZE / scale),
                NSForegroundColorAttributeName: NSColor.controlAccentColor(),
            }
            NSGraphicsContext.saveGraphicsState()
            try:
                # Draw the actual measured pairs behind all labels. Width stays
                # constant on screen, just like the label size and offset.
                NSColor.systemGreenColor().colorWithAlphaComponent_(0.5).set()
                drawn_pairs = set()
                for source, nearest, _distance in measurements:
                    pair = tuple(sorted((pyobjc_id(source), pyobjc_id(nearest))))
                    if pair in drawn_pairs:
                        continue
                    drawn_pairs.add(pair)
                    line = NSBezierPath.bezierPath()
                    line.moveToPoint_(source.position)
                    line.lineToPoint_(nearest.position)
                    line.setLineWidth_(LINE_WIDTH / scale)
                    line.stroke()
                for source, _nearest, distance in measurements:
                    label = NSAttributedString.alloc().initWithString_attributes_(
                        format_distance(distance), attributes
                    )
                    size = label.size()
                    position = source.position
                    x = position.x + LABEL_OFFSET / scale
                    y = position.y + LABEL_OFFSET / scale
                    padding = 2.0 / scale
                    rect = NSMakeRect(
                        x - padding, y - padding,
                        size.width + 2.0 * padding, size.height + 2.0 * padding,
                    )
                    NSColor.controlBackgroundColor().colorWithAlphaComponent_(0.92).set()
                    NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(
                        rect, 3.0 / scale, 3.0 / scale
                    ).fill()
                    label.drawAtPoint_(NSMakePoint(x, y))
            finally:
                NSGraphicsContext.restoreGraphicsState()
        except Exception:
            if not self.reported_error:
                self.reported_error = True
                print("Nearest Node Distance: drawing failed. See details below.")
                print(traceback.format_exc())


def toggle():
    previous = getattr(builtins, _STATE_KEY, None)
    if previous is not None:
        previous.stop()
        delattr(builtins, _STATE_KEY)
        print("Nearest Node Distance: off")
        return
    controller = NearestNodeDistance()
    # Retain across Script menu runs and Macro Panel namespaces.
    setattr(builtins, _STATE_KEY, controller)
    try:
        controller.start()
    except Exception:
        delattr(builtins, _STATE_KEY)
        raise
    Glyphs.redraw()
    print("Nearest Node Distance: on — run again to turn off")


if __name__ == "__main__":
    toggle()
