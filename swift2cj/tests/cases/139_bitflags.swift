// Small #1 (iter11): bit flag packing and permission checks
func hasFlag(_ mask: Int, _ flag: Int) -> Bool {
    return (mask & flag) != 0
}

func addFlag(_ mask: Int, _ flag: Int) -> Int {
    return mask | flag
}

func removeFlag(_ mask: Int, _ flag: Int) -> Int {
    return mask & (~flag)
}

let read = 1
let write = 2
let execute = 4
var mask = 0
mask = addFlag(mask, read)
mask = addFlag(mask, execute)
print("mask=\(mask) r=\(hasFlag(mask, read)) w=\(hasFlag(mask, write)) x=\(hasFlag(mask, execute))")
mask = removeFlag(mask, read)
mask = addFlag(mask, write)
print("mask=\(mask) r=\(hasFlag(mask, read)) w=\(hasFlag(mask, write)) x=\(hasFlag(mask, execute))")
