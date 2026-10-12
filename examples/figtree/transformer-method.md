# Dual-Branch Transformer for Document Grounding

We propose a dual-branch encoder in which a Text Encoder and a Layout Encoder process the input
document in parallel before a Cross Attention block fuses their representations.

## Method

The pipeline is: Token Embedding → (Text Encoder || Layout Encoder) → Cross Attention → Feed Forward → Classifier.
A residual pathway is also used: Cross Attention → Residual Add → Feed Forward.
Dropout is described in the training section but is not connected to any module in the figure.

Input: document tokens, bounding boxes
Output: field labels
Notation: h_t, h_l, α
