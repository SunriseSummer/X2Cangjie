import std.collection.*

func findFirst(list: ArrayList<Int64>, target: Int64): Int64 {
    var i = 0
    while (true) {
        if (i >= list.size) {
            return -1
        }
        if (list[i] == target) {
            return i
        }
        i += 1
    }

    0
}

func readUntilDone(commands: ArrayList<String>): String {
    let result = StringBuilder()
    var idx = 0
    while (true) {
        if (idx >= commands.size) {
            return result.toString()
        }
        let cmd = commands[idx]
        if (cmd == "STOP") {
            return result.toString()
        }
        if ((result.toString().size > 0)) {
            result.append(", ")
        }
        result.append(cmd)
        idx += 1
    }

    ""
}

main() {
    let list = ArrayList([10, 20, 30, 40, 50])
    println("Find 30: index=${findFirst(list, 30)}")
    println("Find 99: index=${findFirst(list, 99)}")
    let cmds = ArrayList(["A", "B", "C", "STOP", "D"])
    println("Commands: ${readUntilDone(cmds)}")
    let cmds2 = ArrayList(["X", "Y", "Z"])
    println("Commands: ${readUntilDone(cmds2)}")
}
