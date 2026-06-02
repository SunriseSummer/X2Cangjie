package proj_extensions

import std.collection.*

extend ArrayList<Int64> {
    func computeAvg(): Int64 {
        if (this.size == 0) {
            return 0
        }
        var sum = 0
        for (n in this) {
            sum += n
        }
        return sum / this.size
    }
}
