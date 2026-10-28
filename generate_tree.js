const fs = require('fs');
const path = require('path');

function generateTree() {
    const vertices = [];
    const faces = [];

    function addV(x, y, z) {
        vertices.push([x, y, z]);
        return vertices.length;
    }

    function addF(a, b, c) {
        faces.push([a, b, c]);
    }

    function createLimb(pts, radii, segs = 8) {
        const rings = [];
        for (let idx = 0; idx < pts.length; idx++) {
            const [px, py, pz] = pts[idx];
            const r = radii[idx];
            const ring = [];
            for (let i = 0; i < segs; i++) {
                const th = (2.0 * Math.PI * i) / segs;
                const wobble = 1.0 + 0.08 * Math.sin(3 * th + pz * 0.5);
                const vx = px + r * Math.cos(th) * wobble;
                const vy = py + r * Math.sin(th) * wobble;
                const vz = pz;
                ring.push(addV(vx, vy, vz));
            }
            rings.push(ring);
        }

        for (let r = 0; r < rings.length - 1; r++) {
            const ra = rings[r];
            const rb = rings[r + 1];
            for (let i = 0; i < segs; i++) {
                const ni = (i + 1) % segs;
                addF(ra[i], ra[ni], rb[ni]);
                addF(ra[i], rb[ni], rb[i]);
            }
        }

        const bc = addV(pts[0][0], pts[0][1], pts[0][2]);
        for (let i = 0; i < segs; i++) {
            const ni = (i + 1) % segs;
            addF(bc, rings[0][ni], rings[0][i]);
        }

        const tc = addV(pts[pts.length - 1][0], pts[pts.length - 1][1], pts[pts.length - 1][2]);
        for (let i = 0; i < segs; i++) {
            const ni = (i + 1) % segs;
            addF(tc, rings[rings.length - 1][i], rings[rings.length - 1][ni]);
        }
    }

    function createFoliagePuff(center, rx, ry, rz, lats = 10, lons = 14) {
        const [cx, cy, cz] = center;
        const grid = [];
        for (let i = 0; i <= lats; i++) {
            const th = (Math.PI * i) / lats;
            const row = [];
            for (let j = 0; j < lons; j++) {
                const ph = (2.0 * Math.PI * j) / lons;
                const disp = 1.0 + 0.14 * Math.sin(4 * ph) * Math.cos(3 * th) +
                                   0.08 * Math.sin(7 * ph + 2 * th);
                const nx = Math.sin(th) * Math.cos(ph);
                const ny = Math.sin(th) * Math.sin(ph);
                const nz = Math.cos(th);
                const vx = cx + rx * nx * disp;
                const vy = cy + ry * ny * disp;
                const vz = cz + rz * nz * disp;
                row.push(addV(vx, vy, vz));
            }
            grid.push(row);
        }

        for (let i = 0; i < lats; i++) {
            for (let j = 0; j < lons; j++) {
                const nj = (j + 1) % lons;
                const v00 = grid[i][j];
                const v01 = grid[i][nj];
                const v10 = grid[i + 1][j];
                const v11 = grid[i + 1][nj];
                if (i === 0) {
                    addF(v00, v11, v10);
                } else if (i === lats - 1) {
                    addF(v00, v01, v11);
                } else {
                    addF(v00, v01, v11);
                    addF(v00, v11, v10);
                }
            }
        }
    }

    const trunkSpline = [
        [0.0, 0.0, 0.0],
        [0.2, 0.1, 4.0],
        [-0.3, 0.5, 10.0],
        [-0.8, 0.8, 18.0],
        [-0.5, 0.4, 26.0],
        [0.0, -0.2, 34.0],
        [0.5, -0.5, 42.0]
    ];
    const trunkRadii = [10.5, 8.2, 6.5, 5.8, 5.2, 4.8, 4.5];
    createLimb(trunkSpline, trunkRadii, 12);

    const buttressAngles = [0.2, 1.3, 2.4, 3.6, 4.8, 5.7];
    for (const a of buttressAngles) {
        const bx = 12.0 * Math.cos(a);
        const by = 12.0 * Math.sin(a);
        const bPts = [
            [bx, by, 0.0],
            [bx * 0.7, by * 0.7, 1.2],
            [bx * 0.4, by * 0.4, 3.5],
            [0.0, 0.0, 6.0]
        ];
        createLimb(bPts, [2.8, 2.4, 2.0, 1.5], 8);
    }

    const mainBranches = [
        { pts: [[0.5, -0.5, 42.0], [-3.5, -3.0, 50.0], [-8.0, -5.5, 58.0], [-13.0, -7.0, 65.0]], radii: [3.8, 3.1, 2.4, 1.7] },
        { pts: [[0.5, -0.5, 42.0], [4.5, -2.5, 51.0], [9.5, -4.0, 59.0], [14.5, -5.0, 66.0]], radii: [3.6, 2.9, 2.3, 1.6] },
        { pts: [[0.5, -0.5, 42.0], [-2.0, 4.0, 52.0], [-5.5, 9.0, 61.0], [-8.5, 13.5, 68.0]], radii: [3.4, 2.8, 2.2, 1.5] },
        { pts: [[0.5, -0.5, 42.0], [3.0, 3.5, 53.0], [7.0, 8.0, 62.0], [10.5, 12.0, 69.0]], radii: [3.5, 2.8, 2.1, 1.5] },
        { pts: [[0.5, -0.5, 42.0], [0.8, 0.5, 54.0], [0.2, 1.0, 66.0], [-0.5, 0.5, 76.0]], radii: [3.7, 3.0, 2.3, 1.6] }
    ];
    for (const b of mainBranches) {
        createLimb(b.pts, b.radii, 8);
    }

    const subBranches = [
        { pts: [[-8.0, -5.5, 58.0], [-11.0, -2.0, 64.0], [-14.0, 1.0, 69.0]], radii: [1.8, 1.4, 1.0] },
        { pts: [[9.5, -4.0, 59.0], [12.0, 0.0, 65.0], [15.0, 4.0, 70.0]], radii: [1.7, 1.3, 1.0] },
        { pts: [[-5.5, 9.0, 61.0], [-8.0, 6.0, 68.0], [-10.5, 3.0, 73.0]], radii: [1.6, 1.2, 0.9] },
        { pts: [[7.0, 8.0, 62.0], [5.0, 12.0, 68.0], [3.0, 15.0, 73.0]], radii: [1.6, 1.2, 0.9] },
        { pts: [[0.2, 1.0, 66.0], [3.5, -2.0, 74.0], [5.0, -3.5, 80.0]], radii: [1.6, 1.2, 0.9] }
    ];
    for (const sb of subBranches) {
        createLimb(sb.pts, sb.radii, 6);
    }

    const puffs = [
        { c: [-0.5, 0.5, 82.0], rx: 14.0, ry: 14.0, rz: 10.0 },
        { c: [3.0, -1.0, 84.0], rx: 12.0, ry: 12.0, rz: 9.0 },
        { c: [-2.5, 2.0, 78.0], rx: 13.0, ry: 13.0, rz: 9.5 },
        { c: [-14.0, -7.0, 68.0], rx: 13.5, ry: 12.5, rz: 9.0 },
        { c: [-15.0, 1.0, 72.0], rx: 12.0, ry: 11.0, rz: 8.5 },
        { c: [-10.0, -6.0, 64.0], rx: 11.0, ry: 10.0, rz: 8.0 },
        { c: [15.0, -5.0, 69.0], rx: 13.0, ry: 12.0, rz: 9.0 },
        { c: [16.0, 4.0, 73.0], rx: 12.5, ry: 11.5, rz: 8.5 },
        { c: [11.0, -4.0, 65.0], rx: 11.5, ry: 10.5, rz: 8.0 },
        { c: [-9.0, 14.0, 71.0], rx: 13.0, ry: 12.0, rz: 9.0 },
        { c: [-11.0, 4.0, 75.0], rx: 12.0, ry: 11.0, rz: 8.5 },
        { c: [11.0, 13.0, 72.0], rx: 13.0, ry: 12.5, rz: 9.0 },
        { c: [4.0, 16.0, 75.0], rx: 12.0, ry: 11.0, rz: 8.5 },
        { c: [-5.0, -2.0, 72.0], rx: 15.0, ry: 14.0, rz: 11.0 },
        { c: [5.0, 1.0, 73.0], rx: 15.0, ry: 14.0, rz: 11.0 },
        { c: [0.0, 6.0, 74.0], rx: 14.0, ry: 14.0, rz: 10.5 },
        { c: [0.0, -5.0, 71.0], rx: 14.0, ry: 13.0, rz: 10.0 }
    ];
    for (const p of puffs) {
        createFoliagePuff(p.c, p.rx, p.ry, p.rz, 10, 14);
    }

    const outLines = [
        '# Realistic 3D Printable Tree Model (Units: mm)',
        '# Features: Flared buttress root base, organic trunk, multi-tier foliage canopy',
        '# Height: ~95 mm, Spread: ~65 mm',
        'o RealisticTree\n'
    ];
    for (let i = 0; i < vertices.length; i++) {
        const [x, y, z] = vertices[i];
        outLines.push(`v ${x.toFixed(3)} ${y.toFixed(3)} ${z.toFixed(3)}`);
    }
    outLines.push('\n# Faces');
    for (let i = 0; i < faces.length; i++) {
        const [a, b, c] = faces[i];
        outLines.push(`f ${a} ${b} ${c}`);
    }

    // Write to a local scratch path in AppData or temp directory
    const scratchDir = 'C:\\Users\\rober\\.gemini\\antigravity\\scratch';
    if (!fs.existsSync(scratchDir)) {
        fs.mkdirSync(scratchDir, { recursive: true });
    }
    const outPath = path.join(scratchDir, 'tree.obj');
    fs.writeFileSync(outPath, outLines.join('\n') + '\n', 'utf8');
    console.log(`Successfully generated in scratch: ${outPath}`);
    console.log(`Vertices: ${vertices.length}, Faces: ${faces.length}`);
}

generateTree();

