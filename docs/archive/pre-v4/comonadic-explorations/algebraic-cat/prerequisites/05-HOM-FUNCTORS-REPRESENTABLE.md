# Hom-Functors and Representable Functors

## Hom-Functors

### Covariant Hom_C(A,-)
**Functor** C → Set
```
X ↦ Hom_C(A, X)  [morphisms FROM A]
(f: X → Y) ↦ (f ∘ -): Hom(A,X) → Hom(A,Y)
```
**Functoriality**: Composition preserved

### Contravariant Hom_C(-, A)
**Functor** C^op → Set
```
X ↦ Hom_C(X, A)  [morphisms TO A]
(f: X → Y) ↦ (- ∘ f): Hom(Y,A) → Hom(X,A)
```
**Arrows reversed** due to contravariance

## Representable Functors

**Definition**: F: C → Set is **representable** if ∃A ∈ C such that:
```
F ≅ Hom_C(A, -)  [natural isomorphism]
```

**Universal Element**: Unique a ∈ F(A) such that F(f)(a) = (f,a) establishes bijection

## Criterion for Representability

**Brown Representability**: F is representable iff:
1. Preserves limits
2. Solution set condition holds

## 10 Detailed Examples

### 1. Forgetful Functor Grp → Set
```
U(G) = underlying set of G
Hom_Grp(ℤ, G) ≅ U(G)  [homomorphisms = elements]
Represented by ℤ
```

### 2. Polynomial Evaluation
```
F: Ring → Set, R ↦ R^n [n-tuples]
Hom_Ring(Z[x₁,...,x_n], R) ≅ R^n  [evaluation]
Represented by polynomial ring
```

### 3. Continuous Functions to Sierpinski
```
F: Top → Set, X ↦ open sets of X
Hom(X, Sierpinski) ≅ Open(X)  [continuous = inclusion]
Represented by Sierpinski space
```

### 4. Power Set Functor
```
F: Set → Set, X ↦ P(X)
Hom(X, {0,1}) ≅ P(X)  [characteristic functions]
Represented by two-element set
```

### 5. Tangent Bundle (Differential Geometry)
```
T: Diff → Set, M ↦ tangent bundle
Representable by infinitesimal construction
```

### 6. Fundamental Group (Pointed Spaces)
```
π₁: Top* → Grp
Hom(S¹, X) ≅ π₁(X)  [loops = elements]
Represented by S¹
```

### 7. Cohomology Ring (Homotopy)
```
H*: Top → Grp
Representable by Eilenberg-MacLane spaces
```

### 8. Tensor Algebra
```
T: Vect → Vect, V ↦ ⊗*V
Hom(T(V), W) ↔ morphisms respecting tensor structure
```

### 9. Free Module Functor
```
F: Grp → Set, X ↦ free Z[G]-module on X
Hom(Z[G], M) ≅ M^G  [G-module structure]
```

### 10. Moduli Space
```
Schemes parameterized by objects
Hilbert scheme: Hom(-, H) represents closed subschemes
```

## Yoneda Embedding

**Embedding** y: C → [C^op, Set]
```
y(A) = Hom_C(-, A)
y(f: A → B) = Hom(f, -): Hom(-,A) ⇒ Hom(-,B)
```

**Theorem**: y is fully faithful

**Consequence**: Every category embeds in presheaves; presheaves are free cocompletions

## Power of Representability

1. **Universal Property Characterization**: Universal properties = representability statements
2. **Computational Power**: Categorical → set-theoretic (via representation)
3. **Automatic Existence/Uniqueness**: From representing object
4. **Natural Constructions**: Representable functors are "canonical"
5. **Foundation for Adjoints**: Adjoints define themselves via representability

## Adjunctions and Representability

**Fundamental Connection**:
```
F ⊣ G  ⟺  Hom_D(F(c), d) ≅ Hom_C(c, G(d))  [natural in both variables]

Right adjoint G: "Represents" the hom-functor
```

## Common Mistakes

❌ "All functors are representable"
✓ Only special ones; most are not

❌ "Representability = free functor"
✓ Related but different concepts

❌ "Solution set condition not important"
✓ Necessary for representability to exist

## Study Guide

1. Master Hom_C(A,-)  definition
2. Understand contravariance in Hom_C(-,A)
3. Work through 5+ examples
4. Prove Yoneda embedding fully faithful
5. Connect to adjoint functors
6. Apply representability to your field

## Key Questions

1. Why is Hom_C(A,-) a functor?
2. What makes a functor representable?
3. Why is Yoneda embedding important?
4. How do represent functors relate to adjoints?
5. What's the geometric meaning of representable?
