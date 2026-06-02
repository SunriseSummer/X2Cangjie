interface Command {
    fun execute(): String
    fun undo(): String
    fun describe(): String
}

class TextDocument {
    var text: String = ""
    val history = ArrayList<Command>()

    fun applyCommand(cmd: Command): String {
        val result = cmd.execute()
        history.add(cmd)
        return result
    }

    fun undoLast(): String {
        if (history.isEmpty()) return "Nothing to undo"
        val cmd = history.removeAt(history.size - 1)
        return cmd.undo()
    }

    fun historyLog(): ArrayList<String> {
        val result = ArrayList<String>()
        for (cmd in history) {
            result.add(cmd.describe())
        }
        return result
    }
}

class AppendCommand(val doc: TextDocument, val content: String) : Command {
    override fun execute(): String {
        doc.text = doc.text + content
        return "Appended: '$content'"
    }

    override fun undo(): String {
        doc.text = doc.text.substring(0, doc.text.length - content.length)
        return "Undone append: '$content'"
    }

    override fun describe(): String = "Append('$content')"
}

class ClearCommand(val doc: TextDocument) : Command {
    private var savedText: String = ""

    override fun execute(): String {
        savedText = doc.text
        doc.text = ""
        return "Cleared text (was: '$savedText')"
    }

    override fun undo(): String {
        doc.text = savedText
        return "Restored text: '$savedText'"
    }

    override fun describe(): String = "Clear"
}
