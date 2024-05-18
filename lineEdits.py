import sys

from PyQt5 import QtWidgets, uic


class LineEdit_main(QtWidgets.QDialog):

    def __init__(self):
        super(LineEdit_main, self).__init__()
        uiFile = __file__.replace('.py', '.ui')
        self._ui = uic.loadUi(uiFile, self)
        self.connectSignals()


    def connectSignals(self):
        self._ui.cursorPositionChanged_lineEdit.cursorPositionChanged.connect(self.cursorPosChanged)
        self._ui.editingFinished_lineEdit.editingFinished.connect(self.editingFinished)
        self._ui.returnPressed_lineEdit.returnPressed.connect(self.returnPressed)
        self._ui.selChanged_lineEdit.selectionChanged.connect(self.selectionChanged)
        self._ui.textChanged_lineEdit.textChanged.connect(self.textChanged)
        self._ui.textEdited_lineEdit.textEdited.connect(self.textEdited)

        self._ui.clearInput_pushButton.released.connect(self.clearAllInput)
        self._ui.clear_pushButton.released.connect(self._ui.result_textEdit.clear)


    def cursorPosChanged(self, a, b):
        currentText = ' {} -- {}'.format(a, b)
        resultText = self.newTextFormat('cursor position changed', currentText)
        self.appendResult(resultText)


    def editingFinished(self):
        currentText = self._ui.editingFinished_lineEdit.text()
        resultText = self.newTextFormat('editing finsished', currentText)
        self.appendResult(resultText)


    def returnPressed(self):
        currentText = self._ui.returnPressed_lineEdit.text()
        resultText = self.newTextFormat('return pressed', currentText)
        self.appendResult(resultText)


    def selectionChanged(self):
        currentText = self._ui.selChanged_lineEdit.selectedText()
        resultText = self.newTextFormat('selected changed', currentText)
        self.appendResult(resultText)


    def textChanged(self, currentText):
        # this signal is also emitted when the text is changed programmatically, for example, by calling setText().
        resultText = self.newTextFormat('text changed', currentText)
        self.appendResult(resultText)


    def textEdited(self, currentText):
        # this signal not emitted when the text is changed programmatically, for example, by calling setText().
        resultText = self.newTextFormat('text edited', currentText)
        self.appendResult(resultText)


    def newTextFormat(self, signalType, currentText):
        return '----- {} -----\n{}'.format(signalType, currentText)


    def appendResult(self, resultText):
        currentResult = self._ui.result_textEdit.toPlainText()
        result  = '{}\n\n{}'.format(resultText, currentResult)
        self._ui.result_textEdit.setText(result)


    def clearAllInput(self):
        lineEdits = [self._ui.cursorPositionChanged_lineEdit,
                     self._ui.editingFinished_lineEdit,
                     self._ui.returnPressed_lineEdit,
                     self._ui.selChanged_lineEdit,
                     self._ui.textChanged_lineEdit,
                     self._ui.textEdited_lineEdit
                     ]
        for lineEdit in lineEdits:
            lineEdit.blockSignals(True)
            lineEdit.setText('')
            lineEdit.blockSignals(False)


# launch UI
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = LineEdit_main()
    window.show()
    app.exec_()