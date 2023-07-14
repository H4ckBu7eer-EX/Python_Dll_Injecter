import sys
from ctypes import *
import psutil

GUI=False
MB_OK=0x00000000
PAGE_READWRITE = 0x04
VORTUAL_MEM = (0x00001000 | 0x00002000)
PROCESS_ALL_ACCESS = (0xFFFF | 0x000F0000 | 0x00100000)
kernel32 = windll.kernel32
WriteLength = c_int(0)
User32=windll.user32



def getprocesslist():
    process_list = []
    for proc in psutil.process_iter(['pid', 'name']):
        process_id = proc.info['pid']
        process_name = proc.info['name']
        process_list.append((process_name, process_id))
    return process_list


def inject(ProcessId, Modulepath="test.dll"):
    print("Injecting...")
    hProcess = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, ProcessId)
    if not hProcess:
        if GUI:
            pass
        else:
            print("OpenProcess失败")
            sys.exit(0)
    ModuleLength = (len(Modulepath) * 2)
    pAddress = kernel32.VirtualAllocEx(hProcess, 0, ModuleLength, VORTUAL_MEM, PAGE_READWRITE)
    if GUI:
        pass
    else:
        if not pAddress:
            print("VirtualAllocEx失败")
        else:
            print("VirtualAllocEx_pAddress: " + str(pAddress))
    kernel32.WriteProcessMemory(hProcess, pAddress, Modulepath, ModuleLength, byref(WriteLength))

    hKernel32=kernel32.GetModuleHandleW("kernel32.dll")
    hLoadLibrary=kernel32.GetProcAddress(hKernel32,b"LoadLibraryW")
    lpThreadID=c_ulong(0)
    hThread=kernel32.CreateRemoteThread(hProcess,None,0,hLoadLibrary,pAddress,0,byref((lpThreadID)))
    if not hThread:
        User32.MessageBoxW(None,"Failed","Failed",MB_OK)
    else:
        User32.MessageBoxW(None, "Success! Addr:{}".format(pAddress), "Success", MB_OK)

if __name__ == '__main__':
    print("=====DLL_LOader=====")
    #inject(1234,"C:\\test.dll")
    #inject(1234)
    process_list = getprocesslist()
    print("=====Pr0cess_L1st=====")
    for process in process_list:
        print("|"+process[0]+"   "+str(process[1])+"|")
        print("-------------------")
    pid=input("输入进程ID：")
    dpath=input("输入DLL路径：")
    inject(pid,dpath)
