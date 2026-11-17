REGISTRY = {}
def task(name):
    def register(fn):
        REGISTRY[name] = fn
        return fn
    return register

@task("add")
def add(a, b):
    return a + b

@task("greet")
def greet(name="there"):
    return f"Hello, {name}!"

@task("uppercase")
def uppercase(text):
    return text.upper()
