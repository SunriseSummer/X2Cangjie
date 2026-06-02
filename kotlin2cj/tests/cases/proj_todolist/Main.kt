fun main() {
    val todos = TodoList()
    todos.addItem("Buy groceries")
    todos.addItem("Write code")
    todos.addItem("Read book")
    todos.completeItem(2)
    todos.printAll()
    println("Done: ${todos.countDone()}, Pending: ${todos.countPending()}")
}
