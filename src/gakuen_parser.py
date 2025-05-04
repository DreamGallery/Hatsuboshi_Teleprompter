from typing import Any, List


def parse_identifier(message, i):
    j = i
    while message[i].isalnum() or message[i] == "_":
        i = i + 1
    return i, message[j:i]


def parse_string(message, i):
    j = i
    n = 0
    while n != 0 or (message[i] != "=" and message[i] != "]"):
        if message[i] == "\\":
            i = i + 1
            if message[i] == "{":
                n = n + 1
            elif message[i] == "}":
                n = n - 1
                if n < 0:
                    raise ValueError()
        i = i + 1
    if message[i] == "=":
        i = i - 1
        while message[i] != " ":
            i = i - 1
    return i, message[j:i]


def parse_object(message, i):
    if message[i] != "[":
        raise ValueError()
    i = i + 1
    i, tag = parse_identifier(message, i)
    obj = {"__tag__": tag}
    while message[i] != "]":
        if message[i] != " ":
            raise ValueError()
        i = i + 1
        i, key = parse_identifier(message, i)
        if key == "__tag__":
            raise ValueError()
        if message[i] != "=":
            raise ValueError()
        i = i + 1
        if message[i] == "[":
            i, value = parse_object(message, i)
        else:
            i, value = parse_string(message, i)
        if key not in obj:
            obj[key] = value
        elif type(obj[key]) is list:
            obj[key].append(value)
        else:
            obj[key] = [obj[key], value]
    if message[i] != "]":
        raise ValueError()
    i = i + 1
    return i, obj


def parse_message(message):
    i, o = parse_object(message, 0)
    if i != len(message):
        raise ValueError()
    return o


def parse_messages(messages: str) -> List[dict[str, Any]]:
    return [
        parse_message(message) for message in messages.split("\n") if message.strip()
    ]


def encode_message_kv(k, v):
    if k == "__tag__":
        if type(v) is not str:
            raise ValueError()
        return v
    if type(v) is list:
        return " ".join([encode_message_kv(k, w) for w in v])
    if type(v) is str:
        return f"{k}={v}"
    if type(v) is not dict:
        return ValueError()
    if "__tag__" not in v:
        raise ValueError()
    return f"{k}={encode_message(v)}"


def encode_message(obj):
    return (
        "["
        + " ".join(
            [obj["__tag__"]]
            + [encode_message_kv(k, v) for k, v in obj.items() if k != "__tag__"]
        )
        + "]"
    )


def encode_messages(objs) -> str:
    return "\n".join(encode_message(obj) for obj in objs)
