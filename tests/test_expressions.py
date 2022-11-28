from ado_pipeline_helper.expression import Visitor
import pytest


expressions = [
    ("${{ 1 }}", 1),
    ("${{ '1' }}", '1'),
    ("${{    1 }}", 1),
    ("${{1}}",1),
    ("${{ -1.0 }}", -1),
    ("${{ .01 }}", 0.01),
    ("${{ .01 }}",  0.01),
    ("${{ false }}", False),
    ("${{ True }}", True),
    ("${{ 'True' }}", 'True'),
    ("${{ 1.2.3.4 }}", "1.2.3.4"),
    ("${{ 1.2.3 }}",  "1.2.3"),
    ("${{ 1.2.3 }}", "1.2.3"),
    ("${{ and(1) }}", True),
    ("${{ and(1,2) }}", True),
    ("${{ and(1,2) }}",True),
    ("${{ variables['MyVar'] }}", 1),
    ("${{ variables.MyVar }}", 1), 
    ]

@pytest.mark.parametrize('expression,expected', expressions, ids = range(len(expressions)))

def test_visitor(expression, expected):
    refs = {'variables': {'MyVar': 1}}
    visitor = Visitor(refs)
    parsed = visitor.parse(expression)
    print(visitor.grammar.parse(expression))
    assert expected == parsed['val']
