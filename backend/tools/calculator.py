
import ast
import operator


class Calculator:

    OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    def calculate(self, expression):

        try:

            tree = ast.parse(
                expression,
                mode="eval"
            )

            result = self._evaluate(
                tree.body
            )

            return result

        except Exception as error:

            raise ValueError(
                "Invalid mathematical expression."
            ) from error

    def _evaluate(self, node):

        if isinstance(node, ast.Constant):

            if isinstance(node.value, (int, float)):
                return node.value

            raise ValueError(
                "Only numbers are allowed."
            )

        if isinstance(node, ast.BinOp):

            operator_type = type(node.op)

            if operator_type not in self.OPERATORS:
                raise ValueError(
                    "Unsupported operator."
                )

            left = self._evaluate(node.left)

            right = self._evaluate(node.right)

            if isinstance(node.op, ast.Pow):
                if abs(right) > 100 or abs(left) > 1e100:
                    raise ValueError(
                        "Power operation is too large."
                    )

            return self.OPERATORS[
                operator_type
            ](left, right)

        if isinstance(node, ast.UnaryOp):

            operator_type = type(node.op)

            if operator_type not in self.OPERATORS:
                raise ValueError(
                    "Unsupported unary operator."
                )

            return self.OPERATORS[
                operator_type
            ](
                self._evaluate(node.operand)
            )

        raise ValueError(
            "Invalid mathematical expression."
        )
