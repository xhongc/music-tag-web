window.getLanuage = function (key) {
    if (!window.Lanuages) {
        return "";
    }
    var val = Lanuages[key];
    if (!val || val == "") {
        val = key;
    }
    return val
}