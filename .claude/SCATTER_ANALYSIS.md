# Vispy2 Scatter Module Analysis

## Executive Summary

**Status:** ✅ **Functionally Complete** but ⚠️ **Needs Polish**

The scatter module works correctly and handles three important rendering modes (pixels, points, markers). However, it **lacks the documentation quality** of the plot module and has **outdated code patterns**.

**Quality Score:** 6/10 (Functional) → 8.5/10 (After fixes)

---

## Module Overview

### What It Does
- Provides a unified `scatter()` function for creating three types of visuals:
  - **Pixels:** Fast rendering of many small dots (2000+ points)
  - **Points:** Medium quality with full customization (100-1000 points)
  - **Markers:** Styled shapes with customizable sizes/colors

### How It Works
```python
scatter(positions, mode="points", face_colors=red, edge_colors=blue, ...)
```

1. **Mode Inference:** If `mode` not provided, infer from parameters:
   - Has `groups`? → Pixels mode
   - Has `marker_shape`? → Markers mode
   - Otherwise → Points mode

2. **Default Generation:** If positions is a Buffer, auto-generate defaults for missing parameters

3. **Dispatch:** Call appropriate helper (`_scatter_pixels`, `_scatter_points`, `_scatter_markers`)

---

## ✅ Strengths

### 1. Smart Mode Inference
```python
# These all work without specifying mode:
scatter(positions, groups=groups)           # Infers: pixels
scatter(positions, marker_shape=MarkerShape.circle)  # Infers: markers
scatter(positions, face_colors=colors)      # Infers: points
```
**Benefit:** Users don't need to memorize mode names.

### 2. Flexible Input Types
Accepts both **Buffer** and **numpy.ndarray**, auto-converting as needed:
```python
scatter(np.random.rand(100, 3))  # Works
scatter(Bufferx.from_numpy(...)) # Also works
```

### 3. Smart Defaults
Generates default buffers from position count if not provided:
```python
# All these create valid visuals with sensible defaults:
scatter(positions)
scatter(positions, sizes=custom_sizes)
scatter(positions, sizes=sizes, face_colors=colors)
```

### 4. Comprehensive Example
The example (`vispy_scatter_example.py`) demonstrates all three modes clearly.

---

## ⚠️ Issues & Gaps

### 1. **Type Hints - OUTDATED** (Low Priority)
**Issue:** Uses old-style Optional/Union syntax
```python
# Current (Python 3.9 style)
mode: Optional[Union[Literal["pixels"], Literal["points"], Literal["markers"]]]

# Should be (Python 3.10+ style, like plot.py)
mode: Literal["pixels", "points", "markers"] | None
```

**Impact:** Inconsistent with plot.py, reduces readability
**Files:** Lines 4, 27, 72, 139, 207

---

### 2. **Documentation - MINIMAL** (High Priority)

#### Module Docstring
**Current:**
```python
"""Unified scatter API to create Points, Pixels or Markers visuals."""
```

**Missing:**
- What are the three modes?
- When should I use each mode?
- What does `groups` mean?
- Example usage

#### Function Docstring Issues
- No explanation of "pixels" vs "points" difference
- `groups` parameter barely explained (what is it? how to create it?)
- No examples of how to use each mode
- Default values not clearly documented
- No mention of performance characteristics (pixels fast for 2000+ points)

**Example - what's missing:**
```
scatter(positions, mode="pixels", colors=colors, groups=group_size)
# What is groups?? Users have to read the example to understand
```

---

### 3. **Confusing API** (High Priority)

#### Pixels vs Points - Unclear Difference
```python
# Pixels mode
scatter(positions, colors=rgba_colors, groups=size)

# Points mode  
scatter(positions, face_colors=colors, edge_colors=edges, edge_widths=widths, sizes=sizes)
```

**Questions users ask:**
- Why `colors` for pixels but `face_colors` for points?
- Should I use pixels or points? (Answer: pixels if 2000+ points, otherwise points)
- What does `groups` do? (Answer: groups points for optimization, but not explained)

#### MarkerShape Not Explained
```python
scatter(positions, marker_shape=MarkerShape.club)  # What shapes exist?
```

No list of available marker shapes in docstring.

---

### 4. **Repetitive Code** (Medium Priority)

Three helper functions (~100 lines each) have ~80% duplicate logic:

```python
# In all three helpers, same pattern:
if isinstance(positions, Buffer):
    position_count = positions.get_count()
    
    if sizes is None:
        sizes_numpy = np.array([40] * position_count, dtype=np.float32)
        sizes = Bufferx.from_numpy(sizes_numpy, BufferType.float32)
    elif isinstance(sizes, np.ndarray):
        sizes = Bufferx.from_numpy(sizes, BufferType.float32)
    
    # ... repeated for colors, edge_colors, edge_widths ...
```

**Impact:** Hard to maintain, easy to introduce bugs, increases code size

---

### 5. **Unused Parameters** (Low Priority)

Each helper receives parameters it doesn't use:
```python
def _scatter_pixels(
    positions: TransBuf,
    *,
    mode: Optional[...] = None,  # ← Received but never used
    sizes: ... = None,  # ← Received but never used
    marker_shape: ... = None,  # ← Received but never used
    ...
) -> VisualBase:
```

**Impact:** Code smell, makes signature confusing, wastes parameters

---

### 6. **Missing Input Validation** (Medium Priority)

No validation before delegating to constructors:
- Empty positions array? → Silently passes to constructor
- Size/color count mismatch? → Constructor fails with opaque error
- Position shape not vec3? → Fails later
- Negative sizes? → No check

**Current approach:** Delegate all validation to underlying visual constructors
**Problem:** Error messages are unclear to users
**Example error:** Instead of "Face colors count (50) must match position count (100)", users get low-level buffer errors

---

### 7. **Example Quality** (Good)

The example (`vispy_scatter_example.py`) is comprehensive:
- Shows all 3 modes
- Demonstrates varying sizes and colors
- Uses color maps
- Shows group handling
- Runnable code

**But:** It's complex and doesn't explain what each mode does.

---

## 🎯 Comparison with Plot Module

| Feature | Plot | Scatter |
|---------|------|---------|
| Type hints | ✓ Modern (`X \| None`) | ✗ Old (`Optional[X]`) |
| Module docstring | ✓ Detailed | ✗ Minimal |
| Function docstring | ✓ Examples | ✗ No examples |
| Clarity | ✓ Intuitive API | ⚠ Confusing (3 modes) |
| Code duplication | ✓ Single function | ✗ 80% repeated |
| User-friendliness | ✓ High | ⚠ Medium |
| Example | ✓ Simple | ✓ Complex but complete |

---

## 📊 What Works Well

1. ✅ Smart mode inference (users don't specify mode)
2. ✅ Flexible input handling (numpy + Buffers)
3. ✅ Smart defaults (generates defaults from position count)
4. ✅ Comprehensive example code
5. ✅ Supports three useful rendering modes
6. ✅ Works correctly (functionally complete)

---

## 🚨 Priority Fixes

### **Priority 1 - HIGH** (Documentation)
- [ ] Add comprehensive module docstring explaining modes
- [ ] Add examples in `scatter()` docstring for each mode
- [ ] Explain `groups` parameter with example
- [ ] Document when to use each mode (performance characteristics)
- [ ] List all available MarkerShape values

### **Priority 2 - MEDIUM** (Code Quality)
- [ ] Modernize type hints: `Optional[X]` → `X | None`
- [ ] Add input validation with clear error messages
- [ ] Document default values clearly
- [ ] Explain "pixels" vs "points" distinction

### **Priority 3 - LOW** (Refactoring)
- [ ] Reduce code duplication in three helpers
- [ ] Remove unused parameters from helper signatures
- [ ] Consider single `_scatter_create()` helper

---

## 💡 Suggested Improvements (Not Critical)

1. **Add validation helper**
   ```python
   def _validate_scatter_inputs(positions, sizes, colors, ...):
       """Validate inputs before creating visuals."""
   ```

2. **Create helper for default generation**
   ```python
   def _generate_defaults(position_count, mode):
       """Generate default buffers for missing parameters."""
   ```

3. **Add MarkerShape.from_string()**
   ```python
   # Like the plot module's fmt string parsing
   marker = MarkerShape.from_string("circle")
   ```

4. **Support shorthand like plot module**
   ```python
   # Instead of this:
   scatter(positions, mode="markers", marker_shape=MarkerShape.circle)
   # Could support this:
   scatter(positions, fmt="o")  # Like plot module
   ```

---

## ✅ Verdict

### Is scatter complete?
**Yes.** The module is functionally complete and handles all three modes correctly.

### Is it production-ready?
**Mostly.** Works well, but documentation/type hints lag behind plot.py.

### Quality Rating
- **Current:** 6/10 (functional, but documentation poor)
- **Target:** 8.5/10 (match plot.py quality)

### Recommendation
**Use as-is, but schedule documentation improvements.** The module is solid but needs love on the documentation side to match plot.py quality.
