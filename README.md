# Nearest Node Distance

A reporter plug-in for **Glyphs 4** by Kasper Pyndt Rasmussen (Approximate Type).

Select a node to see its straight-line distance to the nearest other outline node in the same layer.

- Works across all editable paths in the active layer.
- Supports multiple selected nodes.
- Shows font units, rounded to one decimal where needed.
- Keeps labels and line thickness readable when zooming.
- Excludes Bézier handles, anchors, and component outlines.
- Changes no outlines, metrics, or font data.

The measurement is between nodes, rather than the shortest distance to a curve
or the length of a path segment. Coincident nodes correctly measure zero.

## Installation

1. Choose **Code → Download ZIP** on this page and unzip the download.
2. Open **Nearest Node Distance.glyphsReporter** with Glyphs 4 and confirm installation.
3. Save your work and restart Glyphs.
4. Enable **View → Show Nearest Node Distance**. Standard reporter panels can
   also toggle the plug-in.

If you used the earlier `Show Nearest Node Distance.py` script, leave that
script switched off to avoid duplicate overlays. Restarting Glyphs clears its
temporary drawing callback.

This repository is not yet listed in Plugin Manager.

## Compatibility and validation

Developed for Glyphs 4 on macOS. Bundle loading, geometry calculations,
transparent rendering, and rendering at five zoom levels have been checked in
an isolated **Glyphs 4.1.1 (4108)** CLI process. Live View menu / Reporters panel
toggling has not yet been verified in the Glyphs GUI. Glyphs 3 is untested.

## Development

The reporter entry point is
`Nearest Node Distance.glyphsReporter/Contents/Resources/plugin.py`.
Geometry and drawing live in `at_nearest_node_distance.py` beside it.

The bundle includes the Glyphs SDK loader; preserve its executable permission
when copying or packaging the plug-in. Keep development files outside the
installed Glyphs application bundle.

Run the isolated checks with a Glyphs CLI installation:

```sh
GLYPHS_RUNNER=/path/to/glyphs ./tests/run.sh
```

The tests create disposable in-memory outlines and do not edit open user fonts.

## Licence

Apache-2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE). The bundle contains the
Glyphs SDK licence and loader provenance.
