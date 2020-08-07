def fun1():
    raise Exception("fun1 exception")


def fun2():
    fun1()
    # try:
    #     fun1()
    # except Exception as err:
    #     print("Error:", err)
    # fun1()

try:
    fun2()
except Exception as err:
    print("Error:", err)
