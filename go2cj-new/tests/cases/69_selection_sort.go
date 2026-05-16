package main

import "fmt"

func selectionSort(xs []int) {
	n := len(xs)
	for i := 0; i < n-1; i++ {
		minIdx := i
		for j := i + 1; j < n; j++ {
			if xs[j] < xs[minIdx] {
				minIdx = j
			}
		}
		tmp := xs[i]
		xs[i] = xs[minIdx]
		xs[minIdx] = tmp
	}
}

func main() {
	xs := []int{64, 25, 12, 22, 11}
	selectionSort(xs)
	for _, v := range xs {
		fmt.Println(v)
	}
}
