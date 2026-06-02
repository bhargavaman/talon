import QtQuick 2.15

Item {
	id: root
	property var browsers: []
	property string selectedBrowser: ""
	property string interFontFamily: ""
	property var localizer
	signal browserSelected(string packageId, string browserName)
	signal skipRequested()

	Text {
		anchors.top: parent.top
		anchors.topMargin: 40
		anchors.horizontalCenter: parent.horizontalCenter
		text: root.localizer.text("configuration.browser.title")
		color: "#FFFFFF"
		font.family: root.interFontFamily
		font.pixelSize: 22
	}

	Row {
		anchors.centerIn: parent
		spacing: 22

		Repeater {
			model: root.browsers

			Item {
				width: 132
				height: 164
				property bool hovered: mouseArea.containsMouse

				Rectangle {
					anchors.horizontalCenter: parent.horizontalCenter
					width: 132
					height: 132
					color: "transparent"
					border.width: 1
					border.color: modelData.packageId === "brave"
						? "#F4C430"
						: (root.selectedBrowser === modelData.packageId ? "#FFFFFF" : "#2A2A2A")

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
					font.family: root.interFontFamily
					font.pixelSize: 16
				}

				MouseArea {
					id: mouseArea
					anchors.fill: parent
					hoverEnabled: true
					cursorShape: Qt.PointingHandCursor
					onClicked: root.browserSelected(modelData.packageId, modelData.name)
				}

				Rectangle {
					visible: parent.hovered
					width: Math.min(300, root.width - 48)
					height: tooltipText.implicitHeight + 16
					color: "#0B0B0B"
					border.width: 1
					border.color: "#2A2A2A"
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
						font.family: root.interFontFamily
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
				text: root.localizer.text("configuration.browser.skip")
				color: skipBrowserMouse.containsMouse ? "#FFFFFF" : "#A0A0A0"
				font.family: root.interFontFamily
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
			onClicked: root.skipRequested()
		}
	}
}
