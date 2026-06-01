// Stack implementation and balanced parentheses checker
class Stack {
    private val data = ArrayList<Int>()

    fun push(v: Int) {
        data.add(v)
    }

    fun pop(): Int {
        return data.removeAt(data.size - 1)
    }

    fun peek(): Int {
        return data[data.size - 1]
    }

    fun isEmpty(): Boolean {
        return data.isEmpty()
    }

    fun size(): Int {
        return data.size
    }
}

fun isBalanced(s: String): Boolean {
    val stack = ArrayList<Char>()
    for (c in s) {
        if (c == '(' || c == '[' || c == '{') {
            stack.add(c)
        } else if (c == ')' || c == ']' || c == '}') {
            if (stack.isEmpty()) return false
            val top = stack.removeAt(stack.size - 1)
            if (c == ')' && top != '(') return false
            if (c == ']' && top != '[') return false
            if (c == '}' && top != '{') return false
        }
    }
    return stack.isEmpty()
}

fun main() {
    val s = Stack()
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
