import random, numbers, pickle
from functools import partial

from PyQt5 import QtCore, QtWidgets, QtGui


# ========================================
# custom treeview
# ========================================      
class MyTreeview(QtWidgets.QTreeView):

    selectedItem = QtCore.pyqtSignal(object)
    menuActionA = QtCore.pyqtSignal(object)
    menuActionB = QtCore.pyqtSignal(object)
    menuActionC = QtCore.pyqtSignal(object)

    def __init__(self, parent):
        super(MyTreeview, self).__init__(parent)
        self.setSelectionMode(self.SingleSelection)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)


    def mouseReleaseEvent(self, mouseEvent):
        if mouseEvent.button() != QtCore.Qt.LeftButton:
            return super().mouseReleaseEvent(mouseEvent)
        
        index = self.currentIndex()
        if not index.isValid():
            return super().mouseReleaseEvent(mouseEvent)
        
        item = index.internalPointer()
        if item.getType() == 'file':
            self.selectedItem.emit(item)

        return super().mouseReleaseEvent(mouseEvent)


    def contextMenuEvent(self, contextMenuEvent):
        if contextMenuEvent.reason() != QtGui.QContextMenuEvent.Mouse:
            return super().contextMenuEvent(contextMenuEvent)
            
        index = self.indexAt(contextMenuEvent.pos())
        if not index.isValid():
            return super().contextMenuEvent(contextMenuEvent)
        
        item = index.internalPointer()
        if item.getType() == 'file':
            menu = QtWidgets.QMenu(self)
            actionA = menu.addAction('Action A')
            actionA.triggered.connect(partial(self.menuActionA.emit, item))

            menu.addSeparator()
            actionB = menu.addAction('Action B')
            actionB.triggered.connect(partial(self.menuActionA.emit, item))

            menu.addSection('Section')
            actionB = menu.addAction('Action C')
            actionB.triggered.connect(partial(self.menuActionA.emit, item))

            menu.exec_(self.mapToGlobal(contextMenuEvent.pos()))

        return super().contextMenuEvent(contextMenuEvent)


# ========================================
# comboBox delegate
# ========================================
class ComboDelegate(QtWidgets.QStyledItemDelegate):

    editorCreated = QtCore.pyqtSignal(QtCore.QModelIndex) 
    comboChanged = QtCore.pyqtSignal(str)

    def __init__(self, parent, items):
        super(ComboDelegate, self).__init__(parent)
        self.options = items


    def createEditor(self, parent, option, index):
        comboBox = QtWidgets.QComboBox(parent)
        font = comboBox.font()
        font.setPointSize(8)
        comboBox.setFont(font)
        comboBox.setStyleSheet("background-color: white;\n"
                               "border: 1px solid gray;\n"
                               "padding: 1px 3px 1px 3px;")
        comboBox.addItems(self.options)
        comboBox.currentIndexChanged.connect(self.currentIndexChanged)
        self.editorCreated.emit(index)
        return comboBox


    def currentIndexChanged(self):
        comboBox = self.sender()
        self.commitData.emit(comboBox)
        self.comboChanged.emit(comboBox.currentText())


    def setEditorData(self, editor, index):
        if not index.isValid():
            return 

        editor.blockSignals(True) # block signals that are not caused by the user
        item = index.internalPointer()
        num = self.options.index(item.getOption())
        editor.setCurrentIndex(num)
        editor.blockSignals(False)


    def setModelData(self, editor, model, index):
        item = index.internalPointer()
        item.setOption(editor.currentText())


    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)
        

# ========================================
# setup model with data given
# ========================================
class TreeModel(QtCore.QAbstractItemModel):

    itemDropped = QtCore.pyqtSignal(object)

    def __init__(self, data,  parent=None):
        super(TreeModel, self).__init__(parent)
        self.rootItem = FileItem('root', 'root', None, None)
        self.setup(data)


    def refresh(self):
        self.dataChanged.emit(QtCore.QModelIndex(), QtCore.QModelIndex())

    def getRootItem(self):
        return self.rootItem
    
    def getItemFromIndex(self, index):
        return index.internalPointer() if index.isValid() else self.rootItem
    

# ---------- setup model with data given
    def setup(self, data):
        def getFolderType(folderName):
            fileTypes = {'Pictures': 'jpg',
                         'Documents': 'doc',
                         'Videos': 'MP4'}
            return fileTypes[folderName.split('_')[0]]
                    
        def setupFolderItems(data, parent):
            for keyName, dataA in data.items():
                folderData = {'fileType':getFolderType(keyName)}
                item = FileItem(keyName, 'folder', folderData, parent)
                if isinstance(dataA, dict):
                    setupFolderItems(dataA, item)
                else:
                    setupFileItems(dataA, item)

        def setupFileItems(data, parent):
            for fileData in data:
                FileItem(fileData['filename'], 'file', fileData, parent)

        for keyName, folderData in data.items():
            item = FileItem(keyName, 'usage', None, self.rootItem)
            setupFolderItems(folderData, item)


# ---------- model view stuff
    def rowCount(self, parent):
        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childrenSize()
    

    def columnCount(self, parent):
        return 5


    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.NoItemFlags
        
        item = index.internalPointer()
        column = index.column()
        if column == 1 and not item.isUsage():
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable
        
        if item.getType() == 'file':
            if 3 <= column <= 4:
                return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled #| QtCore.Qt.ItemIsDropEnabled
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsDragEnabled #| QtCore.Qt.ItemIsDropEnabled
        
        if item.getType() == 'folder':
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDropEnabled
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        

    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()
        column = index.column()
        item = index.internalPointer()

        if role == QtCore.Qt.DisplayRole:
            return item.getName() if column == 0 else item.getData(column)
        
        if role == QtCore.Qt.EditRole and column in [0, 2]:
            return item.getData(column) if column == 2 else item.getName()

        if role == QtCore.Qt.TextAlignmentRole:
            if column == 1:
                return QtCore.Qt.AlignHCenter

        if role == QtCore.Qt.BackgroundRole:
            if item.getType() == 'file':
                if item.getData(3) == 'jpg':
                    if item.getCheckedState():
                        return QtGui.QBrush(QtCore.Qt.red)
                    return QtGui.QBrush(QtCore.Qt.darkRed)
                    
                if item.getData(3) == 'doc':
                    if item.getCheckedState():
                        return QtGui.QBrush(QtCore.Qt.green)
                    return QtGui.QBrush(QtCore.Qt.darkGreen)
                
                if item.getData(3) == 'MP4':
                    if item.getCheckedState():
                        return QtGui.QBrush(QtCore.Qt.cyan)
                    return QtGui.QBrush(QtCore.Qt.darkCyan)

        if role == QtCore.Qt.CheckStateRole:
            if column == 1 and not item.isUsage():
                return item.getCheckedState()
        
        return QtCore.QVariant()


    def setData(self, index, value, role):
        if not index.isValid():
            return False

        item = index.internalPointer()
        if role == QtCore.Qt.CheckStateRole:
            item.setCheckedState(value)
            self.refresh()
            return True
        
        column = index.column()
        if role == QtCore.Qt.EditRole and column in [0, 2]:
            if column == 2 and not isinstance(value, numbers.Number):
                return False
            item.setData(column, value)
            self.refresh()
            return True
        return False


    def headerData(self, section, orientation, role):
        header = ['Name', 'State', 'Size', 'FileType', 'Delegate']
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return header[section]
        return None


# ---------- insert rows
    def insertFolder(self, parentItem, name, data):
        parentIndex = self.createIndex(parentItem.getRow(), 0, parentItem)
        start = parentItem.childrenSize()
        end = start + 1
        
        self.beginInsertRows(parentIndex, start, end)
        folderItem = FileItem(name, 'folder', None, parentItem)
        self.endInsertRows()
        self.layoutChanged.emit()

        for fileData in data:
            self.insertFile(folderItem, fileData)

        parentItem.updateParentCheckState()
        return folderItem


    def insertFile(self, parentItem, data):
        parentIndex = self.createIndex(parentItem.getRow(), 0, parentItem)
        start = 0
        if parentItem.haveChildren():
            start = parentItem.childrenSize()
        end = start + 1
            
        self.beginInsertRows(parentIndex, start, end)
        item = FileItem(data['filename'], 'file', data, parentItem)
        self.endInsertRows()
        self.layoutChanged.emit()

        parentItem.updateParentCheckState()
        return item


# ---------- remove rows
    def removeItem(self, item):
        parentItem = item.getParent()
        parentIndex = self.createIndex(parentItem.getRow(), 0, parentItem)
        row = item.getRow()

        self.beginRemoveRows(parentIndex, row, row)
        parentItem.removeChild(row)
        self.endRemoveRows()
        self.layoutChanged.emit()

        parentItem.updateParentCheckState()


# ---------- drag and drop 
    def supportedDropActions(self):
        return QtCore.Qt.MoveAction# | Qt.CopyAction

    def mimeTypes(self):
        return ['bstream', 'text/xml']


    def mimeData(self, indexes):
        mimedata = QtCore.QMimeData()
        bstream = pickle.dumps(self.getItemFromIndex(indexes[0]))
        mimedata.setData('bstream', bstream)
        return mimedata


    def dropMimeData(self, mimedata, action, row, column, parentIndex):
        if action == QtCore.Qt.IgnoreAction: 
            return True  

        item = pickle.loads(mimedata.data('bstream'))
        parentItem = self.getItemFromIndex(parentIndex)
        if item.getFileType() != parentItem.getFileType():
            return False
        
        item.setParent(parentItem)
        self.insertRow(parentItem.childrenSize(), parentIndex)
        parentItem.updateParentCheckState()
        self.refresh()
        self.itemDropped.emit(item)
        return True


    def insertRow(self, row, parent):
        # print (f'Inserting row {row}')
        return self.insertRows(row, 1, parent)
    

    def insertRows(self, row, count, parent):
        # print (f'Inserting rowsssssss {row}')
        self.beginInsertRows(parent, row, row)
        self.endInsertRows()
        return True


    def removeRows(self, row, count, parentIndex):
        # print (f'removing rowsssssss {row}')
        self.beginRemoveRows(parentIndex, row, row)
        parentItem = self.getItemFromIndex(parentIndex)
        parentItem.removeChild(row)
        parentItem.updateParentCheckState()
        self.endRemoveRows()       
        return True


# ---------- don't touch
    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.getChild(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return  QtCore.QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return  QtCore.QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.getParent()

        if parentItem == self.rootItem:
            return  QtCore.QModelIndex()

        return self.createIndex(parentItem.getRow(), 0, parentItem)


# ========================================
# data object for model's item
# ========================================
class FileItem():
    def __init__(self, name, type, data, parent=None):
        self._data = data
        self._name = name
        self._type = type
        self.checkedState = False

        self._parent = parent
        self._children = []
        if self._parent:
            self._parent.addChild(self)


    def setName(self, name):
        self._name = name

    def getName(self):
        return self._name

    def getType(self):
        return self._type

    def getOption(self):
        return self._data['option']
    
    def setOption(self, option):
        self._data['option'] = option
        
    def getFileType(self):
        return self._data['fileType']

    def isUsage(self):
        return self._type == 'usage'

    def getData(self, column):
        if not self._data:
            return None
        if column == 2 and 'size' in self._data:
            return self._data['size']
        if column == 3 and 'fileType' in self._data:
            return self._data['fileType']
        return None

    def setData(self, column, value):
        dataKeys = ['name', 'size', 'fileType', 'option']
        if column == 0:
            self._name = value
        self._data[dataKeys[column]] = value


    def setCheckedState(self, stateId):
        self.checkedState = stateId

        for child in self._children:
            child.setCheckedState(stateId)
        
        self._parent.updateParentCheckState()
  

    def updateParentCheckState(self):
        if self._type in ['root', 'usage']:
            return 
        
        if self.childrenSize() == 1:
            self.checkedState = self._children[0].checkedState
        else:         
            cStates = []
            self.getAllChildrenStates(cStates)
            cStates = set(cStates)
            if len(cStates) > 1:
                self.checkedState = 1        
            else :
                self.checkedState = 0 if 0 in cStates else 2

        self._parent.updateParentCheckState()


    def getAllChildrenStates(self, cStates):
        for child in self._children:
            if child.childrenSize() == 0:
                cStates.append(child.checkedState)
            else:
                child.getAllChildrenStates(cStates)
        

    def getCheckedState(self):
        if self.checkedState == 2:
            return QtCore.Qt.Checked
        elif self.checkedState == 1:
            return QtCore.Qt.PartiallyChecked
        return QtCore.Qt.Unchecked


    def getCheckedStateID(self) :
        return self.checkedState


# ---------- 
    def getRow(self):
        return self._parent._children.index(self)
    
    def setParent(self, parentItem):
        self._parent = parentItem
        self._parent.addChild(self)

    def getParent(self):
        return self._parent
    
    def haveChildren(self):
        return bool(self._children)

    def getAllChildren(self):
        return self._children

    def childrenSize(self):
        return len(self._children)

    def getChild(self, index):
        return self._children[index]

    def addChild(self, child):
        self._children.append(child)

    def removeChild(self, idx):
        self._children.pop(idx)
