from PyQt4 import QtGui, QtCore

class ProcessDialog(QtGui.QDialog):
	def __init__(self, parent=None, fixedHeight=-1):
		QtGui.QDialog.__init__(self)
		if fixedHeight != -1:
			self.setFixedHeight(fixedHeight)

		self.resize(450, 350)
		self.setModal(True)
		self.setWindowTitle('Processing....')
		self.setObjectName('PROCESS_DIALOG')
		self.activityLog = QtGui.QListWidget()

		self.layout = QtGui.QVBoxLayout()
		self.layout.setSpacing(0)
		self.layout.addWidget(self.activityLog, 0)
		self.layout.setContentsMargins(0,0,0,0)
		self.setLayout(self.layout)

	def keyPressEvent(self, QKeyEvent):
		if QKeyEvent.key()==QtCore.Qt.Key_Escape:
			return

	def updateLog(self, message='', success=False, warning=False, error=False):
		import datetime
		time = datetime.time(datetime.datetime.now().hour, datetime.datetime.now().minute, datetime.datetime.now().second)
		time = str(time)
		processWidget = QtGui.QListWidgetItem(time + ': ' +message)
		processWidget.setFlags(QtCore.Qt.ItemIsEnabled)

		if warning == True:
			processWidget.setTextColor(QtGui.QColor('orange'))
		if error == True:
			processWidget.setTextColor(QtGui.QColor('red'))
		if success == True:
			processWidget.setBackgroundColor(QtGui.QColor('green'))

		self.activityLog.addItem(processWidget)
		self.activityLog.scrollToItem(processWidget)
		QtGui.qApp.processEvents()

	def clearLog(self):
		self.activityLog.clear()