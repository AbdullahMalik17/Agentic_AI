from functools import wraps
import time

def advanced_decorator(retry_count=3, delay=1, log_execution_time=False):
    """
    A highly customizable decorator that supports:
    - Retry logic with a specified number of retries and delay.
    - Logging the execution time of the decorated function.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = retry_count
            while retries > 0:
                try:
                    if log_execution_time:
                        start_time = time.time()
                    
                    result = func(*args, **kwargs)
                    
                    if log_execution_time:
                        end_time = time.time()
                        print(f"Execution time for {func.__name__}: {end_time - start_time:.4f} seconds")
                    
                    return result
                except Exception as e:
                    retries -= 1
                    print(f"Error: {e}. Retrying {retries} more time(s)...")
                    time.sleep(delay)
                    if retries == 0:
                        print(f"Function {func.__name__} failed after {retry_count} retries.")
                        raise
        return wrapper
    return decorator

# Example usage
@advanced_decorator(retry_count=3, delay=2, log_execution_time=True)
def risky_function(x):
    if x < 0:
        raise ValueError("Negative value not allowed!")
    return x ** 2

if __name__ == "__main__":
    try:
        print(risky_function(-5))
    except Exception as e:
        print(f"Final exception: {e}")