import QtQuick 2.15

Rectangle {
	id: root
	width: 46
	height: parent ? parent.height : 38
	color: "transparent"

	property string iconType: "minimize"
	property int iconSize: 12
	property real lineWidth: 1
	property color strokeColor: "#FFFFFF"
	property color hoverColor: "#1A1A1A"
	signal clicked()

	Rectangle {
		anchors.fill: parent
		color: mouse.containsMouse ? root.hoverColor : "transparent"
	}

	Canvas {
		id: iconCanvas
		anchors.centerIn: parent
		width: root.iconSize
		height: root.iconSize
		renderTarget: Canvas.Image

		onPaint: {
			var ctx = getContext("2d")
			ctx.setTransform(1, 0, 0, 1, 0, 0)
			ctx.clearRect(0, 0, width, height)
			ctx.strokeStyle = root.strokeColor
			ctx.lineWidth = root.lineWidth
			ctx.lineCap = "square"
			ctx.lineJoin = "miter"
			var offset = 0.5
			if (root.iconType === "minimize") {
				var y = Math.round(height / 2) + 0.5
				ctx.beginPath()
				ctx.moveTo(offset, y)
				ctx.lineTo(width - offset, y)
				ctx.stroke()
			} else if (root.iconType === "maximize") {
				ctx.strokeRect(offset, offset, width - 2 * offset, height - 2 * offset)
			} else if (root.iconType === "restore") {
				var shift = 2
				ctx.fillStyle = "#000000"
				ctx.strokeRect(offset + shift, offset, width - 2 * offset - shift, height - 2 * offset - shift)
				ctx.fillRect(offset, offset + shift, width - 2 * offset - shift, height - 2 * offset - shift)
				ctx.strokeRect(offset, offset + shift, width - 2 * offset - shift, height - 2 * offset - shift)
			} else if (root.iconType === "close") {
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
		onClicked: root.clicked()
	}

	onIconTypeChanged: iconCanvas.requestPaint()
	onIconSizeChanged: iconCanvas.requestPaint()
	onStrokeColorChanged: iconCanvas.requestPaint()
}

