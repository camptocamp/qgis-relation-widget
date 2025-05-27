from qgis.core import QgsApplication, QgsFeature
from qgis.PyQt.QtWidgets import QVBoxLayout, QLabel, QWidget, QListView, QCheckBox, QHBoxLayout, QSizePolicy, QPushButton, QFrame, QAbstractItemView, QMessageBox, QToolButton
from qgis.PyQt.QtGui import QStandardItemModel, QStandardItem
from qgis.PyQt.QtCore import Qt, QSortFilterProxyModel, pyqtSignal
from qgis.gui import QgsAbstractRelationEditorWidget, QgsFilterLineEdit


class CheckableModel(QStandardItemModel):

    selectionChanged = pyqtSignal()
    oldSelectedIndexes = []
    selectedIndexes = []

    def flags(self, index):
        return super().flags(index) | Qt.ItemIsUserCheckable

    def data(self, index, role):
        value = super().data(index, role)
        if (role == Qt.CheckStateRole) and (value is None):
            return Qt.Unchecked
        return value

    def checkedData(self, role):
        return [self.data(self.index(i, 0), role) for i in self.selectedIndexes]

    def setCheckedData(self, data, role, doNotify=True):
        for i in range(self.rowCount()):
            if self.data(self.index(i, 0), role) in data:
                super().setData(self.index(i, 0), Qt.Checked, Qt.CheckStateRole)
            else:
                super().setData(self.index(i, 0), Qt.Unchecked, Qt.CheckStateRole)
        if doNotify:
            self.notifyChanges()

    def setData(self, index, value, role):
        ok = super().setData(index, value, role)
        if ok and (role == Qt.CheckStateRole):
            self.notifyChanges()
        return ok

    def notifyChanges(self):
        self.selectedIndexes = [
            i
            for i in range(self.rowCount())
            if self.data(self.index(i, 0), Qt.CheckStateRole) == Qt.Checked
        ]
        if set(self.oldSelectedIndexes) != (self.selectedIndexes):
            self.selectionChanged.emit()
        self.oldSelectedIndexes = self.selectedIndexes


class MyFilterLineEdit(QgsFilterLineEdit):

    selectionValidated = pyqtSignal()

    def keyPressEvent(self, event):
        if event.key == Qt.Key_Escape:
            if self.text():
                self.clearValue()
                return
        if (event.key() == Qt.Key_Return) or (event.key() == Qt.Key_Enter):
            self.selectionValidated.emit()
            return

        return super().keyPressEvent(event)


class CheckRelationWidget(QgsAbstractRelationEditorWidget):
    checkedDataChanged = pyqtSignal(list)

    def __init__(self, config, parent=None):
        super().__init__(config, parent)

        self.isCollapsible = True  # isCollapsible
        self.wasEditable = False
        self.relationLayer = None
        self.initGui()

        self.firstShow = False
        self.label = "t_name"
        print(f"###\ninit wi {config}\n###")
        self.label = config.get("label")
        self.config = config

        self.model = CheckableModel(0, 1, self)
        self.modelProxy = QSortFilterProxyModel()
        self.modelProxy.setSourceModel(self.model)
        self.modelProxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.listView.setModel(self.modelProxy)
        self.listView.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.model.selectionChanged.connect(self.onSelectionChanged)
        self.model.itemChanged.connect(self.updateRelation)
        self.listView.activated.connect(self.toggleCheckState)

        # self.widgetLayout = QVBoxLayout()
        # self.setLayout(self.widgetLayout)
        # self.widgetLayout.addWidget(QLabel("Widget"))

    def setConfig(self, config):
        self.label = config.get("label")
        self.config = config

    def config(self):
        return self.config
        return {"label": self.label}

    def deselectAllOptions(self):
        self.setAllCheckStates(Qt.Unchecked, False)

    def itemCheckState(self, i):
        return self.model.data(self.model.index(i, 0), Qt.CheckStateRole)

    def setItemCheckState(self, i, state):
        return self.model.setData(self.model.index(i, 0), state, Qt.CheckStateRole)

    def setData(self, data):
        self.model.setCheckedData(data, Qt.UserRole, doNotify=False)

    def count(self):
        return self.model.rowCount()

    def itemData(self, i):
        return self.model.data(self.model.index(i, 0), Qt.UserRole)

    # # end of methods for compatibility with QgsCheckableComboBox # #

    def findData(self, data):
        for i in range(self.model.rowCount()):
            if self.model.data(self.model.index(i, 0), Qt.UserRole) == data:
                return i
        return -1

    def onSelectionChanged(self):
        self.updateText()
        self.checkedDataChanged.emit(self.model.checkedData(Qt.UserRole))

    def updateText(self):
        nbChecked, nbTotal = self.getSelectionStatus(self.model)
        statusText = f"{nbChecked} éléments sélectionnés sur {nbTotal}:\n"
        statusText += " ; ".join(
            self.model.item(i, 0).data(Qt.DisplayRole)
            for i in range(self.model.rowCount())
            if self.model.item(i, 0).data(Qt.CheckStateRole) == Qt.Checked
        )
        self.statusText.setText(statusText)
        self.updateCheckState()

    def updateFilter(self, pattern=""):
        self.modelProxy.setFilterRegularExpression(pattern)
        self.updateCheckState()

    def updateCheckState(self):
        self.selectionCheckBox.blockSignals(True)
        nbChecked, nbTotal = self.getSelectionStatus(self.modelProxy)
        self.selectionCheckBox.setToolTip(f"{nbChecked}/{nbTotal}")
        if nbChecked == nbTotal:
            self.selectionCheckBox.setCheckState(Qt.Checked)
            self.selectionCheckBox.setTristate(False)
        elif nbChecked == 0:
            self.selectionCheckBox.setCheckState(Qt.Unchecked)
            self.selectionCheckBox.setTristate(False)
        else:
            self.selectionCheckBox.setTristate(True)
            self.selectionCheckBox.setCheckState(Qt.PartiallyChecked)
        self.selectionCheckBox.blockSignals(False)

    def getSelectionStatus(self, model):
        nbTotal = model.rowCount()
        nbChecked = sum(
            model.data(model.index(i, 0), Qt.CheckStateRole) == Qt.Checked
            for i in range(nbTotal)
        )
        return nbChecked, nbTotal

    def selectionCheckBoxChanged(self, state):
        self.selectionCheckBox.setTristate(False)
        if state == Qt.Checked:
            self.setAllCheckStates()
        elif state == Qt.Unchecked:
            self.setAllCheckStates(Qt.Unchecked)

    def toggleCheckState(self, index):
        oldState = self.modelProxy.data(index, Qt.CheckStateRole)
        newState = Qt.Unchecked if (oldState == Qt.Checked) else Qt.Checked
        # print (oldState)
        self.modelProxy.setData(index, newState, Qt.CheckStateRole)

    def updateRelation(self, item):
        ownId = next(iter(self.relation().fieldPairs()))
        targetId = next(iter(self.nmRelation().fieldPairs()))
        ownValue = self.feature().id()
        # targetValue = self.modelProxy.data(index, Qt.UserRole)
        targetValue = item.data(Qt.UserRole)
        # print({ownId: ownValue, targetId: targetValue})
        if item.data(Qt.CheckStateRole):
            # add link
            f = QgsFeature(self.relationLayer.fields())
            f.setAttribute(ownId, ownValue)
            f.setAttribute(targetId, targetValue)
            self.relationLayer.addFeature(f)
        else:
            # remove link
            # print(f"\"{ownId}\" = '{ownValue}' and \"{targetId}\" = '{targetValue}'")
            idsToRemoveFromEditbuffer = []
            for f in self.relationLayer.getFeatures(
                    f"\"{ownId}\" = '{ownValue}' and \"{targetId}\" = '{targetValue}'"
            ):
                # print('delete', f.id(), f.attribute(ownId), f.attribute(targetId))
                self.relationLayer.deleteFeature(f.id())
                if f.id() in self.relationLayer.editBuffer().addedFeatures():
                    idsToRemoveFromEditbuffer.append(f.id())
            if idsToRemoveFromEditbuffer:
                idsToDelete = self.relationLayer.editBuffer().deletedFeatureIds()
                # print(idsToDelete)
                featuresToKeep = [f for id, f in self.relationLayer.editBuffer().addedFeatures().items()
                                  if id not in idsToRemoveFromEditbuffer]
                self.relationLayer.editBuffer().rollBack()
                self.relationLayer.deleteFeatures(idsToDelete)
                self.relationLayer.addFeatures(featuresToKeep)

    def setAllCheckStates(self, state=Qt.Checked, filtered=True):
        self.blockSignals(True)
        if filtered:
            model = self.modelProxy
        else:
            model = self.model
        for i in range(model.rowCount()):
            model.setData(model.index(i, 0), state, Qt.CheckStateRole)
        self.blockSignals(False)
        self.checkedDataChanged.emit(self.model.checkedData(Qt.UserRole))

    def initGui(self):
        self._expandIcon = QgsApplication.getThemeIcon("/mIconExpand.svg")
        self._collapseIcon = QgsApplication.getThemeIcon("/mIconCollapse.svg")
        self.statusRow = QFrame(self)
        self.statusText = QLabel(self.statusRow)
        self.statusText.setMaximumHeight(29)  # 2 lines
        self.statusText.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        self.collapsePushButton = QPushButton(self.statusRow)
        self.collapsePushButton.setIcon(self._collapseIcon)
        self.collapsePushButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.collapsePushButton.clicked.connect(self.toggleExpanded)
        self.statusRow.mousePressEvent = lambda event: self.toggleExpanded()
        self.statusRow.setLayout(QHBoxLayout())
        self.statusRow.layout().addWidget(self.statusText)
        if self.isCollapsible:
            self.statusRow.layout().addWidget(self.collapsePushButton)
        self.searchRow = QHBoxLayout()
        self.selectionCheckBox = QCheckBox(self)
        self.selectionCheckBox.stateChanged.connect(self.selectionCheckBoxChanged)
        self.searchLine = MyFilterLineEdit(self)
        self.searchLine.textEdited.connect(self.updateFilter)
        self.searchLine.cleared.connect(self.updateFilter)
        self.searchLine.selectionValidated.connect(self.setAllCheckStates)
        self.searchRow.addWidget(self.selectionCheckBox)
        self.searchRow.addWidget(self.searchLine)
        self.listView = QListView(self)
        self.setLayout(QVBoxLayout())

        # toolBar = QToolBar(self)
        self.editButton = QToolButton()
        self.editButton.setObjectName("editButton")
        self.editButton.setCheckable(True)
        self.editButton.setIcon(QgsApplication.getThemeIcon("mActionToggleEditing.svg"))
        self.editButton.toggled.connect(self.onToggleEdit)

        self.saveButton = QToolButton()
        self.saveButton.setObjectName("saveButton")
        self.saveButton.setIcon(QgsApplication.getThemeIcon("mActionSaveAllEdits.svg"))
        self.saveButton.setEnabled(False)
        self.saveButton.clicked.connect(self.onSaveClick)
        # self.editButton.setChecked(self.wasEditable)
        self.searchRow.addWidget(self.editButton)
        self.searchRow.addWidget(self.saveButton)
        # toolBar.addWidget(self.editButton)
        # toolBar.addWidget(self.saveButton)
        # self.layout().addWidget(toolBar)

        self.layout().addWidget(self.statusRow)
        self.popup = QWidget(self)
        ll = QVBoxLayout()
        self.popup.setLayout(ll)
        ll.addLayout(self.searchRow)
        ll.addWidget(self.listView)
        self.layout().addWidget(self.popup)
        self.layout().addStretch()

    def setExpanded(self, expanded):
        self.popup.setVisible(expanded)
        self.collapsePushButton.setIcon(
            self._collapseIcon if expanded else self._expandIcon
        )
        if expanded:
            self.searchLine.setFocus()

    def toggleExpanded(self):
        self.setExpanded(not self.popup.isVisible())

    def addItem(self, text, data):
        item = QStandardItem(text)
        item.setData(data, Qt.UserRole)
        self.model.appendRow(item)

    # ######

    def setEditorContext(self, ctx):
        # print(ctx.relation(), ctx.relation().id())
        super().setEditorContext(ctx)

    def beforeSetRelations(self, r1, r2):
        # print('brels', r1.id(), r2.id())
        pass

    def afterSetRelations(self):
        # print('arels', self.relation().id(), self.nmRelation().id())
        # print(self.feature().id(), self.features())
        pass

    def afterSetRelationFeature(self):
        # print('afels', self.relation().id(), self.nmRelation().id(), self.feature().id(), self.features())
        pass

    def setNmRelationId(self, id):
        # print('rels', id)
        pass

    # def setConfig(self, config):
    #     print(f"setconf wi {config}")
    #     # print(self.relation().id())
    #     # print(self.nmRelation().id())
    #     # print(self.feature(), self.features())
    #     pass

    # def beforeSetRelationFeature(self, r, f):
    #     print('bb', self.feature(), self.features())

    # def afterSetRelationFeature(self, r, f):
    #     print('aa', self.feature(), self.features())

    def updateUi(self):
        if self.firstShow:
            print('ui', self.feature(), self.features())
            self.setFeatureData()

    def setFeatureData(self):
        relation_features = self.relation().getRelatedFeatures(self.feature())
        # print(relation_feature.id(), relation_feature.attribute('s_name'))
        related_feature_ids = [self.nmRelation().getReferencedFeature(f).id() for f in relation_features]
        # print(related_feature_ids)
        self.setData(related_feature_ids)
        self.updateText()

    def showEvent(self, event):
        # print('show', event, self.feature().id(), self.features())
        self.firstShow = True
        self.initRelation()
        self.setFeatureData()

    def setFeature(self, feat, update):
        super().addFeature(feat, update)
        # print('set', feat, update)
        # self.initRelation()

    def initRelation(self):
        self.relationLayer = self.nmRelation().referencingLayer()
        layer = self.nmRelation().referencedLayer()
        self.model.clear()
        for feature in layer.getFeatures():
            self.addItem(
                f"{feature.attribute(self.label)}",
                feature.id(),
            )
        if self.relationLayer.editBuffer() is not None:
            self.wasEditable = True
            if not self.editButton.isChecked():
                self.editButton.toggle()

    def onToggleEdit(self):
        if self.editButton.isChecked():
            self.relationLayer.startEditing()
        else:
            # if self.relationLayer.editBuffer() and self.relationLayer.editBuffer().isModified():
            if self.relationLayer.editBuffer().isModified():
                if (
                    QMessageBox(
                        QMessageBox.Question,
                        "Relation layer modified.",
                        "The relation layer has unsaved changes. Deactivating edit mode "
                        "will lead to loss of modified data. Do you want to go to read-only "
                        "mode and lose all edits?",
                        QMessageBox.Yes | QMessageBox.No,
                    ).exec()
                    == QMessageBox.Yes
                ):
                    self.relationLayer.rollBack()
                else:
                    self.editButton.setChecked(True)
                    return
            else:
                self.relationLayer.rollBack()

        self.saveButton.setEnabled(self.editButton.isChecked())

    def onSaveClick(self):
        self.relationLayer.commitChanges(stopEditing=False)
