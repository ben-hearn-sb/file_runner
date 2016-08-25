__author__ = 'ben.hearn'

"""
- File Runner is a handy Qt UI class that helps with constant batch processing on files or directories with a twist!
- You can apply any external script you have written to process the files

How to use:
- Simply drag in the directories you want to iterate over into the directories window
- Type in your desired file format

- Drag in the script you want to process your files into the script window
- Type in the name of the function you want to run
- Choose whether or not you want the program to recursively process all sub directories

- Select your desired directories and your desired script
- Click save locations to save your table data
- Click Run. It's as easy as that!

Your input functions:
- To allow the program to work straight off the bat the function you input must be structured like so:
def myTestFunction(filePath):
	# Do something with filePath

- Alternatively you can edit the class so it passes in the list of files and you can iterate the list inside your external script

Edit the class however you see fit  :)

Enjoy!
"""

from PyQt4 import QtCore, QtGui
import sys
import os
import ast
import importlib
import ntpath
from file_runner_process_dialog import ProcessDialog

class DirectoryFunctions(QtGui.QDialog):
	def __init__(self):
		QtGui.QDialog.__init__(self)

		qAppData = str(QtGui.QDesktopServices.storageLocation(QtGui.QDesktopServices.DataLocation))
		self.appDataDir = os.path.join(qAppData, 'CUSTOM_DIR')
		if not os.path.exists(self.appDataDir):
			os.makedirs(self.appDataDir)
		self.inFocusWidget = None
		self.allowedScriptExts = ['py']

		self.processDialog = ProcessDialog(fixedHeight=100)

		self.dirIn = QtGui.QDialog()
		self.dirIn.resize(1000, 500)
		self.dirIn.setWindowTitle("File Runner")
		self.dirIn.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
		width = self.dirIn.width()

		# Master display is the table view that shows our
		self.masterDisplay = QtGui.QTableWidget()
		self.masterDisplay.setColumnCount(2)
		self.masterDisplay.setHorizontalHeaderLabels(['Directories', 'Format'])
		# Setting the stretch to expand with the table
		self.masterDisplay.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Interactive)
		self.masterDisplay.horizontalHeader().resizeSection(0, width/2)
		self.masterDisplay.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)
		self.masterDisplay.verticalHeader().hide()
		self.masterDisplay.setObjectName('master_display')
		self.masterDisplay.itemPressed .connect(lambda: self.setFocusWidget(self.masterDisplay))

		# Script layout
		self.scriptPaths = QtGui.QTableWidget()
		self.scriptPaths.setColumnCount(3)
		self.scriptPaths.setHorizontalHeaderLabels(['Script Name', 'Function Name', 'Recursive'])
		self.scriptPaths.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Interactive)
		self.scriptPaths.horizontalHeader().resizeSection(0, width/2)
		self.scriptPaths.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)
		self.scriptPaths.horizontalHeader().setResizeMode(2, QtGui.QHeaderView.Stretch)
		self.scriptPaths.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
		self.scriptPaths.verticalHeader().hide()
		self.scriptPaths.setObjectName('script_paths')
		self.scriptPaths.itemPressed.connect(lambda: self.setFocusWidget(self.scriptPaths))

		# Create target layout
		btnRun = QtGui.QPushButton('Run On Selected')
		targetLayout = QtGui.QHBoxLayout()
		targetLayout.addWidget(btnRun)

		# Create appdata button layout
		btnCreateAppData = QtGui.QPushButton('Save Locations')
		btnRemoveDir = QtGui.QPushButton('Remove Entry')
		appLayout = QtGui.QHBoxLayout()
		appLayout.addWidget(btnCreateAppData)
		appLayout.addWidget(btnRemoveDir)

		masterLayout = QtGui.QVBoxLayout()
		masterLayout.addWidget(self.masterDisplay)
		masterLayout.addWidget(self.scriptPaths)
		masterLayout.addLayout(targetLayout)
		masterLayout.addLayout(appLayout)
		masterLayout.addWidget(self.processDialog)

		self.masterDisplay.setAcceptDrops(True)
		self.masterDisplay.dragEnterEvent = self.dragEnterEvent
		self.masterDisplay.dragMoveEvent = self.dragMoveEvent
		self.masterDisplay.dropEvent = self.dropEvent

		self.scriptPaths.setAcceptDrops(True)
		self.scriptPaths.dragEnterEvent = self.dragEnterEvent
		self.scriptPaths.dragMoveEvent = self.dragMoveEvent
		self.scriptPaths.dropEvent = self.scriptDropEvent

		btnCreateAppData.pressed.connect(self.createAppData)
		btnRemoveDir.pressed.connect(self.removeDir)
		btnRun.pressed.connect(self.runOnSelected)

		self.dirIn.setLayout(masterLayout)
		self.setupUI()

	def show(self):
		self.dirIn.show()

	def setFocusWidget(self, table):
		self.inFocusWidget = table

	""" Overidden QT drag/drop events """
	def dragEnterEvent(self, event):
		event.accept()

	def dragMoveEvent(self, event):
		event.accept()

	def dropEvent(self, event):
		md = event.mimeData()
		if md.hasUrls():
			for url in md.urls():
				urlPath = url.toLocalFile().toLocal8Bit().data()
				self.masterDisplay.insertRow(self.masterDisplay.rowCount())
				rowNum = self.masterDisplay.rowCount()-1
				item = QtGui.QTableWidgetItem(urlPath)
				formatItem = QtGui.QTableWidgetItem('')
				item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
				formatItem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
				self.masterDisplay.setItem(rowNum, 0, item)
				event.accept()
		else:
			event.ignore()

	def scriptDropEvent(self, event):
		md = event.mimeData()
		if md.hasUrls():
			for url in md.urls():
				urlPath = url.toLocalFile().toLocal8Bit().data()
				if not urlPath.split('.')[-1] in self.allowedScriptExts:
					continue
				self.scriptPaths.insertRow(self.scriptPaths.rowCount())
				rowNum = self.scriptPaths.rowCount()-1
				item = QtGui.QTableWidgetItem(urlPath)
				functionNameItem = QtGui.QTableWidgetItem('')
				item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
				functionNameItem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
				self.scriptPaths.setItem(rowNum, 0, item)

				pWidget = self.setCenterCheckbox()
				self.scriptPaths.setCellWidget(rowNum, 2, pWidget)
				event.accept()
		else:
			event.ignore()

	def setCenterCheckbox(self, checked=False):
		""" Sets a centred checkbox """
		recursiveCheckBox = QtGui.QCheckBox()
		recursiveCheckBox.setChecked(checked)

		pWidget = QtGui.QWidget()
		pLayout = QtGui.QHBoxLayout()
		pLayout.addWidget(recursiveCheckBox)
		pLayout.setAlignment(QtCore.Qt.AlignCenter)
		pLayout.setContentsMargins(0,0,0,0)

		pWidget.setLayout(pLayout)
		return pWidget

	def unpackCheckBox(self, table, row, column):
		return table.cellWidget(row, column).layout().itemAt(0).widget().isChecked()

	def chooseDir(self):
		""" Allows the user to choose a new directory when you right click """
		dirPath = self.openWindowsBrowser()
		indices = self.masterDisplay.selectedIndexes()
		if dirPath:
			dirPath = self.fixPathing(dirPath)
			if not os.path.isdir(dirPath):
				return
			for i in indices:
				row = i.row()
				self.createQtContent(dirPath, row, 0, self.masterDisplay)

	def addFormat(self, formatString=''):
		""" Adds the format string to the format column """
		indices = self.masterDisplay.selectedIndexes()
		for i in indices:
			row = i.row()
			column = i.column()
			self.addFormatItem(row, column, formatString)

	def addFormatItem(self, row, column, exportFormat):
		""" Adds a Qt item to the  """
		formatItem = QtGui.QTableWidgetItem(exportFormat)
		formatItem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
		self.masterDisplay.setItem(row, column, formatItem)

	def openWindowsBrowser(self):
		dirPath = QtGui.QFileDialog.getExistingDirectory(None, 'Select Directory')
		return dirPath

	def createAppData(self):
		""" We create an appdata file in this function to store the source level directories and export location """
		appDataFile = os.path.join(self.appDataDir, 'custom_dirs.txt')
		appDataDict = {}
		scriptDataDict = {}
		tableWidgets = {self.masterDisplay:appDataDict, self.scriptPaths:scriptDataDict}
		for table in tableWidgets:
			for r in range(table.rowCount()):
				for c in range(table.columnCount()):
					if c == 0:
						source = str(table.item(r, c).text())
					elif c == 1:
						if table.item(r, c) is not None:
							format_function = str(table.item(r, c).text())
						else:
							format_function = ''
					elif c == 2:
						checkBoxResult = self.unpackCheckBox(table, r, c)
						format_function += '**' + str(checkBoxResult)

				tableWidgets[table].update({source:format_function})

		with open(appDataFile, 'w+') as appDataFile:
			appDataFile.write(str(appDataDict)+'\n')
			appDataFile.write(str(scriptDataDict))

	def setupUI(self):
		""" Sets up the table UI on first boot """
		appDataFile = os.path.join(self.appDataDir, 'custom_dirs.txt')
		exportDirs = None
		scriptPaths = None
		if not os.path.exists(appDataFile):
			return
		else:
			with open(appDataFile) as f:
				i = 0
				for line in f:
					if i == 0:
						exportDirs = ast.literal_eval(line)
					elif i == 1:
						scriptPaths = ast.literal_eval(line)
					i += 1
			dicts = [exportDirs, scriptPaths]
			for index, d in enumerate(dicts):
				if index == 0:
					table = self.masterDisplay
				elif index == 1:
					table = self.scriptPaths
				if len(d) > 0:
					for index, source in enumerate(d):
						table.insertRow(index)
						content = d[source]

						# If our table is script_paths we need to split our value to get our true/false checkbox value
						if table.objectName() == 'script_paths':
							temp = d[source].split('**')
							content = temp[0]
							checked = temp[1]
							if checked == 'True':
								checked = True
							else:
								checked = False
							pWidget = self.setCenterCheckbox(checked)
							table.setCellWidget(index, 2, pWidget)

						self.createQtContent(source, index, 0, table)
						self.createQtContent(content, index, 1, table)

	def createQtContent(self, content, row, column, table):
		""" Creates a QTableWidgetItem """
		item = QtGui.QTableWidgetItem(content)
		if column == 1:
			item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
		else:
			item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
		table.setItem(row, column, item)

	def fixPathing(self, filePath):
		return filePath.replace('\\', '/')

	def removeDir(self):
		""" Removes the directory from the UI and saves the file
		    Important tip is to remove rows incrementally in reverse
		"""
		try:
			indices = self.inFocusWidget.selectedIndexes()
		except AttributeError:
			self.processDialog.updateLog(message='Please ensure widget is active', error=True)
			return
		# Get all row index
		indexes = []
		for i in indices:
			indexes.append(i.row())
		# Reverse sort rows indexes
		indexes = sorted(indexes, reverse=True)

		# Delete rows
		for rowidx in indexes:
			print 'removing', rowidx
			self.inFocusWidget.removeRow(rowidx)

	def runOnSelected(self):
		"""
			Runs over the selected directories
			Runs some checks on directories, file pathing, format etc.
		"""
		self.processDialog.clearLog()
		self.processDialog.updateLog(message='Running pre-function checks')
		indices = self.masterDisplay.selectedIndexes()
		scriptPathIndices   = self.scriptPaths.selectedItems()

		if len(indices) < 1 or len(scriptPathIndices)< 1:
			self.processDialog.updateLog(message='Please select a script and relevant directories', error=True)
			return

		row                 = scriptPathIndices[0].row()
		scriptPath          = str(self.scriptPaths.item(row, 0).text())
		scriptDir           = os.path.dirname(scriptPath)
		scriptName          = ntpath.basename(scriptPath).split('.')[0]
		functionName        = str(self.scriptPaths.item(row, 1).text())
		recursive           = self.unpackCheckBox(self.scriptPaths, row, 2)

		if not os.path.exists(scriptPath):
			self.processDialog.updateLog(message='Your script no longer lives in this location\nPlease remove entry and choose new location', error=True)
			return

		if not scriptDir in sys.path:
			sys.path.append(scriptDir)
		try:
			externalFunc = getattr(importlib.import_module(scriptName), functionName)
		except AttributeError:
			self.processDialog.updateLog(message='Please check script pathing and function name is correct',error=True)
			return

		checkDirs = self.checkExistingDirs(indices)
		if len(checkDirs) > 0:
			nonExistent = ''
			for d in checkDirs:
				nonExistent += d + '\n'
			self.processDialog.updateLog(message='One or more selected dirs does not exist\n%s'%nonExistent, error=True)
			return

		# Once all our checks are done we can run the main chunk of the function
		for i in indices:
			row = i.row()
			sourceDir = self.masterDisplay.item(row, 0)
			formatString = self.masterDisplay.item(row, 1)

			if sourceDir is None or formatString is None or sourceDir == '' or formatString == '':
				self.processDialog.updateLog(message='Cannot run without a source dir or format' ,error=True)
				return

			sourceDir = str(sourceDir.text())
			formatString = str(formatString.text())
			for root, dirs, files in os.walk(sourceDir):
				self.runExternalFunction(root, files, formatString, externalFunc)
				if recursive == False:
					break

		self.processDialog.updateLog(message='Process complete', success=True)

	def checkExistingDirs(self, indices):
		nonExistent = []
		for i in indices:
			row = i.row()
			sourceDir = str(self.masterDisplay.item(row, 0).text())
			if not os.path.exists(sourceDir):
				nonExistent.append(sourceDir)
		return nonExistent

	def runExternalFunction(self, root, files, format, func):
		if len(files) == 0:
			return
		for f in files:
			if os.path.splitext(f)[-1] == format:
				myFile = os.path.join(root, f).replace('\\', '/')
				func(myFile)


def main():
	""" Setting our Qt application up and setting a name for it """
	app = QtGui.QApplication(sys.argv)
	app.setApplicationName("FILE_RUNNER")
	window = DirectoryFunctions()
	window.show()
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()