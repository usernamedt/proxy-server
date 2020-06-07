from thread_pool import ThreadPool


def test_thread_pool():
    """
    thread pool should be able to handle task processing
    """
    thread_pool = ThreadPool()
    result = []

    def populate_result_task():
        result.extend([i for i in range(0, 10)])
        return

    thread_pool.add_task(populate_result_task)
    thread_pool.tasks.join()
    thread_pool.terminate_all_workers()
    assert result == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]


def test_thread_pool_with_exception():
    """
    thread pool should be able to handle task processing
    even if there were exceptions in some tasks
    """
    thread_pool = ThreadPool()
    result = []

    def throw_ex_task():
        raise Exception()

    def populate_result_task():
        result.extend([i for i in range(0, 10)])
        return

    thread_pool.add_task(throw_ex_task)
    thread_pool.add_task(populate_result_task)

    thread_pool.tasks.join()
    thread_pool.terminate_all_workers()

    assert result == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
