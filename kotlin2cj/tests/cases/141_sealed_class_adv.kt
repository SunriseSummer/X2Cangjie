// Sealed class hierarchy with when exhaustive matching
sealed class Result
class Success(val value: Int) : Result()
class Failure(val message: String) : Result()
class Pending(val progress: Int) : Result()

fun describe(r: Result): String {
    return when (r) {
        is Success -> "OK: ${r.value}"
        is Failure -> "ERR: ${r.message}"
        is Pending -> "WAIT: ${r.progress}%"
    }
}

sealed class Token
class NumberToken(val value: Int) : Token()
class PlusToken : Token()
class MinusToken : Token()
class MulToken : Token()

fun tokenToString(t: Token): String {
    return when (t) {
        is NumberToken -> t.value.toString()
        is PlusToken -> "+"
        is MinusToken -> "-"
        is MulToken -> "*"
    }
}

fun main() {
    val results = arrayListOf<Result>(
        Success(42),
        Failure("not found"),
        Pending(75),
        Success(100),
        Failure("timeout")
    )
    for (r in results) {
        println(describe(r))
    }

    // Token sequence
    val tokens = arrayListOf<Token>(
        NumberToken(3),
        PlusToken(),
        NumberToken(5),
        MulToken(),
        NumberToken(2)
    )
    val parts = ArrayList<String>()
    for (t in tokens) {
        parts.add(tokenToString(t))
    }
    println(parts.joinToString(" "))

    // Count by type
    var successCount = 0
    var failCount = 0
    for (r in results) {
        when (r) {
            is Success -> successCount++
            is Failure -> failCount++
            is Pending -> {}
        }
    }
    println("Success: $successCount, Failures: $failCount")
}
