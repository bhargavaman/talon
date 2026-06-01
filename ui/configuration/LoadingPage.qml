import QtQuick 2.15

Item {
	id: root
	property int step: 0
	property int lines: 12

	Timer {
		interval: 75
		repeat: true
		running: root.visible
		onTriggered: {
			root.step = (root.step + 1) % root.lines
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
			for (var i = 0; i < root.lines; i++) {
				var idx = (root.step + i) % root.lines
				var alpha = (i + 1) / root.lines
				ctx.save()
				ctx.rotate((Math.PI * 2 * idx) / root.lines)
				ctx.fillStyle = "rgba(255,255,255," + alpha + ")"
				ctx.fillRect(14, -1.5, 10, 3)
				ctx.restore()
			}
		}
	}
}

