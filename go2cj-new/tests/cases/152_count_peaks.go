package main

import "fmt"

func countPeaks(nums []int) int {
if len(nums) < 3 {
return 0
}
cnt := 0
for i := 1; i+1 < len(nums); i++ {
if nums[i] > nums[i-1] && nums[i] > nums[i+1] {
cnt++
}
}
return cnt
}

func main() {
fmt.Println(countPeaks([]int{1, 3, 2, 4, 1, 5, 2}))
fmt.Println(countPeaks([]int{1, 2, 3, 4, 5}))
fmt.Println(countPeaks([]int{5, 1, 5, 1, 5}))
}
