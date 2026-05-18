package main

import "fmt"

func maxDiff(nums []int) int {
if len(nums) < 2 {
return 0
}
minV := nums[0]
best := nums[1] - nums[0]
for i := 1; i < len(nums); i++ {
	cur := nums[i]
	d := cur - minV
	if d > best {
	best = d
	}
	if cur < minV {
	minV = cur
	}
}
return best
}

func main() {
fmt.Println(maxDiff([]int{7, 1, 5, 3, 6, 4}))
fmt.Println(maxDiff([]int{9, 8, 7, 6}))
fmt.Println(maxDiff([]int{1, 2}))
}
