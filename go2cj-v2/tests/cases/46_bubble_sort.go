package main

import "fmt"

func main() {
	xs := []int{5, 2, 4, 1, 3}
	for i := 0; i < len(xs)-1; i++ {
		for j := 0; j < len(xs)-1-i; j++ {
			if xs[j] > xs[j+1] {
				xs[j], xs[j+1] = xs[j+1], xs[j]
			}
		}
	}
	for _, v := range xs {
		fmt.Println(v)
	}
}
