package main

import "fmt"

func productExceptSelf(nums []int) []int {
n := len(nums)
ans := make([]int, n)
left := 1
for i := 0; i < n; i++ {
ans[i] = left
left = left * nums[i]
}
right := 1
for i := n - 1; i >= 0; i-- {
ans[i] = ans[i] * right
right = right * nums[i]
}
return ans
}

func main() {
fmt.Println(productExceptSelf([]int{1, 2, 3, 4}))
fmt.Println(productExceptSelf([]int{2, 3, 5}))
}
