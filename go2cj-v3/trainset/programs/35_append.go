package main

import "fmt"

func main() {
	xs := []int{1, 2, 3}
	xs = append(xs, 4)
	xs = append(xs, 5)
	for _, v := range xs {
		fmt.Println(v)
	}
}
