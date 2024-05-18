from PyQt5 import QtCore, QtWidgets, QtGui

class CheckedAbleComboBox(QtWidgets.QComboBox):

    itemChecked = QtCore.pyqtSignal(QtGui.QStandardItem, bool)
    checkedComplete = QtCore.pyqtSignal()

    def __init__(self, parent):
        super(CheckedAbleComboBox, self).__init__(parent)
        self.view().pressed.connect(self.handleItemPressed)
        self.setModel(QtGui.QStandardItemModel(self))
        self._changed = False


    def handleItemPressed(self, index):
        item = self.model().itemFromIndex(index)
        if item.checkState():
            item.setCheckState(QtCore.Qt.Unchecked)
        else:
            item.setCheckState(QtCore.Qt.Checked)
        self.itemChecked.emit(item, bool(item.checkState()))
        self._changed = True


    def hidePopup(self):
        if not self._changed:
            super().hidePopup()
            self.checkedComplete.emit()
        self._changed = False


    def addCheckName(self, name):
        self.addItem(name)
        item = self.model().item(self.count()-1)
        item.setCheckState(QtCore.Qt.Checked)
        item.setTextAlignment(QtCore.Qt.AlignCenter)


    def getAllState(self):
        checkedColumns = []
        for i in range(self.count()):
            item = self.model().item(i)
            if not  item.checkState():
                continue
            checkedColumns.append(item.text())
        return checkedColumns
