from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from app.core.config import PROJECT_ROOT
from app.schemas.prediction import RuleSeverity, TransactionRequest, TriggeredRule


DEFAULT_RULES_PATH = PROJECT_ROOT / "configs" / "rules.yaml"

ALLOWED_CONTEXT_NAMES = {
    "amount",
    "sender_balance",
    "receiver_balance",
    "amount_to_sender_balance_ratio",
    "channel",
    "currency",
    "timestamp_hour",
    "is_round_amount",
}


class RuleEngineError(ValueError):
    """Raised when rule configuration or evaluation is invalid."""


@dataclass(frozen=True)
class Rule:
    id: str
    typology: str
    severity: RuleSeverity
    enabled: bool
    condition: str
    action_hint: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Rule":
        required = {"id", "typology", "severity", "condition"}
        missing = required - set(data)
        if missing:
            raise RuleEngineError(f"Rule is missing required field(s): {sorted(missing)}")

        try:
            severity = RuleSeverity(str(data["severity"]).upper())
        except ValueError as exc:
            raise RuleEngineError(f"Invalid severity for rule {data.get('id')!r}.") from exc

        return cls(
            id=str(data["id"]),
            typology=str(data["typology"]),
            severity=severity,
            enabled=bool(data.get("enabled", True)),
            condition=str(data["condition"]),
            action_hint=data.get("action_hint"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "typology": self.typology,
            "severity": self.severity.value,
            "enabled": self.enabled,
            "condition": self.condition,
            "action_hint": self.action_hint,
        }


class SafeConditionEvaluator(ast.NodeVisitor):
    allowed_nodes = (
        ast.Expression,
        ast.BoolOp,
        ast.UnaryOp,
        ast.Compare,
        ast.Name,
        ast.Load,
        ast.Constant,
        ast.BinOp,
        ast.And,
        ast.Or,
        ast.Not,
        ast.Eq,
        ast.NotEq,
        ast.Lt,
        ast.LtE,
        ast.Gt,
        ast.GtE,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Mod,
    )

    def __init__(self, condition: str) -> None:
        self.condition = condition
        try:
            self.tree = ast.parse(condition, mode="eval")
        except SyntaxError as exc:
            raise RuleEngineError(f"Invalid rule condition syntax: {condition!r}") from exc
        self.visit(self.tree)

    def generic_visit(self, node: ast.AST) -> None:
        if not isinstance(node, self.allowed_nodes):
            raise RuleEngineError(
                f"Unsupported expression node in rule condition: {type(node).__name__}"
            )
        super().generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        if node.id not in ALLOWED_CONTEXT_NAMES:
            raise RuleEngineError(f"Unknown feature in rule condition: {node.id}")

    def evaluate(self, context: dict[str, Any]) -> bool:
        return bool(self._eval_node(self.tree.body, context))

    def _eval_node(self, node: ast.AST, context: dict[str, Any]) -> Any:
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Name):
            return context[node.id]
        if isinstance(node, ast.BoolOp):
            values = [self._eval_node(value, context) for value in node.values]
            if isinstance(node.op, ast.And):
                return all(values)
            if isinstance(node.op, ast.Or):
                return any(values)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            return not self._eval_node(node.operand, context)
        if isinstance(node, ast.BinOp):
            return self._eval_binop(node, context)
        if isinstance(node, ast.Compare):
            left = self._eval_node(node.left, context)
            for operator, comparator in zip(node.ops, node.comparators, strict=True):
                right = self._eval_node(comparator, context)
                if not self._compare(left, operator, right):
                    return False
                left = right
            return True

        raise RuleEngineError(f"Unsupported condition expression: {type(node).__name__}")

    def _eval_binop(self, node: ast.BinOp, context: dict[str, Any]) -> float:
        left = self._eval_node(node.left, context)
        right = self._eval_node(node.right, context)

        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            return left / right
        if isinstance(node.op, ast.Mod):
            return left % right

        raise RuleEngineError(f"Unsupported arithmetic operator: {type(node.op).__name__}")

    @staticmethod
    def _compare(left: Any, operator: ast.cmpop, right: Any) -> bool:
        if isinstance(operator, ast.Eq):
            return left == right
        if isinstance(operator, ast.NotEq):
            return left != right
        if isinstance(operator, ast.Lt):
            return left < right
        if isinstance(operator, ast.LtE):
            return left <= right
        if isinstance(operator, ast.Gt):
            return left > right
        if isinstance(operator, ast.GtE):
            return left >= right

        raise RuleEngineError(f"Unsupported comparison operator: {type(operator).__name__}")


@dataclass(frozen=True)
class CompiledRule:
    rule: Rule
    evaluator: SafeConditionEvaluator


class RuleEngine:
    def __init__(self, version: int, rules: list[Rule]) -> None:
        self.version = version
        self.rules = rules
        self._compiled_rules = [
            CompiledRule(rule=rule, evaluator=SafeConditionEvaluator(rule.condition))
            for rule in rules
        ]

    @classmethod
    def from_file(cls, path: Path = DEFAULT_RULES_PATH) -> "RuleEngine":
        if not path.exists():
            raise RuleEngineError(f"Rule file not found: {path}")

        raw_config = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(raw_config, dict):
            raise RuleEngineError("Rule file must contain a YAML object.")

        version = int(raw_config.get("version", 1))
        raw_rules = raw_config.get("rules", [])
        if not isinstance(raw_rules, list):
            raise RuleEngineError("rules must be a list.")

        rules = [Rule.from_dict(raw_rule) for raw_rule in raw_rules]
        cls._validate_unique_ids(rules)
        return cls(version=version, rules=rules)

    def evaluate(self, transaction: TransactionRequest) -> list[TriggeredRule]:
        context = build_rule_context(transaction)
        triggered_rules = []

        for compiled_rule in self._compiled_rules:
            rule = compiled_rule.rule
            if not rule.enabled:
                continue
            if compiled_rule.evaluator.evaluate(context):
                triggered_rules.append(
                    TriggeredRule(
                        id=rule.id,
                        severity=rule.severity,
                        typology=rule.typology,
                    )
                )

        return triggered_rules

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "rules": [rule.to_dict() for rule in self.rules],
        }

    @staticmethod
    def _validate_unique_ids(rules: list[Rule]) -> None:
        seen_ids = set()
        duplicate_ids = set()
        for rule in rules:
            if rule.id in seen_ids:
                duplicate_ids.add(rule.id)
            seen_ids.add(rule.id)

        if duplicate_ids:
            raise RuleEngineError(f"Duplicate rule id(s): {sorted(duplicate_ids)}")


class RuleEngineManager:
    def __init__(self, rules_path: Path = DEFAULT_RULES_PATH) -> None:
        self.rules_path = rules_path
        self._engine = RuleEngine.from_file(rules_path)

    @property
    def engine(self) -> RuleEngine:
        return self._engine

    def reload(self) -> RuleEngine:
        next_engine = RuleEngine.from_file(self.rules_path)
        self._engine = next_engine
        return self._engine


def build_rule_context(transaction: TransactionRequest) -> dict[str, Any]:
    sender_balance = transaction.sender_balance
    if sender_balance <= 0:
        amount_to_sender_balance_ratio = 1.0 if transaction.amount > 0 else 0.0
    else:
        amount_to_sender_balance_ratio = transaction.amount / sender_balance

    return {
        "amount": transaction.amount,
        "sender_balance": sender_balance,
        "receiver_balance": transaction.receiver_balance,
        "amount_to_sender_balance_ratio": amount_to_sender_balance_ratio,
        "channel": transaction.channel.value,
        "currency": transaction.currency,
        "timestamp_hour": transaction.timestamp.hour,
        "is_round_amount": transaction.amount > 0 and transaction.amount % 1_000_000 == 0,
    }


rule_engine_manager = RuleEngineManager()
