package main

import "fmt"

func minLen(target int, nums []int) int {
	left := 0
	sum := 0
	const INF = 1 << 30
	best := INF
	for right := 0; right < len(nums); right++ {
		v := nums[right]
		sum = sum + v
		for sum >= target {
			cur := right - left + 1
			if cur < best {
				best = cur
			}
			sum -= nums[left]
			left++
		}
	}
	if best == INF {
		return 0
	}
	return best
}

func main() {
	fmt.Println(minLen(7, []int{2, 3, 1, 2, 4, 3}))
	fmt.Println(minLen(11, []int{1, 1, 1, 1, 1, 1, 1, 1}))
	fmt.Println(minLen(4, []int{1, 4, 4}))
}
