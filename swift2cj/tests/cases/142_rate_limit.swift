// Medium #2 (iter11): fixed-window rate limiter
class RateLimiter {
    let limit: Int
    var counts: [String: Int] = [:]
    init(_ limit: Int) { self.limit = limit }
    func allow(_ user: String) -> Bool {
        let c = counts[user] ?? 0
        if c >= limit { return false }
        counts[user] = c + 1
        return true
    }
    func reset(_ user: String) { counts[user] = 0 }
}

let limiter = RateLimiter(3)
let events = ["a", "b", "a", "a", "b", "a", "c", "b", "b"]
for e in events {
    print(e + "=" + "\(limiter.allow(e))")
}
limiter.reset("a")
print("a=" + "\(limiter.allow("a"))")
