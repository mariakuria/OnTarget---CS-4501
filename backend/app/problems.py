"""The coding-problem catalog (hardcoded for Alpha)."""
from pydantic import BaseModel

LANGUAGES = ["Python", "Java", "C++", "JavaScript"]


class Example(BaseModel):
    input: str
    output: str


class ProblemSummary(BaseModel):
    id: str
    title: str
    difficulty: str


class Problem(ProblemSummary):
    topics: list[str]
    description: list[str]
    examples: list[Example]
    constraints: list[str]
    starter_code: dict[str, str]


# Function signatures used to build starter code in each language.
_SIGS = {
    "two-sum": dict(fn="twoSum", py="nums: list[int], target: int", py_ret="list[int]",
                    java="int[] nums, int target", java_ret="int[]",
                    cpp="vector<int>& nums, int target", cpp_ret="vector<int>", js="nums, target"),
    "top-k-words": dict(fn="topKFrequent", py="words: list[str], k: int", py_ret="list[str]",
                        java="String[] words, int k", java_ret="List<String>",
                        cpp="vector<string>& words, int k", cpp_ret="vector<string>", js="words, k"),
    "merge-intervals": dict(fn="merge", py="intervals: list[list[int]]", py_ret="list[list[int]]",
                            java="int[][] intervals", java_ret="int[][]",
                            cpp="vector<vector<int>>& intervals", cpp_ret="vector<vector<int>>", js="intervals"),
    "num-islands": dict(fn="numIslands", py="grid: list[list[str]]", py_ret="int",
                        java="char[][] grid", java_ret="int",
                        cpp="vector<vector<char>>& grid", cpp_ret="int", js="grid"),
    "rotting-oranges": dict(fn="orangesRotting", py="grid: list[list[int]]", py_ret="int",
                            java="int[][] grid", java_ret="int",
                            cpp="vector<vector<int>>& grid", cpp_ret="int", js="grid"),
    "meeting-rooms": dict(fn="minMeetingRooms", py="intervals: list[list[int]]", py_ret="int",
                          java="int[][] intervals", java_ret="int",
                          cpp="vector<vector<int>>& intervals", cpp_ret="int", js="intervals"),
    "trap-water": dict(fn="trap", py="height: list[int]", py_ret="int",
                       java="int[] height", java_ret="int",
                       cpp="vector<int>& height", cpp_ret="int", js="height"),
}


def _starter_code(problem_id: str) -> dict[str, str]:
    s = _SIGS[problem_id]
    return {
        "Python": f"class Solution:\n    def {s['fn']}(self, {s['py']}) -> {s['py_ret']}:\n        pass\n",
        "Java": f"class Solution {{\n    public {s['java_ret']} {s['fn']}({s['java']}) {{\n        \n    }}\n}}\n",
        "C++": f"class Solution {{\npublic:\n    {s['cpp_ret']} {s['fn']}({s['cpp']}) {{\n        \n    }}\n}};\n",
        "JavaScript": f"var {s['fn']} = function({s['js']}) {{\n    \n}};\n",
    }


def _p(id, title, difficulty, topics, description, examples, constraints) -> Problem:
    return Problem(
        id=id, title=title, difficulty=difficulty, topics=topics, description=description,
        examples=[Example(input=i, output=o) for i, o in examples],
        constraints=constraints, starter_code=_starter_code(id),
    )


_CATALOG = [
    _p("two-sum", "Two Sum", "Easy", ["Array", "Hash Table"],
       ["Given an array of integers nums and an integer target, return the indices of the two numbers that add up to target.",
        "Exactly one valid answer exists, and you may not use the same element twice. The answer can be in any order."],
       [("nums = [2,7,11,15], target = 9", "[0,1]"), ("nums = [3,2,4], target = 6", "[1,2]")],
       ["2 <= nums.length <= 10^4", "-10^9 <= nums[i] <= 10^9", "Exactly one valid answer exists"]),
    _p("top-k-words", "Top K Frequent Words", "Medium", ["Hash Table", "Heap", "Sorting"],
       ["Given an array of strings words and an integer k, return the k most frequent words.",
        "Sort the answer by frequency from highest to lowest. Words with the same frequency are sorted in alphabetical order."],
       [('words = ["i","love","leetcode","i","love","coding"], k = 2', '["i","love"]'),
        ('words = ["the","day","is","sunny","the","the","the","sunny","is","is"], k = 4', '["the","is","sunny","day"]')],
       ["1 <= words.length <= 500", "words[i] is lowercase English letters", "k is in [1, number of unique words]"]),
    _p("merge-intervals", "Merge Intervals", "Medium", ["Array", "Sorting"],
       ["Given an array of intervals where each interval is [start, end], merge all overlapping intervals.",
        "Return an array of the non-overlapping intervals that cover all the ranges in the input."],
       [("intervals = [[1,3],[2,6],[8,10],[15,18]]", "[[1,6],[8,10],[15,18]]"), ("intervals = [[1,4],[4,5]]", "[[1,5]]")],
       ["1 <= intervals.length <= 10^4", "intervals[i].length == 2", "0 <= start <= end <= 10^4"]),
    _p("num-islands", "Number of Islands", "Medium", ["Graph", "DFS", "Matrix"],
       ["Given an m x n grid of \"1\" (land) and \"0\" (water), return the number of islands.",
        "An island is surrounded by water and formed by connecting adjacent land cells horizontally or vertically."],
       [('grid = [["1","1","0"],["0","1","0"],["0","0","1"]]', "2"),
        ('grid = [["1","1","1"],["1","1","0"],["0","0","0"]]', "1")],
       ["1 <= m, n <= 300", "grid[i][j] is \"0\" or \"1\""]),
    _p("rotting-oranges", "Rotting Oranges", "Medium", ["BFS", "Matrix"],
       ["In a grid, 0 is an empty cell, 1 is a fresh orange, and 2 is a rotten orange.",
        "Every minute, any fresh orange next to a rotten one (up, down, left, right) becomes rotten. Return the minutes until no fresh orange remains, or -1 if that is impossible."],
       [("grid = [[2,1,1],[1,1,0],[0,1,1]]", "4"), ("grid = [[2,1,1],[0,1,1],[1,0,1]]", "-1")],
       ["1 <= m, n <= 10", "grid[i][j] is 0, 1, or 2"]),
    _p("meeting-rooms", "Meeting Rooms II", "Medium", ["Array", "Heap", "Sorting"],
       ["Given an array of meeting time intervals [start, end], return the minimum number of conference rooms required so that no two meetings overlap in the same room."],
       [("intervals = [[0,30],[5,10],[15,20]]", "2"), ("intervals = [[7,10],[2,4]]", "1")],
       ["1 <= intervals.length <= 10^4", "0 <= start < end <= 10^6"]),
    _p("trap-water", "Trapping Rain Water", "Hard", ["Array", "Two Pointers"],
       ["Given n non-negative integers representing an elevation map where each bar has width 1, compute how much water it can trap after raining."],
       [("height = [0,1,0,2,1,0,1,3,2,1,2,1]", "6"), ("height = [4,2,0,3,2,5]", "9")],
       ["n == height.length", "1 <= n <= 2 * 10^4", "0 <= height[i] <= 10^5"]),
]

PROBLEMS: dict[str, Problem] = {p.id: p for p in _CATALOG}
