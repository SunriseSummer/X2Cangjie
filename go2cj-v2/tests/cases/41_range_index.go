package main

import "fmt"

func main() {
	xs := []int{1, 2, 3, 4, 5}
	for i, v := range xs {
		fmt.Println(i, v)
	}
}
