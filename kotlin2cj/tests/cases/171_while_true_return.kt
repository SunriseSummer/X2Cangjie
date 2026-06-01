// Test: while(true) return type inference
fun findFirst(list: ArrayList<Int>, target: Int): Int {
    var i = 0
    while (true) {
        if (i >= list.size) return -1
        if (list[i] == target) return i
        i++
    }
}

fun readUntilDone(commands: ArrayList<String>): String {
    val result = StringBuilder()
    var idx = 0
    while (true) {
        if (idx >= commands.size) return result.toString()
        val cmd = commands[idx]
        if (cmd == "STOP") return result.toString()
        if (result.isNotEmpty()) result.append(", ")
        result.append(cmd)
        idx++
    }
}

fun main() {
    val list = arrayListOf(10, 20, 30, 40, 50)
    println("Find 30: index=${findFirst(list, 30)}")
    println("Find 99: index=${findFirst(list, 99)}")

    val cmds = arrayListOf("A", "B", "C", "STOP", "D")
    println("Commands: ${readUntilDone(cmds)}")

    val cmds2 = arrayListOf("X", "Y", "Z")
    println("Commands: ${readUntilDone(cmds2)}")
}
