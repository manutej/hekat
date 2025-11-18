# Topos Theory and Categorical Logic: A Comprehensive Treatment

## What is a Topos?

A **topos** is a category that behaves like the category of sets, but with more flexibility. Topoi provide:
- An alternative foundation for mathematics (not ZFC)
- Categorical treatment of geometry (via sheaves)
- Constructive/intuitionistic mathematics naturally
- Internal logic (automatic reasoning within the topos)

## Elementary Topoi: Complete Axiomatization

### Formal Definition

A category ℰ is an **elementary topos** if:

**1. Finite Limits**:
- Has terminal object 1
- Has binary products X × Y for all X,Y
- Has equalizers for parallel pairs f,g: X → Y

Consequence: Has all finite limits (products, pullbacks, etc.)

**2. Cartesian Closure**:
- For all X,Y ∈ ℰ, there exists internal hom [X,Y]
- Exponential adjunction: Hom(X × Y, Z) ≅ Hom(X, [Y,Z])

**3. Subobject Classifier**:
- Existence of object Ω with universal property:
  - Subobjects of X ↔ Morphisms X → Ω (bijection)
  - For each monic m: S → X, unique χ_m with:
    ```
    S ---m---→ X
    |          |
    !          χ_m
    |          |
    1 ---T---→ Ω

    [pullback diagram]
    ```

Where T: 1 → Ω is "true" element.

## Why These Axioms?

### Finite Limits
- **Terminal 1**: Single element (like ∅ or point)
- **Products**: Combine structures (like Cartesian product)
- **Equalizers**: Define subobjects by equations
- Together: Allow constructing all finite limits (universal properties)

### Cartesian Closure
- **[X,Y]**: Internalize morphisms as objects
- **Exponential law**: Move arguments in/out of exponents
- **Allows**: Function spaces, higher-order structures
- **Consequence**: Topos is a **closed symmetric monoidal category** (with × as tensor)

### Subobject Classifier Ω
- **Generalizes {true, false}**: Ω is "object of truth values"
- **Subobjects via morphisms**: Instead of "X ⊆ Y", use characteristic function
- **Makes logic internal**: Type theory works inside topos automatically

## Examples of Elementary Topoi

### 1. Set: The Prototypical Topos
```
Objects: Sets
Morphisms: Functions
Limits: Ordinary set operations
Ω = {true, false}
[X,Y] = Y^X (functions X→Y)
Logic: Classical (every truth value is true or false)
```

### 2. Presheaf Topoi: [C^op, Set]
```
Objects: Functors C^op → Set (presheaves)
Morphisms: Natural transformations
Limits: Pointwise (computed in Set)

Example: Simplicial sets = [Δ^op, Set]
```

**Key property**: Always a topos!

### 3. Sheaf Topoi: Sh(X)
```
Objects: Sheaves on topological space X
Morphisms: Sheaf morphisms
Limits: Pointwise

Subobject classifier Ω:
- Ω(U) = {open sets V ⊆ U} (all opens)
- Open sets glue by unions
```

**Characteristic function**: χ_S(U) = {V ⊆ U | V ⊆ S}

### 4. Effective Topos: Eff
```
Objects: Assemblies (sets with realizability notion)
Morphisms: Realizable functions

Logic: Intuitionistic (excludes law of excluded middle)
Church's thesis: true as internal axiom
Application: Computability theory
```

### 5. G-Sets: G-Equivariant Sets
```
Objects: Sets with G-action (G finite group)
Morphisms: G-equivariant functions

Ω = G-set of subgroups (with action)
Classifier: χ_S(g) = stability group of gS
```

### 6. Simplicial Sets: sSet = [Δ^op, Set]
```
Δ = simplicial category (finite non-empty ordinals)
Objects: X_n = n-simplices (with face/degeneracy)
Morphisms: Simplicial maps

Logic: Classical (Set-based)
Application: Homotopy theory, ∞-categories
```

### 7. Realizability Topos: RT(A)
```
A = partial combinatory algebra (computation model)
Objects: Assemblies (sets with realizable proofs)
Morphisms: Realizable functions

Church-Turing thesis true internally
Application: Recursive mathematics
```

## Subobject Classifier and Logical Structure

### The Power Object Ω

**Definition**: Ω is the **terminal object** in the category of subobject classifiers.

**Universal property**:
```
For any monic m: S → X:

∃! χ_m (characteristic function) making diagram pullback:

S ---m---→ X
|          |
|          χ_m
|          |
1 ---T---→ Ω
```

**Elements of Ω**: Truth values in the topos

In Set: Ω = {T, F}
In Sh(X): Ω(U) = opens of U
In Eff: Ω = partial recursive functions

### Power Objects: Ω^X

**Definition**: P(X) = [X, Ω] (exponential in topos)

**Universal property**: Morphisms X → Ω correspond to subobjects of X

**Comprehension**:
```
{x ∈ X | φ(x)} ↔ characteristic function X → Ω
```

**Higher-order logic**: P(P(X)) exists, giving impredicative quantification

## Grothendieck Topoi and Sheaves

### Sites and Grothendieck Topologies

A **Grothendieck topology** on small category C:
- For each X ∈ C, collection Cov(X) of "covering families"
- Must satisfy:
  1. Identity covers (single id morphism)
  2. Stability under pullback
  3. Transitivity (covers of covers)

**Examples**:
- Zariski topology (on schemes): Open covers in spec(R)
- Étale topology: Étale morphisms as covers
- Canonical: All families with epi legs (arrows)

### Sheaves on Sites

**Presheaf** F: C^op → Set

**Sheaf condition**: For covering family {U_i → X}:
```
F(X) → ∏F(U_i) ⟹ ∏F(U_i ×_X U_j)
(matching condition: gluability axiom)
```

**Consequence**: F is **continuous** with respect to Grothendieck topology

### Sheafification

**Theorem**: Every presheaf extends to sheaf (sheafification functor)

```
Presheaves ⊇ Sheaves
(lex reflective subcategory)
```

**Construction**: F^+ = sheafification
- F^+(X) = colimit of compatible families of F-sections
- Natural map F → F^+ universal

## Topoi as Foundations for Mathematics

### Why Not ZFC?

**ZFC Axioms**:
- Materialism (elements matter)
- Global membership ∈
- Law of excluded middle
- Axiom of choice

**Alternative in topoi**:
- Structuralism (relationships matter)
- Local logic internal to topos
- Constructive/intuitionistic reasoning
- Choice axiom optional

### Elementary Topos Category Theory (ETCS)

**Lawvere-Maclane**: Axioms for category of sets (category-theoretic)

Instead of axioms on ∈, axioms on:
- Objects (sets)
- Morphisms (functions)
- Composition, identity
- Finite limits, colimits, exponentials

**Theorem (Lawvere)**: ETCS equivalent to bounded ZFC

### Natural Numbers Objects (NNO)

**Definition**: N is NNO if:
```
0: 1 → N
s: N → N (successor)

∀f: X → X and e: 1 → X, ∃! u: N → X:
u ∘ 0 = e
u ∘ s = f ∘ u
(recursion principle)
```

**Consequence**: Can define all arithmetic in topos!

## Internal Logic of Topoi

### Mitchell-Bénabou Language

**Internal language**: Reason "as if" objects are sets

**Kripke-Joyal Semantics**: Truth notion for internal formulas

For formula φ(x) and stage U:
```
U ⊨ φ(x)  iff  characteristic function lands in true

More precisely: U → [1, Ω] lands in T: 1 → Ω
```

### Intuitionistic Logic

In topoi (especially non-Boolean):
- **Law of excluded middle fails**: A ∨ ¬A not provable
- **Double negation**: ¬¬A not equivalent to A
- **Proof by contradiction**: Not valid in constructive logic
- **BHK interpretation**: Proofs are constructions, not just existence claims

### Examples of Intuitionistic Reasoning

In effective topos:
```
∀x ∃y φ(x,y)  [universal + existential]

≠ ∃f ∀x φ(x, f(x))  [requires choice function!]

Church's thesis: all functions are computable
```

## Geometric Morphisms

### Definition

**Geometric morphism** f: ℰ → ℱ (f: ℱ → ℰ in opposite direction):
```
f*: ℱ → ℰ  (inverse image, must be left exact)
f_*: ℰ → ℱ  (direct image, right adjoint to f*)
```

**Left exactness of f***: Preserves finite limits

**Key property**: f* ⊣ f_* always holds!

### Essential Geometric Morphisms

When f_* also has left adjoint f!:
```
f! ⊣ f* ⊣ f_*
(essential morphism)
```

**Consequence**: Much stronger, allows comparing logic

### Boolean Topoi

**Topos ℰ is Boolean** if:
```
Ω = {T, F}  (two-element set)

Equivalently: Law of excluded middle
Equivalently: Every object decidable
```

**Theorem (Barr)**: Every topos has Boolean sheafification

## Applications Throughout Mathematics

### 1. Sheaf Cohomology
```
H^i(X, F) = Ext^i(𝒪_X, F)

Define via exact sequences in Sh(X)
Works for any sheaf on any topos
```

### 2. Étale Topology and Algebraic Geometry
```
Scheme X has étale topology
Sheaves measure étale structure
Adic rings from sheaf sections
```

### 3. Effective Topos and Computability
```
Every morphism is algorithm
Decidability is propositional form
Computability provable internally
```

### 4. Synthetic Differential Geometry
```
Smooth topos SDG:
- Infinitesimals exist (dx)
- Taylor expansion automatic
- Derivatives from logic
```

### 5. Homotopy Type Theory
```
Types are ∞-groupoids
Paths are proofs of equality
Univalence: equivalence = equality

∞-topoi (Lurie): Higher sheaf theory
```

## Comparisons: Topoi vs Set Theory

| Aspect | ZFC | Topos |
|--------|-----|-------|
| Foundation | Sets + membership | Categories + morphisms |
| Logic | Classical (LEM) | Constructive (default) |
| Geometry | External | Internal + via sheaves |
| Functions | Global | Local (sheaves) |
| Truth values | {T,F} | Ω object (variable) |
| Choice | Axiom | Optional |

## Common Mistakes

❌ **Mistake**: "Topos = generalization of Set"
✓ **Reality**: Topos = flexible foundation, Set is special case

❌ **Mistake**: "Topoi must satisfy classical logic"
✓ **Reality**: Default is intuitionistic; Boolean is special

❌ **Mistake**: "Sheaves are only topological"
✓ **Reality**: Sheaves work on any site (Zariski, étale, etc.)

❌ **Mistake**: "Subobject classifier is just truth values"
✓ **Reality**: Ω is sophisticated object controlling all logic

## Study Guide

1. Master finite limits and cartesian closure
2. Understand subobject classifier deeply
3. Work through presheaf example [C^op, Set]
4. Study sheafification on topological space
5. Learn internal logic (Mitchell-Bénabou)
6. Explore Kripke-Joyal semantics
7. Apply to effective topos
8. Connect to homotopy type theory

## Further Reading

- Mac Lane & Moerdijk, "Sheaves in Geometry and Logic" (foundational)
- Johnstone, "Sketches of an Elephant" (comprehensive reference)
- Taylor, "Practical Foundations of Mathematics" (constructive approach)
- Univalent Foundations, "Homotopy Type Theory" (modern direction)

## Research Questions

1. Why must subobject classifier exist?
2. How does logic emerge from Ω?
3. Why is classical logic exceptional?
4. What makes Grothendieck topologies fundamental?
5. How do topoi generalize ZFC?
6. Why is sheafification universal?
