interface Command {
    fun execute(): String
    fun undo(): String
    fun describe(): String
}

class TextEditor(initialText: String = "") {
    var text: String = initialText
    private val undoStack = ArrayList<Command>()
    private val redoStack = ArrayList<Command>()
    val timeline = ArrayList<String>()

    fun normalizePosition(position: Int): Int {
        if (position < 0) {
            return 0
        }
        if (position > text.length) {
            return text.length
        }
        return position
    }

    fun insertRaw(position: Int, content: String) {
        val safe = normalizePosition(position)
        val prefix = text.substring(0, safe)
        val suffix = text.substring(safe, text.length)
        text = prefix + content + suffix
    }

    fun deleteRaw(position: Int, length: Int): String {
        if (length <= 0) {
            return ""
        }
        val safe = normalizePosition(position)
        var end = safe + length
        if (end > text.length) {
            end = text.length
        }
        val removed = text.substring(safe, end)
        text = text.substring(0, safe) + text.substring(end, text.length)
        return removed
    }

    fun findFirst(target: String): Int {
        if (target.length == 0) {
            return 0
        }
        var start = 0
        while (start <= text.length - target.length) {
            val piece = text.substring(start, start + target.length)
            if (piece == target) {
                return start
            }
            start += 1
        }
        return -1
    }

    fun replaceFirstRaw(target: String, replacement: String): Boolean {
        if (!text.contains(target)) {
            return false
        }
        val index = findFirst(target)
        if (index < 0) {
            return false
        }
        text = text.substring(0, index) + replacement + text.substring(index + target.length, text.length)
        return true
    }

    fun replaceAllRaw(target: String, replacement: String): Int {
        var count = 0
        while (text.contains(target)) {
            val changed = replaceFirstRaw(target, replacement)
            if (!changed) {
                break
            }
            count += 1
        }
        return count
    }

    fun executeCommand(command: Command): String {
        val result = command.execute()
        undoStack.add(command)
        redoStack.clear()
        timeline.add("execute:${command.describe()} => $text")
        return result
    }

    fun undo(): String {
        if (undoStack.size == 0) {
            val message = "undo: nothing"
            timeline.add(message)
            return message
        }
        val command = undoStack.removeAt(undoStack.size - 1)
        val result = command.undo()
        redoStack.add(command)
        timeline.add("undo:${command.describe()} => $text")
        return result
    }

    fun redo(): String {
        if (redoStack.size == 0) {
            val message = "redo: nothing"
            timeline.add(message)
            return message
        }
        val command = redoStack.removeAt(redoStack.size - 1)
        val result = command.execute()
        undoStack.add(command)
        timeline.add("redo:${command.describe()} => $text")
        return result
    }

    fun snapshot(): String {
        return if (text == "") "<empty>" else text
    }

    fun historySize(): Int {
        return undoStack.size
    }

    fun redoSize(): Int {
        return redoStack.size
    }
}

class InsertCommand(
    val editor: TextEditor,
    val position: Int,
    val content: String
) : Command {
    var lastPosition = 0
    var executed = false

    override fun execute(): String {
        lastPosition = editor.normalizePosition(position)
        editor.insertRaw(lastPosition, content)
        executed = true
        return "insert '$content' at $lastPosition"
    }

    override fun undo(): String {
        if (!executed) {
            return "undo insert skipped"
        }
        editor.deleteRaw(lastPosition, content.length)
        return "undo insert '$content' at $lastPosition"
    }

    override fun describe(): String {
        return "Insert(position=$position, content=$content)"
    }
}

class DeleteCommand(
    val editor: TextEditor,
    val position: Int,
    val length: Int
) : Command {
    var removedText = ""
    var actualPosition = 0
    var executed = false

    override fun execute(): String {
        actualPosition = editor.normalizePosition(position)
        removedText = editor.deleteRaw(actualPosition, length)
        executed = true
        return "delete '$removedText' at $actualPosition"
    }

    override fun undo(): String {
        if (!executed) {
            return "undo delete skipped"
        }
        editor.insertRaw(actualPosition, removedText)
        return "undo delete '$removedText' at $actualPosition"
    }

    override fun describe(): String {
        return "Delete(position=$position, length=$length)"
    }
}

class ReplaceCommand(
    val editor: TextEditor,
    val target: String,
    val replacement: String,
    val replaceAll: Boolean = false
) : Command {
    var beforeText = ""
    var changedCount = 0

    override fun execute(): String {
        beforeText = editor.text
        changedCount = if (replaceAll) {
            editor.replaceAllRaw(target, replacement)
        } else {
            if (editor.replaceFirstRaw(target, replacement)) 1 else 0
        }
        return "replace '$target' with '$replacement' count=$changedCount"
    }

    override fun undo(): String {
        val current = editor.text
        editor.text = beforeText
        return "undo replace restore '$current'"
    }

    override fun describe(): String {
        return "Replace(target=$target, replacement=$replacement, replaceAll=$replaceAll)"
    }
}
