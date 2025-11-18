# Categories: Foundational Definition and Examples

## What is a Category?

A **category** is an abstract structure capturing:
- **Objects**: Things being studied (sets, groups, topological spaces, etc.)
- **Morphisms**: Structure-preserving maps between objects
- **Composition**: How morphisms combine

## Formal Definition

Category C = (Ob(C), Mor(C), ∘, id) where:

**1. Collections**:
- Ob(C): objects of C
- For each X, Y ∈ Ob(C): Hom_C(X,Y) = morphisms f: X → Y

**2. Composition**:
```
∘: Hom(Y,Z) × Hom(X,Y) → Hom(X,Z)
  (g,f) ↦ g ∘ f
```

**3. Identities**:
```
For each X ∈ Ob(C): id_X ∈ Hom(X,X)
```

**4. Axioms**:
```
ASSOCIATIVITY: (h ∘ g) ∘ f = h ∘ (g ∘ f)
IDENTITY: id_Y ∘ f = f = f ∘ id_X
```

## 11 Concrete Examples

### 1. Set: Sets and Functions
Objects: All sets
Morphisms: Functions f: X → Y
Composition: Function composition
Identity: id_X(x) = x

### 2. Top: Topological Spaces
Objects: Topological spaces
Morphisms: Continuous functions
Composition: Functional composition (continuous ∘ continuous = continuous)

### 3. Grp: Groups and Homomorphisms
Objects: Groups (G, ·)
Morphisms: Group homomorphisms φ: G → H (preserve multiplication)
Composition: Function composition (homomorphism ∘ homomorphism = homomorphism)

### 4. Vect_k: Vector Spaces
Objects: Vector spaces over field k
Morphisms: k-linear maps f: V → W (f(av + bw) = af(v) + bf(w))

### 5. Ring: Rings and Ring Homomorphisms
Objects: Rings (R, +, ×)
Morphisms: Ring homomorphisms (preserve both operations)

### 6. Poset: Partially Ordered Sets
Objects: Posets (S, ≤)
Morphisms: f: S → T with x ≤ y ⟹ f(x) ≤ f(y) (order-preserving)

### 7. Rel: Relations
Objects: Sets
Morphisms: Relations R ⊆ X × Y
Composition: Relational composition {(x,z) | ∃y: (x,y) ∈ R, (y,z) ∈ S}

### 8. Mon: Monoids
Objects: Monoids (M, ·, e)
Morphisms: Monoid homomorphisms

### 9. Cat: The Category of Categories
Objects: Small categories
Morphisms: Functors (structure-preserving maps between categories)

### 10. Met: Metric Spaces
Objects: Metric spaces (X, d)
Morphisms: Continuous functions (distance-preserving)

### 11. Measured Spaces
Objects: Measurable spaces (X, Σ)
Morphisms: Measurable functions

## Morphism Properties

### Isomorphism
f: X → Y with ∃g: Y → X where g ∘ f = id_X and f ∘ g = id_Y

**Interpretation**: X and Y are "same" in category

### Monomorphism (Monic)
f: X → Y such that f ∘ g₁ = f ∘ g₂ ⟹ g₁ = g₂

**In Set**: Injective functions
**General**: Left-cancellative

### Epimorphism (Epic)  
f: X → Y such that h₁ ∘ f = h₂ ∘ f ⟹ h₁ = h₂

**In Set**: Surjective functions
**General**: Right-cancellative
**Warning**: NOT always surjective! (Example: ℤ → ℚ in Ring)

### Endomorphism
f: X → X (morphism from object to itself)

### Automorphism  
f: X → X that is isomorphism

### Bimorphism
f that is both monic and epic (but may not be iso!)

## Commutative Diagrams

Visual representation of morphism relationships:

```
       f
   X ---→ Y
   |      |
  g|      |h
   |      |
   ↓      ↓
   Z ---→ W
       k
```

Diagram commutes if: k ∘ g = h ∘ f

## Small vs Large Categories

**Locally Small**: Hom_C(X,Y) is a set (not proper class)

**Small Category**: Ob(C) and Mor(C) are sets

**Large Category**: Allow proper classes of objects/morphisms
Example: Category Cat of all categories (proper class of objects)

## Why Categories?

1. **Unifies Mathematics**: Same structure in algebra, topology, logic
2. **Universal Properties**: Characterize objects by relationships
3. **Morphisms Over Elements**: Focus on structure-preserving maps
4. **Duality**: Opposite category gives free theorems
5. **Abstraction**: Common patterns across disciplines

## Common Mistakes

❌ "Objects are primary, morphisms secondary"
✓ Actually: Morphisms define structure; objects are just labels

❌ "Monomorphism = Injective"  
✓ Only in concrete categories; ℤ → ℚ is monic epic but not iso

❌ "Categories require elements"
✓ No: Categories are purely structural

## Key Takeaways

- Categories capture mathematical structure abstractly
- Morphisms are the primary data
- Composition respects structure
- Many familiar structures are categories
- Universal properties are morphism conditions

## Study Questions

1. What makes a morphism an isomorphism?
2. Why isn't every bimorphism an isomorphism?
3. How do limits generalize universal properties?
4. What does locally small mean?
5. Why focus on morphisms instead of elements?
