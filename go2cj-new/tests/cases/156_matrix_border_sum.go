package main

import "fmt"

func borderSum(mat [][]int) int {
n := len(mat)
m := len(mat[0])
if n == 1 {
s := 0
for j := 0; j < m; j++ {
s += mat[0][j]
}
return s
}
if m == 1 {
s := 0
for i := 0; i < n; i++ {
s += mat[i][0]
}
return s
}
s := 0
for j := 0; j < m; j++ {
s += mat[0][j]
s += mat[n-1][j]
}
for i := 1; i+1 < n; i++ {
s += mat[i][0]
s += mat[i][m-1]
}
return s
}

func main() {
fmt.Println(borderSum([][]int{{1, 2, 3}, {4, 5, 6}, {7, 8, 9}}))
fmt.Println(borderSum([][]int{{5, 1, 2, 3}}))
fmt.Println(borderSum([][]int{{1}, {2}, {3}, {4}}))
}
