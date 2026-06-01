data class TodoItem(val id: Int, val title: String, val done: Boolean)

class TodoList {
    val items = mutableListOf<TodoItem>()
    var nextId = 1

    fun addItem(title: String) {
        items.add(TodoItem(nextId, title, false))
        nextId++
    }

    fun completeItem(id: Int) {
        for (i in 0 until items.size) {
            if (items[i].id == id) {
                items[i] = TodoItem(items[i].id, items[i].title, true)
            }
        }
    }

    fun printAll() {
        for (item in items) {
            val status = if (item.done) "[x]" else "[ ]"
            println("$status #${item.id}: ${item.title}")
        }
    }

    fun countDone(): Int = items.count { it.done }
    fun countPending(): Int = items.count { !it.done }
}
