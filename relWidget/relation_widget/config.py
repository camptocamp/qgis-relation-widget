from qgis.gui import QgsAbstractRelationEditorConfigWidget
from qgis.PyQt.QtWidgets import QVBoxLayout, QComboBox


class CheckRelationConfigWidget(QgsAbstractRelationEditorConfigWidget):
    def __init__(self, relation, parent):
        self.relation = relation
        super().__init__(relation, parent)
        self.initGui()
        self.conf = None

    def initGui(self):
        self.boxLayout = QVBoxLayout()
        self.setLayout(self.boxLayout)
        self.targetLabelComboBox = QComboBox(self)
        self.targetLabelComboBox.addItem("s_name")
        self.targetLabelComboBox.addItem("t_name")
        self.boxLayout.addWidget(self.targetLabelComboBox)

    def setConfig(self, config):
        print(f"set conf: {config}")
        i = self.targetLabelComboBox.findText(config.get("label"))
        print(i)
        self.targetLabelComboBox.setCurrentIndex(
            self.targetLabelComboBox.findText(config.get("label"))
        )

    def config(self):
        print(f"which conf {self.targetLabelComboBox.currentText()}")
        self.conf = {
            "label": self.targetLabelComboBox.currentText()
        }
        return self.conf
