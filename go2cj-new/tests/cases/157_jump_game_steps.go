package main

import "fmt"

func minJumps(nums []int) int {
if len(nums) <= 1 {
return 0
}
steps := 0
end := 0
far := 0
for i := 0; i < len(nums)-1; i++ {
step := nums[i]
reach := i + step
if reach > far {
far = reach
}
if i == end {
steps++
end = far
}
}
return steps
}

func main() {
fmt.Println(minJumps([]int{2, 3, 1, 1, 4}))
fmt.Println(minJumps([]int{2, 3, 0, 1, 4}))
fmt.Println(minJumps([]int{1, 1, 1, 1}))
}
