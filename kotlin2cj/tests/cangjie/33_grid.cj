main() {
    let size = 5
    for (i in 1..=size) {
        var line = ""
        for (j in 1..=size) {
            if (j <= i) {
                line += "*"
            } else {
                line += "."
            }
        }
        println(line)
    }
}
