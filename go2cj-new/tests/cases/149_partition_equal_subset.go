package main

import "fmt"

func canPartition(nums []int) bool {
sum := 0
for _, x := range nums {
sum += x
}
if sum%2 == 1 {
return false
}
t := sum / 2
dp := make([]bool, t+1)
dp[0] = true
for _, x := range nums {
for j := t; j >= x; j-- {
if dp[j-x] {
dp[j] = true
}
}
}
return dp[t]
}

func main() {
fmt.Println(canPartition([]int{1, 5, 11, 5}))
fmt.Println(canPartition([]int{1, 2, 3, 5}))
fmt.Println(canPartition([]int{2, 2, 3, 5}))
}
