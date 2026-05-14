package main

import "fmt"

func bubbleSort(xs []int) {
	n := len(xs)
	for i := 0; i < n-1; i++ {
		for j := 0; j < n-1-i; j++ {
			if xs[j] > xs[j+1] {
				xs[j], xs[j+1] = xs[j+1], xs[j]
			}
		}
	}
}

func main() {
	xs := []int{5, 2, 4, 1, 3}
	bubbleSort(xs)
	for _, v := range xs {
		fmt.Println(v)
	}
}
