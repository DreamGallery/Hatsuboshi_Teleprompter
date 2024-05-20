# import json

# config_line = '[message text=つ……つっかれたぁ～～～～～～～～～～～～～！ name=ことね clip=\{"_startTime":50.4069926726,"_duration":3.2666664124,"_clipIn":0.0,"_easeInDuration":0.0,"_easeOutDuration":0.0,"_blendInDuration":-1.0,"_blendOutDuration":-1.0,"_mixInEaseType":1,"_mixInCurve":\{"serializedVersion":"2","m_Curve":[],"m_PreInfinity":2,"m_PostInfinity":2,"m_RotationOrder":4\},"_mixOutEaseType":1,"_mixOutCurve":\{"serializedVersion":"2","m_Curve":[],"m_PreInfinity":2,"m_PostInfinity":2,"m_RotationOrder":4\},"_timeScale":1.0\}]'

# content = config_line[1:-1].split()
# category_key = content.pop(0)
# data={}
# for item in content:
#     key = item.split("=")[0]
#     if key == "clip":
#         value = json.loads(item.split("=")[1].replace("\\", ""))
#     else:
#         value = item.split("=")[1]
#     data[key] = value
# config_line_dict = {category_key:data}

# print(config_line_dict)

{
    "choicegroup": {
        "choices": [
            {"choice": {"text": "期待以上です"}},
            {"choice": {"text": "さすが咲季さん"}},
            {"choice": {"text": "感動しました"}},
        ],
        "clip": {
            "_startTime": 195.0800040046,
            "_duration": 1.0,
            "_clipIn": 0.0,
            "_easeInDuration": 0.0,
            "_easeOutDuration": 0.0,
            "_blendInDuration": -1.0,
            "_blendOutDuration": -1.0,
            "_mixInEaseType": 1,
            "_mixInCurve": {
                "serializedVersion": "2",
                "m_Curve": [],
                "m_PreInfinity": 2,
                "m_PostInfinity": 2,
                "m_RotationOrder": 4,
            },
            "_mixOutEaseType": 1,
            "_mixOutCurve": {
                "serializedVersion": "2",
                "m_Curve": [],
                "m_PreInfinity": 2,
                "m_PostInfinity": 2,
                "m_RotationOrder": 4,
            },
            "_timeScale": 1.0,
        },
    }
}
