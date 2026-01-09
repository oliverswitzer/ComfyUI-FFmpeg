# ADR 0001: Natural Sorting for Image Sequences

## Status

Accepted

## Context

The Frames2Video node was experiencing incorrect ordering of sequential image frames when converting them to video. Specifically, when processing multiple scenes with filenames like `SCENE__1_00001.png`, `SCENE__2_00001.png`, ..., `SCENE__10_00001.png`, `SCENE__11_00001.png`, Python's default lexicographic string sorting would place scenes 10 and 11 at the beginning of the video before scenes 1-9.

This occurred because `images.sort()` performs character-by-character ASCII comparison, where "SCENE__10" sorts before "SCENE__2" (comparing '1','0' vs '1','_', where '0' < '_' in ASCII order).

The issue manifested when users had:
- Multiple scenes numbered 1-11 (or any multi-digit scene numbers)
- 121 frames per scene
- Filenames following the pattern: `SCENE__<scene_number>_<frame_number>.png`

## Decision

Implement natural sorting (also called human sorting) using a custom sort key function that:

1. Splits filenames into text and numeric components using regex pattern `r'(\d+)'`
2. Converts numeric components to integers for proper numerical comparison
3. Keeps text components as strings for alphabetical comparison
4. Applies this via `images.sort(key=natural_sort_key)`

The implementation adds:
- `import re` module at the top of `nodes/frames2video.py`
- A `natural_sort_key()` function that extracts the basename and splits it into comparable parts
- Replaces simple `images.sort()` with `images.sort(key=natural_sort_key)`

## Consequences

### Positive

- Image sequences now sort in human-expected order: SCENE__1 → SCENE__2 → ... → SCENE__9 → SCENE__10 → SCENE__11
- Works with any numeric sequences in filenames (scene numbers, frame numbers, etc.)
- No external dependencies required (uses standard library `re` module)
- Minimal performance impact for typical image sequence sizes

### Negative

- Slight computational overhead from regex splitting and type conversion (negligible for typical use cases)
- Additional import and function definition adds ~10 lines of code

## References

- Commit: 703e22e (attempted fix but only addressed Windows path handling)
- Issue: Scene 10 and 11 appearing at start of video instead of proper sequence order
