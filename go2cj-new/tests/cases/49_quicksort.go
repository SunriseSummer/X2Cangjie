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
	xs := []int{9, 4, 7, 1, 3, 8, 2, 6, 5}
	quicksort(xs, 0, len(xs)-1)
	for _, v := range xs {
		fmt.Println(v)
	}
}
