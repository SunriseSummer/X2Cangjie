enum class LogLevel(val weight: Int) {
    DEBUG(1),
    INFO(2),
    WARN(3),
    ERROR(4)
}

data class LogMessage(val level: LogLevel, val channel: String, val text: String)

abstract class Logger(val loggerName: String, val threshold: LogLevel) {
    var next: Logger? = null
    val handled = ArrayList<String>()

    fun setNext(logger: Logger): Logger {
        next = logger
        return logger
    }

    fun log(message: LogMessage): MutableList<String> {
        val lines = mutableListOf<String>()
        if (message.level.weight >= threshold.weight) {
            val rendered = write(message)
            handled.add(rendered)
            lines.add("$loggerName handled ${message.level}:${message.channel}:${message.text}")
        } else {
            lines.add("$loggerName skipped ${message.level}:${message.channel}:${message.text}")
        }
        if (next != null) {
            for (line in next!!.log(message)) {
                lines.add(line)
            }
        }
        return lines
    }

    abstract fun write(message: LogMessage): String

    fun summary(): String {
        val entriesText = handled.joinToString(" || ")
        return "$loggerName stored=${handled.size} entries=$entriesText"
    }
}

class ConsoleLogger(name: String, threshold: LogLevel) : Logger(name, threshold) {
    override fun write(message: LogMessage): String {
        return "console:${message.level}:${message.channel}:${message.text}"
    }
}

class FileLogger(name: String, threshold: LogLevel) : Logger(name, threshold) {
    override fun write(message: LogMessage): String {
        return "file:${message.level}:${message.channel}:${message.text}"
    }
}

class ErrorLogger(name: String, threshold: LogLevel) : Logger(name, threshold) {
    override fun write(message: LogMessage): String {
        return "error:${message.level}:${message.channel}:${message.text.manualUpper()}"
    }
}
