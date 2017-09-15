from winreg import EnumKey, EnumValue

# 所有子键生成器
def keys(pkey):
    i = 0
    while 1:
        try:
            key = EnumKey(pkey, i); i += 1
            yield key
        except OSError:
            break
# 所有键值生成器
def values(key):
    i = 0
    while 1:
        try:
            value = EnumValue(key, i); i += 1
            yield value
        except OSError:
            break
