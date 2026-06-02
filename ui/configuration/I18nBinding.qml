import QtQuick 2.15

QtObject {
	id: root
	property string languageCode: i18n.currentLanguage

	function text(key) {
		root.languageCode
		return i18n.t(key)
	}
}
