import sys

from PyQt5 import QtWidgets, QtCore, QtGui, uic


class ComboBox_main(QtWidgets.QDialog):

    def __init__(self):
        super(ComboBox_main, self).__init__()
        uiFile = __file__.replace('.py', '.ui')
        self._ui = uic.loadUi(uiFile, self)
        self._index = 1
        self.connectSignals()

    
    def connectSignals(self):
        self._ui.activated_comboBox.activated.connect(self.activatedInt)
        self._ui.activated_comboBox.activated['QString'].connect(self.activatedStr)

        self._ui.currentIndexChanged_comboBox.currentIndexChanged['QString'].connect(self.currentIndexChanged)
        self._ui.editTextChanged_comboBox.editTextChanged.connect(self.editTextChanged)
        self._ui.highLighted_comboBox.highlighted['QString'].connect(self.highlighted)
        self._ui.checkable_comboBox.itemChecked.connect(self.checkedCombo)
        self._ui.withDelegate_comboBox.currentIndexChanged['QString'].connect(self.treeCombo)
        
        self._ui.addItems_pushButton.released.connect(self.addItems)
        self._ui.clear_pushButton.released.connect(self._ui.result_textEdit.clear)


    def activatedInt(self, index):
        # Note that this signal is sent even when the choice is not changed
        if self._ui.activated_checkBox.isChecked():
            return
        resultText = self.newTextFormat('activated (INT)', index)
        self.appendResult(resultText)


    def activatedStr(self, currentText):
        # Note that this signal is sent even when the choice is not changed
        if not self._ui.activated_checkBox.isChecked():
            return
        resultText = self.newTextFormat('activated (STR)', currentText)
        self.appendResult(resultText)


    def currentIndexChanged(self, currentItem):
        # changes either through user interaction or programmatically
        resultText = self.newTextFormat('current index changed (STR)', currentItem)
        self.appendResult(resultText)


    def editTextChanged(self, currentItem):
        resultText = self.newTextFormat('edit text changed (STR)', currentItem)
        self.appendResult(resultText)


    def highlighted(self, currentItem):
        resultText = self.newTextFormat('highlight (STR)', currentItem)
        self.appendResult(resultText)


    def checkedCombo(self, item, state):
        resultText = self.newTextFormat('Checked ComboBox', item.text(), state)
        self.appendResult(resultText)


    def treeCombo(self, currentItem):
        pass


    def addItems(self):
        if self._index > 26:
            self.appendResult("No adding after Z")
            return
        
        suffix = chr(64+self._index)
        itemName = 'Item_{}'.format(suffix)
        self._ui.activated_comboBox.addItem(itemName)
        self._ui.currentIndexChanged_comboBox.addItem(itemName)
        self._ui.editTextChanged_comboBox.addItem(itemName)
        self._ui.highLighted_comboBox.addItem(itemName)
        self._ui.checkable_comboBox.addCheckName(itemName)
        self._index += 1


    def newTextFormat(self, signalType, *currentText):
        txt = f'----- {signalType} -----'
        for t in currentText:
            txt += f'\n{t}'
        return txt


    def appendResult(self, newText):
        currentResult = self._ui.result_textEdit.toPlainText()
        result  = '{}\n\n{}'.format(newText, currentResult)
        self._ui.result_textEdit.setText(result)


# launch UI
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = ComboBox_main()
    window.show()
    app.exec_()