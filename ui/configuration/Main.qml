import QtQuick 2.15
import QtQuick.Window 2.15

Window {
	id: window
	visible: true
	width: 1100
	height: 660
	color: "transparent"
	title: "RAVEN Talon"
	flags: Qt.Window | Qt.FramelessWindowHint
	visibility: Window.Windowed

	property int titleBarHeight: 38
	property int titleFontSize: 14
	property color borderColor: "#2A2A2A"
	property int resizeMargin: 6
	property int currentPage: 0
	property bool internetAvailable: true

	function refreshPlanViews() {
		if (typeof readyPage !== "undefined") {
			readyPage.refreshAdvancedArgs()
			readyPage.refreshConfigItems()
		}
	}

	Component.onCompleted: {
		if (window.visibility !== Window.Maximized) {
			Qt.callLater(function() {
				window.x = Math.round((Screen.width - window.width) / 2)
				window.y = Math.round((Screen.height - window.height) / 2)
			})
		}
	}

	FontLoader { id: sarpanchFont; source: "../../media/sarpanch_bold.ttf" }
	FontLoader { id: interFont; source: "../../media/inter_regular.ttf" }
	FontLoader { id: cascadiaMonoFont; source: "../../media/cascadia_mono.ttf" }

	WindowChrome {
		anchors.fill: parent
		appWindow: window
		titleBarHeight: window.titleBarHeight
		titleFontSize: window.titleFontSize
		resizeMargin: window.resizeMargin
		borderColor: window.borderColor

		LoadingPage {
			anchors.fill: parent
			visible: window.currentPage === 0
		}

		Item {
			id: readyPage
			anchors.fill: parent
			visible: window.currentPage === 1

			property bool showBrowserSelection: false
			property bool showDebloatSummary: false
			property bool showAdvancedPage: false
			property bool transitionToSummaryInProgress: false
			property string selectedBrowser: ""
			property string selectedBrowserName: ""
			property var configItems: []
			property var advancedArgs: []
			property var browsers: []

			function refreshConfigItems() {
				configItems = bridge.getInstallPlanItems()
			}

			function refreshAdvancedArgs() {
				advancedArgs = bridge.getAdvancedArgs()
			}

			function openWin11ArgsDialog() {
				advancedDialog.openDialog(i18n.t("configuration.dialogs.win11_args_title"), bridge.getWin11DebloatArgsText(), "win11debloat")
			}

			function openRegistryChangesDialog() {
				advancedDialog.openDialog(i18n.t("configuration.dialogs.registry_changes_title"), bridge.getRegistryChangesText(), "registry-changes")
			}

			onVisibleChanged: {
				if (visible) {
					showBrowserSelection = false
					showDebloatSummary = false
					showAdvancedPage = false
					transitionToSummaryInProgress = false
					selectedBrowser = ""
					selectedBrowserName = ""
					browsers = bridge.getBrowserOptions()
					refreshConfigItems()
					refreshAdvancedArgs()
					introTimer.restart()
				}
			}

			Timer {
				id: introTimer
				interval: 2000
				repeat: false
				onTriggered: {
					if (window.internetAvailable)
						readyPage.showBrowserSelection = true
					else
						readyPage.showDebloatSummary = true
				}
			}

			Timer {
				id: browserToSummaryTimer
				interval: 500
				repeat: false
				onTriggered: {
					readyPage.showDebloatSummary = true
					readyPage.transitionToSummaryInProgress = false
				}
			}

			Row {
				id: logoRow
				anchors.horizontalCenter: parent.horizontalCenter
				anchors.verticalCenter: parent.verticalCenter
				spacing: 10
				height: 34
				opacity: (readyPage.showBrowserSelection || readyPage.showDebloatSummary || readyPage.showAdvancedPage) ? 0.0 : 1.0

				Behavior on opacity { NumberAnimation { duration: 500 } }

				Image {
					source: "../../media/talon_icon.png"
					width: 34
					height: 34
					fillMode: Image.PreserveAspectFit
					smooth: true
				}

				Text {
					text: "TALON"
					color: "#FFFFFF"
					font.family: sarpanchFont.name
					font.pixelSize: 28
					font.bold: true
					anchors.verticalCenter: parent.verticalCenter
					verticalAlignment: Text.AlignVCenter
				}
			}

			BrowserSelectionPage {
				anchors.fill: parent
				opacity: readyPage.showBrowserSelection && !readyPage.showDebloatSummary && !readyPage.showAdvancedPage && !readyPage.transitionToSummaryInProgress ? 1.0 : 0.0
				visible: opacity > 0.0
				browsers: readyPage.browsers
				selectedBrowser: readyPage.selectedBrowser
				interFontFamily: interFont.name
				Behavior on opacity { NumberAnimation { duration: 500 } }
				onBrowserSelected: function(packageId, browserName) {
					if (readyPage.transitionToSummaryInProgress || readyPage.showDebloatSummary)
						return
					readyPage.selectedBrowser = packageId
					readyPage.selectedBrowserName = browserName
					bridge.selectBrowser(packageId, browserName)
					readyPage.refreshConfigItems()
					readyPage.transitionToSummaryInProgress = true
					browserToSummaryTimer.restart()
				}
				onSkipRequested: {
					if (readyPage.transitionToSummaryInProgress || readyPage.showDebloatSummary)
						return
					readyPage.selectedBrowser = ""
					readyPage.selectedBrowserName = ""
					bridge.skipBrowserInstall()
					readyPage.refreshConfigItems()
					readyPage.transitionToSummaryInProgress = true
					browserToSummaryTimer.restart()
				}
			}

			ReviewPlanPage {
				anchors.fill: parent
				opacity: readyPage.showDebloatSummary ? 1.0 : 0.0
				visible: opacity > 0.0
				configItems: readyPage.configItems
				internetAvailable: window.internetAvailable
				interFontFamily: interFont.name
				Behavior on opacity { NumberAnimation { duration: 500 } }
				onRemoveItem: function(index) {
					bridge.removeInstallPlanItem(index)
					readyPage.refreshConfigItems()
				}
				onResetDefaults: {
					bridge.resetInstallPlanDefaults()
					readyPage.refreshConfigItems()
					readyPage.refreshAdvancedArgs()
				}
				onBackRequested: {
					readyPage.showDebloatSummary = false
					readyPage.transitionToSummaryInProgress = false
					readyPage.showBrowserSelection = true
				}
				onAdvancedRequested: {
					readyPage.showDebloatSummary = false
					readyPage.showAdvancedPage = true
					readyPage.refreshAdvancedArgs()
				}
				onStartRequested: bridge.startDebloat()
			}

			AdvancedSettingsPage {
				anchors.fill: parent
				opacity: readyPage.showAdvancedPage ? 1.0 : 0.0
				visible: opacity > 0.0
				advancedArgs: readyPage.advancedArgs
				internetAvailable: window.internetAvailable
				interFontFamily: interFont.name
				Behavior on opacity { NumberAnimation { duration: 500 } }
				onImportPlan: {
					bridge.importInstallPlan()
					window.refreshPlanViews()
				}
				onImportWinUtil: bridge.importWinUtilConfig()
				onEditWin11Args: readyPage.openWin11ArgsDialog()
				onEditRegistryChanges: readyPage.openRegistryChangesDialog()
				onExportPlan: bridge.exportInstallPlan()
				onSetBackground: bridge.setAppliedBackground()
				onToggleArg: function(key) {
					bridge.toggleAdvancedArg(key)
					window.refreshPlanViews()
				}
				onConfirm: {
					readyPage.showAdvancedPage = false
					readyPage.showDebloatSummary = true
					readyPage.refreshConfigItems()
				}
			}

			AdvancedTextDialog {
				id: advancedDialog
				interFontFamily: interFont.name
				monoFontFamily: cascadiaMonoFont.name
				onSaveRequested: function(mode, text) {
					var ok = false
					if (mode === "win11debloat")
						ok = bridge.saveWin11DebloatArgsText(text)
					else if (mode === "registry-changes")
						ok = bridge.saveRegistryChangesText(text)
					if (ok)
						advancedDialog.closeDialog()
				}
			}
		}
	}
}
