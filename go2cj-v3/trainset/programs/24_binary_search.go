package main

import "fmt"

func binarySearch(xs []int, target int) int {
	lo, hi := 0, len(xs)-1
	for lo <= hi {
		mid := (lo + hi) / 2
		if xs[mid] == target {
			return mid
		}
		if xs[mid] < target {
			lo = mid + 1
		} else {
			hi = mid - 1
		}
	}
	return -1
}

func main() {
	xs := []int{1, 3, 5, 7, 9, 11, 13, 15}
	fmt.Println(binarySearch(xs, 7))
	fmt.Println(binarySearch(xs, 1))
	fmt.Println(binarySearch(xs, 15))
	fmt.Println(binarySearch(xs, 4))
}
