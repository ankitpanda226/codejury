from typing import Dict


class ProblemClassifier:
    def classify(self, problem: str, code: str) -> Dict[str, object]:
        text = f"{problem}\n{code}".lower()

        if "two numbers" in text and "target" in text and "indices" in text:
            return {
                "category": "two_sum",
                "confidence": 0.97,
                "tags": ["array", "pair_search", "hashmap_or_bruteforce"]
            }

        if "binary search" in text or ("sorted array" in text and "return the index" in text):
            return {
                "category": "binary_search",
                "confidence": 0.96,
                "tags": ["sorted_input", "search", "divide_and_conquer"]
            }

        if "palindrome" in text:
            return {
                "category": "palindrome_string",
                "confidence": 0.9,
                "tags": ["string", "two_pointers"]
            }

        if "maximum subarray" in text or "max subarray" in text:
            return {
                "category": "max_subarray",
                "confidence": 0.92,
                "tags": ["array", "dp", "kadane"]
            }

        if "sliding window" in text or ("substring" in text) or ("subarray" in text and "window" in text):
            return {
                "category": "sliding_window",
                "confidence": 0.8,
                "tags": ["array_or_string", "window"]
            }

        if "linked list" in text or "listnode" in text or "next pointer" in text:
            return {
                "category": "linked_list",
                "confidence": 0.88,
                "tags": ["linked_list"]
            }

        if "binary tree" in text or "tree node" in text or "treenode" in text:
            return {
                "category": "tree",
                "confidence": 0.88,
                "tags": ["tree", "dfs_or_bfs"]
            }

        if "graph" in text or "adjacency" in text or "bfs" in text or "dfs" in text:
            return {
                "category": "graph",
                "confidence": 0.84,
                "tags": ["graph", "traversal"]
            }

        if "priority queue" in text or "heap" in text or "min heap" in text or "max heap" in text:
            return {
                "category": "heap",
                "confidence": 0.85,
                "tags": ["heap", "priority_queue"]
            }

        if "interval" in text or "merge intervals" in text or "meeting rooms" in text:
            return {
                "category": "interval",
                "confidence": 0.84,
                "tags": ["interval", "sorting", "greedy"]
            }

        if "dynamic programming" in text or "memoization" in text or "tabulation" in text or " dp " in f" {text} ":
            return {
                "category": "dp",
                "confidence": 0.82,
                "tags": ["dp"]
            }

        if "backtracking" in text or "subsets" in text or "permutations" in text or "n-queens" in text or "combination sum" in text:
            return {
                "category": "backtracking",
                "confidence": 0.82,
                "tags": ["backtracking", "search"]
            }

        if "matrix" in text or "2d grid" in text or "grid" in text:
            return {
                "category": "matrix",
                "confidence": 0.8,
                "tags": ["matrix", "grid"]
            }

        if "search" in text and "array" in text:
            return {
                "category": "generic_array_search",
                "confidence": 0.68,
                "tags": ["array", "search"]
            }

        return {
            "category": "generic",
            "confidence": 0.5,
            "tags": ["generic"]
        }