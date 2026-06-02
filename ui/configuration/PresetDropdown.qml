import QtQuick 2.15

Item {
	id: root
	width: parent ? parent.width : 220
	height: dropdown.visible ? 32 + dropdown.height : 32
	z: 80

	property var presets: []
	property string selectedPresetKey: ""
	property string interFontFamily: ""
	property var localizer
	property bool openUp: false
	signal presetRequested(string key)

	property string selectedPresetName: {
		for (var i = 0; i < root.presets.length; i++) {
			var preset = root.presets[i]
			if (preset.key === root.selectedPresetKey)
				return preset.name
		}
		return root.localizer.text("configuration.review.custom_preset")
	}

	function closeDropdown() {
		dropdown.visible = false
	}

	Rectangle {
		id: button
		y: root.openUp && dropdown.visible ? dropdown.height + 4 : 0
		width: parent.width
		height: 32
		color: presetMouse.containsMouse || dropdown.visible ? "#101010" : "#000000"
		border.width: 1
		border.color: dropdown.visible ? "#FFFFFF" : "#2A2A2A"

		Text {
			anchors.left: parent.left
			anchors.right: arrowCanvas.left
			anchors.leftMargin: 10
			anchors.rightMargin: 8
			anchors.verticalCenter: parent.verticalCenter
			text: root.selectedPresetName
			color: "#FFFFFF"
			font.family: root.interFontFamily
			font.pixelSize: 14
			elide: Text.ElideRight
		}

		Canvas {
			id: arrowCanvas
			width: 18
			height: 18
			anchors.right: parent.right
			anchors.rightMargin: 8
			anchors.verticalCenter: parent.verticalCenter
			renderTarget: Canvas.Image

			onPaint: {
				var ctx = getContext("2d")
				ctx.setTransform(1, 0, 0, 1, 0, 0)
				ctx.clearRect(0, 0, width, height)
				ctx.strokeStyle = "#A0A0A0"
				ctx.lineWidth = 1.5
				ctx.lineCap = "square"
				ctx.lineJoin = "miter"
				var cx = width / 2
				var cy = width / 2
				ctx.beginPath()
				ctx.moveTo(cx - 5, cy - 2)
				ctx.lineTo(cx, cy + 3)
				ctx.lineTo(cx + 5, cy - 2)
				ctx.stroke()
			}
		}

		MouseArea {
			id: presetMouse
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
		y: root.openUp ? 0 : 36
		width: root.width
		height: Math.min(presetColumn.implicitHeight, 220)
		color: "#000000"
		border.width: 1
		border.color: "#2A2A2A"
		clip: true
		z: 90

		Flickable {
			anchors.fill: parent
			contentWidth: width
			contentHeight: presetColumn.implicitHeight
			boundsBehavior: Flickable.StopAtBounds

			Column {
				id: presetColumn
				width: parent.width

				Repeater {
					model: root.presets

					Rectangle {
						width: presetColumn.width
						height: 32
						color: presetOptionMouse.containsMouse ? "#151515" : (modelData.key === root.selectedPresetKey ? "#0D0D0D" : "#000000")

						Text {
							anchors.left: parent.left
							anchors.right: parent.right
							anchors.leftMargin: 10
							anchors.rightMargin: 10
							anchors.verticalCenter: parent.verticalCenter
							text: modelData.name
							color: modelData.key === root.selectedPresetKey ? "#FFFFFF" : "#A0A0A0"
							font.family: root.interFontFamily
							font.pixelSize: 14
							elide: Text.ElideRight
						}

						MouseArea {
							id: presetOptionMouse
							anchors.fill: parent
							hoverEnabled: true
							cursorShape: Qt.PointingHandCursor
							onClicked: {
								dropdown.visible = false
								root.presetRequested(modelData.key)
							}
						}
					}
				}
			}
		}
	}
}
