package main

import "fmt"

func twoSumSorted(xs []int, target int) (int, int) {
i := 0
j := len(xs) - 1
for i < j {
s := xs[i] + xs[j]
if s == target {
return i, j
}
if s < target {
i = i + 1
} else {
j = j - 1
}
}
return -1, -1
}

func main() {
a, b := twoSumSorted([]int{1, 2, 4, 7, 11}, 9)
fmt.Println(a)
fmt.Println(b)

c, d := twoSumSorted([]int{2, 3, 5, 7, 9}, 11)
fmt.Println(c)
fmt.Println(d)

e, f := twoSumSorted([]int{1, 4, 8}, 100)
fmt.Println(e)
fmt.Println(f)
}
