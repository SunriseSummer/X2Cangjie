enum class Product(val label: String, val price: Int) {
    WATER("Water", 3),
    JUICE("Juice", 5),
    TEA("Tea", 4)
}

fun allProducts(): MutableList<Product> {
    return mutableListOf(Product.WATER, Product.JUICE, Product.TEA)
}

sealed class MachineState
class IdleState : MachineState()
class HasMoneyState(val balance: Int) : MachineState()
class DispensingState(val product: Product, val change: Int) : MachineState()

class VendingMachine {
    var state: MachineState = IdleState()
    private val inventory = HashMap<String, Int>()
    val log = ArrayList<String>()

    init {
        inventory[Product.WATER.label] = 2
        inventory[Product.JUICE.label] = 1
        inventory[Product.TEA.label] = 3
    }

    fun stockOf(product: Product): Int {
        return inventory[product.label] ?: 0
    }

    fun status(): String {
        val balanceText = when (state) {
            is IdleState -> "Idle(balance=0)"
            is HasMoneyState -> {
                val current = state as HasMoneyState
                "HasMoney(balance=${current.balance})"
            }
            is DispensingState -> {
                val current = state as DispensingState
                "Dispensing(product=${current.product.label}, change=${current.change})"
            }
        }
        val stockLines = mutableListOf<String>()
        for (product in allProducts()) {
            stockLines.add("${product.label}=${stockOf(product)}")
        }
        val joinedStock = stockLines.joinToString(", ")
        return "$balanceText stock[$joinedStock]"
    }

    fun insertCoin(amount: Int): String {
        if (amount <= 0) {
            val message = "insert rejected amount=$amount"
            log.add(message)
            return message
        }
        val message = when (state) {
            is IdleState -> {
                state = HasMoneyState(amount)
                "inserted $amount -> balance $amount"
            }
            is HasMoneyState -> {
                val current = state as HasMoneyState
                val next = current.balance + amount
                state = HasMoneyState(next)
                "inserted $amount -> balance $next"
            }
            is DispensingState -> "insert blocked during dispensing"
        }
        log.add(message)
        return message
    }

    fun select(product: Product): String {
        val stock = stockOf(product)
        val message = when (state) {
            is IdleState -> "select ${product.label} failed: no money"
            is HasMoneyState -> {
                val current = state as HasMoneyState
                if (stock <= 0) {
                    "select ${product.label} failed: out of stock"
                } else if (current.balance < product.price) {
                    "select ${product.label} failed: need ${product.price - current.balance} more"
                } else {
                    val change = current.balance - product.price
                    inventory[product.label] = stock - 1
                    state = DispensingState(product, change)
                    "select ${product.label} accepted: change $change"
                }
            }
            is DispensingState -> "select ${product.label} blocked: dispensing"
        }
        log.add(message)
        return message
    }

    fun finishDispense(): String {
        val message = when (state) {
            is DispensingState -> {
                val current = state as DispensingState
                state = IdleState()
                "dispensed ${current.product.label} change ${current.change}"
            }
            else -> "dispense skipped"
        }
        log.add(message)
        return message
    }

    fun refund(): String {
        val message = when (state) {
            is HasMoneyState -> {
                val current = state as HasMoneyState
                state = IdleState()
                "refund ${current.balance}"
            }
            is IdleState -> "refund 0"
            is DispensingState -> "refund blocked during dispensing"
        }
        log.add(message)
        return message
    }

    fun auditLines(): MutableList<String> {
        val lines = mutableListOf<String>()
        var index = 1
        for (entry in log) {
            lines.add("$index.$entry")
            index += 1
        }
        return lines
    }
}
