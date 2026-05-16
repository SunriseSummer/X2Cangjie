package main

import "fmt"

func quicksort(xs []int, lo int, hi int) {
	if lo >= hi {
		return
	}
	pivot := xs[hi]
	i := lo
	for j := lo; j < hi; j++ {
		if xs[j] < pivot {
			xs[i], xs[j] = xs[j], xs[i]
			i++
		}
	}
	xs[i], xs[hi] = xs[hi], xs[i]
	quicksort(xs, lo, i-1)
	quicksort(xs, i+1, hi)
}

func main() {
	xs := []int{5, 2, 8, 1, 9, 3, 7, 4, 6}
	quicksort(xs, 0, len(xs)-1)
	for _, v := range xs {
		fmt.Println(v)
	}
}
