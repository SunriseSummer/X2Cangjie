package main

import "fmt"

func canSum(nums []int, target int) bool {
dp := make([]int, target+1)
dp[0] = 1
for _, x := range nums {
for s := target; s >= x; s-- {
if dp[s-x] == 1 {
dp[s] = 1
}
}
}
return dp[target] == 1
}

func main() {
fmt.Println(canSum([]int{3, 5, 9}, 8))
fmt.Println(canSum([]int{3, 5, 9}, 7))
fmt.Println(canSum([]int{2, 4, 6}, 12))
}
