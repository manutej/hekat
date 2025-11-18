# The Yoneda Lemma: Central Theorem of Category Theory

## Statement

**Theorem (Yoneda Lemma)**:
For any functor F: C^op í Set and any object A  C:
```
Nat(Hom(-,A), F) E F(A)
```

The isomorphism is **natural in both F and A**.

## Interpretation

**In English**: "Natural transformations from the Hom-functor to F are in bijection with elements of F(A)."

More precisely: Evaluating a natural transformation ∑ at the identity element id_A gives you the element ∑_A(id_A)  F(A), and this map is bijective.

## Proof Sketch

1. **Forward direction**: ∑ ¶ ∑_A(id_A)
   - Given natural transformation ∑: Hom(-,A) “ F
   - Evaluate at A: ∑_A: Hom(A,A) í F(A)
   - Apply to identity: ∑_A(id_A)  F(A)

2. **Reverse direction**: x ¶ natural transformation ∑_x
   - Given element x  F(A)
   - For each f: B í A and y: Hom(B,A), define:
     ```
     ∑_x,B(f) = F(f)(x)
     ```
   - This is natural: commutes with further morphisms

3. **Bijection verification**: The forward-backward compositions are identities.

## Four Equivalent Formulations

### 1. Hom-Set Version (Most Common)
```
Nat(Hom(A,-), F) E F(A)
∑ î ∑_A(id_A)
```

### 2. Representation Version
For any functor F: C í Set:
```
F is representable ˙  A  C such that F E Hom(A,-)
```

### 3. Natural Transformation Version
Every natural transformation ∑: Hom(-,A) “ F is uniquely determined by ∑_A(id_A).

### 4. Embedding Version (Yoneda Embedding Corollary)
The Yoneda embedding:
```
y: C í [C^op, Set]
X ¶ Hom(-,X)
```
is **fully faithful**: For any A,B  C:
```
Hom_C(A,B) E Nat(Hom(-,A), Hom(-,B))
```

## Why This Is True (The Deep Reason)

The Yoneda lemma is true because **morphisms uniquely determine functors**.

When you have a natural transformation ∑: Hom(-,A) “ F, the naturality square:
```
        Hom(B,A) --∑_Bí F(B)
          ë            ë
      post-comp   F(post-comp)
          |            |
      Hom(A,A) --∑_Aí F(A)
```

forces ∑_B to be completely determined by what ∑ does at id_A  Hom(A,A).

This is because **every morphism f: B í A can be expressed as post-composition of id_A with something**, and naturality forces ∑_B(f) to be determined by ∑_A(id_A).

## 12 Critical Examples

### 1. **Forgetful Functor is Representable**
F: Grp í Set (forgetful) E Hom($, -)
Elements of F(G) = homomorphisms from $ = elements of G

### 2. **Free Functor is Represented**
F: Set í Grp (free group) has right adjoint (forgetful)
So F is left adjoint to Hom(F(-),-)

### 3. **Power Set is Representable**
P(X) E [X, {0,1}]
Subsets of X î functions to two-element set

### 4. **Fundamental Group Functor**
¿Å: Top* í Grp
Not representable (why? would need universal space with specific homotopy properties)

### 5. **Homology Functors**
H_n: Top í Ab
Not representable (Eilenberg-MacLane spaces represent these)

### 6. **Tangent Space in Manifolds**
T_p M E (m_p / m_p≤)* where m_p = ideal of functions vanishing at p
This is representability in derived setting

### 7. **Scheme Points**
Spec(R): Hom(-,Spec(R)) represents points of scheme
Yoneda: points are functors from finitely-generated algebras

### 8. **Tensor Product is Representable**
M ó_R N represents: Hom(-, M ó_R N) E Bilinear maps

### 9. **Determinant as Representable Functor**
det: GL_n(R) í R* is represented by the universal matrix

### 10. **Moduli Spaces as Representing Objects**
Moduli of curves M_g: Hom(-,M_g) = families of curves over -
Yoneda: moduli spaces represent universal families

### 11. **Stone Duality**
Spec(Boolean algebra) E representation by Boolean algebra operations
Boolean algebras are representable in topological spaces

### 12. **Eilenberg-MacLane Spaces**
K(G,n): Hom(-, K(G,n)) E H^n(-, G)
Cohomology is representable by topological spaces

## Three Consequences

### Consequence 1: Density Theorem
**Every presheaf is a colimit of representables**.

```
F  [C^op, Set] = colim_{Hom(c,-) í F} Hom(c,-)
```

where the colimit is over the **category of elements** (c, x) where c  C and x  F(c).

### Consequence 2: Functors Determine Each Other via Hom
If two functors F, G: C^op í Set satisfy:
```
Hom(Y_C(A), F) E Hom(Y_C(A), G) for all A  C
```
(where Y_C(A) = Hom(-,A)), then F E G.

This is because every presheaf is a colimit of representables, and Hom commutes with limits.

### Consequence 3: The Yoneda Embedding is Dense
The image of y: C í [C^op, Set] is **dense**: every presheaf is a colimit of representables.

## The Converse (Co-Yoneda)

**Lemma (Duality)**: For contravariant F (F: C í Set), similarly:
```
Nat(Hom(A,-), F) E F(A)
```

with the covariant version of composition.

This is why **left/right Kan extensions are dual**.

## Study Checklist

- [ ] Understand the Yoneda lemma statement word-by-word
- [ ] Verify it in 3-4 concrete examples (representable functors)
- [ ] Understand why the bijection is natural
- [ ] Know the Yoneda embedding and why it's fully faithful
- [ ] Understand density theorem (colimit of representables)
- [ ] Connect to Kan extensions (representables as Kan extensions)

## Key Insight

The Yoneda lemma says: **Morphisms and natural transformations freely determine functors.**

This is why Kan extensions exist: they're asking "What's the universal way to extend a functor?" The answer is determined by the Yoneda lemma structure.

Every representable functor is a **right Kan extension** of the identity functor. Understanding Yoneda deeply means understanding why Kan extensions work.

## Relation to Kan Extensions

The Yoneda lemma is the **simplest case** of Kan extension theory:
- Hom(-,A) is obtained by Kan extending along the Yoneda embedding
- The natural isomorphism in Yoneda is the universal property of this Kan extension
- The density theorem (colimit of representables) is the **density theorem for Kan extensions**

In fact: **Yoneda lemma = Kan extension in the category [C^op, Set]**.

This is why mastering Yoneda is essential preparation for Kan extensions.
