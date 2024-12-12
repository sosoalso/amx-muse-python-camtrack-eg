# ---------------------------------------------------------------------------- #
from camtrackpreset import CamtrackPreset
from lib_tp import tp_add_watcher, tp_set_button
from micmanager import MicManager
from mojo import context
from userdata import UserData

# ---------------------------------------------------------------------------- #
dv_muse = context.devices.get("idevice")
dv_mic = dv_muse.serial[0]
dv_tp = context.devices.get("AMX-10003")

# ---------------------------------------------------------------------------- #
camtrack_preset = CamtrackPreset(max_preset_index=40)
mic_manager = MicManager(max_mic_index=40, last_mic_enabled=False)
user_data = UserData()
# ---------------------------------------------------------------------------- #
camtrackEnabled = user_data.get_value("camtrackEnabled") or False
# ---------------------------------------------------------------------------- #


# 실제 카메라 프리셋 리콜 동작 넣기
def cam_recall_preset(index_cam, index_preset):
    print(f"cam_recall_preset {index_cam=}, {index_preset=}")


# ---------------------------------------------------------------------------- #


# 마이크가 켜졌을 때 동작
def handle_mic_on(mic_index):
    print(mic_manager.get_mic_status(mic_index))
    # 버튼 피드백 예시
    tp_set_button(dv_tp, 5, 10 + mic_index, mic_manager.get_mic_status(mic_index))
    # cam_recall_preset(cam, preset_no)
    # 카메라 트래킹 활성화 비활성화 변수 조절
    if camtrackEnabled is True:
        preset = camtrack_preset.get_preset(mic_index)
        index_cam = preset["camera"]
        index_preset = preset["preset"]
        print(f"handle_mic_on {index_cam=}, {index_preset=}")
        # 해당 카메라 프리셋 리콜 동작 넣기 예시
        cam_recall_preset(index_cam, index_preset)
    # ---------------------------------------------------------------------------- #


# 마이크가 꺼졌을 때 동작
def handle_mic_off(mic_index):
    print(mic_manager.get_mic_status(mic_index))
    preset = camtrack_preset.get_preset(mic_index)
    index_cam = preset["camera"]
    index_preset = preset["preset"]
    print(f"handle_mic_off {index_cam=}, {index_preset=}")
    # 버튼 피드백 예시
    tp_set_button(dv_tp, 5, 10 + mic_index, mic_manager.get_mic_status(mic_index))


# 모든 마이크가 꺼졌을 때 동작
def handle_mic_all_off():
    print("handle_mic_all_off")
    cam_recall_preset(3, 40)  # 초기값 프리셋 리콜 동작 넣기 예시
    # 버튼 피드백 예시
    for mic_index in range(1, 5):
        tp_set_button(dv_tp, 5, 10 + mic_index, mic_manager.get_mic_status(mic_index))


# ---------------------------------------------------------------------------- #
# 마이크 매니저에 마이크 켜짐/꺼짐 동작 시 발생하는 이벤트 핸들러 집어넣기기
def init_mic_manager(*args):
    # .turn_mic_on -> "on" 이벤트 발생 시 동작 집어넣기기
    mic_manager.add_event_handler("on", handle_mic_on)

    # .turn_mic_off -> "off" 이벤트 발생 시 동작 집어넣기기
    mic_manager.add_event_handler("off", handle_mic_off)

    # .all_off -> "off" 이벤트 발생 후 모든 마이크가 꺼져있으면 발생하는 동작 집어넣기기
    mic_manager.add_event_handler("all_off", handle_mic_all_off)


dv_muse.online(init_mic_manager)


# ---------------------------------------------------------------------------- #
# 실제 마이크 상태를 받아서 처리하는 곳
def handle_mic_receive(evt):
    received_message = evt.arguments["data"].decode()
    mic_idx = 0
    # 해당 마이크가 켜졌을 때 동작
    mic_manager.turn_mic_on(mic_idx)
    # 해당 마이크가 꺼졌을 때 동작
    mic_manager.turn_mic_off(mic_idx)


# 예시 - 시리얼 통신을 통해 마이크 상태를 받아서 처리
dv_mic.receive.listen(handle_mic_receive)


# 카메라 트래킹 활성화 비활성화 변수 조절
# ---------------------------------------------------------------------------- #
def enable_camtrack(evt):
    if evt.value:
        global camtrackEnabled
        print("enable_camtrack: ", enable_camtrack)
        camtrackEnabled = True
        user_data.set_value("camtrackEnabled", camtrackEnabled)
        ui_refresh_camtrack_enabled()


def disable_camtrack(evt):
    if evt.value:
        global camtrackEnabled
        print("disable_camtrack: ", disable_camtrack)
        camtrackEnabled = False
        user_data.set_value("camtrackEnabled", camtrackEnabled)
        ui_refresh_camtrack_enabled()


def ui_refresh_camtrack_enabled():
    tp_set_button(dv_tp, 5, 31, camtrackEnabled is True)
    tp_set_button(dv_tp, 5, 32, camtrackEnabled is False)


def handle_mic_on_button(evt, mic_idx):
    if evt.value:
        mic_manager.turn_mic_on(mic_idx)


def handle_mic_off_button(evt, mic_idx):
    if evt.value:
        mic_manager.turn_mic_off(mic_idx)


# ---------------------------------------------------------------------------- #


# ---------------------------------------------------------------------------- #
def tp_add_mic_on_off_test_button(*args):
    for index in range(11, 15):
        tp_add_watcher(dv_tp, 5, index, lambda evt, mic_index=index - 10: handle_mic_on_button(evt, mic_index))

    for index in range(21, 25):
        tp_add_watcher(dv_tp, 5, index, lambda evt, mic_index=index - 20: handle_mic_off_button(evt, mic_index))


# ---------------------------------------------------------------------------- #
dv_muse.online(tp_add_mic_on_off_test_button)


tp_add_watcher(dv_tp, 5, 31, enable_camtrack)
tp_add_watcher(dv_tp, 5, 32, disable_camtrack)


# ---------------------------------------------------------------------------- #
# 마이크 인덱스에 따른 카메라 번호 - 프리셋 리콜 번호 설정
camtrack_preset.set_preset(1, 1, 4)
camtrack_preset.set_preset(2, 2, 3)
camtrack_preset.set_preset(3, 3, 2)
camtrack_preset.set_preset(4, 4, 1)

# camtrackEnabled = True
# user_data.set_value("camtrackEnabled", camtrackEnabled)
ui_refresh_camtrack_enabled()

# ---------------------------------------------------------------------------- #
context.run(globals())
