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
	property bool isMaximized: (visibility === Window.Maximized)
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

	FontLoader {
		id: sarpanchFont
		source: "../../media/sarpanch_bold.ttf"
	}

	FontLoader {
		id: interFont
		source: "../../media/inter_regular.ttf"
	}

	FontLoader {
		id: cascadiaMonoFont
		source: "../../media/cascadia_mono.ttf"
	}

	Rectangle {
		id: rootFrame
		anchors.fill: parent
		color: "transparent"
		border.color: window.borderColor
		border.width: 1

		Rectangle {
			id: titleBar
			x: 0
			y: 0
			width: parent.width
			height: window.titleBarHeight
			color: "#000000"

			MouseArea {
				anchors.fill: parent
				acceptedButtons: Qt.LeftButton

				onPressed: window.startSystemMove()

				onDoubleClicked: {
					if (window.visibility === Window.Maximized)
						window.visibility = Window.Windowed
					else
						window.visibility = Window.Maximized
				}
			}

			Row {
				anchors.left: parent.left
				anchors.leftMargin: 12
				anchors.verticalCenter: parent.verticalCenter
				height: parent.height
				width: parent.width - buttonsRow.width - 24
				spacing: 4
				clip: true

				Image {
					source: "../../media/raven_logo.png"
					width: 54
					height: 11
					fillMode: Image.PreserveAspectFit
					smooth: true
					anchors.verticalCenter: parent.verticalCenter
				}

				Text {
					text: "Talon"
					color: "#FFFFFF"
					font.pixelSize: window.titleFontSize
					anchors.verticalCenter: parent.verticalCenter
					elide: Text.ElideRight
				}
			}

			Row {
				id: buttonsRow
				spacing: 0
				anchors.right: parent.right
				anchors.top: parent.top
				anchors.bottom: parent.bottom

				VectorTitleButton {
					iconType: "minimize"
					onClicked: window.showMinimized()
				}

				VectorMaximizeButton {
					onClicked: {
						if (window.visibility === Window.Maximized)
							window.visibility = Window.Windowed
						else
							window.visibility = Window.Maximized
					}
				}

				VectorTitleButton {
					iconType: "close"
					iconSize: 12
					hoverColor: "#B00020"
					onClicked: Qt.quit()
				}
			}
		}

		Rectangle {
			x: 0
			y: window.titleBarHeight
			width: parent.width
			height: 1
			color: window.borderColor
		}

		Rectangle {
			id: contentBackground
			x: 0
			y: window.titleBarHeight + 1
			width: parent.width
			height: parent.height - window.titleBarHeight - 1
			color: "#000000"
			opacity: 0.9

			Item {
				id: loadingPage
				anchors.fill: parent
				visible: window.currentPage === 0

				property int step: 0
				property int lines: 12

				Timer {
					interval: 75
					repeat: true
					running: loadingPage.visible
					onTriggered: {
						loadingPage.step = (loadingPage.step + 1) % loadingPage.lines
						spinnerCanvas.requestPaint()
					}
				}

				Canvas {
					id: spinnerCanvas
					anchors.centerIn: parent
					width: 44
					height: 44
					renderTarget: Canvas.Image

					onPaint: {
						var ctx = getContext("2d")
						ctx.setTransform(1, 0, 0, 1, 0, 0)
						ctx.clearRect(0, 0, width, height)
						ctx.translate(width / 2, height / 2)
						for (var i = 0; i < loadingPage.lines; i++) {
							var idx = (loadingPage.step + i) % loadingPage.lines
							var alpha = (i + 1) / loadingPage.lines
							ctx.save()
							ctx.rotate((Math.PI * 2 * idx) / loadingPage.lines)
							ctx.fillStyle = "rgba(255,255,255," + alpha + ")"
							ctx.fillRect(14, -1.5, 10, 3)
							ctx.restore()
						}
					}
				}
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
				property string advancedDialogMode: ""
				property var browsers: [
					{
						name: "Edge",
						icon: "../../media/browser_edge.png",
						packageId: "microsoft-edge",
						tooltip: "Edge is not recommended unless necessary for your purposes, as it is very invasive to your privacy and embeds ads."
					},
					{
						name: "Waterfox",
						icon: "../../media/browser_waterfox.png",
						packageId: "waterfox",
						tooltip: "Waterfox is recommended over Firefox, but not Brave. It's based on Firefox, but removes tracking and telemetry."
					},
					{
						name: "Brave",
						icon: "../../media/browser_brave.png",
						packageId: "brave",
						tooltip: "Brave is the recommended browser, as it is the closest to Chrome while respecting your privacy."
					},
					{
						name: "LibreWolf",
						icon: "../../media/browser_librewolf.png",
						packageId: "librewolf",
						tooltip: "LibreWolf is only recommended for tech-savvy users. It is designed for maximum privacy and security, but can be harder to use."
					},
					{
						name: "Firefox",
						icon: "../../media/browser_firefox.png",
						packageId: "firefox",
						tooltip: "Firefox is not recommended unless necessary for your purposes, as it includes telemetry and sponsored content by default."
					}
				]
				function refreshConfigItems() {
					configItems = bridge.getInstallPlanItems()
				}

				function refreshAdvancedArgs() {
					advancedArgs = bridge.getAdvancedArgs()
				}

				function openWin11ArgsDialog() {
					advancedDialogTitle.text = "Set Win11Debloat Arguments"
					advancedDialogEditor.text = bridge.getWin11DebloatArgsText()
					advancedDialogMode = "win11debloat"
					advancedDialogOverlay.visible = true
					advancedDialogEditor.forceActiveFocus()
				}

				function openRegistryChangesDialog() {
					advancedDialogTitle.text = "Edit Registry Changes"
					advancedDialogEditor.text = bridge.getRegistryChangesText()
					advancedDialogMode = "registry-changes"
					advancedDialogOverlay.visible = true
					advancedDialogEditor.forceActiveFocus()
				}

				function closeAdvancedDialog() {
					advancedDialogOverlay.visible = false
					advancedDialogMode = ""
				}

				function saveAdvancedDialog() {
					var ok = false
					if (advancedDialogMode === "win11debloat")
						ok = bridge.saveWin11DebloatArgsText(advancedDialogEditor.text)
					else if (advancedDialogMode === "registry-changes")
						ok = bridge.saveRegistryChangesText(advancedDialogEditor.text)
					if (ok)
						closeAdvancedDialog()
				}

				function hasBrowserInstallItem() {
					for (var i = 0; i < configItems.length; i++) {
						var item = configItems[i]
						if (typeof item === "object" && item.key === "browser-installation")
							return true
					}
					return false
				}

				function hasConfigureUpdatesItem() {
					for (var i = 0; i < configItems.length; i++) {
						var item = configItems[i]
						if (typeof item === "object" && item.key === "configure-updates")
							return true
					}
					return false
				}

				onVisibleChanged: {
					if (visible) {
						showBrowserSelection = false
						showDebloatSummary = false
						showAdvancedPage = false
						transitionToSummaryInProgress = false
						selectedBrowser = ""
						selectedBrowserName = ""
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

					Behavior on opacity {
						NumberAnimation { duration: 500 }
					}

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

				Item {
					id: browserSelectionView
					anchors.fill: parent
					opacity: readyPage.showBrowserSelection && !readyPage.showDebloatSummary && !readyPage.showAdvancedPage && !readyPage.transitionToSummaryInProgress ? 1.0 : 0.0
					visible: opacity > 0.0

					Behavior on opacity {
						NumberAnimation { duration: 500 }
					}

					Text {
						anchors.top: parent.top
						anchors.topMargin: 40
						anchors.horizontalCenter: parent.horizontalCenter
						text: "Welcome. Please select your web browser."
						color: "#FFFFFF"
						font.family: interFont.name
						font.pixelSize: 22
					}

					Row {
						anchors.centerIn: parent
						spacing: 30

						Repeater {
							model: readyPage.browsers

							Item {
								width: 132
								height: 164
								property bool hovered: mouseArea.containsMouse

								Rectangle {
									anchors.horizontalCenter: parent.horizontalCenter
									y: 0
									width: 132
									height: 132
									color: "transparent"
									border.width: 1
									border.color: modelData.packageId === "brave"
										? "#F4C430"
										: (readyPage.selectedBrowser === modelData.packageId ? "#FFFFFF" : "#2A2A2A")

									Image {
										anchors.centerIn: parent
										source: modelData.icon
										width: 96
										height: 96
										fillMode: Image.PreserveAspectFit
										smooth: true
									}
								}

								Text {
									anchors.top: parent.top
									anchors.topMargin: 138
									anchors.horizontalCenter: parent.horizontalCenter
									text: modelData.name
									color: modelData.packageId === "brave" ? "#F4C430" : "#FFFFFF"
									font.family: interFont.name
									font.pixelSize: 16
								}

								MouseArea {
									id: mouseArea
									anchors.fill: parent
									hoverEnabled: true
									cursorShape: Qt.PointingHandCursor
									onClicked: {
										if (readyPage.transitionToSummaryInProgress || readyPage.showDebloatSummary)
											return
										readyPage.selectedBrowser = modelData.packageId
										readyPage.selectedBrowserName = modelData.name
										bridge.selectBrowser(modelData.packageId, modelData.name)
										readyPage.refreshConfigItems()
										readyPage.transitionToSummaryInProgress = true
										browserToSummaryTimer.restart()
									}
								}

								Rectangle {
									visible: parent.hovered
									width: 300
									height: tooltipText.implicitHeight + 16
									color: "#0B0B0B"
									border.width: 1
									border.color: "#2A2A2A"
									radius: 0
									anchors.horizontalCenter: parent.horizontalCenter
									anchors.top: parent.bottom
									anchors.topMargin: 12
									z: 30

									Text {
										id: tooltipText
										anchors.fill: parent
										anchors.margins: 8
										text: modelData.tooltip
										wrapMode: Text.WordWrap
										color: "#FFFFFF"
										font.family: interFont.name
										font.pixelSize: 12
									}
								}
							}
						}
					}

					Item {
						id: skipBrowserInstallButton
						anchors.right: parent.right
						anchors.rightMargin: 22
						anchors.bottom: parent.bottom
						anchors.bottomMargin: 22
						height: 30
						width: skipBrowserRow.width

						Row {
							id: skipBrowserRow
							anchors.verticalCenter: parent.verticalCenter
							spacing: 6

							Text {
								text: "Do not install a browser"
								color: skipBrowserMouse.containsMouse ? "#FFFFFF" : "#A0A0A0"
								font.family: interFont.name
								font.pixelSize: 15
								anchors.verticalCenter: parent.verticalCenter
							}

							Canvas {
								id: skipArrowIcon
								width: 18
								height: 18
								anchors.verticalCenter: parent.verticalCenter
								renderTarget: Canvas.Image

								onPaint: {
									var ctx = getContext("2d")
									ctx.setTransform(1, 0, 0, 1, 0, 0)
									ctx.clearRect(0, 0, width, height)
									ctx.strokeStyle = skipBrowserMouse.containsMouse ? "#FFFFFF" : "#A0A0A0"
									ctx.lineWidth = 1.5
									ctx.lineCap = "square"
									ctx.lineJoin = "miter"

									var cx = width / 2
									var cy = height / 2
									ctx.beginPath()
									ctx.moveTo(cx - 5, cy)
									ctx.lineTo(cx + 5, cy)
									ctx.moveTo(cx + 5, cy)
									ctx.lineTo(cx + 1, cy - 4)
									ctx.moveTo(cx + 5, cy)
									ctx.lineTo(cx + 1, cy + 4)
									ctx.stroke()
								}
							}
						}

						MouseArea {
							id: skipBrowserMouse
							anchors.fill: parent
							hoverEnabled: true
							cursorShape: Qt.PointingHandCursor
							onContainsMouseChanged: skipArrowIcon.requestPaint()
							onClicked: {
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
					}
				}

				Item {
					id: debloatSummaryView
					anchors.fill: parent
					opacity: readyPage.showDebloatSummary ? 1.0 : 0.0
					visible: opacity > 0.0

					Behavior on opacity {
						NumberAnimation { duration: 500 }
					}

					Text {
						id: debloatSummaryTitle
						anchors.top: parent.top
						anchors.topMargin: 40
						anchors.horizontalCenter: parent.horizontalCenter
						text: "System is ready to debloat. Please review."
						color: "#FFFFFF"
						font.family: interFont.name
						font.pixelSize: 22
					}

					Rectangle {
						id: splitLine
						width: 1
						color: "#2A2A2A"
						anchors.horizontalCenter: parent.horizontalCenter
						anchors.top: debloatSummaryTitle.bottom
						anchors.topMargin: 24
						anchors.bottom: parent.bottom
						anchors.bottomMargin: 30
					}

					Item {
						id: leftPanel
						anchors.top: splitLine.top
						anchors.bottom: splitLine.bottom
						anchors.left: parent.left
						anchors.right: splitLine.left
						anchors.leftMargin: 36
						anchors.rightMargin: 24
						property string hoveredTooltip: ""
						property real hoveredTooltipY: 0

						ListView {
							id: configList
							anchors.fill: parent
							clip: true
							spacing: 0
							model: readyPage.configItems

							delegate: Item {
								width: configList.width
								height: 42

								Text {
									anchors.left: parent.left
									anchors.right: removeItemButton.left
									anchors.rightMargin: 12
									anchors.verticalCenter: parent.verticalCenter
									text: modelData.text
									color: "#FFFFFF"
									font.family: interFont.name
									font.pixelSize: 16
									wrapMode: Text.NoWrap
									elide: Text.ElideRight
								}

								MouseArea {
									anchors.left: parent.left
									anchors.right: removeItemButton.left
									anchors.top: parent.top
									anchors.bottom: parent.bottom
									acceptedButtons: Qt.NoButton
									hoverEnabled: true
									onEntered: {
										leftPanel.hoveredTooltip = modelData.tooltip
										leftPanel.hoveredTooltipY = (parent.y - configList.contentY) + parent.height + 6
									}
									onExited: {
										if (leftPanel.hoveredTooltip === modelData.tooltip)
											leftPanel.hoveredTooltip = ""
									}
								}

								Item {
									id: removeItemButton
									width: 22
									height: 22
									anchors.right: parent.right
									anchors.rightMargin: 2
									anchors.verticalCenter: parent.verticalCenter

									Rectangle {
										anchors.fill: parent
										color: removeMouse.containsMouse ? "#1A1A1A" : "transparent"
									}

									Canvas {
										anchors.fill: parent
										renderTarget: Canvas.Image
										onPaint: {
											var ctx = getContext("2d")
											ctx.setTransform(1, 0, 0, 1, 0, 0)
											ctx.clearRect(0, 0, width, height)
											ctx.strokeStyle = "#FFFFFF"
											ctx.lineWidth = 1
											var offset = 6.5
											ctx.beginPath()
											ctx.moveTo(offset, offset)
											ctx.lineTo(width - offset, height - offset)
											ctx.moveTo(width - offset, offset)
											ctx.lineTo(offset, height - offset)
											ctx.stroke()
										}
									}

									MouseArea {
										id: removeMouse
										anchors.fill: parent
										hoverEnabled: true
										cursorShape: Qt.PointingHandCursor
										onClicked: {
											bridge.removeInstallPlanItem(index)
											readyPage.refreshConfigItems()
										}
									}
								}

								Rectangle {
									visible: index < readyPage.configItems.length - 1
									anchors.left: parent.left
									anchors.right: parent.right
									anchors.bottom: parent.bottom
									height: 1
									color: "#2A2A2A"
								}
							}
						}

						Text {
							anchors.centerIn: parent
							visible: readyPage.configItems.length === 0
							text: "No items."
							color: "#7A7A7A"
							font.family: interFont.name
							font.pixelSize: 15
						}

						Rectangle {
							visible: leftPanel.hoveredTooltip.length > 0
							anchors.left: parent.left
							anchors.right: parent.right
							y: Math.min(
								Math.max(0, leftPanel.hoveredTooltipY),
								Math.max(0, leftPanel.height - height)
							)
							height: leftTooltipText.implicitHeight + 16
							color: "#0B0B0B"
							border.width: 1
							border.color: "#2A2A2A"
							z: 40

							Text {
								id: leftTooltipText
								anchors.fill: parent
								anchors.margins: 8
								text: leftPanel.hoveredTooltip
								wrapMode: Text.WordWrap
								color: "#FFFFFF"
								font.family: interFont.name
								font.pixelSize: 12
							}
						}
					}

					Item {
						id: rightPanel
						anchors.top: splitLine.top
						anchors.bottom: splitLine.bottom
						anchors.left: splitLine.right
						anchors.right: parent.right
						anchors.leftMargin: 24
						anchors.rightMargin: 36

						Text {
							id: rightGuidanceText
							anchors.top: parent.top
							anchors.left: parent.left
							anchors.right: parent.right
							text: "The list on the left shows everything Talon is going to do to your system. If there's something you don't want it to do, you can remove items from the list.\n\nIf everything looks good to you, select \"Start.\""
							color: "#FFFFFF"
							font.family: interFont.name
							font.pixelSize: 15
							wrapMode: Text.WordWrap
							horizontalAlignment: Text.AlignLeft
						}

						Row {
							id: noBrowserWarning
							anchors.top: rightGuidanceText.bottom
							anchors.topMargin: 14
							anchors.left: parent.left
							spacing: 8
							visible: window.internetAvailable && !readyPage.hasBrowserInstallItem()

							Image {
								source: "../../media/icon_warning.png"
								width: 24
								height: 24
								fillMode: Image.PreserveAspectFit
								smooth: true
							}

							Text {
								anchors.verticalCenter: parent.verticalCenter
								text: "No browser will be installed."
								color: "#FF0000"
								font.family: interFont.name
								font.pixelSize: 15
							}
						}

						Row {
							id: noInternetInfo
							anchors.top: rightGuidanceText.bottom
							anchors.topMargin: 14
							anchors.left: parent.left
							spacing: 8
							visible: !window.internetAvailable

							Image {
								source: "../../media/icon_info.png"
								width: 24
								height: 24
								fillMode: Image.PreserveAspectFit
								smooth: true
							}

							Text {
								anchors.verticalCenter: parent.verticalCenter
								text: "You aren't connected to internet. Talon won't install a browser."
								color: "#00FFFF"
								font.family: interFont.name
								font.pixelSize: 15
							}
						}

						Row {
							id: noUpdatesInfo
							anchors.top: noInternetInfo.visible
								? noInternetInfo.bottom
								: (noBrowserWarning.visible ? noBrowserWarning.bottom : rightGuidanceText.bottom)
							anchors.topMargin: 8
							anchors.left: parent.left
							spacing: 8
							visible: !readyPage.hasConfigureUpdatesItem()

							Image {
								source: "../../media/icon_warning.png"
								width: 24
								height: 24
								fillMode: Image.PreserveAspectFit
								smooth: true
							}

							Text {
								anchors.verticalCenter: parent.verticalCenter
								width: rightPanel.width - 40
								text: "Update policy won't be configured. Updates may restore bloat and undo some of Talon's settings."
								color: "#FF0000"
								font.family: interFont.name
								font.pixelSize: 15
								wrapMode: Text.WordWrap
							}
						}

						Row {
							anchors.top: noUpdatesInfo.visible
								? noUpdatesInfo.bottom
								: (noInternetInfo.visible
									? noInternetInfo.bottom
									: (noBrowserWarning.visible ? noBrowserWarning.bottom : rightGuidanceText.bottom))
							anchors.topMargin: 8
							anchors.left: parent.left
							spacing: 8
							visible: readyPage.configItems.length === 0

							Image {
								source: "../../media/icon_warning.png"
								width: 24
								height: 24
								fillMode: Image.PreserveAspectFit
								smooth: true
							}

							Text {
								anchors.verticalCenter: parent.verticalCenter
								text: "Cannot start debloat process. Nothing to do."
								color: "#FF0000"
								font.family: interFont.name
								font.pixelSize: 15
							}
						}
					}

					Text {
						id: resetDefaultsButton
						anchors.right: leftPanel.right
						anchors.bottom: parent.bottom
						anchors.bottomMargin: 28
						text: "Reset to Defaults"
						color: resetDefaultsMouse.containsMouse ? "#FFFFFF" : "#A0A0A0"
						font.family: interFont.name
						font.pixelSize: 15

						MouseArea {
							id: resetDefaultsMouse
							anchors.fill: parent
							hoverEnabled: true
							cursorShape: Qt.PointingHandCursor
							onClicked: {
								bridge.resetInstallPlanDefaults()
								readyPage.refreshConfigItems()
							}
						}
					}

					Item {
						id: backButton
						width: 30
						height: 30
						visible: window.internetAvailable
						anchors.left: parent.left
						anchors.leftMargin: 22
						anchors.bottom: parent.bottom
						anchors.bottomMargin: 22

						Canvas {
							id: backIcon
							anchors.fill: parent
							renderTarget: Canvas.Image

							onPaint: {
								var ctx = getContext("2d")
								ctx.setTransform(1, 0, 0, 1, 0, 0)
								ctx.clearRect(0, 0, width, height)
								ctx.strokeStyle = backMouse.containsMouse ? "#FFFFFF" : "#A0A0A0"
								ctx.lineWidth = 1.5
								ctx.lineCap = "square"
								ctx.lineJoin = "miter"

								var cx = width / 2
								var cy = height / 2
								ctx.beginPath()
								ctx.moveTo(cx + 7, cy)
								ctx.lineTo(cx - 6, cy)
								ctx.moveTo(cx - 6, cy)
								ctx.lineTo(cx - 1, cy - 5)
								ctx.moveTo(cx - 6, cy)
								ctx.lineTo(cx - 1, cy + 5)
								ctx.stroke()
							}
						}

						MouseArea {
							id: backMouse
							anchors.fill: parent
							hoverEnabled: true
							cursorShape: Qt.PointingHandCursor
							onContainsMouseChanged: backIcon.requestPaint()
							onClicked: {
								readyPage.showDebloatSummary = false
								readyPage.transitionToSummaryInProgress = false
								readyPage.showBrowserSelection = true
							}
						}
					}

					Text {
						id: advancedButton
						anchors.left: rightPanel.left
						anchors.bottom: parent.bottom
						anchors.bottomMargin: 28
						text: "Advanced"
						color: advancedMouse.containsMouse ? "#FFFFFF" : "#A0A0A0"
						font.family: interFont.name
						font.pixelSize: 15

						MouseArea {
							id: advancedMouse
							anchors.fill: parent
							hoverEnabled: true
							cursorShape: Qt.PointingHandCursor
							onClicked: {
								readyPage.showDebloatSummary = false
								readyPage.showAdvancedPage = true
								readyPage.refreshAdvancedArgs()
							}
						}
					}

					Item {
						id: startButtonWrap
						width: rightGuidanceText.width
						height: 46
						anchors.left: advancedButton.left
						anchors.bottom: advancedButton.top
						anchors.bottomMargin: 12

						Rectangle {
							id: startButton
							anchors.fill: parent
							color: readyPage.configItems.length > 0
								? (startMouse.containsMouse ? "#EAEAEA" : "#FFFFFF")
								: "#1A1A1A"
							border.width: 1
							border.color: readyPage.configItems.length > 0 ? "#FFFFFF" : "#2A2A2A"
						}

						Text {
							anchors.centerIn: parent
							text: "START"
							color: readyPage.configItems.length > 0 ? "#000000" : "#7A7A7A"
							font.family: interFont.name
							font.pixelSize: 16
							font.bold: true
						}

						MouseArea {
							id: startMouse
							anchors.fill: parent
							hoverEnabled: true
							enabled: readyPage.configItems.length > 0
							cursorShape: enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
							onClicked: bridge.startDebloat()
						}
					}
				}

				Item {
					id: advancedPageView
					anchors.fill: parent
					opacity: readyPage.showAdvancedPage ? 1.0 : 0.0
					visible: opacity > 0.0

					Behavior on opacity {
						NumberAnimation { duration: 500 }
					}

					Text {
						anchors.top: parent.top
						anchors.topMargin: 40
						anchors.horizontalCenter: parent.horizontalCenter
						text: "Advanced settings"
						color: "#FFFFFF"
						font.family: interFont.name
						font.pixelSize: 22
					}

					Row {
						anchors.top: parent.top
						anchors.topMargin: 90
						anchors.horizontalCenter: parent.horizontalCenter
						spacing: 8

						Image {
							source: "../../media/icon_warning.png"
							width: 24
							height: 24
							fillMode: Image.PreserveAspectFit
							smooth: true
						}

						Text {
							anchors.verticalCenter: parent.verticalCenter
							text: "Do not touch unless you know what you're doing!"
							color: "#FF0000"
							font.family: interFont.name
							font.pixelSize: 15
						}
					}

					Flow {
						id: advancedActionsRow
						anchors.top: parent.top
						anchors.topMargin: 132
						anchors.left: parent.left
						anchors.right: parent.right
						anchors.leftMargin: 36
						anchors.rightMargin: 36
						spacing: 10

						Rectangle {
							width: importPlanLabel.implicitWidth + 22
							height: 30
							color: importPlanMouse.containsMouse ? "#101010" : "#000000"
							border.width: 1
							border.color: "#2A2A2A"

							Text {
								id: importPlanLabel
								anchors.centerIn: parent
								text: "Import Talon Install Plan"
								color: "#FFFFFF"
								font.family: interFont.name
								font.pixelSize: 14
							}

							MouseArea {
								id: importPlanMouse
								anchors.fill: parent
								hoverEnabled: true
								cursorShape: Qt.PointingHandCursor
								onClicked: {
									bridge.importInstallPlan()
									window.refreshPlanViews()
								}
							}
						}

						Rectangle {
							width: importWinutilLabel.implicitWidth + 22
							height: 30
							color: importWinutilMouse.containsMouse ? "#101010" : "#000000"
							border.width: 1
							border.color: "#2A2A2A"

							Text {
								id: importWinutilLabel
								anchors.centerIn: parent
								text: "Import WinUtil Config"
								color: "#FFFFFF"
								font.family: interFont.name
								font.pixelSize: 14
							}

							MouseArea {
								id: importWinutilMouse
								anchors.fill: parent
								hoverEnabled: true
								cursorShape: Qt.PointingHandCursor
								onClicked: bridge.importWinUtilConfig()
							}
						}

						Rectangle {
							width: win11ArgsLabel.implicitWidth + 22
							height: 30
							color: win11ArgsMouse.containsMouse ? "#101010" : "#000000"
							border.width: 1
							border.color: "#2A2A2A"

							Text {
								id: win11ArgsLabel
								anchors.centerIn: parent
								text: "Set Win11Debloat Arguments"
								color: "#FFFFFF"
								font.family: interFont.name
								font.pixelSize: 14
							}

							MouseArea {
								id: win11ArgsMouse
								anchors.fill: parent
								hoverEnabled: true
								cursorShape: Qt.PointingHandCursor
								onClicked: readyPage.openWin11ArgsDialog()
							}
						}

						Rectangle {
							width: regChangesLabel.implicitWidth + 22
							height: 30
							color: regChangesMouse.containsMouse ? "#101010" : "#000000"
							border.width: 1
							border.color: "#2A2A2A"

							Text {
								id: regChangesLabel
								anchors.centerIn: parent
								text: "Edit Registry Changes"
								color: "#FFFFFF"
								font.family: interFont.name
								font.pixelSize: 14
							}

							MouseArea {
								id: regChangesMouse
								anchors.fill: parent
								hoverEnabled: true
								cursorShape: Qt.PointingHandCursor
								onClicked: readyPage.openRegistryChangesDialog()
							}
						}

						Rectangle {
							width: exportPlanLabel.implicitWidth + 22
							height: 30
							color: exportPlanMouse.containsMouse ? "#101010" : "#000000"
							border.width: 1
							border.color: "#2A2A2A"

							Text {
								id: exportPlanLabel
								anchors.centerIn: parent
								text: "Export As Install Plan"
								color: "#FFFFFF"
								font.family: interFont.name
								font.pixelSize: 14
							}

							MouseArea {
								id: exportPlanMouse
								anchors.fill: parent
								hoverEnabled: true
								cursorShape: Qt.PointingHandCursor
								onClicked: bridge.exportInstallPlan()
							}
						}

						Rectangle {
							width: setBackgroundLabel.implicitWidth + 22
							height: 30
							color: setBackgroundMouse.containsMouse ? "#101010" : "#000000"
							border.width: 1
							border.color: "#2A2A2A"

							Text {
								id: setBackgroundLabel
								anchors.centerIn: parent
								text: "Set Applied Background"
								color: "#FFFFFF"
								font.family: interFont.name
								font.pixelSize: 14
							}

							MouseArea {
								id: setBackgroundMouse
								anchors.fill: parent
								hoverEnabled: true
								cursorShape: Qt.PointingHandCursor
								onClicked: bridge.setAppliedBackground()
							}
						}
					}

					ListView {
						id: advancedArgsList
						anchors.top: advancedActionsRow.bottom
						anchors.topMargin: 12
						anchors.bottom: confirmButtonWrap.top
						anchors.bottomMargin: 18
						anchors.left: parent.left
						anchors.leftMargin: 36
						anchors.right: parent.right
						anchors.rightMargin: 36
						clip: true
						spacing: 0
						model: readyPage.advancedArgs

						delegate: Item {
							width: advancedArgsList.width
							height: 42
							property bool unavailableNoInternet: !window.internetAvailable && modelData.key === "browser-installation"

							Text {
								anchors.left: parent.left
								anchors.right: valueButton.left
								anchors.rightMargin: 12
								anchors.verticalCenter: parent.verticalCenter
								text: modelData.label
								color: unavailableNoInternet ? "#7A7A7A" : "#FFFFFF"
								font.family: interFont.name
								font.pixelSize: 16
								wrapMode: Text.NoWrap
								elide: Text.ElideRight
							}

							Rectangle {
								id: valueButton
								width: 72
								height: 28
								anchors.right: parent.right
								anchors.verticalCenter: parent.verticalCenter
								color: unavailableNoInternet ? "#050505" : (valueMouse.containsMouse ? "#111111" : "#000000")
								border.width: 1
								border.color: unavailableNoInternet ? "#1A1A1A" : "#2A2A2A"

								Text {
									anchors.centerIn: parent
									text: modelData.value ? "true" : "false"
									color: unavailableNoInternet ? "#7A7A7A" : "#FFFFFF"
									font.family: interFont.name
									font.pixelSize: 14
								}

								MouseArea {
									id: valueMouse
									anchors.fill: parent
									hoverEnabled: true
									enabled: !unavailableNoInternet
									cursorShape: enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
									onClicked: {
										bridge.toggleAdvancedArg(modelData.key)
										window.refreshPlanViews()
									}
								}
							}

							Rectangle {
								visible: index < advancedArgsList.count - 1
								anchors.left: parent.left
								anchors.right: parent.right
								anchors.bottom: parent.bottom
								height: 1
								color: "#2A2A2A"
							}
						}
					}

					Text {
						id: seeDocsButton
						anchors.left: parent.left
						anchors.leftMargin: 36
						anchors.bottom: parent.bottom
						anchors.bottomMargin: 28
						text: "See Documentation"
						color: seeDocsMouse.containsMouse ? "#FFFFFF" : "#A0A0A0"
						font.family: interFont.name
						font.pixelSize: 15

						MouseArea {
							id: seeDocsMouse
							anchors.fill: parent
							hoverEnabled: true
							cursorShape: Qt.PointingHandCursor
							onClicked: Qt.openUrlExternally("https://github.com/ravendevteam/talon/blob/main/DOCUMENTATION.md")
						}
					}

					Item {
						id: confirmButtonWrap
						width: 98
						height: 38
						anchors.right: parent.right
						anchors.rightMargin: 22
						anchors.bottom: parent.bottom
						anchors.bottomMargin: 22

						Rectangle {
							anchors.fill: parent
							color: "transparent"
							border.width: 1
							border.color: "#FFFFFF"
							opacity: 0.45
						}

						Rectangle {
							id: confirmButton
							anchors.fill: parent
							anchors.margins: 3
							color: confirmMouse.containsMouse ? "#1A1A1A" : "#000000"
							border.width: 0

							Text {
								anchors.centerIn: parent
								text: "Confirm"
								color: "#FFFFFF"
								font.family: interFont.name
								font.pixelSize: 15
							}

							MouseArea {
								id: confirmMouse
								anchors.fill: parent
								hoverEnabled: true
								cursorShape: Qt.PointingHandCursor
								onClicked: {
									readyPage.showAdvancedPage = false
									readyPage.showDebloatSummary = true
									readyPage.refreshConfigItems()
								}
							}
						}
					}

					Rectangle {
						id: advancedDialogOverlay
						anchors.fill: parent
						visible: false
						color: "#80000000"
						z: 200

						MouseArea {
							anchors.fill: parent
							acceptedButtons: Qt.LeftButton
							hoverEnabled: true
							onClicked: {}
							onWheel: wheel.accepted = true
						}

						Rectangle {
							id: advancedDialogFrame
							width: Math.min(parent.width - 80, 760)
							height: Math.min(parent.height - 80, 500)
							anchors.centerIn: parent
							color: "#000000"
							border.color: "#2A2A2A"
							border.width: 1

							Rectangle {
								id: advancedDialogBar
								anchors.top: parent.top
								anchors.left: parent.left
								anchors.right: parent.right
								height: 30
								color: "#000000"

								Text {
									id: advancedDialogTitle
									anchors.left: parent.left
									anchors.leftMargin: 10
									anchors.verticalCenter: parent.verticalCenter
									text: ""
									color: "#FFFFFF"
									font.family: interFont.name
									font.pixelSize: 12
								}

								Rectangle {
									anchors.right: parent.right
									anchors.top: parent.top
									anchors.bottom: parent.bottom
									width: 28
									color: advancedDialogCloseMouse.containsMouse ? "#B00020" : "transparent"

									Canvas {
										anchors.centerIn: parent
										width: 12
										height: 12
										renderTarget: Canvas.Image

										onPaint: {
											var ctx = getContext("2d")
											ctx.setTransform(1, 0, 0, 1, 0, 0)
											ctx.clearRect(0, 0, width, height)
											ctx.strokeStyle = "#FFFFFF"
											ctx.lineWidth = 1
											ctx.lineCap = "square"
											ctx.lineJoin = "miter"
											var offset = 0.5
											ctx.beginPath()
											ctx.moveTo(offset, offset)
											ctx.lineTo(width - offset, height - offset)
											ctx.moveTo(width - offset, offset)
											ctx.lineTo(offset, height - offset)
											ctx.stroke()
										}
									}

									MouseArea {
										id: advancedDialogCloseMouse
										anchors.fill: parent
										hoverEnabled: true
										cursorShape: Qt.PointingHandCursor
										onClicked: readyPage.closeAdvancedDialog()
									}
								}
							}

							Rectangle {
								anchors.top: advancedDialogBar.bottom
								anchors.topMargin: 14
								anchors.left: parent.left
								anchors.right: parent.right
								anchors.leftMargin: 14
								anchors.rightMargin: 14
								anchors.bottom: actionsRow.top
								anchors.bottomMargin: 14
								color: "#000000"
								border.color: "#2A2A2A"
								border.width: 1
								clip: true

								Flickable {
									id: advancedDialogFlick
									anchors.fill: parent
									anchors.margins: 8
									contentWidth: width
									contentHeight: Math.max(height, advancedDialogEditor.paintedHeight + 4)
									boundsBehavior: Flickable.StopAtBounds

									TextEdit {
										id: advancedDialogEditor
										width: advancedDialogFlick.width
										color: "#FFFFFF"
										font.family: cascadiaMonoFont.name
										font.pixelSize: 14
										wrapMode: TextEdit.Wrap
										selectByMouse: true
										persistentSelection: true
										cursorVisible: activeFocus
									}
								}
							}

							Row {
								id: actionsRow
								anchors.right: parent.right
								anchors.bottom: parent.bottom
								anchors.rightMargin: 14
								anchors.bottomMargin: 14
								spacing: 8

								Rectangle {
									width: cancelDialogLabel.implicitWidth + 22
									height: 30
									color: cancelDialogMouse.containsMouse ? "#101010" : "#000000"
									border.width: 1
									border.color: "#2A2A2A"

									Text {
										id: cancelDialogLabel
										anchors.centerIn: parent
										text: "Cancel"
										color: "#FFFFFF"
										font.family: interFont.name
										font.pixelSize: 14
									}

									MouseArea {
										id: cancelDialogMouse
										anchors.fill: parent
										hoverEnabled: true
										cursorShape: Qt.PointingHandCursor
										onClicked: readyPage.closeAdvancedDialog()
									}
								}

								Rectangle {
									width: saveDialogLabel.implicitWidth + 22
									height: 30
									color: saveDialogMouse.containsMouse ? "#EAEAEA" : "#FFFFFF"
									border.width: 1
									border.color: "#FFFFFF"

									Text {
										id: saveDialogLabel
										anchors.centerIn: parent
										text: "Save Changes"
										color: "#000000"
										font.family: interFont.name
										font.pixelSize: 14
									}

									MouseArea {
										id: saveDialogMouse
										anchors.fill: parent
										hoverEnabled: true
										cursorShape: Qt.PointingHandCursor
										onClicked: readyPage.saveAdvancedDialog()
									}
								}
							}
						}
					}
				}
			}
		}
	}

	Rectangle {
		anchors.fill: parent
		color: "transparent"
		border.color: window.borderColor
		border.width: 1
	}

	MouseArea {
		anchors.left: parent.left
		anchors.top: parent.top
		anchors.bottom: parent.bottom
		width: window.resizeMargin
		acceptedButtons: Qt.LeftButton
		cursorShape: Qt.SizeHorCursor
		enabled: !window.isMaximized
		onPressed: window.startSystemResize(Qt.LeftEdge)
	}

	MouseArea {
		anchors.right: parent.right
		anchors.top: parent.top
		anchors.bottom: parent.bottom
		width: window.resizeMargin
		acceptedButtons: Qt.LeftButton
		cursorShape: Qt.SizeHorCursor
		enabled: !window.isMaximized
		onPressed: window.startSystemResize(Qt.RightEdge)
	}

	MouseArea {
		anchors.left: parent.left
		anchors.right: parent.right
		anchors.top: parent.top
		height: window.resizeMargin
		acceptedButtons: Qt.LeftButton
		cursorShape: Qt.SizeVerCursor
		enabled: !window.isMaximized
		onPressed: window.startSystemResize(Qt.TopEdge)
	}

	MouseArea {
		anchors.left: parent.left
		anchors.right: parent.right
		anchors.bottom: parent.bottom
		height: window.resizeMargin
		acceptedButtons: Qt.LeftButton
		cursorShape: Qt.SizeVerCursor
		enabled: !window.isMaximized
		onPressed: window.startSystemResize(Qt.BottomEdge)
	}

	MouseArea {
		anchors.left: parent.left
		anchors.top: parent.top
		width: window.resizeMargin
		height: window.resizeMargin
		acceptedButtons: Qt.LeftButton
		cursorShape: Qt.SizeFDiagCursor
		enabled: !window.isMaximized
		onPressed: window.startSystemResize(Qt.TopEdge | Qt.LeftEdge)
	}

	MouseArea {
		anchors.right: parent.right
		anchors.top: parent.top
		width: window.resizeMargin
		height: window.resizeMargin
		acceptedButtons: Qt.LeftButton
		cursorShape: Qt.SizeBDiagCursor
		enabled: !window.isMaximized
		onPressed: window.startSystemResize(Qt.TopEdge | Qt.RightEdge)
	}

	MouseArea {
		anchors.left: parent.left
		anchors.bottom: parent.bottom
		width: window.resizeMargin
		height: window.resizeMargin
		acceptedButtons: Qt.LeftButton
		cursorShape: Qt.SizeBDiagCursor
		enabled: !window.isMaximized
		onPressed: window.startSystemResize(Qt.BottomEdge | Qt.LeftEdge)
	}

	MouseArea {
		anchors.right: parent.right
		anchors.bottom: parent.bottom
		width: window.resizeMargin
		height: window.resizeMargin
		acceptedButtons: Qt.LeftButton
		cursorShape: Qt.SizeFDiagCursor
		enabled: !window.isMaximized
		onPressed: window.startSystemResize(Qt.BottomEdge | Qt.RightEdge)
	}

	component VectorTitleButton: Rectangle {
		width: 46
		height: parent.height
		color: "transparent"

		property string iconType: "minimize"
		property int iconSize: 12
		property real lineWidth: 1
		property color strokeColor: "#FFFFFF"
		property color hoverColor: "#1A1A1A"
		signal clicked()

		Rectangle {
			anchors.fill: parent
			color: mouse.containsMouse ? hoverColor : "transparent"
		}

		Canvas {
			id: iconCanvas
			anchors.centerIn: parent
			width: parent.iconSize
			height: parent.iconSize
			renderTarget: Canvas.Image

			onPaint: {
				var ctx = getContext("2d")
				ctx.setTransform(1, 0, 0, 1, 0, 0)
				ctx.clearRect(0, 0, width, height)
				ctx.strokeStyle = parent.strokeColor
				ctx.lineWidth = parent.lineWidth
				ctx.lineCap = "square"
				ctx.lineJoin = "miter"

				var offset = 0.5
				if (parent.iconType === "minimize") {
					var y = Math.round(height / 2) + 0.5
					ctx.beginPath()
					ctx.moveTo(offset, y)
					ctx.lineTo(width - offset, y)
					ctx.stroke()
				} else if (parent.iconType === "maximize") {
					ctx.strokeRect(offset, offset, width - 2 * offset, height - 2 * offset)
				} else if (parent.iconType === "restore") {
					var shift = 2
					ctx.fillStyle = "#000000"
					ctx.strokeRect(offset + shift, offset, width - 2 * offset - shift, height - 2 * offset - shift)
					ctx.fillRect(offset, offset + shift, width - 2 * offset - shift, height - 2 * offset - shift)
					ctx.strokeRect(offset, offset + shift, width - 2 * offset - shift, height - 2 * offset - shift)
				} else if (parent.iconType === "close") {
					ctx.beginPath()
					ctx.moveTo(offset, offset)
					ctx.lineTo(width - offset, height - offset)
					ctx.moveTo(width - offset, offset)
					ctx.lineTo(offset, height - offset)
					ctx.stroke()
				}
			}
		}

		MouseArea {
			id: mouse
			anchors.fill: parent
			hoverEnabled: true
			onClicked: parent.clicked()
		}

		onIconTypeChanged: iconCanvas.requestPaint()
		onIconSizeChanged: iconCanvas.requestPaint()
		onStrokeColorChanged: iconCanvas.requestPaint()
	}

	component VectorMaximizeButton: VectorTitleButton {
		property bool isMaximized: window.visibility === Window.Maximized
		iconType: isMaximized ? "restore" : "maximize"
	}
}
