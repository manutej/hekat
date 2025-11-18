# Functor Categories [C,D]: Categories of Functors

## Definition

The **functor category** [C,D] is the category whose:
- **Objects**: Functors F: C í D
- **Morphisms**: Natural transformations between functors

## Core Axioms

[C,D] is a legitimate category:

1. **Identity**: For each functor F, identity natural transformation id_F: F “ F (id_F(X) = id_{F(X)})
2. **Composition**: For ∑: F “ G and ∂: G “ H, their composition (∂  ∑): F “ H is defined componentwise:
   ```
   (∂  ∑)_X = ∂_X  ∑_X: F(X) í H(X)
   ```
3. **Associativity**: (∏  ∂)  ∑ = ∏  (∂  ∑)
4. **Identity Laws**: id_G  ∑ = ∑ and ∑  id_F = ∑

## Key Observation

Morphisms in [C,D] are **natural transformations**composition respects the naturality squares.

## 8 Critical Examples

1. **[C^op, Set] = Presheaf Category**
   - Fundamental in category theory
   - Every category embeds densely here via Yoneda embedding
   - Limits/colimits computed pointwise

2. **Simplicial Sets [î^op, Set]**
   - Objects: simplicial complexes with degenerate faces
   - Used in algebraic topology, higher category theory
   - Quasi-categories live in here

3. **[G, Set] = G-Sets (Group Actions)**
   - Objects: functors from one-object-one-morphism G to Set (= G-actions)
   - Morphisms: natural transformations (= equivariant maps)
   - Category of G-sets and G-equivariant functions

4. **[J, Ab] (Direct Limits)**
   - Objects: functors J í Ab (families of abelian groups)
   - Colimit in [J,Ab] computed in Ab gives direct limit
   - The directed limit limí is the colimit in this functor category

5. **[^op, Grp] (Inverse Limits)**
   - Objects: sequences of groups and homomorphisms
   - Inverse limit is the limit in this functor category
   - limê computed as product of stabilizing sequences

6. **[2, Set] (Spans and Correspondences)**
   - Objects: functors from 2-element category {" í "}
   - = Pairs of functions with common codomain
   - Morphisms: commutative triangles

7. **[î, C] (Simplicial Objects in C)**
   - Objects: simplicial objects in any category C
   - Used in homological algebra, derived functors
   - Simplicial complexes, simplicial abelian groups, etc.

8. **[C, _i D_i] (Product of Functor Categories)**
   - Products of functor categories are functor categories
   - [C, DÅ ◊ DÇ] E [C, DÅ] ◊ [C, DÇ]
   - Functors into product = pair of functors into factors

## Fundamental Properties

### Limits and Colimits (Computed Pointwise)

**Theorem**: Limits and colimits in [C,D] are computed **pointwise**:

If ∑: F “ G and we want the limit, for each object X in C:
```
(lim ∑)_X = lim ∑_X
```

**Why**: Natural transformations are compatible with limits, so we can compute limits of components independently.

**Example**:
- lim F in [C, Set] is the functor that assigns to each X the limit lim_{jJ} F(j)(X)
- Yoneda embedding y: C í [C^op, Set] preserves limits

### Completeness and Cocompleteness

**Theorem**: If D is complete/cocomplete, so is [C,D].

**Proof**: Use pointwise computation of limits/colimits.

**Significance**: This means:
- [C, Set] is complete and cocomplete
- Presheaves have all limits and colimits
- Every category embeds into a complete/cocomplete category

### Yoneda Embedding: C í [C^op, Set]

The Yoneda embedding is the **fundamental functor**:

```
y: C í [C^op, Set]
X ¶ Hom(-,X)
(f: X í Y) ¶ (natural transformation: post-composition by f)
```

**Theorem (Yoneda Fully Faithful)**: y is fully faithful.
- Injective on objects (up to isomorphism)
- Bijective on morphisms

**Theorem (Yoneda Density)**: Every presheaf is the **colimit of representables**.

```
F  [C^op, Set] = colim_{X(¿ìF)} Hom(-,X)
```

where (¿ìF) is the comma category of representables under F.

## Fundamental Theorem of Category Theory

**Theorem**: Every functor F: C í D can be **uniquely extended** to a continuous functor (preserving limits) from [C^op, Set] to [D^op, Set]:

```
C --Fí D
 |      |
 yì     ìy
[C^op,Set] --Ran_y F-í [D^op,Set]
```

This extension is given by the **right Kan extension** of F along the Yoneda embedding.

## Relation to Kan Extensions

Everything in functor categories is built from Kan extensions:

1. **Yoneda embedding**: y_C: C í [C^op, Set] is defined by Kan extensions
2. **Limits in [C,D]**: Computed via Kan extensions in D
3. **Extensions of functors**: Via Kan extensions along Yoneda
4. **Density theorem**: Every presheaf is colimit of representables (= left Kan extension)

## Study Checklist

- [ ] Understand [C^op, Set] as the free cocompletion of C
- [ ] Recognize [C^op, Set] in multiple examples
- [ ] Verify Yoneda lemma in simple cases
- [ ] Compute limits/colimits pointwise in [C,D]
- [ ] See connection to Kan extensions

## Key Insight

Functor categories are the bridge between individual categories and the universal properties that define them. In [C,D], natural transformations are the **morphisms**, which means **Kan extensions are the universal morphisms** in functor categories.

This is why [C^op, Set] is so important: it's the **universal** category containing C (via Yoneda), and every construction in category theory can be understood as happening in some functor category.
