class Account(val owner: String, var balance: Int) {
    fun deposit(amount: Int) {
        balance += amount
    }
    fun withdraw(amount: Int): Boolean {
        if (amount > balance) {
            return false
        }
        balance -= amount
        return true
    }
}
fun main() {
    val acc = Account("alice", 100)
    acc.deposit(50)
    val ok1 = acc.withdraw(30)
    val ok2 = acc.withdraw(500)
    println("owner=${acc.owner} balance=${acc.balance}")
    println("ok1=$ok1 ok2=$ok2")
}
