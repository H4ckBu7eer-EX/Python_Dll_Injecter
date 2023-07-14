import sys
import threading
from ctypes import *
import psutil
from PyQt5.QtWidgets import QApplication
from PyQt5 import uic
from qt_material import apply_stylesheet


MB_OK=0x00000000
PAGE_READWRITE = 0x04
VORTUAL_MEM = (0x00001000 | 0x00002000)
PROCESS_ALL_ACCESS = (0xFFFF | 0x000F0000 | 0x00100000)
kernel32 = windll.kernel32
WriteLength = c_int(0)
User32=windll.user32

if __name__ == '__main__':

    def getprocesslist():
        process_list = []
        for proc in psutil.process_iter(['pid', 'name']):
            process_id = proc.info['pid']
            process_name = proc.info['name']
            process_list.append((process_name, process_id))
        textBrowser.append("=====Pr0cess_L1st=====")
        for process in process_list:
            textBrowser.append("|" + process[0] + "   " + str(process[1]) + "|")
            textBrowser.append("-----------------------------")

    def inject(ProcessId, Modulepath):
        textBrowser.append("Injecting...")
        hProcess = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, ProcessId)
        if not hProcess:
            textBrowser.append("OpenProcess失败")
        ModuleLength = (len(Modulepath) * 2)
        pAddress = kernel32.VirtualAllocEx(hProcess, 0, ModuleLength, VORTUAL_MEM, PAGE_READWRITE)
        if not pAddress:
            textBrowser.append("VirtualAllocEx失败")
        else:
            textBrowser.append("VirtualAllocEx_pAddress: " + str(pAddress))
        kernel32.WriteProcessMemory(hProcess, pAddress, Modulepath, ModuleLength, byref(WriteLength))

        hKernel32 = kernel32.GetModuleHandleW("kernel32.dll")
        hLoadLibrary = kernel32.GetProcAddress(hKernel32, b"LoadLibraryW")
        lpThreadID = c_ulong(0)
        hThread = kernel32.CreateRemoteThread(hProcess, None, 0, hLoadLibrary, pAddress, 0, byref((lpThreadID)))
        if not hThread:
            User32.MessageBoxW(None, "加载失败！", "Failed", MB_OK)
        else:
            User32.MessageBoxW(None, "加载成功! 模块地址:{}".format(pAddress), "Success", MB_OK)



    def inject_t(pid,dpath):
        t = threading.Thread(target=inject, args=(pid, dpath))
        t.start()


    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='dark_red.xml')
    ui = uic.loadUi("./untitled.ui")
    lineEdit = ui.lineEdit  # PID
    lineEdit_2 = ui.lineEdit_2  # dll path
    pushButton = ui.pushButton  # 进程列表
    pushButton_2 = ui.pushButton_2  # 加载
    textBrowser = ui.textBrowser  # 结果显示区

    pid = lineEdit.text()
    dpath = lineEdit_2.text()
    textBrowser.append("当前参数 PID:"+pid+" | dllpath:"+dpath)

    
    def on_pushButton_2_clicked():
        pid = lineEdit.text()
        dpath = lineEdit_2.text()
        textBrowser.append("当前参数 PID:" + pid + " | dllpath:" + dpath)
        inject_t(int(pid), dpath)

    pushButton_2.clicked.connect(on_pushButton_2_clicked)
    pushButton.clicked.connect(getprocesslist)

    #print(ui.__dict__)
    # 展示窗口
    ui.show()
    app.exec()