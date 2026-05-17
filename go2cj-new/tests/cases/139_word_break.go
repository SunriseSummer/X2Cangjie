package main

import "fmt"

func rob(nums []int) int {
if len(nums) == 0 {
return 0
}
if len(nums) == 1 {
return nums[0]
}
prev2 := nums[0]
if nums[1] > nums[0] {
prev2 = nums[1]
}
prev1 := prev2
for i := 2; i < len(nums); i++ {
pick := prev2 + nums[i]
if i == 2 {
pick = nums[0] + nums[i]
}
if pick > prev1 {
tmp := prev1
prev1 = pick
prev2 = tmp
} else {
prev2 = prev1
}
}
return prev1
}

func main() {
fmt.Println(rob([]int{1, 2, 3, 1}))
fmt.Println(rob([]int{2, 7, 9, 3, 1}))
fmt.Println(rob([]int{2, 1, 1, 2}))
}
