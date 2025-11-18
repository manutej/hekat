# Natural Transformations

## Definition

A **natural transformation** η: F ⇒ G between functors F,G: C → D is:

**Collection** {η_X : F(X) → G(X) | X ∈ C} of morphisms in D

**Naturality Axiom**: For all f: X → Y in C, the diagram commutes:

```
F(X) --η_X-→ G(X)
  |           |
F(f)        G(f)
  |           |
  ↓           ↓
F(Y) --η_Y-→ G(Y)
```

This ensures η is "natural" - doesn't depend on arbitrary choices.

## Why Naturality?

Without naturality condition, just collection of morphisms.

With naturality: Forces compatibility with categorical structure.

**Eilenberg-Mac Lane insight**: Naturality formalizes "canonical" constructions.

## 15+ Examples

### 1. Double Dual (Finite-Dim Vect)
η_V: V → V** sending v to evaluation at v
Natural, but not iso for infinite-dimensional

### 2. Abelianization
Forgetful Grp → Ab composed with universal map
Natural endomorphism

### 3. Fundamental Group
π₁: Top → Grp from basepoint
Homotopy equivalence is natural transformation

### 4. Determinant
det: GL(n) → k*
Natural between linear group and multiplicative

### 5. Homology Theories
Singular vs simplicial homology
Natural isomorphic via Eilenberg-Zilber

### 6. Tensor-Hom Adjunction
Natural bijection between bilinear and linear maps

### 7. Yoneda Embedding
y: C → [C^op, Set]
Fully faithful natural embedding

### 8. Unit/Counit of Adjunction
η: id ⇒ G∘F and ε: F∘G ⇒ id
Natural transformations defining adjoints

### 9-15: Many more in algebra, topology, logic...

## Composition of Natural Transformations

### Vertical Composition
η: F ⇒ G and μ: G ⇒ H give (μ ∘ η): F ⇒ H

Component: (μ ∘ η)_X = μ_X ∘ η_X

### Horizontal Composition (Godement Product)
For η: F ⇒ G (C → D) and μ: F' ⇒ G' (D → E):

(μ * η): F' ∘ F ⇒ G' ∘ G

Component: Commutative square combining both

### Interchange Law
(μ₂ ∘ μ₁) * (η₂ ∘ η₁) = (μ₂ * η₂) ∘ (μ₁ * η₁)

Both compositions compatible!

## Natural Isomorphism

**Natural isomorphism**: All components η_X are isomorphisms

**F ≅ G**: Functors naturally isomorphic

**Equivalence of categories**: F ∘ G ≅ id and G ∘ F ≅ id

## Functor Categories

Natural transformations make [C,D] into category:
- Objects: Functors C → D
- Morphisms: Natural transformations
- Composition: Vertical composition

## Key Theorems

- **Yoneda Lemma**: Nat(Hom(-,A), F) ≅ F(A)
- **Mac Lane Coherence**: Associator/unitor natural isos satisfy pentagon
- **Adjoint Naturality**: Unit/counit are natural transformations

## Common Mistakes

❌ "Just a collection of morphisms"
✓ Must satisfy naturality square

❌ "Natural = canonical"
✓ More precise: canonical constructions are natural

❌ "Horizontal composition = vertical"
✓ Different operations (Godement ≠ pointwise)

## Study Guide

1. Master naturality square
2. Work through 5+ examples carefully
3. Prove vertical composition associative
4. Understand horizontal composition
5. Recognize natural isos in your field
6. Connect to adjoints and Yoneda

## Questions

1. What does naturality square express?
2. Why call it "natural"?
3. How do compositions interact?
4. What makes Yoneda lemma natural?
5. How do natural transformations lift to categories?
