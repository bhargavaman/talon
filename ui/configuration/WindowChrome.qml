import QtQuick 2.15
import QtQuick.Window 2.15

Item {
	id: root
	property var appWindow
	property int titleBarHeight: 38
	property int titleFontSize: 14
	property int resizeMargin: 6
	property color borderColor: "#2A2A2A"
	default property alias content: contentBackground.data

	Rectangle {
		id: rootFrame
		anchors.fill: parent
		color: "transparent"
		border.color: root.borderColor
		border.width: 1

		Rectangle {
			id: titleBar
			width: parent.width
			height: root.titleBarHeight
			color: "#000000"

			MouseArea {
				anchors.fill: parent
				acceptedButtons: Qt.LeftButton
				onPressed: root.appWindow.startSystemMove()
				onDoubleClicked: {
					if (root.appWindow.visibility === Window.Maximized)
						root.appWindow.visibility = Window.Windowed
					else
						root.appWindow.visibility = Window.Maximized
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
					font.pixelSize: root.titleFontSize
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

				TitleButton {
					iconType: "minimize"
					onClicked: root.appWindow.showMinimized()
				}

				TitleButton {
					iconType: root.appWindow.visibility === Window.Maximized ? "restore" : "maximize"
					onClicked: {
						if (root.appWindow.visibility === Window.Maximized)
							root.appWindow.visibility = Window.Windowed
						else
							root.appWindow.visibility = Window.Maximized
					}
				}

				TitleButton {
					iconType: "close"
					iconSize: 12
					hoverColor: "#B00020"
					onClicked: Qt.quit()
				}
			}
		}

		Rectangle {
			y: root.titleBarHeight
			width: parent.width
			height: 1
			color: root.borderColor
		}

		Rectangle {
			id: contentBackground
			x: 0
			y: root.titleBarHeight + 1
			width: parent.width
			height: parent.height - root.titleBarHeight - 1
			color: "#000000"
			opacity: 0.9
		}
	}

	Rectangle {
		anchors.fill: parent
		color: "transparent"
		border.color: root.borderColor
		border.width: 1
	}

	MouseArea {
		anchors.left: parent.left
		anchors.top: parent.top
		anchors.bottom: parent.bottom
		width: root.resizeMargin
		acceptedButtons: Qt.LeftButton
		cursorShape: Qt.SizeHorCursor
		enabled: root.appWindow.visibility !== Window.Maximized
		onPressed: root.appWindow.startSystemResize(Qt.LeftEdge)
	}

	MouseArea {
		anchors.right: parent.right
		anchors.top: parent.top
		anchors.bottom: parent.bottom
		width: root.resizeMargin
		acceptedButtons: Qt.LeftButton
		cursorShape: Qt.SizeHorCursor
		enabled: root.appWindow.visibility !== Window.Maximized
		onPressed: root.appWindow.startSystemResize(Qt.RightEdge)
	}

	MouseArea {
		anchors.left: parent.left
		anchors.right: parent.right
		anchors.top: parent.top
		height: root.resizeMargin
		acceptedButtons: Qt.LeftButton
		cursorShape: Qt.SizeVerCursor
		enabled: root.appWindow.visibility !== Window.Maximized
		onPressed: root.appWindow.startSystemResize(Qt.TopEdge)
	}

	MouseArea {
		anchors.left: parent.left
		anchors.right: parent.right
		anchors.bottom: parent.bottom
		height: root.resizeMargin
		acceptedButtons: Qt.LeftButton
		cursorShape: Qt.SizeVerCursor
		enabled: root.appWindow.visibility !== Window.Maximized
		onPressed: root.appWindow.startSystemResize(Qt.BottomEdge)
	}

	MouseArea {
		anchors.left: parent.left
		anchors.top: parent.top
		width: root.resizeMargin
		height: root.resizeMargin
		acceptedButtons: Qt.LeftButton
		cursorShape: Qt.SizeFDiagCursor
		enabled: root.appWindow.visibility !== Window.Maximized
		onPressed: root.appWindow.startSystemResize(Qt.TopEdge | Qt.LeftEdge)
	}

	MouseArea {
		anchors.right: parent.right
		anchors.top: parent.top
		width: root.resizeMargin
		height: root.resizeMargin
		acceptedButtons: Qt.LeftButton
		cursorShape: Qt.SizeBDiagCursor
		enabled: root.appWindow.visibility !== Window.Maximized
		onPressed: root.appWindow.startSystemResize(Qt.TopEdge | Qt.RightEdge)
	}

	MouseArea {
		anchors.left: parent.left
		anchors.bottom: parent.bottom
		width: root.resizeMargin
		height: root.resizeMargin
		acceptedButtons: Qt.LeftButton
		cursorShape: Qt.SizeBDiagCursor
		enabled: root.appWindow.visibility !== Window.Maximized
		onPressed: root.appWindow.startSystemResize(Qt.BottomEdge | Qt.LeftEdge)
	}

	MouseArea {
		anchors.right: parent.right
		anchors.bottom: parent.bottom
		width: root.resizeMargin
		height: root.resizeMargin
		acceptedButtons: Qt.LeftButton
		cursorShape: Qt.SizeFDiagCursor
		enabled: root.appWindow.visibility !== Window.Maximized
		onPressed: root.appWindow.startSystemResize(Qt.BottomEdge | Qt.RightEdge)
	}
}

