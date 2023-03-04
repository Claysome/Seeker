"""
@author: Claysome
@email: claysomes@outlook.com
"""


import time


class Timer:
    """Time counter"""
    def __init__(self):
        self.elapsed = 0

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop = time.perf_counter()
        self.elapsed = self.stop - self.start


# if __name__ == '__main__':
#     with Timer() as timer:
#         res = []
#         for i in range(1000):
#             res.append(i ** 2)
#
#     print(timer.elapsed)