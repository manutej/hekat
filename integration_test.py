"""Integration test for all 8 HEKAT DSL patterns."""

from hekat_lexer import Lexer, TokenType

# Test all 8 abstract query types from implementation plan
queries = [
    ('Simple', 'agent : "prompt"'),
    ('Skilled', 'agent + skill : "prompt"'),
    ('Sequential', 'A -> B -> C : "prompt"'),
    ('Parallel', '(A || B || C) : "prompt"'),
    ('Mixed', 'A -> (B || C) -> D : "prompt"'),
    ('Fallback', 'A ? B ? C : "prompt"'),
    ('Ensemble', 'sample^3 ; merge ; synthesize : "prompt"'),
    ('Commanded', '@ctx7(agent) : "prompt"'),
]

print('HEKAT DSL Lexer - Integration Test')
print('=' * 60)
print()

for pattern_name, dsl in queries:
    lexer = Lexer(dsl)
    tokens = lexer.tokenize()
    token_count = len([t for t in tokens if t.type != TokenType.EOF])
    print(f'✓ {pattern_name:12} - {token_count:2} tokens - {dsl}')

print()
print('=' * 60)
print('✅ ALL 8 PATTERNS TOKENIZE SUCCESSFULLY')
print('=' * 60)
