package main

import "fmt"

func quickSort(xs []int, lo int, hi int) {
	if lo >= hi {
		return
	}
	pivot := xs[hi]
	i := lo - 1
	for j := lo; j < hi; j++ {
		if xs[j] <= pivot {
			i = i + 1
			tmp := xs[i]
			xs[i] = xs[j]
			xs[j] = tmp
		}
	}
	i = i + 1
	tmp := xs[i]
	xs[i] = xs[hi]
	xs[hi] = tmp
	quickSort(xs, lo, i-1)
	quickSort(xs, i+1, hi)
}

func main() {
	xs := []int{10, 7, 8, 9, 1, 5}
	quickSort(xs, 0, len(xs)-1)
	for _, v := range xs {
		fmt.Println(v)
	}
}
