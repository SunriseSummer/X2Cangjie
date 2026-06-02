package proj_registry

import std.collection.*

class Service {
    let name: String
    let version: Int64
    init(name: String, version: Int64) {
        this.name = name
        this.version = version
    }
    var running: Bool = false
    func start() {
        running = true
        println("  Service '${name}' v${version} started")
    }
    func stop() {
        running = false
        println("  Service '${name}' v${version} stopped")
    }
    func status(): String {
        let state = if (running) {
            "RUNNING"
        } else {
            "STOPPED"
        }
        return "${name}(v${version}): ${state}"
    }
}

class Registry {
    let services = HashMap<String, Service>()
    func register(name: String, version: Int64): Bool {
        for ((k, _) in services) {
            if (k == name) {
                println("  Registry: '${name}' already registered")
                return false
            }
        }
        services[name] = Service(name, version)
        println("  Registry: '${name}' registered")
        return true
    }
    func findService(name: String): ?Service {
        for ((k, v) in services) {
            if (k == name) {
                return v
            }
        }
        return None
    }
    func unregister(name: String): Bool {
        let svc = findService(name)
        if (let Some(svc) <- svc) {
            if (svc.running) {
                svc.stop()
            }
            services.remove(name)
            println("  Registry: '${name}' unregistered")
            return true
        }
        println("  Registry: '${name}' not found")
        return false
    }
    func startService(name: String) {
        let svc = findService(name)
        if (let Some(svc) <- svc) {
            svc.start()
        } else {
            println("  Service '${name}' not found")
        }
    }
    func stopService(name: String) {
        let svc = findService(name)
        if (let Some(svc) <- svc) {
            svc.stop()
        } else {
            println("  Service '${name}' not found")
        }
    }
    func listServices() {
        if (services.isEmpty()) {
            println("  (no services)")
            return
        }
        let names = ArrayList<String>()
        for ((k, _) in services) {
            names.add(k)
        }
        for (i in 0..names.size) {
            for (j in (i + 1)..names.size) {
                if (names[j] < names[i]) {
                    let tmp = names[i]
                    names[i] = names[j]
                    names[j] = tmp
                }
            }
        }
        for (n in names) {
            let svc = findService(n)
            if (let Some(svc) <- svc) {
                println("  ${svc.status()}")
            }
        }
    }
    func countRunning(): Int64 {
        var count = 0
        for ((_, svc) in services) {
            if (svc.running) {
                count += 1
            }
        }
        return count
    }
    func totalServices(): Int64 {
        return services.size
    }
}

main() {
    let reg = Registry()
    println("Register services:")
    reg.register("auth", 1)
    reg.register("database", 2)
    reg.register("cache", 1)
    reg.register("auth", 3)
    println("\nAll services:")
    reg.listServices()
    println("\nStart some services:")
    reg.startService("auth")
    reg.startService("database")
    reg.startService("missing")
    println("\nAll services:")
    reg.listServices()
    println("Running: ${reg.countRunning()}, Total: ${reg.totalServices()}")
    println("\nStop auth:")
    reg.stopService("auth")
    println("\nUnregister cache:")
    reg.unregister("cache")
    println("\nAll services:")
    reg.listServices()
    println("Running: ${reg.countRunning()}, Total: ${reg.totalServices()}")
}