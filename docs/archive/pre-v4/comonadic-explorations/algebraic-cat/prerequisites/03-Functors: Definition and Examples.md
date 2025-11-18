# Functors: Definition and Examples

## What is a Functor?

A **functor** F: C → D (between categories) preserves categorical structure:

F(f ∘ g) = F(f) ∘ F(g) [composition]
F(id_X) = id_{F(X)} [identity]

### Covariant vs Contravariant
- **Covariant**: Preserves direction of arrows
- **Contravariant**: Reverses arrows (F(f: X → Y) becomes F(f): F(Y) → F(X))

## 12 Examples

1. **Forgetful U: Grp → Set** - Forget group structure
2. **Free F: Set → Grp** - Generate free group on set  
3. **Fundamental Group π₁: Top → Grp** - Topological invariant
4. **Homology Hₙ: Top → Ab** - Algebraic topology
5. **Dual Space (-)* : Vect → Vect** (contravariant)
6. **Opposite Inclusion C ↪ [C^op, Set]** - Yoneda embedding
7. **Universal Enveloping U: LieAlg → Alg** - Algebraic enveloping
8. **Abelianization G ↦ G/[G,G]: Grp → Ab**
9. **Tensor Product (-) ⊗ k: Mod_R → Vect_k**
10. **Spectrum Spec: Comm(Ring)^op → Sch** - Algebraic geometry
11. **Determinant det: GL(n) → k*: Grp → Grp**
12. **Inclusion functors** between subcategories

## Functor Properties

**Faithful**: Injective on hom-sets
**Full**: Surjective on hom-sets  
**Essentially Surjective**: Objects covered up to isomorphism

## Key Theorems
- Faithful functors reflect monos/epis/isos
- Full faithful functors are embeddings
- Fully faithful + ess surj = equivalence of categories

