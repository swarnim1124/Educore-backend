"""
LibCST-based source editor for CRUD-style method operations on a primary class.
"""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent, indent
from typing import Sequence

import libcst as cst


class CodeEditor:
    """
    Edit methods on the primary top-level class in a Python source file.

    The editor parses the file once on construction, applies LibCST-only
    transformations in memory, and writes the updated source back on `save()`.
    """

    def __init__(self, file_path: str | Path) -> None:
        self.file_path = Path(file_path)

        if not self.file_path.is_file():
            raise FileNotFoundError(f"Python file does not exist: {self.file_path}")

        self.original_source = self.file_path.read_text(encoding="utf-8")
        self.tree = cst.parse_module(self.original_source)

    def save(self) -> None:
        """Persist the current LibCST tree back to disk."""
        self.file_path.write_text(self.tree.code, encoding="utf-8")

    def create_class(self, class_source: str) -> None:
        """
        Parse and append a top-level class definition to the module.

        Raises:
            ValueError: If the supplied source is invalid, does not parse to a
                single class definition, or a class with the same name already
                exists in the module.
        """

        new_class = self.build_class_node(class_source)
        self.ensure_class_missing(new_class.name.value)

        transformer = AppendClassTransformer(
            class_node=new_class,
            class_leading_lines=self.infer_class_leading_lines(),
        )
        self.tree = self.tree.visit(transformer)

    def create_method(
        self,
        method_name: str,
        parameters: Sequence[str],
        body: str,
        docstring: str | None = None,
    ) -> None:
        """
        Create a new method on the primary class as its last method.

        Raises:
            ValueError: If the method already exists or the generated method is
                not valid Python.
        """

        class_def = self.get_primary_class()
        self.ensure_method_missing(class_def, method_name)

        new_method = self.build_method_node(
            method_name=method_name,
            parameters=parameters,
            body=body,
            docstring=docstring,
        )
        transformer = AppendMethodTransformer(
            class_name=class_def.name.value,
            method_node=new_method,
            method_leading_lines=self.infer_method_leading_lines(class_def),
        )
        self.tree = self.tree.visit(transformer)

    def rename_method(self, old_name: str, new_name: str) -> None:
        """
        Rename a method definition on the primary class.

        Only the method definition name is changed. Method calls and variables
        are left untouched.
        """

        class_def = self.get_primary_class()
        self.ensure_method_exists(class_def, old_name)
        self.ensure_method_missing(class_def, new_name)

        transformer = RenameMethodTransformer(
            class_name=class_def.name.value,
            old_name=old_name,
            new_name=new_name,
        )
        self.tree = self.tree.visit(transformer)

    def delete_method(self, method_name: str) -> None:
        """Delete a method from the primary class."""

        class_def = self.get_primary_class()
        self.ensure_method_exists(class_def, method_name)

        transformer = DeleteMethodTransformer(
            class_name=class_def.name.value,
            method_name=method_name,
        )
        self.tree = self.tree.visit(transformer)

    def get_primary_class(self) -> cst.ClassDef:
        class_defs = [
            statement
            for statement in self.tree.body
            if isinstance(statement, cst.ClassDef)
        ]

        if len(class_defs) != 1:
            raise ValueError(
                "Expected exactly one top-level primary class in the Python file."
            )

        return class_defs[0]

    def get_module_classes(self) -> list[cst.ClassDef]:
        """Return all top-level classes defined in the module."""
        return [
            statement
            for statement in self.tree.body
            if isinstance(statement, cst.ClassDef)
        ]

    def get_module_class_names(self) -> set[str]:
        """Return the names of all top-level classes defined in the module."""
        return {class_def.name.value for class_def in self.get_module_classes()}

    def ensure_class_missing(self, class_name: str) -> None:
        """Raise if a top-level class with the given name already exists."""
        if class_name in self.get_module_class_names():
            raise ValueError(f"Class '{class_name}' already exists.")

    def get_class_method_names(self, class_def: cst.ClassDef) -> set[str]:
        return {
            statement.name.value
            for statement in class_def.body.body
            if isinstance(statement, cst.FunctionDef)
        }

    def ensure_method_exists(self, class_def: cst.ClassDef, method_name: str) -> None:
        if method_name not in self.get_class_method_names(class_def):
            raise ValueError(f"Method '{method_name}' does not exist.")

    def ensure_method_missing(self, class_def: cst.ClassDef, method_name: str) -> None:
        if method_name in self.get_class_method_names(class_def):
            raise ValueError(f"Method '{method_name}' already exists.")

    def infer_method_leading_lines(
        self, class_def: cst.ClassDef
    ) -> tuple[cst.EmptyLine, ...]:
        for statement in class_def.body.body:
            if isinstance(statement, cst.FunctionDef) and statement.leading_lines:
                return tuple(statement.leading_lines)

        if class_def.body.body:
            return (cst.EmptyLine(),)

        return ()

    def infer_class_leading_lines(self) -> tuple[cst.EmptyLine, ...]:
        """
        Infer blank-line spacing for a newly appended top-level class.
        """
        for statement in self.tree.body:
            if isinstance(statement, cst.ClassDef) and statement.leading_lines:
                return tuple(statement.leading_lines)

        if self.tree.body:
            return (cst.EmptyLine(), cst.EmptyLine())

        return ()

    def build_class_node(self, class_source: str) -> cst.ClassDef:
        """
        Parse the supplied source and return a top-level ClassDef node.
        """
        try:
            parsed = cst.parse_module(dedent(class_source).strip())
        except cst.ParserSyntaxError as exc:
            raise ValueError(f"Unable to create class: {exc}") from exc

        if len(parsed.body) != 1:
            raise ValueError(
                "Supplied class source must contain exactly one top-level class definition."
            )

        statement = parsed.body[0]
        if not isinstance(statement, cst.ClassDef):
            raise ValueError("Supplied source must be a top-level class definition.")

        return statement

    def build_method_node(
        self,
        method_name: str,
        parameters: Sequence[str],
        body: str,
        docstring: str | None,
    ) -> cst.FunctionDef:
        signature_parts = ["sel"]
        signature_parts.extend(self.normalize_parameters(parameters))
        signature = ", ".join(signature_parts)

        method_body = self.compose_method_body(body=body, docstring=docstring)
        method_source = f"def {method_name}({signature}):\n{method_body}\n"

        try:
            parsed = cst.parse_module(method_source)
        except cst.ParserSyntaxError as exc:
            raise ValueError(f"Unable to create method '{method_name}': {exc}") from exc

        statement = parsed.body[0]
        if not isinstance(statement, cst.FunctionDef):
            raise ValueError(f"Generated method '{method_name}' is not a function.")

        return statement

    def normalize_parameters(self, parameters: Sequence[str]) -> list[str]:
        normalized: list[str] = []

        for parameter in parameters:
            cleaned = parameter.strip()
            if not cleaned or cleaned == "sel":
                continue
            normalized.append(cleaned)

        return normalized

    def compose_method_body(self, body: str, docstring: str | None) -> str:
        statements: list[str] = []

        if docstring is not None:
            statements.append(self.format_docstring_literal(docstring))

        cleaned_body = dedent(body).strip("\n")
        if cleaned_body:
            statements.append(cleaned_body)

        if not statements:
            statements.append("pass")

        return indent("\n\n".join(statements), "    ")

    def format_docstring_literal(self, docstring: str) -> str:
        escaped = docstring.replace('"""', '\\"\\"\\"')
        return f'"""{escaped}"""'

    def create_variable(self, variable_name: str, value) -> None:
        """Create a new class variable on the primary class."""
        class_def = self.get_primary_class()
        self.ensure_variable_missing(class_def, variable_name)

        new_variable = self.build_variable_node(variable_name, value)
        transformer = AppendVariableTransformer(
            class_name=class_def.name.value,
            variable_node=new_variable,
        )
        self.tree = self.tree.visit(transformer)

    def read_variable(self, variable_name: str):
        """Read the value of a class variable."""
        class_def = self.get_primary_class()
        self.ensure_variable_exists(class_def, variable_name)

        for statement in class_def.body.body:
            if isinstance(statement, cst.SimpleStatementLine):
                for element in statement.body:
                    if isinstance(element, cst.Assign):
                        for target in element.targets:
                            if (
                                isinstance(target.target, cst.Name)
                                and target.target.value == variable_name
                            ):
                                return self.extract_variable_value(element.value)
        raise ValueError(f"Variable '{variable_name}' not found.")

    def read_all_variables(self) -> dict:
        """Read all class variables defined in the primary class."""
        class_def = self.get_primary_class()

        variables = {}
        for statement in class_def.body.body:
            if isinstance(statement, cst.SimpleStatementLine):
                for element in statement.body:
                    if isinstance(element, cst.Assign):
                        for target in element.targets:
                            if isinstance(target.target, cst.Name):
                                variables[target.target.value] = (
                                    self.extract_variable_value(element.value)
                                )
        return variables

    def update_variable(self, variable_name: str, value) -> None:
        """Update the value of an existing class variable."""
        class_def = self.get_primary_class()
        self.ensure_variable_exists(class_def, variable_name)

        try:
            new_value_node = cst.parse_expression(repr(value))
        except cst.ParserSyntaxError as exc:
            raise ValueError(f"Unable to parse value: {exc}") from exc

        transformer = UpdateVariableTransformer(
            class_name=class_def.name.value,
            variable_name=variable_name,
            new_value_node=new_value_node,
        )
        self.tree = self.tree.visit(transformer)

    def rename_variable(self, old_name: str, new_name: str) -> None:
        """Rename an existing class variable."""
        class_def = self.get_primary_class()
        self.ensure_variable_exists(class_def, old_name)
        self.ensure_variable_missing(class_def, new_name)

        transformer = RenameVariableTransformer(
            class_name=class_def.name.value,
            old_name=old_name,
            new_name=new_name,
        )
        self.tree = self.tree.visit(transformer)

    def delete_variable(self, variable_name: str) -> None:
        """Delete a class variable from the primary class."""
        class_def = self.get_primary_class()
        self.ensure_variable_exists(class_def, variable_name)

        transformer = DeleteVariableTransformer(
            class_name=class_def.name.value,
            variable_name=variable_name,
        )
        self.tree = self.tree.visit(transformer)

    def get_class_variable_names(self, class_def: cst.ClassDef) -> set[str]:
        """Return the names of all class variables defined in a class."""
        variables = set()
        for statement in class_def.body.body:
            if isinstance(statement, cst.SimpleStatementLine):
                for element in statement.body:
                    if isinstance(element, cst.Assign):
                        for target in element.targets:
                            if isinstance(target.target, cst.Name):
                                variables.add(target.target.value)
        return variables

    def ensure_variable_exists(
        self, class_def: cst.ClassDef, variable_name: str
    ) -> None:
        if variable_name not in self.get_class_variable_names(class_def):
            raise ValueError(f"Variable '{variable_name}' does not exist.")

    def ensure_variable_missing(
        self, class_def: cst.ClassDef, variable_name: str
    ) -> None:
        if variable_name in self.get_class_variable_names(class_def):
            raise ValueError(f"Variable '{variable_name}' already exists.")

    def build_variable_node(self, variable_name: str, value) -> cst.SimpleStatementLine:
        """Build a CST node for a class variable assignment."""
        try:
            value_node = cst.parse_expression(repr(value))
        except cst.ParserSyntaxError as exc:
            raise ValueError(f"Unable to parse value: {exc}") from exc

        return cst.SimpleStatementLine(
            body=[
                cst.Assign(
                    targets=[cst.AssignTarget(target=cst.Name(variable_name))],
                    value=value_node,
                )
            ]
        )

    def extract_variable_value(self, node: cst.BaseExpression):
        """Extract a Python value from a LibCST expression node."""
        mod = cst.Module([])
        code = mod.code_for_node(node)
        return eval(code)


class ClassMethodTransformer(cst.CSTTransformer):
    """Base transformer that applies updates only to the selected class."""

    def __init__(self, class_name: str) -> None:
        self.class_name = class_name

    def is_target_class(self, node: cst.ClassDef) -> bool:
        return node.name.value == self.class_name


class AppendClassTransformer(cst.CSTTransformer):
    def __init__(
        self,
        class_node: cst.ClassDef,
        class_leading_lines: Sequence[cst.EmptyLine],
    ) -> None:
        self.class_node = class_node
        self.class_leading_lines = tuple(class_leading_lines)

    def leave_Module(
        self, original_node: cst.Module, updated_node: cst.Module
    ) -> cst.Module:
        appended_class = self.class_node.with_changes(
            leading_lines=self.class_leading_lines
        )
        return updated_node.with_changes(body=(*updated_node.body, appended_class))


class AppendMethodTransformer(ClassMethodTransformer):
    def __init__(
        self,
        class_name: str,
        method_node: cst.FunctionDef,
        method_leading_lines: Sequence[cst.EmptyLine],
    ) -> None:
        super().__init__(class_name)
        self.method_node = method_node
        self.method_leading_lines = tuple(method_leading_lines)

    def leave_ClassDef(
        self, original_node: cst.ClassDef, updated_node: cst.ClassDef
    ) -> cst.ClassDef:
        if not self.is_target_class(original_node):
            return updated_node

        appended_method = self.method_node.with_changes(
            leading_lines=self.method_leading_lines
        )
        updated_body = updated_node.body.with_changes(
            body=(*updated_node.body.body, appended_method)
        )
        return updated_node.with_changes(body=updated_body)


class RenameMethodTransformer(ClassMethodTransformer):
    def __init__(self, class_name: str, old_name: str, new_name: str) -> None:
        super().__init__(class_name)
        self.old_name = old_name
        self.new_name = new_name

    def leave_ClassDef(
        self, original_node: cst.ClassDef, updated_node: cst.ClassDef
    ) -> cst.ClassDef:
        if not self.is_target_class(original_node):
            return updated_node

        updated_statements = []
        for statement in updated_node.body.body:
            if (
                isinstance(statement, cst.FunctionDef)
                and statement.name.value == self.old_name
            ):
                statement = statement.with_changes(name=cst.Name(self.new_name))
            updated_statements.append(statement)

        updated_body = updated_node.body.with_changes(body=tuple(updated_statements))
        return updated_node.with_changes(body=updated_body)


class DeleteMethodTransformer(ClassMethodTransformer):
    def __init__(self, class_name: str, method_name: str) -> None:
        super().__init__(class_name)
        self.method_name = method_name

    def leave_ClassDef(
        self, original_node: cst.ClassDef, updated_node: cst.ClassDef
    ) -> cst.ClassDef:
        if not self.is_target_class(original_node):
            return updated_node

        remaining_statements = tuple(
            statement
            for statement in updated_node.body.body
            if not (
                isinstance(statement, cst.FunctionDef)
                and statement.name.value == self.method_name
            )
        )
        updated_body = updated_node.body.with_changes(body=remaining_statements)
        return updated_node.with_changes(body=updated_body)


class AppendVariableTransformer(ClassMethodTransformer):
    def __init__(
        self,
        class_name: str,
        variable_node: cst.SimpleStatementLine,
    ) -> None:
        super().__init__(class_name)
        self.variable_node = variable_node

    def leave_ClassDef(
        self, original_node: cst.ClassDef, updated_node: cst.ClassDef
    ) -> cst.ClassDef:
        if not self.is_target_class(original_node):
            return updated_node

        insert_idx = 0
        for i, statement in enumerate(updated_node.body.body):
            if isinstance(statement, cst.FunctionDef):
                break
            insert_idx = i + 1

        new_body = list(updated_node.body.body)
        new_body.insert(insert_idx, self.variable_node)

        updated_body = updated_node.body.with_changes(body=tuple(new_body))
        return updated_node.with_changes(body=updated_body)


class UpdateVariableTransformer(ClassMethodTransformer):
    def __init__(
        self, class_name: str, variable_name: str, new_value_node: cst.BaseExpression
    ) -> None:
        super().__init__(class_name)
        self.variable_name = variable_name
        self.new_value_node = new_value_node

    def leave_ClassDef(
        self, original_node: cst.ClassDef, updated_node: cst.ClassDef
    ) -> cst.ClassDef:
        if not self.is_target_class(original_node):
            return updated_node

        new_body = []
        for statement in updated_node.body.body:
            if isinstance(statement, cst.SimpleStatementLine):
                new_statement_body = []
                statement_changed = False
                for element in statement.body:
                    if isinstance(element, cst.Assign):
                        for target in element.targets:
                            if (
                                isinstance(target.target, cst.Name)
                                and target.target.value == self.variable_name
                            ):
                                element = element.with_changes(
                                    value=self.new_value_node
                                )
                                statement_changed = True
                                break
                    new_statement_body.append(element)

                if statement_changed:
                    statement = statement.with_changes(body=tuple(new_statement_body))
            new_body.append(statement)

        updated_body = updated_node.body.with_changes(body=tuple(new_body))
        return updated_node.with_changes(body=updated_body)


class DeleteVariableTransformer(ClassMethodTransformer):
    def __init__(self, class_name: str, variable_name: str) -> None:
        super().__init__(class_name)
        self.variable_name = variable_name

    def leave_ClassDef(
        self, original_node: cst.ClassDef, updated_node: cst.ClassDef
    ) -> cst.ClassDef:
        if not self.is_target_class(original_node):
            return updated_node

        new_body = []
        for statement in updated_node.body.body:
            if isinstance(statement, cst.SimpleStatementLine):
                new_statement_body = []
                for element in statement.body:
                    keep_element = True
                    if isinstance(element, cst.Assign):
                        for target in element.targets:
                            if (
                                isinstance(target.target, cst.Name)
                                and target.target.value == self.variable_name
                            ):
                                keep_element = False
                                break
                    if keep_element:
                        new_statement_body.append(element)

                if not new_statement_body:
                    continue
                elif len(new_statement_body) != len(statement.body):
                    statement = statement.with_changes(body=tuple(new_statement_body))

            new_body.append(statement)

        updated_body = updated_node.body.with_changes(body=tuple(new_body))
        return updated_node.with_changes(body=updated_body)


class RenameVariableTransformer(ClassMethodTransformer):
    def __init__(self, class_name: str, old_name: str, new_name: str) -> None:
        super().__init__(class_name)
        self.old_name = old_name
        self.new_name = new_name

    def leave_ClassDef(
        self, original_node: cst.ClassDef, updated_node: cst.ClassDef
    ) -> cst.ClassDef:
        if not self.is_target_class(original_node):
            return updated_node

        new_body = []
        for statement in updated_node.body.body:
            if isinstance(statement, cst.SimpleStatementLine):
                new_statement_body = []
                statement_changed = False
                for element in statement.body:
                    if isinstance(element, cst.Assign):
                        new_targets = []
                        for target in element.targets:
                            if (
                                isinstance(target.target, cst.Name)
                                and target.target.value == self.old_name
                            ):
                                new_targets.append(
                                    target.with_changes(target=cst.Name(self.new_name))
                                )
                                statement_changed = True
                            else:
                                new_targets.append(target)
                        if statement_changed:
                            element = element.with_changes(targets=tuple(new_targets))
                    new_statement_body.append(element)

                if statement_changed:
                    statement = statement.with_changes(body=tuple(new_statement_body))
            new_body.append(statement)

        updated_body = updated_node.body.with_changes(body=tuple(new_body))
        return updated_node.with_changes(body=updated_body)
