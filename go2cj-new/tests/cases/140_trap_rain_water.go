package main

import "fmt"

func trap(height []int) int {
l, r := 0, len(height)-1
leftMax, rightMax := 0, 0
ans := 0
for l < r {
if height[l] < height[r] {
if height[l] >= leftMax {
leftMax = height[l]
} else {
ans = ans + (leftMax - height[l])
}
l++
} else {
if height[r] >= rightMax {
rightMax = height[r]
} else {
ans = ans + (rightMax - height[r])
}
r--
}
}
return ans
}

func main() {
fmt.Println(trap([]int{0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1}))
fmt.Println(trap([]int{4, 2, 0, 3, 2, 5}))
}
