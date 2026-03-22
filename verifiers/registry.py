from verifiers.backtracking import BacktrackingVerifier
from verifiers.binary_search import BinarySearchVerifier
from verifiers.dp import DPVerifier
from verifiers.generic import GenericVerifier
from verifiers.generic_array_search import GenericArraySearchVerifier
from verifiers.graph import GraphVerifier
from verifiers.heap import HeapVerifier
from verifiers.interval import IntervalVerifier
from verifiers.linked_list import LinkedListVerifier
from verifiers.matrix import MatrixVerifier
from verifiers.max_subarray import MaxSubarrayVerifier
from verifiers.palindrome_string import PalindromeStringVerifier
from verifiers.sliding_window import SlidingWindowVerifier
from verifiers.tree import TreeVerifier
from verifiers.two_sum import TwoSumVerifier


def get_verifier(category: str):
    mapping = {
        "two_sum": TwoSumVerifier,
        "binary_search": BinarySearchVerifier,
        "sliding_window": SlidingWindowVerifier,
        "palindrome_string": PalindromeStringVerifier,
        "max_subarray": MaxSubarrayVerifier,
        "generic_array_search": GenericArraySearchVerifier,
        "linked_list": LinkedListVerifier,
        "tree": TreeVerifier,
        "graph": GraphVerifier,
        "heap": HeapVerifier,
        "interval": IntervalVerifier,
        "dp": DPVerifier,
        "backtracking": BacktrackingVerifier,
        "matrix": MatrixVerifier,
        "generic": GenericVerifier,
    }
    return mapping.get(category, GenericVerifier)()