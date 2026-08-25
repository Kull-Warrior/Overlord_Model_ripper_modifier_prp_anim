# Overlord (2007) `.prp` resource format – what the importer relies on

Everything below was verified against every `.prp` of the game (`Resources/` and `Expansion/*/Resources/`):
35 123 bones, 148 000 animation bone tracks, ~2 100 skinned meshes.

## Coordinate systems

| space | axes | used by |
|---|---|---|
| **game / skeleton** | **Y up, +Z forward (the direction a character faces), +X = character's left**, right handed | bone rest matrices, bone quaternions, all animation keys, meshes of models **without** a skeleton |
| **skin mesh** | X identical, **Y forward, Z down** (= game space rotated by −90° around X) | vertices and normals of meshes that belong to a model **with** a skeleton |
| **Blender** | Z up, −Y forward, +X = character's left | |

Conversions (all pure rotations, so nothing is mirrored and triangle winding is unaffected):

```
game  -> Blender : rotate +90° around X   (x, y, z) -> (x, -z, y)      myFunction.GAME_TO_BLENDER
skin  -> game    : rotate +90° around X   (x, y, z) -> (x, -z, y)      myFunction.SKIN_TO_GAME
skin  -> Blender : rotate 180° around X   (x, y, z) -> (x, -y, -z)     myFunction.SKIN_TO_BLENDER
```

Evidence: feet bones sit at y ≈ 0 and heads at +y; `L_*` bones are at +x, `R_*` at −x; the head of every
character is at +z. The weighted centroid of the vertices skinned to a bone lands on that bone only after
rotating the mesh by +90° around X (1824 of ~2150 meshes, the rest are single-bone rigid parts where the
centroid is not meaningful). Static props (doors, banners, posters) are Y-up directly. A wedding poster
with a painted date renders readable from its front side, so no mirroring is involved.

Triangles are stored **clockwise** with respect to the stored vertex normals (99.7 % of all faces), so
the importer swaps the last two indices of every triangle to get Blender's counter clockwise front faces.
UV `v` is flipped (`1 - v`), DirectX style.

## Matrices and quaternions

4×4 matrices are row major with the translation in the **last row** (DirectX row-vector convention,
`v' = v · M`). `myFunction.row_matrix_to_column()` transposes them into Blender's column-vector convention.
Quaternions are stored as `(x, y, z, w)`; `mathutils.Quaternion((w, x, y, z))` is the matching rotation.

## Skeleton (model chunk, item 33)

`count` bones of 144 bytes each, parents always precede their children:

| offset | type | meaning |
|---|---|---|
| 0 | char[32] | bone name |
| 32 | float[16] | **parent relative** rest matrix (row major, translation in the last row) |
| 96 | float[4] | same rotation as quaternion `(x, y, z, w)` |
| 112 | float[3] | same translation |
| 124 | int32 | **skin id** – the index used by the mesh bone maps; `-1` for bones never skinned to (END effectors, IK helpers) |
| 128 | int32 | parent bone index (`-1` = root) |
| 132 | int32 | next sibling (`-1` = none) |
| 136 | int32 | first child (`-1` = none) |
| 140 | int32 | flags (always 0) |

World rest matrix: `W_bone = W_parent @ L_bone` (column convention). A handful of cut-scene chain bones
carry scale in the matrix and an un-normalised quaternion; everything else is a rigid transform.

## Skinned meshes

Vertex declaration elements `(usage index, stream, usage, type)`; usages seen in the game:
`1` position (3 floats), `4` normal (3 floats), `5` uv (2 floats), `11` bone index (1 byte, three of them),
`10` bone weight (1 byte, two of them – the third weight is `255 - w1 - w2`), `9` tangent (16 bytes).

Bone indices are local to the mesh and go through the model's bone map (model chunk item 35, flag 160):
`skeleton bone = bone with skin_id == bone_map[local index]`. One vertex may list the same bone twice;
the weights add up.

## Animations (flag `(5,0,65,0)`)

Header: item 30 = frame rate (float, 15 fps everywhere), item 31 = duration in **microseconds**
(`frames = duration · fps / 1e6 + 1`). Then one track per bone (flag `(7,0,65,0)`), matched to
skeletons **by bone name**; a track may reference rig-only bones (`*_IK`, `*_FK`) that do not exist in
the export skeleton – they are ignored.

Every key is an **absolute parent relative transform** (not a delta from the rest pose). Bones without a
track keep their rest pose.

* **position track** (item 24): `count` sparse keys of 16 bytes `uint32 time_us, float x, y, z`
  (game space). Linear interpolation. A single key means a constant value. No track = rest translation.
* **rotation track** (item 25 → 21): `count` keys, **one per frame**, 6 bytes each:
  `int16 x, y, z` = quaternion `x, y, z · 32767`. `w = ±sqrt(1 − x² − y² − z²)`, and the sign of `w`
  comes from item 24 of the same list: a bit array of `ceil(count / 8)` bytes, bit `i` of byte `i >> 3`
  (LSB first) set ⇔ `w` of key `i` is negative. Without the sign bits every animation shows 100–180°
  flips on individual bones; with them the idle animations are smooth (≤ 24° between frames).
* **scale track** (items 30/31) exists in the reader but never occurs in the game files.

### Blender mapping

For a bone with rest local matrix `R` (Blender space), animated local matrix `A` and the extra rotation
`K` that `skeletonLib` applies to point the Blender bone at its child:

```
pose_bone.matrix_basis = K⁻¹ · R⁻¹ · A · K
```

`R` and `K` are stored as custom properties (`ovl_rest_local`, `ovl_orient`) on every bone so that
`.anim` files can be applied later to the selected armature.

## `.anim` files written by `save_data()`

```
char[8]  "OVLANIM2"
float32  fps
uint32   duration_us
int32    bone count
per bone:
  int32 name length, char[] name
  int32 position key count,  per key: uint32 time_us, float32 x, y, z      (game space)
  int32 rotation key count,  uint8 type (22), per key int16 x, y, z (·32767), then ceil(count/8) sign bytes
```
