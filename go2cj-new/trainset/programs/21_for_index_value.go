package main

import "fmt"

func main() {
	xs := []int{10, 20, 30}
	for i, v := range xs {
		fmt.Println(i, v)
	}
}
