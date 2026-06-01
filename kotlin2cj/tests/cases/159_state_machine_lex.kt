// Complex enum with when: state machine for parsing
enum class State {
    START, IN_WORD, IN_NUMBER, IN_STRING, DONE
}

fun lexAnalyze(input: String): ArrayList<String> {
    val tokens = ArrayList<String>()
    var state = State.START
    var buffer = StringBuilder()

    for (c in input) {
        when (state) {
            State.START -> {
                when {
                    c in 'a'..'z' || c in 'A'..'Z' -> {
                        state = State.IN_WORD
                        buffer.append(c)
                    }
                    c in '0'..'9' -> {
                        state = State.IN_NUMBER
                        buffer.append(c)
                    }
                    c == '"' -> {
                        state = State.IN_STRING
                    }
                    c == ' ' -> {}
                    else -> {
                        tokens.add(c.toString())
                    }
                }
            }
            State.IN_WORD -> {
                if (c in 'a'..'z' || c in 'A'..'Z' || c in '0'..'9') {
                    buffer.append(c)
                } else {
                    tokens.add("WORD:${buffer}")
                    buffer = StringBuilder()
                    state = State.START
                    if (c != ' ') tokens.add(c.toString())
                }
            }
            State.IN_NUMBER -> {
                if (c in '0'..'9') {
                    buffer.append(c)
                } else {
                    tokens.add("NUM:${buffer}")
                    buffer = StringBuilder()
                    state = State.START
                    if (c != ' ') tokens.add(c.toString())
                }
            }
            State.IN_STRING -> {
                if (c == '"') {
                    tokens.add("STR:${buffer}")
                    buffer = StringBuilder()
                    state = State.START
                } else {
                    buffer.append(c)
                }
            }
            State.DONE -> {}
        }
    }
    // Flush remaining buffer
    val remaining = buffer.toString()
    if (remaining.isNotEmpty()) {
        when (state) {
            State.IN_WORD -> tokens.add("WORD:${remaining}")
            State.IN_NUMBER -> tokens.add("NUM:${remaining}")
            else -> {}
        }
    }
    return tokens
}

fun main() {
    val tokens1 = lexAnalyze("hello 123 world")
    println(tokens1.joinToString(", "))

    val tokens2 = lexAnalyze("x+42*y")
    println(tokens2.joinToString(", "))

    val tokens3 = lexAnalyze("say \"hello world\" end")
    println(tokens3.joinToString(", "))

    val tokens4 = lexAnalyze("abc123 456def")
    println(tokens4.joinToString(", "))
}
