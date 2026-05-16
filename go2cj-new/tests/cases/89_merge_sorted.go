package main

import "fmt"

func mergeSorted(a []int, b []int) []int {
	out := []int{}
	i := 0
	j := 0
	for i < len(a) && j < len(b) {
		if a[i] <= b[j] {
			out = append(out, a[i])
			i = i + 1
		} else {
			out = append(out, b[j])
			j = j + 1
		}
	}
	for i < len(a) {
		out = append(out, a[i])
		i = i + 1
	}
	for j < len(b) {
		out = append(out, b[j])
		j = j + 1
	}
	return out
}

func main() {
	a := []int{1, 3, 5, 7}
	b := []int{2, 4, 6, 8, 10}
	c := mergeSorted(a, b)
	for _, v := range c {
		fmt.Println(v)
	}
}
