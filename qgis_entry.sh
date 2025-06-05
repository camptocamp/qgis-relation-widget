#!/bin/sh
set -e

#sed -i 's/old-text/new-text/g' /profiles
mkdir -p /root/.local/share/QGIS/QGIS3/profiles/default/QGIS/
cp /QGIS3.ini /root/.local/share/QGIS/QGIS3/profiles/default/QGIS/QGIS3.ini

# Execute the passed command
exec "$@"
