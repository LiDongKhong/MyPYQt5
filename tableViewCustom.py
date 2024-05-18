import numbers
from functools import partial

from PyQt5 import QtCore, QtWidgets, QtGui

# ========================================
# custom tabel view
# ========================================      
# data --> bool, str, value, combobox
class MyTableView(QtWidgets.QTableView):

    selectedCellIndex = QtCore.pyqtSignal(int, int)
    cellMouseOver = QtCore.pyqtSignal(int, int)
    menuActionA = QtCore.pyqtSignal(int, int)
    menuActionB = QtCore.pyqtSignal(int, int)
    menuActionC = QtCore.pyqtSignal(int, int)
    enterWidget = QtCore.pyqtSignal()
    leaveWidget = QtCore.pyqtSignal()

    def __init__(self, parent):
        super(MyTableView, self).__init__(parent)
        self.setMouseTracking(True)


    def mouseReleaseEvent(self, mouseEvent):
        if mouseEvent.button() == QtCore.Qt.LeftButton:
            index = self.currentIndex()
            self.selectedCellIndex.emit(index.row(), index.column())
        
        return super().mouseReleaseEvent(mouseEvent)
    

    def mouseMoveEvent(self, event):
        if not event.buttons():
            index = self.indexAt(event.pos())
            if not index.row() == -1 and not index.column() == -1:
                self.cellMouseOver.emit(index.row(), index.column())
        super().mouseMoveEvent(event)


    def contextMenuEvent(self, ContextMenuEvent):
        if ContextMenuEvent.reason() != QtGui.QContextMenuEvent.Mouse:
            return super().contextMenuEvent(ContextMenuEvent)
            
        index = self.indexAt(ContextMenuEvent.pos())
        if not index.isValid():
            return super().contextMenuEvent(ContextMenuEvent)
        
        column = index.column()
        menu = None
        if 0 <= column <= 2:
            menu = QtWidgets.QMenu(self)
            actionA = menu.addAction('Action A')
            actionA.triggered.connect(partial(self.emitMenuActionA, index))

        if 1 <= column <= 2:
            menu.addSeparator()
            actionB = menu.addAction('Action B')
            actionB.triggered.connect(partial(self.emitMenuActionB, index))

        if column == 2:
            menu.addSection('Section')
            actionB = menu.addAction('Action C')
            actionB.triggered.connect(partial(self.emitMenuActionC, index))

        if menu:    
            menu.exec_(self.mapToGlobal(ContextMenuEvent.pos()))

        return super().contextMenuEvent(ContextMenuEvent)

    def emitMenuActionA(self, index):
        self.menuActionA.emit(index.row(), index.column())
    
    def emitMenuActionB(self, index):
        self.menuActionB.emit(index.row(), index.column())

    def emitMenuActionC(self, index):
        self.menuActionC.emit(index.row(), index.column())

    def enterEvent(self, event):
        self.enterWidget.emit()
        super().leaveEvent(event)

    def leaveEvent(self, event):
        self.leaveWidget.emit()
        super().enterEvent(event)
        
# ========================================
# custom table view model
# ========================================    
class TableModel(QtCore.QAbstractTableModel):
    
    rowEnabled = QtCore.pyqtSignal(int)

    def __init__(self, data, parent=None):
        super(TableModel, self).__init__(parent)
        self._data = data

    def refresh(self):
        self.dataChanged.emit(QtCore.QModelIndex(), QtCore.QModelIndex())

    def rowCount(self, parent):
        return len(self._data)
    
    def columnCount(self, parent):
        return 4
    
    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.NoItemFlags
        
        column = index.column()
        if column == 0:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsSelectable
        if 1 <= column <= 2:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable


    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()
        
        row = index.row()
        column = index.column()
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            if 1 <= column <= 2:
                return self._data[row][column]
        
        if role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter

        if role == QtCore.Qt.BackgroundRole and not self._data[row][0]:
            return QtGui.QBrush(QtCore.Qt.darkGray)
        
        if role == QtCore.Qt.ForegroundRole and not self._data[row][0]:
             return QtGui.QBrush(QtCore.Qt.white)
            
        if role == QtCore.Qt.CheckStateRole and column == 0:
            return QtCore.Qt.Checked if self._data[row][0] else QtCore.Qt.Unchecked
        
        return QtCore.QVariant()
        
        
    def setData(self, index, value, role):
        if not index.isValid():
            return False
        
        row = index.row()
        column = index.column()
        if role == QtCore.Qt.EditRole and 1 <= column <= 2:
            if column == 2 :
                if not isinstance(value, numbers.Number):
                    self.refresh()
                    return False
                else:
                    value = float("{0:.2f}".format(value))
            self._data[row][column] = value
            self.refresh()
            return True
        
        if role == QtCore.Qt.CheckStateRole and column == 0:
            self._data[row][0] = bool(value)
            self.refresh()
            self.rowEnabled.emit(row)
            return True

        return False


    def headerData(self, section, orientation, role):
        header = ['CheckBox', 'String', 'Number', 'Widget']
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return header[section]

            if orientation == QtCore.Qt.Vertical:
                return section



