package main

import "fmt"

func countIslands(g [][]int) int {
n := len(g)
m := len(g[0])
cnt := 0
dx := []int{1, -1, 0, 0}
dy := []int{0, 0, 1, -1}
for i := 0; i < n; i++ {
for j := 0; j < m; j++ {
if g[i][j] != 1 {
continue
}
			cnt++
			q := [][]int{{i, j}}
			g[i][j] = 0
			head := 0
			for head < len(q) {
				x, y := q[head][0], q[head][1]
				for k := 0; k < 4; k++ {
					nx, ny := x+dx[k], y+dy[k]
					if nx < 0 || nx >= n || ny < 0 || ny >= m || g[nx][ny] != 1 {
						continue
}
					g[nx][ny] = 0
					q = append(q, []int{nx, ny})
				}
				head++
			}
		}
	}
return cnt
}

func main() {
g1 := [][]int{{1, 1, 0, 0}, {1, 0, 0, 1}, {0, 0, 1, 1}, {0, 0, 0, 1}}
g2 := [][]int{{1, 1, 1}, {0, 1, 0}, {1, 0, 1}}
fmt.Println(countIslands(g1))
fmt.Println(countIslands(g2))
}
