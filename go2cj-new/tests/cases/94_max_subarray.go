package main

import "fmt"

func maxSubarray(xs []int) int {
	best := xs[0]
	cur := xs[0]
	for i := 1; i < len(xs); i++ {
		if cur+xs[i] > xs[i] {
			cur = cur + xs[i]
		} else {
			cur = xs[i]
		}
		if cur > best {
			best = cur
		}
	}
	return best
}

func main() {
	xs := []int{-2, 1, -3, 4, -1, 2, 1, -5, 4}
	fmt.Println(maxSubarray(xs))
	ys := []int{1, 2, 3, 4, 5}
	fmt.Println(maxSubarray(ys))
	zs := []int{-1, -2, -3}
	fmt.Println(maxSubarray(zs))
}
