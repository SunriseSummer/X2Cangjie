package main

import "fmt"

type Item struct {
	W int
	V int
}

func totalWeight(xs []Item) int {
	s := 0
	for _, it := range xs {
		s = s + it.W
	}
	return s
}

func main() {
	xs := []Item{{W: 2, V: 3}, {W: 4, V: 5}, {W: 6, V: 7}}
	fmt.Println(totalWeight(xs))
}
