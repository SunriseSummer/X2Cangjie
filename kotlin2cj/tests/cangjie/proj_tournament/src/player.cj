package proj_tournament

import std.collection.*

class TournPlayer <: ToString {
    let name: String
    let skill: Int64
    init(name: String, skill: Int64) {
        this.name = name
        this.skill = skill
    }
    var wins: Int64 = 0
    var losses: Int64 = 0
    func record(): String {
        return "${wins}-${losses}"
    }
    func describe(): String {
        return "${name} (skill=${skill}, record=${record()})"
    }
    public func toString(): String {
        return "TournPlayer(name=${this.name}, skill=${this.skill})"
    }
}
