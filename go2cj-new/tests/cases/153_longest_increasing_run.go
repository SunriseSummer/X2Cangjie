package main

import "fmt"

func longestRun(nums []int) int {
if len(nums) == 0 {
return 0
}
best := 1
cur := 1
for i := 1; i < len(nums); i++ {
if nums[i] > nums[i-1] {
cur++
} else {
cur = 1
}
if cur > best {
best = cur
}
}
return best
}

func main() {
fmt.Println(longestRun([]int{1, 2, 3, 1, 2, 3, 4, 0}))
fmt.Println(longestRun([]int{9, 8, 7}))
fmt.Println(longestRun([]int{1, 2, 2, 3, 4, 5}))
}
