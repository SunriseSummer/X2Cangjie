package main

import "fmt"

func arrayMaxMin(xs []int) (int, int) {
	mx := xs[0]
	mn := xs[0]
	for _, v := range xs {
		if v > mx {
			mx = v
		}
		if v < mn {
			mn = v
		}
	}
	return mx, mn
}

func main() {
	xs := []int{3, 1, 4, 1, 5, 9, 2, 6, 5, 3}
	mx, mn := arrayMaxMin(xs)
	fmt.Println(mx)
	fmt.Println(mn)
}
