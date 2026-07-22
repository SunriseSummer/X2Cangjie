package main

import "fmt"

func minRotated(nums []int) int {
l, r := 0, len(nums)-1
for l < r {
m := l + (r-l)/2
if nums[m] > nums[r] {
l = m + 1
} else {
r = m
}
}
return nums[l]
}

func main() {
fmt.Println(minRotated([]int{4, 5, 6, 7, 0, 1, 2}))
fmt.Println(minRotated([]int{2, 3, 4, 5, 1}))
fmt.Println(minRotated([]int{1, 2, 3}))
}
