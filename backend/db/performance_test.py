import time

start = time.time()
normal_query()
normal_time = time.time() - start

start = time.time()
optimized_query()
optimized_time = time.time() - start
