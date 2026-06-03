package proj_collections

import std.collection.*
import std.sort.*

class DataProcessor {
    let data: ArrayList<Int64>
    init(data: ArrayList<Int64>) {
        this.data = data
    }
    func doubleAll(): ArrayList<Int64> {
        return collectArrayList(data.iterator().map({ it => it * 2 }))
    }
    func onlyPositive(): ArrayList<Int64> {
        return collectArrayList(data.iterator().filter({ it => it > 0 }))
    }
    func removeNegative(): ArrayList<Int64> {
        return collectArrayList(data.iterator().filter({ _e => !({ it => it < 0 })(_e) }))
    }
    func withIndices(): ArrayList<Int64> {
        return collectArrayList(data.iterator().enumerate().map({ _p => ({ i, v => (i * 10) + v })(_p[0], _p[1]) }))
    }
    func total(): Int64 {
        return data.iterator().fold<Int64>(0, {acc, x => acc + x})
    }
    func productReduce(): Int64 {
        return data.iterator().reduce({ a, b => a * b }).getOrThrow()
    }
}
