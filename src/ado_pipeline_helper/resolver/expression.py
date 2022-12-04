import re
from typing import Optional

from parsimonious import NodeVisitor
from parsimonious.grammar import Grammar

from ado_pipeline_helper.resolver.parameters import Context
from ado_pipeline_helper.utils import listify

g = Grammar(
    r"""
expression = expression_open conditional? (loop / expr) expression_close
expression_open  = "${{" ws*
expression_close = ws* "}}"
expr = literal / function / reference
literal = version / boolean / number / string
number   = (("-"? ~"[0-9]"+ "."? ~"[0-9]"*) / ("-"?"." ~"[0-9]"+)) 
boolean = true / false
true = "true" / "True"
false = "false" / "False"
string_delimiter = "'"
string = string_delimiter ~"[\w]"+ string_delimiter
version   = major "." minor "." patch "."? fix?
major   = int+
minor   = int+
patch   = int+
fix   = int+
int = ~"[0-9]"
function = ws? function_name "(" function_argument* ")" ws?
function_argument = ws? expr ","? ws?
function_name = ~"\w"+
conditional = ws? ("elseif" / "else" / "if" ) ws?
loop = "each" ws+ ~"\w"+ ws+ "in" ws+ expr
ws          = ~"\s*"
reference = index_ref / prop_ref
prop_ref = var_name "." property_name
var_name = ~"[_a-zA-Z]"+
property_name = ~"[a-zA-Z_]" ~"[a-zA-Z0-9_]"+
index_ref = var_name "[" "'" property_name "'" "]"
"""
)

# An expression can be
# - a literal
# - a reference to a variable
# - a reference to a dependency
# - a function
# - a valid nested combination of these.


class ExpressionResolver(NodeVisitor):
    grammar = g

    def __init__(self, context: Context):
        self.context = context

    def generic_visit(self, node, visited_children):
        if len(visited_children) == 1:
            return visited_children[0]
        return visited_children

    def visit_number(self, node, visited_children):
        return float(node.text)

    def visit_string(self, node, visited_children):
        return node.children[1].text

    def visit_false(self, node, visited_children):
        return False

    def visit_true(self, node, visited_children):
        return True

    def visit_version(self, node, visited_children):
        return str(node.text)

    def visit_var_name(self, node, visited_children):
        return node.text

    def visit_property_name(self, node, visited_children):
        return node.text

    def visit_index_ref(self, node, visited_children):
        var_name = visited_children[0]
        property_name = visited_children[3]
        return self._get_parm_value(var_name, property_name)

    def visit_prop_ref(self, node, visited_children):
        var_name = visited_children[0]
        property_name = visited_children[2]
        return self._get_parm_value(var_name, property_name)

    def _get_parm_value(self, var_name: str, property_name: str):
        if var_name == "parameters":
            val = self.context.parameter_values.get(property_name)
            default = self.context.parameters.__root__[property_name].default
            return val or default
        elif var_name == "variables":
            if self.context.variables is None:
                raise ValueError(
                    f"Accessing variables.{property_name} but no variables have been set."
                )
            return self.context.variables[property_name]
        else:
            raise ValueError("Can only index into variables or parameters")

    def visit_literal(self, node, visited_children):
        return visited_children[0]  # text rule

    def visit_function_name(self, node, visited_children):
        return node.text

    def visit_function(self, node, visited_children):
        function_name = visited_children[1]
        arguments = listify(visited_children[3])
        func = AdoFunctions.get_func(function_name)
        return func(*arguments)

    def visit_function_argument(self, node, visited_children):
        return visited_children[1]

    def visit_expr(self, node, visited_children):
        return visited_children[0]

    def visit_expression(self, node, visited_children):
        return {
            "txt": node.text,
            "conditional": visited_children[1],
            "val": visited_children[2],
        }

    def evaluate(self, obj) -> dict:
        return self.parse(obj)

    @staticmethod
    def find_expression_in_string(input_str) -> Optional[str]:
        matches = re.findall(r"\${{.*?}}", input_str)
        if matches:
            return matches[0]
        else:
            return None


class AdoFunctions:
    @classmethod
    def get_func(cls, name: str):
        funcs = {"and": cls.and_, "coalesce": cls.coalesce, "contains": cls.contains}
        return funcs[name]

    @staticmethod
    def boolify(obj) -> bool:
        return bool(obj)

    @classmethod
    def and_(cls, *args):
        return all(cls.boolify(a) for a in args)

    @classmethod
    def coalesce(cls, *args):
        for arg in args:
            if not arg == "" and arg is None:
                return arg

    @classmethod
    def contains(cls, *args):
        return str(args[0]).lower() in str(args[1]).lower()
