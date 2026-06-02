import QtQuick 2.15

Item {
	id: root
	width: dropdown.visible ? dropdown.width : 34
	height: dropdown.visible ? 40 + dropdown.height : 34
	z: 150

	property var languages: []
	property string currentLanguage: ""
	property string interFontFamily: ""
	property alias dropdownOpen: dropdown.visible
	signal languageRequested(string code)

	function closeDropdown() {
		dropdown.visible = false
	}

	Rectangle {
		id: button
		width: 34
		height: 34
		color: "transparent"

		Image {
			anchors.centerIn: parent
			source: "../../media/icon_globe.png"
			width: 20
			height: 20
			fillMode: Image.PreserveAspectFit
			smooth: true
		}

		MouseArea {
			id: selectorMouse
			anchors.fill: parent
			hoverEnabled: true
			cursorShape: Qt.PointingHandCursor
			onClicked: dropdown.visible = !dropdown.visible
		}
	}

	Rectangle {
		id: dropdown
		visible: false
		x: 0
		y: 40
		width: 220
		height: Math.min(languageColumn.implicitHeight, 260)
		color: "#000000"
		border.width: 1
		border.color: "#2A2A2A"
		clip: true
		z: 160

		Flickable {
			anchors.fill: parent
			contentWidth: width
			contentHeight: languageColumn.implicitHeight
			boundsBehavior: Flickable.StopAtBounds

			Column {
				id: languageColumn
				width: parent.width

				Repeater {
					model: root.languages

					Rectangle {
						width: languageColumn.width
						height: 32
						color: languageMouse.containsMouse ? "#151515" : (modelData.code === root.currentLanguage ? "#0D0D0D" : "#000000")

						Text {
							anchors.left: parent.left
							anchors.right: parent.right
							anchors.leftMargin: 10
							anchors.rightMargin: 10
							anchors.verticalCenter: parent.verticalCenter
							text: modelData.native_name || modelData.english_name || modelData.code
							color: modelData.code === root.currentLanguage ? "#FFFFFF" : "#A0A0A0"
							font.family: root.interFontFamily
							font.pixelSize: 14
							elide: Text.ElideRight
						}

						MouseArea {
							id: languageMouse
							anchors.fill: parent
							hoverEnabled: true
							cursorShape: Qt.PointingHandCursor
							onClicked: {
								dropdown.visible = false
								root.languageRequested(modelData.code)
							}
						}
					}
				}
			}
		}
	}
}
