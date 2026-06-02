package proj_patterns

import std.collection.*
import std.deriving.*

interface Command {
    func execute(): String
    func undo(): String
    func describe(): String
}

class TextDocument {
    var text: String = ""
    let history = ArrayList<Command>()
    func applyCommand(cmd: Command): String {
        let result = cmd.execute()
        history.add(cmd)
        return result
    }
    func undoLast(): String {
        if (history.isEmpty()) {
            return "Nothing to undo"
        }
        let cmd = history.remove(at: history.size - 1)
        return cmd.undo()
    }
    func historyLog(): ArrayList<String> {
        let result = ArrayList<String>()
        for (cmd in history) {
            result.add(cmd.describe())
        }
        return result
    }
}

class AppendCommand <: Command {
    let doc: TextDocument
    let content: String
    init(doc: TextDocument, content: String) {
        this.doc = doc
        this.content = content
    }
    public override func execute(): String {
        doc.text = doc.text.toString() + content
        return "Appended: '${content}'"
    }
    public override func undo(): String {
        doc.text = doc.text[0..doc.text.size - content.size]
        return "Undone append: '${content}'"
    }
    public override func describe(): String {
        return "Append('${content}')"
    }
}

class ClearCommand <: Command {
    let doc: TextDocument
    init(doc: TextDocument) {
        this.doc = doc
    }
    var savedText: String = ""
    public override func execute(): String {
        savedText = doc.text
        doc.text = ""
        return "Cleared text (was: '${savedText}')"
    }
    public override func undo(): String {
        doc.text = savedText
        return "Restored text: '${savedText}'"
    }
    public override func describe(): String {
        return "Clear"
    }
}
