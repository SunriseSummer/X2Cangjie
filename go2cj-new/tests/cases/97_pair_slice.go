package main

import "fmt"

type Pair struct {
	K int
	V int
}

func sumValues(ps []Pair) int {
	s := 0
	for _, p := range ps {
		s = s + p.V
	}
	return s
}

func main() {
	ps := []Pair{{K: 1, V: 10}, {K: 2, V: 20}, {K: 3, V: 30}}
	fmt.Println(sumValues(ps))
}
