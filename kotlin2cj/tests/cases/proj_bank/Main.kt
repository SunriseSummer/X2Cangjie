fun main() {
    val bank = Bank()
    val alice = bank.createAccount("Alice", 1000.0)
    val bob = bank.createAccount("Bob", 500.0)

    println("Initial state:")
    bank.printAllAccounts()

    println("\nTransfer 200 from Alice to Bob:")
    bank.transfer(1, 2, 200.0)

    println("\nAfter transfer:")
    bank.printAllAccounts()

    println("\nTry withdraw 2000 from Bob:")
    bob.withdraw(2000.0)

    println("\nFinal state:")
    bank.printAllAccounts()
}
