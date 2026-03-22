import multiprocessing as mp
import textwrap
from typing import Any, Dict, List, Tuple

from models.schemas import ExecutionReport


def _run_user_function(code: str, fn_name: str, args: tuple, queue):
    namespace: Dict[str, Any] = {}
    try:
        exec(textwrap.dedent(code), namespace)
        fn = namespace.get(fn_name)
        if fn is None:
            queue.put(("error", f"Function '{fn_name}' not found."))
            return
        result = fn(*args)
        queue.put(("ok", result))
    except Exception as e:
        queue.put(("error", repr(e)))


def run_with_timeout(code: str, fn_name: str, args: tuple, timeout: int = 2):
    queue = mp.Queue()
    proc = mp.Process(target=_run_user_function, args=(code, fn_name, args, queue))
    proc.start()
    proc.join(timeout)

    if proc.is_alive():
        proc.terminate()
        proc.join()
        return ("timeout", "Execution timed out.")

    if queue.empty():
        return ("error", "No result produced.")

    return queue.get()


class PythonExecutionRunner:
    def _tests_for_category(self, category: str) -> Tuple[str, List[Tuple[tuple, Any]]]:
        if category == "two_sum":
            return (
                "two_sum",
                [
                    ((([2, 7, 11, 15], 9)), lambda out: out in ([0, 1], [1, 0])),
                    ((([3, 2, 4], 6)), lambda out: out in ([1, 2], [2, 1])),
                    ((([], 5)), lambda out: out == []),
                ],
            )

        if category == "binary_search":
            return (
                "search",
                [
                    ((([], 3)), lambda out: out == -1),
                    ((([5], 5)), lambda out: out == 0),
                    ((([5], 4)), lambda out: out == -1),
                    ((([1, 3], 3)), lambda out: out == 1),
                    ((([1, 3, 5, 7], 6)), lambda out: out == -1),
                ],
            )

        if category == "palindrome_string":
            return (
                "is_palindrome",
                [
                    ((("A man, a plan, a canal: Panama",)), lambda out: out is True),
                    ((("race a car",)), lambda out: out is False),
                    ((("",)), lambda out: out is True),
                ],
            )

        if category == "max_subarray":
            return (
                "max_subarray",
                [
                    ((([-2,1,-3,4,-1,2,1,-5,4],)), lambda out: out == 6),
                    ((([1],)), lambda out: out == 1),
                    ((([-1,-2,-3],)), lambda out: out == -1),
                ],
            )

        if category == "generic_array_search":
            return (
                "search",
                [
                    ((([1, 3, 5], 3)), lambda out: out == 1),
                    ((([1, 3, 5], 2)), lambda out: out == -1),
                ],
            )

        return ("", [])

    def execute(self, category: str, code: str) -> ExecutionReport:
        fn_name, tests = self._tests_for_category(category)
        if not fn_name or not tests:
            return ExecutionReport(
                supported=False,
                verdict="revise",
                confidence=40,
                findings=["No runtime test suite configured for this category."],
                passed=0,
                total=0,
            )

        findings = []
        passed = 0
        total = len(tests)

        for args, checker in tests:
            status, result = run_with_timeout(code, fn_name, args, timeout=2)

            if status == "ok":
                try:
                    if checker(result):
                        passed += 1
                    else:
                        findings.append(f"Failed test for args={args}: got {result}")
                except Exception as e:
                    findings.append(f"Checker failed for args={args}: {e}")
            else:
                findings.append(f"{status} for args={args}: {result}")

        if passed == total:
            verdict = "accept"
            confidence = 95
        elif passed >= max(1, total - 1):
            verdict = "revise"
            confidence = 65
        else:
            verdict = "reject"
            confidence = 90

        if not findings:
            findings.append(f"Passed all {total} runtime tests.")

        return ExecutionReport(
            supported=True,
            verdict=verdict,
            confidence=confidence,
            findings=findings,
            passed=passed,
            total=total,
        )