// Medium #1 (iter12): coupon rule selection
enum CouponKind {
    case amount
    case percent
}

class Coupon {
    let code: String
    let kind: CouponKind
    let value: Int
    let minTotal: Int
    init(_ code: String, _ kind: CouponKind, _ value: Int, _ minTotal: Int) {
        self.code = code
        self.kind = kind
        self.value = value
        self.minTotal = minTotal
    }
    func discount(_ total: Int) -> Int {
        if total < minTotal { return 0 }
        switch kind {
        case .amount:
            return value
        case .percent:
            return total * value / 100
        }
    }
}

func bestCoupon(_ total: Int, _ coupons: [Coupon]) -> String {
    var bestCode = "none"
    var bestDiscount = 0
    for c in coupons {
        let d = c.discount(total)
        if d > bestDiscount {
            bestDiscount = d
            bestCode = c.code
        }
    }
    return bestCode + ":" + "\(bestDiscount)" + ":pay=" + "\(total - bestDiscount)"
}

let coupons = [Coupon("A10", .amount, 10, 50), Coupon("P20", .percent, 20, 80), Coupon("A30", .amount, 30, 120)]
for total in [40, 90, 150] { print(bestCoupon(total, coupons)) }
