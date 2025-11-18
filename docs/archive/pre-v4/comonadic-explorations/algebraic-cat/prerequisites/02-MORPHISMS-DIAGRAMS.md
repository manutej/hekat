# Morphisms and Commutative Diagrams

## Morphism Types Complete Reference

### Monomorphism (Monic, ↪)
f: X → Y is monic if: f ∘ g₁ = f ∘ g₂ ⟹ g₁ = g₂

In **Set**: Injective
In **Ring**: ℤ → ℚ is monic (non-injective!)

### Epimorphism (Epic, ↠)
f: X → Y is epic if: h₁ ∘ f = h₂ ∘ f ⟹ h₁ = h₂

In **Set**: Surjective
In **Ring**: ℤ → ℚ is epic (non-surjective!)

### Isomorphism (Iso, ≅)
∃g: Y → X with g ∘ f = id_X and f ∘ g = id_Y

### Endomorphism (Endo)
f: X → X (self-map)

### Automorphism (Auto)
Endomorphism that is also isomorphism

### Bimorphism
Both monic and epic (but NOT necessarily iso!)

## Commutative Diagrams

Diagrams express equalities between morphism paths:

```
     f
 X ---→ Y
 |      |
g|      |h
 |      |
 ↓      ↓
 Z ---→ W
     k
Commutes: k ∘ g = h ∘ f
```

### Five Lemma
Classical result for chasing diagrams in exact sequences

```
... → A → B → C → D → E → ...
      |   |   |   |   |
      ↓   ↓   ↓   ↓   ↓
... → A'→ B'→ C'→ D'→ E'→ ...

If outer four preserve exactness, middle does too
```

### Snake Lemma
Produces connecting homomorphism between kernels/cokernels

```
0 → A → B → C → 0
    |   |   |
    ↓   ↓   ↓
0 → A'→ B'→ C'→ 0

Gives connecting map: ker(C→C') → coker(A→A')
```

## Special Morphism Classes

### Split Monomorphism  
f: X → Y with ∃r: Y → X where r ∘ f = id_X (retraction)

### Split Epimorphism
f: X → Y with ∃s: Y → X where f ∘ s = id_Y (section)

### Regular Mono
Equalizer of some pair of morphisms

### Regular Epi
Coequalizer of some pair of morphisms

### Normal Mono (in abelian)
Kernel of some morphism

### Normal Epi (in abelian)
Cokernel of some morphism

## Diagram Chasing Techniques

1. **Element chasing**: In concrete categories, follow elements through diagrams
2. **Freyd-Mitchell embedding**: Abelian categories embed into module categories
3. **Diagram lemmas**: Five lemma, snake lemma, 3×3 lemma

## Study Guide
- Master monomorphism vs injectivity
- Understand why ℤ → ℚ is monic
- Work through five lemma proof
- Practice snake lemma construction
- Learn diagram chasing in abelian categories

## Key Questions
1. Why is monic ≠ injective in general?
2. How do five and snake lemmas relate?
3. What makes diagram chasing valid?
4. How do normal monos differ from regular?
