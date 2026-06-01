fun main() {
    val reg = Registry()

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
