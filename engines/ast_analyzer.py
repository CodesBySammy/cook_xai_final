import ast
from radon.complexity import cc_visit

class ASTAutoFixer(ast.NodeVisitor):
    def __init__(self):
        self.suggestions = []

    def visit_FunctionDef(self, node):
        for arg in node.args.defaults:
            if isinstance(arg, (ast.List, ast.Dict, ast.Set)):
                ticks = "```"
                self.suggestions.append(
                    f"**Line {node.lineno}**: 🐛 **STATE BUG** - Mutable default in `{node.name}()`.\n"
                    f"**💡 Auto-Fix:**\n{ticks}python\ndef {node.name}(data=None):\n    if data is None: data = []\n{ticks}"
                )
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        # Catches 'except Exception: pass' or 'except: pass'
        if node.type is None or (isinstance(node.type, ast.Name) and node.type.id == 'Exception'):
            for child in node.body:
                if isinstance(child, ast.Pass):
                    self.suggestions.append(f"**Line {node.lineno}**: 🚨 **RELIABILITY BUG** - Silent failure detected! Do not use `except: pass`. Log the error instead.")
        self.generic_visit(node)

class ASTEngine:
    def scan(self, raw_code: str, filename: str) -> str:
        report = ""
        try:
            for block in cc_visit(raw_code):
                # Lowered from 10 to 6 so it catches your demo script!
                if block.complexity >= 6:
                    report += f"* 🔴 **High Complexity ({block.complexity})**: Refactor `{block.name}`. Too many nested conditions.\n"
        except Exception: pass

        try:
            scanner = ASTAutoFixer()
            scanner.visit(ast.parse(raw_code))
            for suggestion in scanner.suggestions:
                report += f"* {suggestion}\n"
        except SyntaxError:
            report += "* ❌ **Syntax Error**: Invalid Python syntax.\n"
            
        return report

ast_engine = ASTEngine()