from .widget import CheckRelationWidget
from .config import CheckRelationConfigWidget


from qgis.gui import (
    QgsAbstractRelationEditorWidgetFactory,
    QgsAbstractRelationEditorConfigWidget,
)


class Conf(QgsAbstractRelationEditorConfigWidget):
    def setConfig(self, config):
        return

    def config(self):
        return {}


class CheckRelationWidgetFactory(QgsAbstractRelationEditorWidgetFactory):
    def create(self, config, parent=None):
        # print("confi1")
        print(f"fact create {config}")
        print(self.conf)
        print(self.conf.conf)
        self.widget = CheckRelationWidget(config, parent)
        return self.widget

    def configWidget(self, relation, parent=None):
        # print("confix1")
        # print("confi2")
        self.conf = CheckRelationConfigWidget(relation, parent)
        # print("confi3")
        # print(self.conf)
        return self.conf

    def name(self):
        return "Check Relation Widget"

    def type(self):
        return "checkRelationWidget"
