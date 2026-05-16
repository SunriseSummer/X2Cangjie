package main

import "fmt"

func bubbleSort(xs []int) {
	n := len(xs)
	for i := 0; i < n; i++ {
		for j := 0; j < n-i-1; j++ {
			if xs[j] > xs[j+1] {
				tmp := xs[j]
				xs[j] = xs[j+1]
				xs[j+1] = tmp
			}
		}
	}
}

func main() {
	xs := []int{5, 2, 8, 1, 9, 3, 7, 4, 6}
	bubbleSort(xs)
	for _, v := range xs {
		fmt.Println(v)
	}
}
