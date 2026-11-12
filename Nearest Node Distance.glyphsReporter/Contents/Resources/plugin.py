# encoding: utf-8
# Glyphs SDK reporter wrapper, Apache-2.0; see GlyphsSDK-LICENSE.txt.
import os
import sys

import objc
from GlyphsApp.plugins import ReporterPlugin

_resources = os.path.dirname(__file__)
if _resources not in sys.path:
    sys.path.insert(0, _resources)
from at_nearest_node_distance import NearestNodeDistance


class ATNearestNodeDistanceReporter(ReporterPlugin):
    @objc.python_method
    def settings(self):
        self.menuName = "Nearest Node Distance"
        # Glyphs controls activation. Do not register a script callback here.
        self._overlay = NearestNodeDistance()

    @objc.python_method
    def foreground(self, layer):
        self._overlay.draw(layer, {"Scale": self.getScale()})

    @objc.python_method
    def __file__(self):
        return __file__
