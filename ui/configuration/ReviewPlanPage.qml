import QtQuick 2.15

Item {
	id: root
	property var configItems: []
	property bool internetAvailable: true
	property string interFontFamily: ""
	signal removeItem(int index)
	signal resetDefaults()
	signal backRequested()
	signal advancedRequested()
	signal startRequested()

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

	Text {
		id: title
		anchors.top: parent.top
		anchors.topMargin: 40
		anchors.horizontalCenter: parent.horizontalCenter
		text: i18n.t("configuration.review.title")
		color: "#FFFFFF"
		font.family: root.interFontFamily
		font.pixelSize: 22
	}

	Rectangle {
		id: splitLine
		width: 1
		color: "#2A2A2A"
		anchors.horizontalCenter: parent.horizontalCenter
		anchors.top: title.bottom
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
			model: root.configItems

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
					font.family: root.interFontFamily
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
						onClicked: root.removeItem(index)
					}
				}

				Rectangle {
					visible: index < root.configItems.length - 1
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
			visible: root.configItems.length === 0
			text: i18n.t("configuration.review.empty")
			color: "#7A7A7A"
			font.family: root.interFontFamily
			font.pixelSize: 15
		}

		Rectangle {
			visible: leftPanel.hoveredTooltip.length > 0
			anchors.left: parent.left
			anchors.right: parent.right
			y: Math.min(Math.max(0, leftPanel.hoveredTooltipY), Math.max(0, leftPanel.height - height))
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
				font.family: root.interFontFamily
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
			text: i18n.t("configuration.review.guidance")
			color: "#FFFFFF"
			font.family: root.interFontFamily
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
			visible: root.internetAvailable && !root.hasBrowserInstallItem()

			Image { source: "../../media/icon_warning.png"; width: 24; height: 24; fillMode: Image.PreserveAspectFit; smooth: true }
			Text {
				anchors.verticalCenter: parent.verticalCenter
				text: i18n.t("configuration.review.no_browser_warning")
				color: "#FF0000"
				font.family: root.interFontFamily
				font.pixelSize: 15
			}
		}

		Row {
			id: noInternetInfo
			anchors.top: rightGuidanceText.bottom
			anchors.topMargin: 14
			anchors.left: parent.left
			spacing: 8
			visible: !root.internetAvailable

			Image { source: "../../media/icon_info.png"; width: 24; height: 24; fillMode: Image.PreserveAspectFit; smooth: true }
			Text {
				anchors.verticalCenter: parent.verticalCenter
				text: i18n.t("configuration.review.no_internet_info")
				color: "#00FFFF"
				font.family: root.interFontFamily
				font.pixelSize: 15
			}
		}

		Row {
			id: noUpdatesInfo
			anchors.top: noInternetInfo.visible ? noInternetInfo.bottom : (noBrowserWarning.visible ? noBrowserWarning.bottom : rightGuidanceText.bottom)
			anchors.topMargin: 8
			anchors.left: parent.left
			spacing: 8
			visible: !root.hasConfigureUpdatesItem()

			Image { source: "../../media/icon_warning.png"; width: 24; height: 24; fillMode: Image.PreserveAspectFit; smooth: true }
			Text {
				anchors.verticalCenter: parent.verticalCenter
				width: rightPanel.width - 40
				text: i18n.t("configuration.review.no_updates_warning")
				color: "#FF0000"
				font.family: root.interFontFamily
				font.pixelSize: 15
				wrapMode: Text.WordWrap
			}
		}

		Row {
			anchors.top: noUpdatesInfo.visible ? noUpdatesInfo.bottom : (noInternetInfo.visible ? noInternetInfo.bottom : (noBrowserWarning.visible ? noBrowserWarning.bottom : rightGuidanceText.bottom))
			anchors.topMargin: 8
			anchors.left: parent.left
			spacing: 8
			visible: root.configItems.length === 0

			Image { source: "../../media/icon_warning.png"; width: 24; height: 24; fillMode: Image.PreserveAspectFit; smooth: true }
			Text {
				anchors.verticalCenter: parent.verticalCenter
				text: i18n.t("configuration.review.nothing_to_do")
				color: "#FF0000"
				font.family: root.interFontFamily
				font.pixelSize: 15
			}
		}
	}

	Text {
		anchors.right: leftPanel.right
		anchors.bottom: parent.bottom
		anchors.bottomMargin: 28
		text: i18n.t("configuration.review.reset_defaults")
		color: resetDefaultsMouse.containsMouse ? "#FFFFFF" : "#A0A0A0"
		font.family: root.interFontFamily
		font.pixelSize: 15

		MouseArea {
			id: resetDefaultsMouse
			anchors.fill: parent
			hoverEnabled: true
			cursorShape: Qt.PointingHandCursor
			onClicked: root.resetDefaults()
		}
	}

	Item {
		id: backButton
		width: 30
		height: 30
		visible: root.internetAvailable
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
			onClicked: root.backRequested()
		}
	}

	Text {
		id: advancedButton
		anchors.left: rightPanel.left
		anchors.bottom: parent.bottom
		anchors.bottomMargin: 28
		text: i18n.t("configuration.review.advanced")
		color: advancedMouse.containsMouse ? "#FFFFFF" : "#A0A0A0"
		font.family: root.interFontFamily
		font.pixelSize: 15

		MouseArea {
			id: advancedMouse
			anchors.fill: parent
			hoverEnabled: true
			cursorShape: Qt.PointingHandCursor
			onClicked: root.advancedRequested()
		}
	}

	Item {
		width: rightGuidanceText.width
		height: 46
		anchors.left: advancedButton.left
		anchors.bottom: advancedButton.top
		anchors.bottomMargin: 12

		Rectangle {
			anchors.fill: parent
			color: root.configItems.length > 0 ? (startMouse.containsMouse ? "#EAEAEA" : "#FFFFFF") : "#1A1A1A"
			border.width: 1
			border.color: root.configItems.length > 0 ? "#FFFFFF" : "#2A2A2A"
		}

		Text {
			anchors.centerIn: parent
			text: i18n.t("configuration.review.start_button")
			color: root.configItems.length > 0 ? "#000000" : "#7A7A7A"
			font.family: root.interFontFamily
			font.pixelSize: 16
			font.bold: true
		}

		MouseArea {
			id: startMouse
			anchors.fill: parent
			hoverEnabled: true
			enabled: root.configItems.length > 0
			cursorShape: enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
			onClicked: root.startRequested()
		}
	}
}
