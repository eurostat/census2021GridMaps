from qgis.core import (
    QgsApplication,
    QgsProject,
    QgsVectorLayer
)

# Initialize QGIS Application
#QgsApplication.setPrefixPath("/usr/bin/qgis", True)
#qgs = QgsApplication([], False)
#qgs.initQgis()

# Load a vector layer
layer = QgsVectorLayer("/home/juju/geodata/gisco/CNTR_BN_100K_2016.shp", "layer name", "ogr")
if not layer.isValid():
    print("Layer failed to load!")
else:
    QgsProject.instance().addMapLayer(layer)
    print("Layer loaded successfully!")

# Exit QGIS Application
#qgs.exitQgis()
