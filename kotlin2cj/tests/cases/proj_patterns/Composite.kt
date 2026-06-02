interface FileSystemNode {
    val nodeName: String
    fun size(): Int
    fun list(indent: String = ""): MutableList<String>
    fun find(name: String): FileSystemNode?
    fun countNodes(): Int
    fun kind(): String
}

class FileNode(override val nodeName: String, val content: String) : FileSystemNode {
    override fun size(): Int = content.length

    override fun list(indent: String): MutableList<String> {
        return mutableListOf("$indent- FILE $nodeName (${size()})")
    }

    override fun find(name: String): FileSystemNode? {
        return if (nodeName == name) this else null
    }

    override fun countNodes(): Int = 1

    override fun kind(): String = "file"

    fun preview(): String {
        return if (content.length <= 12) {
            content
        } else {
            content.substring(0, 12)
        }
    }
}

class DirectoryNode(override val nodeName: String) : FileSystemNode {
    private val children = ArrayList<FileSystemNode>()

    fun add(node: FileSystemNode): DirectoryNode {
        children.add(node)
        return this
    }

    fun remove(name: String): Boolean {
        var i = 0
        while (i < children.size) {
            if (children[i].nodeName == name) {
                children.removeAt(i)
                return true
            }
            i += 1
        }
        return false
    }

    fun childNames(): MutableList<String> {
        val result = mutableListOf<String>()
        for (child in children) {
            result.add(child.nodeName)
        }
        return result
    }

    override fun size(): Int {
        var sum = 0
        for (child in children) {
            sum += child.size()
        }
        return sum
    }

    override fun list(indent: String): MutableList<String> {
        val lines = mutableListOf<String>()
        lines.add("$indent+ DIR $nodeName (${size()})")
        for (child in children) {
            for (line in child.list(indent + "  ")) {
                lines.add(line)
            }
        }
        return lines
    }

    override fun find(name: String): FileSystemNode? {
        if (nodeName == name) {
            return this
        }
        for (child in children) {
            val found = child.find(name)
            if (found != null) {
                return found
            }
        }
        return null
    }

    override fun countNodes(): Int {
        var total = 1
        for (child in children) {
            total += child.countNodes()
        }
        return total
    }

    override fun kind(): String = "directory"

    fun flatten(prefix: String = ""): MutableList<String> {
        val lines = mutableListOf<String>()
        val current = if (prefix == "") nodeName else "$prefix/$nodeName"
        lines.add(current)
        for (child in children) {
            if (child is DirectoryNode) {
                for (line in child.flatten(current)) {
                    lines.add(line)
                }
            } else {
                lines.add("$current/${child.nodeName}")
            }
        }
        return lines
    }
}
