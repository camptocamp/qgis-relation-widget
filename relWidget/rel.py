# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RelationPlugin
                                 A QGIS plugin
Registers a widget for editing multi-multi relationships between layers
                              -------------------
        begin                : 2024-02-15
        git sha              : $Format:%H$
        copyright            : (C) 2024 by Camptocamp
        email                : info@camptocamp.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.gui import QgsGui
from .relation_widget.factory import CheckRelationWidgetFactory


class RelationPlugin:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        QgsGui.relationWidgetRegistry().removeRelationWidget('checkRelationWidget')
        QgsGui.relationWidgetRegistry().addRelationWidget(CheckRelationWidgetFactory())        

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        pass

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        QgsGui.relationWidgetRegistry().removeRelationWidget('checkRelationWidget')

    # --------------------------------------------------------------------------

    # def run(self):
    #     """Run method that loads and starts the plugin"""

    #     if not self.pluginIsActive:
    #         self.pluginIsActive = True

    #         # dockwidget may not exist if:
    #         #    first run of plugin
    #         #    removed on close (see self.onClosePlugin method)
    #         if self.dockwidget is None:
    #             # Create the dockwidget (after translation) and keep reference
    #             self.dockwidget = OspDockWidget()

    #         # connect to provide cleanup on closing of dockwidget
    #         self.dockwidget.closingPlugin.connect(self.onClosePlugin)

    #         # show the dockwidget
    #         # TODO: fix to allow choice of dock location
    #         self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)
    #         self.dockwidget.show()
