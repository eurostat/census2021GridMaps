from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsRuleBasedRenderer,
    QgsMarkerSymbol,
    QgsSimpleMarkerSymbolLayer,
    QgsProperty
)
from qgis.PyQt.QtGui import QColor

# Get the layer by name
layer = QgsProject.instance().mapLayersByName('grid_1km_point')[0]

# Create the symbol
symbol = QgsMarkerSymbol.createSimple({
    'name': 'circle',
    'color': '255,0,0,255',  # Red color (RGBA format)
    'outline_color': '255,255,255,0',  # Transparent outline (RGBA format)
    'size': '1000',  # Diameter in map units (CRS units)
    'size_unit': 'MapUnit'
})

# Get the current renderer (assuming it's a rule-based renderer)
renderer = layer.renderer()

# Check if the renderer is rule-based
if isinstance(renderer, QgsRuleBasedRenderer):
    # Get the root rule
    root_rule = renderer.rootRule()

    # Iterate over each rule
    for rule in root_rule.children():
        # Set the symbol for each rule
        rule.symbol().changeSymbolLayer(0, symbol.clone())

    # Update the layer renderer
    layer.setRenderer(renderer)
    layer.triggerRepaint()  # Refresh the layer to apply changes

    print("Style applied to 'grid_1km_point'")
else:
    print("Layer does not use a QgsRuleBasedRenderer")