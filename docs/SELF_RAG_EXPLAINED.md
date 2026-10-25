# Self-RAG-style reflection

Self-RAG is about deciding when to retrieve and reflecting on evidence and generated answers. Here, `evaluate_answer` checks whether evidence exists, whether answer tokens overlap the evidence, and whether question terms overlap the answer. It returns structured diagnostic fields and can recommend abstention.

The current evaluator is intentionally lightweight and is not a trained Self-RAG model, does not use the original reflection tokens, and does not perform reliable semantic entailment or contradiction detection. It is useful as an inspectable baseline only. A production upgrade should use a calibrated claim-level verifier, adversarial evaluation, and human-labelled grounding tests. Do not treat its numeric score as a probability of truth.
