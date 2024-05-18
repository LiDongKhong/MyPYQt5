from PyQt5 import QtGui, QtCore, QtWidgets


class CollapsibleArrow(QtWidgets.QFrame):
    def __init__(self, parent=None):
        QtWidgets.QFrame.__init__(self, parent=parent)
        self.arrowState = True
        self.arrowOpen = None
        self.arrowClose = None
        self.arrowCurrent = None
        self.setStyleSheet("QFrame {\
        background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #545454, stop: 1 #232323);\
        border-top: 1px solid rgba(192, 192, 192, 255);\
        border-left: 1px solid rgba(192, 192, 192, 255);\
        border-right: 1px solid rgba(32, 32, 32, 255);\
        border-bottom: 1px solid rgba(64, 64, 64, 255);\
        margin: 0px, 0px, 0px, 0px;\
        padding: 0px, 0px, 0px, 0px;}\
        QFrame:hover {background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #232323, stop: 1 #545454);\
        }")
        self.setSize(24)
        
    def setArrow(self, openState=None):
        if openState != None:
            self.arrowState = openState
        self.arrowCurrent = self.arrowOpen if self.arrowState else self.arrowClose        
       
    def setSize(self, size):
        self.setMinimumSize(size, size)
        self.setMaximumSize(size, size)
        self.arrowOpen = (QtCore.QPointF(4.0, 8.0), QtCore.QPointF(size-4, 8.0), QtCore.QPointF(int(size/2), size-8))
        self.arrowClose = (QtCore.QPointF(8.0, 4.0), QtCore.QPointF(size-8, int(size*0.5)), QtCore.QPointF(8.0, size-4))
        self.setArrow()

    def paintEvent(self, event):        
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setBrush(QtGui.QColor(192, 192, 192))
        qp.setPen(QtGui.QColor(64, 64, 64))
        qp.drawPolygon(*self.arrowCurrent)
        qp.end()
        

class CollapsibleTitleLabel(QtWidgets.QLabel):
    def __init__(self, parent = None):
        QtWidgets.QLabel.__init__(self, parent = parent)
        self.setStyleSheet("CollapsibleTitleLabel {background-color: rgba(0, 0, 0, 0);\
        color: white;\
        border-left: 1px solid rgba(128, 128, 128, 255);\
        border-top: 0px transparent;\
        border-right: 0px transparent;\
        border-bottom: 0px transparent;\
        }")


class CollapsibleTitleFrame(QtWidgets.QFrame):

    opened = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.arrow = CollapsibleArrow(self)    
        self.label = CollapsibleTitleLabel(self)
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("QFrame {\
        background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #545454, stop: 1 #232323);\
        border-top: 1px solid rgba(192, 192, 192, 255);\
        border-left: 1px solid rgba(192, 192, 192, 255);\
        border-right: 1px solid rgba(64, 64, 64, 255);\
        border-bottom: 1px solid rgba(64, 64, 64, 255);\
        margin: 0px, 0px, 0px, 0px;\
        padding: 0px, 0px, 0px, 0px;\
        }")

    def setOpenState(self, state):
        self.arrow.setArrow(state)

    def setSize(self, size):
        self.arrow.setSize(size)
        self.setMinimumHeight(size)
        self.setMaximumHeight(size)
        self.label.setMinimumHeight(size)
        self.label.move(QtCore.QPoint(size, 0))

    def mousePressEvent(self, event):
        self.opened.emit()
        return super(CollapsibleTitleFrame, self).mousePressEvent(event)


class CollapsibleFrame(QtWidgets.QFrame):

    opened = QtCore.pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.openState = True
        self.contentWidgets = {}
        self.init_frameSettings()

        self.mainLayout = self.createVerticalLayout()
        self.setLayout(self.mainLayout)

        self.titleFrame = self.init_titleFrame()
        self.mainLayout.addWidget(self.titleFrame)

        self.contentFrame = self.init_contentFrame()
        self.contentLayout = self.createVerticalLayout()
        self.contentFrame.setLayout(self.contentLayout)
        self.mainLayout.addWidget(self.contentFrame)


    def isOpen(self):
        return self.openState

    def setHeight(self, heightVal):
        self.titleFrame.setSize(heightVal)

    def setText(self, text):
        self.titleFrame.label.setText(f'  {text}')

    def addWidget(self, widgetName, widget):
        self.contentWidgets[widgetName] = widget
        self.contentLayout.addWidget(widget)

    def getWidget(self, widgetName):
        return self.contentWidgets[widgetName]

    def getAllWidgets(self):
        return [widget for widget in self.contentWidgets.values()]


    def init_frameSettings(self):
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("QFrame {\
        border: 0px solid;\
        margin: 0px, 0px, 0px, 0px;\
        padding: 0px, 0px, 0px, 0px;\
        }")

    def init_titleFrame(self):
        frame = CollapsibleTitleFrame()
        frame.setSize(24)
        frame.opened.connect(self.toggleFrame)
        return frame

    def toggleFrame(self):
        self.openState = not self.openState
        self.contentFrame.setVisible(self.openState)
        self.titleFrame.setOpenState(self.openState)
        self.opened.emit(self.openState)

    def init_contentFrame(self):
        contentFrame = QtWidgets.QFrame()
        contentFrame.setContentsMargins(3, 3, 3, 3)
        contentFrame.setStyleSheet("QFrame {\
        background-color: grey;\
        border-top: 1px solid rgba(64, 64, 64, 255);\
        border-left: 1px solid rgba(64, 64, 64, 255);\
        border-right: 1px solid rgba(192, 192, 192, 255);\
        border-bottom: 1px solid rgba(192, 192, 192, 255);\
        margin: 0px, 0px, 0px, 0px;\
        padding: 0px, 0px, 0px, 0px;\
        }")
        return contentFrame

    def createVerticalLayout(self):
        vLayout = QtWidgets.QVBoxLayout()
        vLayout.setContentsMargins(0, 0, 0, 0)
        vLayout.setSpacing(0)
        return vLayout
    


if __name__ == '__main__':
    def openCloseFrame(state):
        if state:
            print ('frame is open')
        else:
            print ('frame is close')

    import sys
    app = QtWidgets.QApplication(sys.argv)
    win = QtWidgets.QMainWindow()
    win.setStyleSheet("QMainWindow {background-color: green;}")
    w = QtWidgets.QWidget()   
    win.setCentralWidget(w)
    l = QtWidgets.QVBoxLayout()
    l.setSpacing(0)
    l.setAlignment(QtCore.Qt.AlignTop)
    w.setLayout(l)

    f1 = CollapsibleFrame()
    f1.opened.connect(openCloseFrame)
    f1.setText('test')
    f1.setHeight(30)
    f1.addWidget('btn1', QtWidgets.QPushButton('a'))
    f1.addWidget('btn2', QtWidgets.QPushButton('b'))
    f1.addWidget('btn3', QtWidgets.QPushButton('c'))
    l.addWidget(f1)

    win.show()
    
    sys.exit(app.exec_())