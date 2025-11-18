# Higher Category Theory: A Comprehensive Treatment

## Why Higher Categories?

Ordinary category theory models objects and morphisms between them. But mathematics often has **morphisms between morphisms** (natural transformations), requiring a second level. Higher category theory extends this to arbitrary depth.

### The Homotopy Problem

In ordinary categories: **a = b ⟹ all properties equal**

But in topology: **paths a ~ b at same points** (homotopy equivalence)

Higher categories capture **homotopical equality** systematically.

## 2-Categories: Complete Foundations

### Formal Definition

A **2-category** C consists of:

**1. Objects**: Collection of 0-cells Ob(C)

**2. 1-Morphisms**: For X,Y ∈ Ob(C), a set C(X,Y) of 1-cells f,g,...

**3. 2-Morphisms**: For f,g: X → Y, a set C(f,g) of 2-cells α: f ⇒ g

**4. Horizontal Composition**:
```
f: X → Y  and  g: Y → Z
_________________________________
g ∘ f: X → Z  (compose 1-cells)
```

**5. Vertical Composition**:
```
α: f ⇒ f'  and  β: f' ⇒ f''
_________________________________
β ∘ α: f ⇒ f''  (compose 2-cells)
```

**6. Interchange Law**:
```
(β ∘ α) ∘ (δ ∘ γ) = (β ∘ δ) ∘ (α ∘ γ)

Horizontal and vertical compositions commute
```

### Axioms

1. **Associativity**: Both ∘ operations associative
2. **Identity**: Identity 1-cells and 2-cells
3. **Interchange**: Above law holds
4. **Strictness**: All diagrams commute exactly (no coherence data)

### 8 Fundamental Examples

#### 1. Cat: Category of Categories
- **Objects**: Small categories
- **1-Morphisms**: Functors
- **2-Morphisms**: Natural transformations
- **Vertical ∘**: Natural transformation composition
- **Horizontal ∘**: Functor composition
- **Interchange**: Godement product associativity

#### 2. Span: Spans in a Category
```
Objects: Same as base category
1-cells: Spans X ← S → Y
2-cells: Morphisms between spans
```

**Composition**: Pullback of middle objects

#### 3. Prof: Profunctors (Distributors)
```
1-cells: Profunctors F: C ⇸ D (contravariant in domain)
2-cells: Natural transformations
```

**Composition**: Profunctor composition (via coend)

#### 4. One-Object 2-Categories (Monoidal Categories)
```
Objects: single point *
1-cells: elements of monoidal category M
2-cells: any morphisms
```

Result: 2-category with one object = monoidal structure!

#### 5. Enriched Categories
```
Objects: objects of base category
1-cells: morphisms
2-cells: between morphisms in enriching category V
```

V-enriched categories = 2-categories with specific structure

#### 6. Topological 2-Categories
```
1-cells: continuous maps
2-cells: homotopies between continuous maps
```

#### 7. Simplicial 2-Categories
```
Based on simplicial sets
Extra homotopy structure at each level
```

#### 8. Algebraic 2-Categories
```
Objects: algebraic structures
1-cells: homomorphisms
2-cells: homotopies or derivations
```

## Bicategories: Weak Higher Structures

### The Problem with Strictness

In practice, categorical structures are **weakly associative**:
```
(W ∘ X) ∘ Y ≠ W ∘ (X ∘ Y)
but
(W ∘ X) ∘ Y ≅ W ∘ (X ∘ Y)  [natural isomorphism]
```

Strict associativity too restrictive!

### Bicategory Definition

A **bicategory** C consists of (same as 2-category, but):

**Compositions are only associative up to natural isomorphism**:

```
ASSOCIATOR:
a_{X,Y,Z,W}: (h ∘ g) ∘ f ⇒ h ∘ (g ∘ f)
[2-morphism, not identity]

LEFT UNITOR:
l_f: id ∘ f ⇒ f

RIGHT UNITOR:
r_f: f ∘ id ⇒ f
```

### Coherence Axioms

```
PENTAGON AXIOM (associators cohere):
((k∘j)∘i)∘h  ---α---→  (k∘j)∘(i∘h)
    ↓                         ↓
(k∘(j∘i))∘h  ---α---→  k∘((j∘i)∘h)
    ↓                         ↓
k∘(j∘(i∘h))  [commutes via α and intermediate α's]

TRIANGLE AXIOM (unitors cohere):
(f∘id)∘g  ---r⊗id---→  f∘g
    ↓                    ↓
f∘(id∘g)  ---id⊗l---→  f∘g
```

**Mac Lane Coherence Theorem**: These two axioms guarantee all diagrams commute!

## Examples of Bicategories

1. **Span(C)**: Spans with pullback composition
2. **Prof**: Profunctors with coend composition
3. **Cat**: Enriched over itself
4. **Alg(T)**: Algebras over monad T
5. **Modules**: Bimodules between rings
6. **Tangles**: Tangle diagrams with composition
7. **Matroid**: Matroids with weak operations
8. **Schemes**: Over common base (weak fiber product)

## Higher Categories: n-Categories and ∞-Categories

### Recursive Definition of n-Categories

```
0-category: Set
1-category: Ordinary category
2-category: As defined above
n-category: Category enriched in (n-1)-categories
∞-category: Limit as n → ∞
```

### Coherence Complexity

| Dimension | Coherence | Examples |
|-----------|-----------|----------|
| 1 | Associativity + identity | Ordinary categories |
| 2 | Pentagon + triangle | Bicategories |
| 3 | 6+ coherence axioms | Tricategories |
| 4+ | Impossible to classify | Need weak structure |
| ∞ | Coherence by definition | ∞-categories |

**Simpson's Conjecture**: For n ≥ 4, strictification not possible (beyond Mac Lane).

### Strictification: From Weak to Strict

**Theorem (Mac Lane)**: Every bicategory biequivalent to strict 2-category.

**Key**: Associators/unitors become identities via equivalence.

**Fails for n ≥ 3**: Tricategories cannot always be strictified!

**Solution**: Accept weak structure, use coherence directly.

## ∞-Categories: Multiple Models

### Five Equivalent Models

1. **Simplicial Sets**: Nerves of simplicial complexes
2. **Topological**: Topological spaces (∞-groupoids are spaces)
3. **Quasi-categories**: Simplicial sets with inner horn filling
4. **Segal Spaces**: Iteration of spaces with Segal maps
5. **Complete Segal Spaces**: Segal with equivalences

**Theorem (Joyal, Lurie, Rezk)**: All models equivalent!

### Quasi-Categories (Joyal-Lurie Model)

#### Simplicial Sets Background

**Δ^n** = standard n-simplex (vertices 0,1,...,n with order)

**Simplicial set** X = functor Δ^op → Set
```
X_n = n-simplices
face maps: delete vertices
degeneracy: repeat vertices
```

#### Horns: Partial Simplices

**Λ^k_n** = simplicial subset of Δ^n (all faces except interior of one)

Example: Λ^1_2 = two edges of triangle (missing middle face)

#### Quasi-Category Definition

Simplicial set X is **quasi-category** if:

**Inner horn filling**: Every Λ^k_n → X (k ≠ 0,n) extends to Δ^n → X

**Intuition**: Composable chains of arrows always have filler compositions

### (∞,1)-Categories

Focus on 1-morphisms (objects and arrows), ignore higher structure.

```
Homotopy hypothesis:
∞-groupoids ≅ homotopy types (topological spaces)

(∞,1)-categories:
Objects and arrows, higher structure are homotopy equivalences
```

## Stable ∞-Categories

### Motivation from Triangulated Categories

Classical **triangulated categories** (homological algebra) have:
- Shift functor Σ (suspension)
- Distinguished triangles (exact sequences)
- Octahedral axioms

**Problem**: Axioms don't lift to homotopy theory naturally.

### Stable ∞-Category Definition

∞-category C is **stable** if:

```
1. Finite limits and colimits exist
2. Pushouts = pullbacks (by pointing)
3. Shift/suspension: Σ: C → C is equivalence
4. Fiber sequences = cofiber sequences
```

**Key insight**: Cancels distinction between hom and suspension!

### Examples

1. **Sp**: Spectra (fundamental stable category)
2. **D(R)**: Derived category of module category
3. **D^perf(X)**: Perfect complexes on scheme X
4. **Perf(X)**: Perfectoid spaces
5. **QC(X)**: Quasi-coherent sheaves on stack

### t-Structures

**t-structure** on stable category:
```
C^≤0, C^≥0: Subcategories satisfying axioms
Heart: C^≤0 ∩ C^≥0 = abelian category
```

**Recovery**:
```
Homology: H^i(X) = Hom(Σ^i Y, X) where Y ∈ Heart
```

Recovers classical homology from categorical structure!

## Homotopy Type Theory Connection

### Homotopy Hypothesis

**Conjecture**: ∞-groupoids = homotopy types (spaces)

**Statement**:
```
Category of ∞-groupoids ≅ Homotopy category of spaces
```

**Implications for higher categories**:
- Types are spaces
- Equality is homotopy
- Identity types give paths

### Univalence Axiom

**Voevodsky's axiom**:
```
(A ≃ B) ≅ (A = B)
[equivalence = equality]
```

**Consequence**: All mathematics expressible in homotopy-invariant way!

## Applications Across Mathematics

### Derived Algebraic Geometry

Use ∞-categories to define:
- **Derived schemes**: Locally ringed with derived structure sheaf
- **Cotangent complex**: Derived analog of differentials
- **Serre intersection formula**: In stable homotopy theory

### Homotopy Type Theory (HoTT)

Proof assistant system where:
- Types are ∞-groupoids
- Proofs are homotopy paths
- Univalence axiom allows type equality
- Applications: Formalized mathematics

### Topological Quantum Field Theory

**Cobordism hypothesis (Baez-Dolan)**:

∞-functors from cobordism category to vector spaces = TQFTs

**Higher versions**:
- Extended TQFTs (higher dimensions)
- Factorization algebras (∞-categorical structure)

### Higher Gauge Theory

Quantum field theory with higher symmetries:
- 2-gauge connections (higher connections)
- ∞-categories of principal bundles
- Chern-Simons theory revisited

## Why Beyond Ordinary Categories?

1. **Homotopy natural**: Captures spaces up to equivalence
2. **Derived structures**: Shadows of classical constructions
3. **∞-functors**: Automatically preserve homotopy structure
4. **Modern physics**: String theory requires higher structures
5. **Algebraic topology**: Intersection homology, perverse sheaves

## Common Mistakes

❌ **Mistake**: "Bicategories need all Pentagon/Triangle axioms"
✓ **Reality**: Mac Lane shows only these two; others automatic

❌ **Mistake**: "∞-categories are ∞-groupoids"
✓ **Reality**: (∞,1)-categories focus on 1-morphisms

❌ **Mistake**: "Can strictify all coherences"
✓ **Reality**: Fails for n ≥ 3 (Simpson's Conjecture)

❌ **Mistake**: "Homotopy Type Theory replaces set theory"
✓ **Reality**: HoTT = constructive mathematics + univalence

## Study Guide

1. Master 2-categories and bicategories
2. Understand associator/unitor coherence
3. Learn simplicial sets (background for ∞-categories)
4. Study quasi-categories systematically
5. Apply to homotopy theory
6. Explore stable categories
7. Connect to homotopy type theory

## Further Reading

- Leinster, "Higher Operads, Higher Categories" (introduction)
- Lurie, "Higher Topos Theory" (foundational ∞-category text)
- Riehl & Verity, "Elements of ∞-Category Theory" (modern treatment)
- Univalent Foundations, "Homotopy Type Theory: UF" (HoTT book)

## Research Questions

1. Why is weak structure necessary for higher categories?
2. How does simplicial nerve recover categorical structure?
3. Why is univalence axiom profound?
4. How do stable categories generalize homological algebra?
5. What makes ∞-categories the "right" framework?
6. How does TQFT interpret cobordisms as functors?
