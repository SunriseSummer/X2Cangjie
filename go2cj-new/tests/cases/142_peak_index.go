package main

import "fmt"

func peakIndex(a []int) int {
l, r := 0, len(a)-1
for l < r {
m := l + (r-l)/2
if a[m] < a[m+1] {
l = m + 1
} else {
r = m
}
}
return l
}

func main() {
fmt.Println(peakIndex([]int{1, 3, 5, 4, 2}))
fmt.Println(peakIndex([]int{0, 2, 6, 9, 7, 1}))
}
