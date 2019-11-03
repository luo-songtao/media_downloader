import asyncio
import functools

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor


class AsyncManager(object):
    __process_pool_executor = None
    __thread_pool_executor = None

    @classmethod
    def _get_or_create_process_pool_executor(cls, *args, **kwargs):
        cls.__process_pool_executor = cls.__process_pool_executor or ProcessPoolExecutor(*args, **kwargs)
        return cls.__process_pool_executor

    @classmethod
    def _get_or_create_thread_pool_executor(cls, *args, **kwargs):
        cls.__thread_pool_executor = cls.__thread_pool_executor or ThreadPoolExecutor(*args, **kwargs)
        return cls.__thread_pool_executor

    @classmethod
    def async_run_in_processing_pool(cls, loop=None, *executor_args, **executor_kwargs):
        """
        Attention: 本装饰器不能使用@符号进行装饰，
        example： wrapped_func_name = async_run_in_process_pool()(real_func)
        :param executor:
        :param loop:
        :param executor_args:
        :param executor_kwargs:
        :return:
        """
        loop = asyncio.get_event_loop() if loop is None else loop
        executor = cls._get_or_create_process_pool_executor(*executor_args, **executor_kwargs)

        def _async_run_in_process_pool(func):
            @functools.wraps(func)
            def inner_func(*args):
                return loop.run_in_executor(executor, func, *args)

            return inner_func

        return _async_run_in_process_pool

    @classmethod
    def async_run_in_threading_pool(cls, loop=None, *executor_args, **executor_kwargs):
        loop = asyncio.get_event_loop() if loop is None else loop
        executor = cls._get_or_create_thread_pool_executor(*executor_args, **executor_kwargs)

        def _async_run_in_thread_pool(func):
            @functools.wraps(func)
            def inner_func(*args):
                return loop.run_in_executor(executor, func, *args)

            return inner_func

        return _async_run_in_thread_pool

    @staticmethod
    def async_starter(entrance, loop=None):
        loop = asyncio.get_event_loop() if loop is None else loop
        @functools.wraps(entrance)
        def func(*args, **kwargs):
            loop.run_until_complete(entrance(*args, **kwargs))
        return func
