package main

import "fmt"

func reverse(a []int, l, r int) {
for l < r {
a[l], a[r] = a[r], a[l]
l++
r--
}
}

func rotateRight(a []int, k int) {
n := len(a)
if n == 0 {
return
}
k = k % n
reverse(a, 0, n-1)
reverse(a, 0, k-1)
reverse(a, k, n-1)
}

func main() {
a := []int{1, 2, 3, 4, 5, 6}
rotateRight(a, 2)
fmt.Println(a[0], a[1], a[2], a[3], a[4], a[5])
b := []int{7, 8, 9, 10, 11}
rotateRight(b, 3)
fmt.Println(b[0], b[1], b[2], b[3], b[4])
}
