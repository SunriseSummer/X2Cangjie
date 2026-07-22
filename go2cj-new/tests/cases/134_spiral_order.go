package main

import "fmt"

func spiralOrder(a [][]int) []int {
if len(a) == 0 || len(a[0]) == 0 {
return []int{}
}
top, bottom := 0, len(a)-1
left, right := 0, len(a[0])-1
ans := []int{}
for top <= bottom && left <= right {
for j := left; j <= right; j++ {
ans = append(ans, a[top][j])
}
top++
for i := top; i <= bottom; i++ {
ans = append(ans, a[i][right])
}
right--
if top <= bottom {
for j := right; j >= left; j-- {
ans = append(ans, a[bottom][j])
}
bottom--
}
if left <= right {
for i := bottom; i >= top; i-- {
ans = append(ans, a[i][left])
}
left++
}
}
return ans
}

func main() {
a := spiralOrder([][]int{{1, 2, 3}, {4, 5, 6}, {7, 8, 9}})
b := spiralOrder([][]int{{1, 2, 3, 4}, {5, 6, 7, 8}})
for i := 0; i < len(a); i++ {
if i > 0 {
fmt.Print(" ")
}
fmt.Print(a[i])
}
fmt.Println()
for i := 0; i < len(b); i++ {
if i > 0 {
fmt.Print(" ")
}
fmt.Print(b[i])
}
fmt.Println()
}
