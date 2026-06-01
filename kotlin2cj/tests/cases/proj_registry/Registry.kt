class Service(val name: String, val version: Int) {
    var running: Boolean = false

    fun start() {
        running = true
        println("  Service '$name' v$version started")
    }

    fun stop() {
        running = false
        println("  Service '$name' v$version stopped")
    }

    fun status(): String {
        val state = if (running) "RUNNING" else "STOPPED"
        return "$name(v$version): $state"
    }
}

class Registry {
    val services = HashMap<String, Service>()

    fun register(name: String, version: Int): Boolean {
        for ((k, _) in services) {
            if (k == name) {
                println("  Registry: '$name' already registered")
                return false
            }
        }
        services[name] = Service(name, version)
        println("  Registry: '$name' registered")
        return true
    }

    fun findService(name: String): Service? {
        for ((k, v) in services) {
            if (k == name) return v
        }
        return null
    }

    fun unregister(name: String): Boolean {
        val svc = findService(name)
        if (svc != null) {
            if (svc.running) {
                svc.stop()
            }
            services.remove(name)
            println("  Registry: '$name' unregistered")
            return true
        }
        println("  Registry: '$name' not found")
        return false
    }

    fun startService(name: String) {
        val svc = findService(name)
        if (svc != null) {
            svc.start()
        } else {
            println("  Service '$name' not found")
        }
    }

    fun stopService(name: String) {
        val svc = findService(name)
        if (svc != null) {
            svc.stop()
        } else {
            println("  Service '$name' not found")
        }
    }

    fun listServices() {
        if (services.isEmpty()) {
            println("  (no services)")
            return
        }
        val names = mutableListOf<String>()
        for ((k, _) in services) {
            names.add(k)
        }
        // Sort names manually
        for (i in 0 until names.size) {
            for (j in i + 1 until names.size) {
                if (names[j] < names[i]) {
                    val tmp = names[i]
                    names[i] = names[j]
                    names[j] = tmp
                }
            }
        }
        for (n in names) {
            val svc = findService(n)
            if (svc != null) {
                println("  ${svc.status()}")
            }
        }
    }

    fun countRunning(): Int {
        var count = 0
        for ((_, svc) in services) {
            if (svc.running) count++
        }
        return count
    }

    fun totalServices(): Int = services.size
}
