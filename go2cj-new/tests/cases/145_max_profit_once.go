package main

import "fmt"

func maxProfit(prices []int) int {
if len(prices) == 0 {
return 0
}
minP := prices[0]
best := 0
for i := 1; i < len(prices); i++ {
if prices[i]-minP > best {
best = prices[i] - minP
}
if prices[i] < minP {
minP = prices[i]
}
}
return best
}

func main() {
fmt.Println(maxProfit([]int{7, 1, 5, 3, 6, 4}))
fmt.Println(maxProfit([]int{7, 6, 4, 3, 1}))
fmt.Println(maxProfit([]int{2, 4, 1}))
}
