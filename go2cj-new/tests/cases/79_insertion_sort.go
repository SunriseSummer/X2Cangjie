package main

import "fmt"

func insertionSort(xs []int) {
	n := len(xs)
	for i := 1; i < n; i++ {
		key := xs[i]
		j := i - 1
		for j >= 0 && xs[j] > key {
			xs[j+1] = xs[j]
			j = j - 1
		}
		xs[j+1] = key
	}
}

func main() {
	xs := []int{12, 11, 13, 5, 6, 7}
	insertionSort(xs)
	for _, v := range xs {
		fmt.Println(v)
	}
}
