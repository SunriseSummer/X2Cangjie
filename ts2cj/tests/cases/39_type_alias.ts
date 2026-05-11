type Vec3 = [number, number, number];

function dot(a: Vec3, b: Vec3): number {
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2];
}

const u: Vec3 = [1, 2, 3];
const v: Vec3 = [4, 5, 6];
console.log(dot(u, v));
