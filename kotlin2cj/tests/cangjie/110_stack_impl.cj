import std.collection.*

class Stack {
    let data = ArrayList<Int64>()
    func push(v: Int64) {
        data.add(v)
    }
    func pop(): Int64 {
        return data.remove(at: data.size - 1)
    }
    func peek(): Int64 {
        return data[data.size - 1]
    }
    func isEmpty(): Bool {
        return data.isEmpty()
    }
    func size(): Int64 {
        return data.size
    }
}

func isBalanced(s: String): Bool {
    let stack = ArrayList<Rune>()
    for (c in s.runes()) {
        if (((c == r'(') || (c == r'[')) || (c == r'{')) {
            stack.add(c)
        } else if (((c == r')') || (c == r']')) || (c == r'}')) {
            if (stack.isEmpty()) {
                return false
            }
            let top = stack.remove(at: stack.size - 1)
            if ((c == r')') && (top != r'(')) {
                return false
            }
            if ((c == r']') && (top != r'[')) {
                return false
            }
            if ((c == r'}') && (top != r'{')) {
                return false
            }
        }
    }
    return stack.isEmpty()
}

main() {
    let s = Stack()
    s.push(10)
    s.push(20)
    s.push(30)
    println("Top: ${s.peek()}")
    println("Pop: ${s.pop()}")
    println("Size: ${s.size()}")
    println("() balanced: ${isBalanced("()")}")
    println("([{}]) balanced: ${isBalanced("([{}])")}")
    println("([)] balanced: ${isBalanced("([)]")}")
    println("empty balanced: ${isBalanced("")}")
}
