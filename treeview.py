import sys
import random
from PyQt5 import QtWidgets, uic

import treeViewCustom as tvc

class Treeview_main(QtWidgets.QDialog):

    def __init__(self):
        super(Treeview_main, self).__init__()
        uiFile = __file__.replace('.py', '.ui')
        self._ui = uic.loadUi(uiFile, self)
        self._treeModel = None
        self._comboDelegate = None
        self.setup()
        self.connectSignals()


    def setup(self):
        self._treeModel = tvc.TreeModel(self.generateData())
        self._ui.treeView.setModel(self._treeModel)

        self._ui.treeView.setAlternatingRowColors(True)
        self._ui.treeView.setUniformRowHeights(True)
        header = self._ui.treeView.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.swapSections(0,1)

        self._comboDelegate = tvc.ComboDelegate(self, ["Option1", "Option2", "Option3"])
        self._comboDelegate.comboChanged.connect(self.comboChanged)
        self._ui.treeView.setItemDelegateForColumn(4, self._comboDelegate)

        self.setPersistentComboBoxes(self._treeModel.getRootItem())


    def connectSignals(self):
        self._ui.regen_pushButton.released.connect(self.setup)
        self._ui.add_pushButton.released.connect(self.addItem)
        self._ui.remove_pushButton.released.connect(self.removeItem)
        self._ui.treeView.selectedItem.connect(self.selectedItem)
        self._ui.treeView.menuActionA.connect(self.menuActionA)
        self._ui.treeView.menuActionB.connect(self.menuActionB)
        self._ui.treeView.menuActionC.connect(self.menuActionC)


# ---------- refresh all delegate's widgets
    def setPersistentComboBoxes(self, parentItem):
        for childItem in parentItem.getAllChildren():
            if childItem.getType() == 'file':
                parentIndex = self._treeModel.createIndex(parentItem.getRow(), 0, parentItem)
                index = self._treeModel.index(childItem.getRow(), 4, parentIndex)
                self.openComboBox(index)

            if childItem.haveChildren():
                self.setPersistentComboBoxes(childItem)


# ---------- open delegate's widgets 
    def openComboBox(self, index):
        self.closeComboBox(index)
        self._ui.treeView.openPersistentEditor(index)


# ---------- open delegate's widgets
    def closeComboBox(self, index):
        if self._ui.treeView.isPersistentEditorOpen(index):
            self._ui.treeView.closePersistentEditor(index)


    def addItem(self):
        index = self._ui.treeView.currentIndex()
        if not index.isValid():
            return
        item = index.internalPointer()
        itemType = item.getType()
        parentItem = item.getParent()
        
        if itemType == 'file':
            fileID = parentItem.childrenSize()
            folderType = parentItem.getName().split('_')[0]
            fileData = self.generateFileData(fileID, folderType)
            index = self._treeModel.insertFile(parentItem, fileData)
            self.openComboBox(index)
            
        elif itemType == 'folder':
            folderID = parentItem.childrenSize()
            folderName, folderType = self.generateFolderName(folderID)
            fileDatas = self.addFiles(folderType)
            folderItem = self._treeModel.insertFolder(parentItem, folderName, fileDatas)
            self.setPersistentComboBoxes(folderItem)
        
    
    def removeItem(self):
        index = self._ui.treeView.currentIndex()
        if not index.isValid():
            return
        
        item = index.internalPointer()
        if item.isUsage():
            return 
        
        self.closeComboBox(index)
        self._treeModel.removeItem(item)
        

    def selectedItem(self, item, extraText=None):
        txt = '----- This is From Selected Item\n'
        if extraText:
            txt = f'{extraText}\n'

        txt += f'name --> {item.getName()}'
        txt += f'\nSize --> {item.getData(2)}'
        txt += f'\nFileType --> {item.getData(3)}'
        txt += f'\nOptions --> {item.getOption()}'
        txt += f'\nState --> {bool(item.checkedState)}'
        self._ui.textEdit.clear()
        self._ui.textEdit.setText(txt)


    def menuActionA(self, item):
        self.selectedItem(item, '----- This is From Context Menu A')


    def menuActionB(self, item):
        self.selectedItem(item, '----- This is From Context Menu B')


    def menuActionC(self, item):
        self.selectedItem(item, '----- This is From Context Menu C')


    def comboChanged(self, newOption):
        self._ui.textEdit.clear()
        self._ui.textEdit.setText(f'comboBoxChanged --> {newOption}')


# ---------- generate random tree data
    def generateData(self):
        def addFolders(parentData, maxRange, chance=0.5):
            folderCount = random.randint(1, maxRange) if maxRange > 2 else 1
            for folderID in range(folderCount):
                folderName, folderType = self.generateFolderName(folderID)
                if random.random() < chance and maxRange > 2:
                    parentData[folderName] = {}
                    addFolders(parentData[folderName], int(maxRange*0.5))
                else:
                    parentData[folderName] = self.addFiles(folderType)

        data = {'Users': {},
                'Applications':{}
                }
        for _, usageData in data.items():
            addFolders(usageData, 6)
        return data
    

    def generateFolderName(self, folderID):
        folderTypes = ['Pictures', 'Documents', 'Videos']
        folderType = random.sample(folderTypes, 1)[0]
        folderName = f'{folderType}_{folderID}'
        return folderName, folderType


    def addFiles(self, folderType):
        files = []
        for fileID in range(random.randint(1, 10)):
            files.append(self.generateFileData(fileID, folderType))
        return files  


    def generateFileData(self, fileID, folderType):
        fileTypes = {'Pictures': '.jpg',
                     'Documents': '.doc',
                     'Videos': '.MP4'}
        fileType = fileTypes[folderType]
        return {'filename':f'file_{fileID}{fileType}',
                'size': random.randint(50, 2000),
                'fileType': fileType[1:]
                }


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Treeview_main()
    window.show()
    app.exec_()