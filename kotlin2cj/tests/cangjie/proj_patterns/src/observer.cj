package proj_patterns

import std.collection.*
import std.deriving.*

interface Observer {
    func onEvent(event: String): Unit
    func observerName(): String
}

class EventBus {
    let listeners = ArrayList<Observer>()
    func subscribe(observer: Observer) {
        listeners.add(observer)
    }
    func publish(event: String) {
        for (listener in listeners) {
            listener.onEvent(event)
        }
    }
    func subscriberCount(): Int64 {
        return listeners.size
    }
}

class LogObserver <: Observer & ToString {
    let name: String
    init(name: String) {
        this.name = name
    }
    let logs = ArrayList<String>()
    public override func onEvent(event: String) {
        logs.add("[${name}] received: ${event}")
    }
    public override func observerName(): String {
        return name
    }
    public override func toString(): String {
        let builder = StringBuilder()
        for (log in logs) {
            builder.append(log)
            builder.append("\n")
        }
        return builder.toString().trimAscii()
    }
}

class FilterObserver <: Observer {
    let name: String
    let keyword: String
    init(name: String, keyword: String) {
        this.name = name
        this.keyword = keyword
    }
    let logs = ArrayList<String>()
    public override func onEvent(event: String) {
        if (event.contains(keyword)) {
            logs.add("[${name}] matched '${keyword}' in: ${event}")
        }
    }
    public override func observerName(): String {
        return name
    }
}
