import sys, random

from PyQt5 import QtWidgets, uic
import tableViewCustom as tvc

# data --> bool, str, value, combobox

categories = ["Food", "Groceries", "Transportation",
                "Personal Care", "Medical Stuff", "Clothing",
                "Sport", "Movies", "Games", "Electronics",
                "Vacation", "Stock", "Others", "Gardening",
                "Furnitures", "Utilities/Bills", "Rent"]
banks = ['POSB', 'OCBC', 'UOB', 'HSBC']
incomeTypes = ["Salary", "Claim", "Dividend"]

class TableView_main(QtWidgets.QDialog):

    def __init__(self):
        super(TableView_main, self).__init__()
        self._data = None
        uiFile = __file__.replace('.py', '.ui')
        self._ui = uic.loadUi(uiFile, self)
        self._tableModel = None
        self.intialSetup()
        self.connectSignals()


    def intialSetup(self):
        self.generateInitalData()
        header = self._ui.tableView.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)


    def generateInitalData(self):
        self._data = [self.generateData() for _ in range(random.randint(3, 10))]
        self._tableModel = tvc.TableModel(self._data)
        self._tableModel.rowEnabled.connect(self.rowEnabled)
        self._ui.tableView.setModel(self._tableModel)
        for row, data in enumerate(self._data):
            self.createComboBox(row, data)


    def createComboBox(self, row, data):
        if not data[0]:
            return
        data[3] = self.getRandomComboValue()
        index = self._tableModel.index(row, 3)
        comboBox = QtWidgets.QComboBox()
        comboList = incomeTypes #if data[0] else banks
        comboBox.addItems(comboList)
        comboBox.setCurrentIndex(comboList.index(data[3]))
        comboBox.currentIndexChanged['QString'].connect(self.updateComboValue)
        self._ui.tableView.setIndexWidget(index, comboBox)


    def connectSignals(self):
        self._ui.tableView.selectedCellIndex.connect(self.printSelCellIndex)
        self._ui.tableView.cellMouseOver.connect(self.printCellMouseOver)
        self._ui.tableView.menuActionA.connect(self.printMenuActionA)
        self._ui.tableView.menuActionB.connect(self.printMenuActionB)
        self._ui.tableView.menuActionC.connect(self.printMenuActionC)
        self._ui.tableView.enterWidget.connect(self.printEnteringTableView)
        self._ui.tableView.leaveWidget.connect(self.printLeavingTableView)

        self._ui.add_pushButton.released.connect(self.addItem)
        self._ui.remove_pushButton.released.connect(self.removeItem)
        self._ui.regen_pushButton.released.connect(self.generateInitalData)
        

    def addItem(self):
        start = len(self._data)
        self._tableModel.beginInsertRows(self._ui.tableView.rootIndex(), start, start+1)
        data = self.generateData()
        self._data.append(data)
        self._tableModel.endInsertRows()
        self._tableModel.layoutChanged.emit()
        self.createComboBox(start, data)


    def removeItem(self):
        index = self._ui.tableView.currentIndex()
        row = index.row()
        self._tableModel.beginRemoveRows(self._ui.tableView.rootIndex(), row, row)
        if self._data:
            self._data.pop(row)
        self._tableModel.endRemoveRows()

        
    def printSelCellIndex(self, row, column, mouseAction='Mouse Click'):
        txt = f'---------- {mouseAction} ----------\n'
        txt += '---------- Cell Info ----------\n'
        if self._data:
            txt += f'row -- {row}\ncolumn -- {column}\n'
            txt += f'{self._data[row][column]}\n'
            txt += '\n---------- Row Info ----------\n'
            txt += '\n'.join(f'{self._data[row][c]}' for c in range(4))
        else:
            txt = 'NO DATA !!!!'

        self._ui.textEdit.clear()
        self._ui.textEdit.setText(txt)


    def printCellMouseOver(self, row, column):
        if self._ui.mouseOver_checkBox.isChecked():
            self.printSelCellIndex(row, column, 'Mouse Hover')


    def updateComboValue(self, value):
        index = self._ui.tableView.currentIndex()
        row = index.row()
        self._data[row][3] = value
        txt = '---------- Update Bank Name ----------\n'
        if self._data[row][0]:
            txt = '---------- Update Income Type ----------\n'
        txt += str(self._data[row][3])
        self._ui.textEdit.clear()
        self._ui.textEdit.setText(txt)


    def printMenuActionA(self, row, column):
        txt = '---------- Menu Action A----------\n'
        txt += f'row -- {row}\ncolumn -- {column}\n'
        txt += f'{self._data[row][column]}\n'
        self._ui.textEdit.clear()
        self._ui.textEdit.setText(txt)


    def printMenuActionB(self, row, column):
        txt = '---------- Menu Action B----------\n'
        txt += f'row -- {row}\ncolumn -- {column}\n'
        txt += f'{self._data[row][column]}\n'
        self._ui.textEdit.clear()
        self._ui.textEdit.setText(txt)


    def printMenuActionC(self, row, column):
        txt = '---------- Menu Action C----------\n'
        txt += f'row -- {row}\ncolumn -- {column}\n'
        txt += f'{self._data[row][column]}\n'
        self._ui.textEdit.clear()
        self._ui.textEdit.setText(txt)


    def printEnteringTableView(self):
        txt = '---------- Entering TableView----------\n'
        self._ui.textEdit.clear()
        self._ui.textEdit.setText(txt)


    def printLeavingTableView(self):
        txt = '---------- Leaving TableView----------\n'
        self._ui.textEdit.clear()
        self._ui.textEdit.setText(txt)

    
    def rowEnabled(self, row):
        index = self._tableModel.index(row, 3)
        if self._data[row][0]:
            self.createComboBox(row, self._data[row])
        else:
            self._ui.tableView.setIndexWidget(index, None)
            self._data[row][3] = None


# ---------- generate random tree data
    def generateData(self):
        state = random.sample([True, False], 1)[0]
        category = random.sample(categories, 1)[0]
        ranFloat = float("{0:.2f}".format(random.uniform(20, 0)))
        comboVal = self.getRandomComboValue(state)
        return [state, category, ranFloat, comboVal]
    

    def getRandomComboValue(self, state=True):
        if state:
            return random.sample(incomeTypes, 1)[0]
        return None
    

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = TableView_main()
    window.show()
    app.exec_()